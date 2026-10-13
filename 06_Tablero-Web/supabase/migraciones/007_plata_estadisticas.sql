-- 007_plata_estadisticas.sql — Fase 3B
-- Plata (entregar efectivo, consignar) + estadísticas (real vs proyección) + ranking de vendedores.
-- Las fórmulas vienen de 04_Finanzas/modelo-financiero.xlsx (decisión 59):
--   EMPIEZA!C8  caso_malo        = pagados*precio - premio - premio_vendedor - gastos_varios
--   EMPIEZA!C10 faltan_al_piso   = max(0, ceil((piso+premio+premio_vend+varios)/precio) - pagados)
--   EMPIEZA!C12 llego_al_piso    = (caso_malo >= piso)
--   REGLA-PREMIO G al nivel N    = prob*neto_vendido + (1-prob)*neto_consolacion   (ver rifa.proyeccion_regla_premio)
-- Todo lee rifa.config: fuente única, nunca hardcoded en JS.

-- ────────── Helper: REGLA-PREMIO al nivel N vendidos ──────────

create or replace function rifa.proyeccion_regla_premio(p_vendidos int) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare
  v_total int; v_precio numeric; v_precio_nzd numeric; v_tasa numeric;
  v_premio numeric; v_premio_vend numeric; v_varios numeric;
  v_pct_nz numeric; v_pct_tiendas numeric; v_comision numeric;
  v_consolacion numeric; v_tizumba int; v_tizumba_costo numeric;
  v_prob numeric; v_nz int; v_tiendas int; v_directo int;
  v_ingreso numeric; v_costos numeric;
  v_neto_vendido numeric; v_neto_consolacion numeric; v_esperado numeric;
begin
  select (valor #>> '{}')::int     into v_total        from rifa.config where clave='total_numeros';
  select (valor #>> '{}')::numeric into v_precio       from rifa.config where clave='precio_cop';
  select (valor #>> '{}')::numeric into v_precio_nzd   from rifa.config where clave='precio_nzd';
  select (valor #>> '{}')::numeric into v_tasa         from rifa.config where clave='tasa_cop_nzd';
  select (valor #>> '{}')::numeric into v_premio       from rifa.config where clave='premio';
  select (valor #>> '{}')::numeric into v_premio_vend  from rifa.config where clave='premio_vendedor';
  select (valor #>> '{}')::numeric into v_varios       from rifa.config where clave='gastos_varios';
  select (valor #>> '{}')::numeric into v_pct_nz       from rifa.config where clave='pct_nz';
  select (valor #>> '{}')::numeric into v_pct_tiendas  from rifa.config where clave='pct_tiendas';
  select (valor #>> '{}')::numeric into v_comision     from rifa.config where clave='comision_tienda';
  select (valor #>> '{}')::numeric into v_consolacion  from rifa.config where clave='consolacion';
  select (valor #>> '{}')::int     into v_tizumba      from rifa.config where clave='tizumba';
  select (valor #>> '{}')::numeric into v_tizumba_costo from rifa.config where clave='tizumba_costo';

  if p_vendidos is null or p_vendidos < 0 then p_vendidos := 0; end if;
  if p_vendidos > v_total then p_vendidos := v_total; end if;

  v_prob    := p_vendidos::numeric / v_total::numeric;
  v_nz      := round(p_vendidos * v_pct_nz);
  v_tiendas := round(p_vendidos * v_pct_tiendas);
  v_directo := p_vendidos - v_nz - v_tiendas;
  v_ingreso := v_directo * v_precio + v_tiendas * v_precio + v_nz * (v_precio_nzd * v_tasa);
  v_costos  := v_varios + v_tiendas * v_precio * v_comision + v_tizumba * v_tizumba_costo;
  v_neto_vendido     := v_ingreso - v_costos - v_premio - v_premio_vend;
  v_neto_consolacion := v_ingreso - v_costos - v_consolacion - v_premio_vend;
  v_esperado         := v_prob * v_neto_vendido + (1 - v_prob) * v_neto_consolacion;

  return jsonb_build_object(
    'vendidos', p_vendidos,
    'prob_premio', round(v_prob, 4),
    'ingreso',          round(v_ingreso)::bigint,
    'costos',           round(v_costos)::bigint,
    'neto_vendido',     round(v_neto_vendido)::bigint,
    'neto_consolacion', round(v_neto_consolacion)::bigint,
    'esperado',         round(v_esperado)::bigint
  );
end $$;

-- ────────── entregar_efectivo ──────────
-- Pasa una fila de rifa.pagos con tiene='VENDEDOR' a tiene='SANTIAGO' + entregado_en=now().
-- Solo admin. Lo que crea la fila es registrar_venta(... EFECTIVO_VENDEDOR) desde 006.

create or replace function public.entregar_efectivo(p_pago_id bigint, p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); antes rifa.pagos%rowtype;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede entregar efectivo'; end if;
  select * into antes from rifa.pagos where id = p_pago_id for update;
  if not found then raise exception 'pago % inexistente', p_pago_id; end if;
  if antes.tiene <> 'VENDEDOR' then raise exception 'ese pago no está «con vendedor»'; end if;
  if antes.entregado_en is not null then raise exception 'ya fue entregado'; end if;
  update rifa.pagos set tiene = 'SANTIAGO', entregado_en = p_ahora where id = p_pago_id;
  perform rifa.auditar('ENTREGAR_EFECTIVO', p_pago_id::text, to_jsonb(antes),
    (select to_jsonb(x) from rifa.pagos x where id = p_pago_id), v_lote);
  return jsonb_build_object('ok', true, 'pago_id', p_pago_id, 'lote', v_lote);
end $$;
grant execute on function public.entregar_efectivo(bigint, timestamptz) to authenticated;

-- ────────── consignar ──────────
-- Marca uno o varios pagos como consignados. Idempotente: lo ya consignado se ignora.

create or replace function public.consignar(p_pago_ids bigint[], p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  rol text; v_lote uuid := gen_random_uuid();
  v_id bigint; antes rifa.pagos%rowtype; n_hechos int := 0; n_omit int := 0;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede consignar'; end if;
  if p_pago_ids is null or array_length(p_pago_ids, 1) is null then raise exception 'faltan pagos'; end if;
  foreach v_id in array p_pago_ids loop
    select * into antes from rifa.pagos where id = v_id for update;
    if not found then raise exception 'pago % inexistente', v_id; end if;
    if antes.consignado_en is not null then n_omit := n_omit + 1; continue; end if;
    if antes.medio <> 'EFECTIVO' then raise exception 'pago % no es efectivo', v_id; end if;
    update rifa.pagos set consignado_en = p_ahora where id = v_id;
    perform rifa.auditar('CONSIGNAR', v_id::text, to_jsonb(antes),
      (select to_jsonb(x) from rifa.pagos x where id = v_id), v_lote);
    n_hechos := n_hechos + 1;
  end loop;
  return jsonb_build_object('ok', true, 'lote', v_lote, 'consignados', n_hechos, 'omitidos', n_omit);
end $$;
grant execute on function public.consignar(bigint[], timestamptz) to authenticated;

-- ────────── pagos_efectivo_pendientes ──────────
-- Lista para la pestaña Plata. Dos bloques: con vendedor (esperando entrega) y sin consignar.

create or replace function public.pagos_efectivo_pendientes() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  rol text; v_umbral_entregar int; v_umbral_consignar int;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  select (valor #>> '{}')::int into v_umbral_entregar from rifa.config where clave='horas_efectivo_vendedor';
  select (valor #>> '{}')::int into v_umbral_consignar from rifa.config where clave='horas_consignar';

  return jsonb_build_object(
    'umbral_entregar_h', v_umbral_entregar,
    'umbral_consignar_h', v_umbral_consignar,
    'con_vendedor', (
      select coalesce(jsonb_agg(x order by (x->>'horas')::numeric desc), '[]'::jsonb) from (
        select jsonb_build_object(
          'pago_id', p.id,
          'vendedor_id', p.vendedor_id,
          'codigo', v.codigo,
          'nombre', v.nombre_completo,
          'monto_cop', p.monto_cop::bigint,
          'recibido_en', p.recibido_en,
          'horas', round(extract(epoch from (now() - p.recibido_en)) / 3600.0, 1),
          'numeros', (select coalesce(array_agg(n.numero order by n.numero), '{}')::text[]
                      from rifa.numeros n where n.pago_id = p.id)
        ) as x
        from rifa.pagos p
        left join rifa.vendedores v on v.id = p.vendedor_id
        where p.tiene = 'VENDEDOR' and p.entregado_en is null
      ) t
    ),
    'sin_consignar', (
      select coalesce(jsonb_agg(x order by (x->>'horas')::numeric desc), '[]'::jsonb) from (
        select jsonb_build_object(
          'pago_id', p.id,
          'medio', p.medio,
          'monto_cop', p.monto_cop::bigint,
          'recibido_en', p.recibido_en,
          'entregado_en', p.entregado_en,
          'horas', round(extract(epoch from (now() - coalesce(p.entregado_en, p.recibido_en))) / 3600.0, 1),
          'codigo_vendedor', v.codigo,
          'numeros', (select coalesce(array_agg(n.numero order by n.numero), '{}')::text[]
                      from rifa.numeros n where n.pago_id = p.id)
        ) as x
        from rifa.pagos p
        left join rifa.vendedores v on v.id = p.vendedor_id
        where p.tiene = 'SANTIAGO' and p.medio = 'EFECTIVO' and p.consignado_en is null
      ) t
    )
  );
end $$;
grant execute on function public.pagos_efectivo_pendientes() to authenticated;

-- ────────── estadisticas ──────────
-- Dos bloques separados: REAL (lo que ya pasó) y PROYECCIÓN (si el ritmo sigue igual).
-- Nada se mezcla. El panel los pinta aparte (decisión 59).

create or replace function public.estadisticas() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  rol text;
  v_pagados int; v_apartados int; v_libres int;
  v_pagos int; v_compradores int;
  v_precio numeric; v_premio numeric; v_premio_vend numeric; v_varios numeric; v_piso numeric;
  v_caso_malo numeric; v_faltan int;
  v_cierre timestamptz; v_ventas_7d int; v_dias_restan numeric; v_proy_vendidos int;
  v_sin_vendedor int; v_con_vendedor int;
  v_pct_cumplido numeric;
  v_pc jsonb; v_pc_actual jsonb;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;

  select (valor #>> '{}')::numeric into v_precio      from rifa.config where clave='precio_cop';
  select (valor #>> '{}')::numeric into v_premio      from rifa.config where clave='premio';
  select (valor #>> '{}')::numeric into v_premio_vend from rifa.config where clave='premio_vendedor';
  select (valor #>> '{}')::numeric into v_varios      from rifa.config where clave='gastos_varios';
  select (valor #>> '{}')::numeric into v_piso        from rifa.config where clave='piso_neto';
  select (valor #>> '{}')::timestamptz into v_cierre  from rifa.config where clave='cierre';
  select valor into v_pc from rifa.config where clave='puntos_control';

  select count(*) into v_pagados      from rifa.numeros where estado='PAGADO';
  select count(*) into v_apartados    from rifa.numeros where estado='APARTADO';
  select count(*) into v_libres       from rifa.numeros where estado='LIBRE';
  select count(*) into v_pagos        from rifa.pagos;
  select count(distinct comprador_id) into v_compradores
         from rifa.numeros where estado in ('PAGADO','APARTADO');
  select count(*) into v_sin_vendedor from rifa.numeros
         where estado in ('PAGADO','APARTADO') and vendedor_id is null;
  select count(*) into v_con_vendedor from rifa.numeros
         where estado in ('PAGADO','APARTADO') and vendedor_id is not null;

  -- EMPIEZA!C8 y C10 (modelo financiero)
  v_caso_malo := v_pagados * v_precio - v_premio - v_premio_vend - v_varios;
  v_faltan := greatest(0,
    ceil((v_piso + v_premio + v_premio_vend + v_varios)::numeric / v_precio) - v_pagados
  )::int;

  -- Ritmo últimos 7 días → proyección al cierre
  select count(*) into v_ventas_7d from rifa.numeros
    where estado='PAGADO' and pagado_en >= now() - interval '7 days';
  v_dias_restan := greatest(0, extract(epoch from (v_cierre - now())) / 86400.0);
  v_proy_vendidos := least(1000, v_pagados + round((v_ventas_7d::numeric / 7.0) * v_dias_restan)::int);

  -- Punto de control activo: la primera fecha >= hoy; si no hay, la última
  select to_jsonb(x) into v_pc_actual from (
    select p->>'meta' as meta, p->>'fecha' as fecha,
           ((p->>'meta')::int - v_pagados) as faltan_a_meta,
           round((v_pagados::numeric / nullif((p->>'meta')::numeric,0)) * 100, 1) as pct
    from jsonb_array_elements(v_pc) p
    where (p->>'fecha')::date >= current_date
    order by (p->>'fecha')::date asc
    limit 1
  ) x;
  if v_pc_actual is null then
    select to_jsonb(x) into v_pc_actual from (
      select p->>'meta' as meta, p->>'fecha' as fecha,
             ((p->>'meta')::int - v_pagados) as faltan_a_meta,
             round((v_pagados::numeric / nullif((p->>'meta')::numeric,0)) * 100, 1) as pct
      from jsonb_array_elements(v_pc) p
      order by (p->>'fecha')::date desc limit 1
    ) x;
  end if;

  return jsonb_build_object(
    'generado_en', now(),
    'real', jsonb_build_object(
      'pagados', v_pagados,
      'apartados', v_apartados,
      'libres', v_libres,
      'compradores', v_compradores,
      'pagos_registrados', v_pagos,
      'ingresos_cop', coalesce((select sum(monto_cop) from rifa.pagos), 0)::bigint,
      'por_metodo', (select coalesce(jsonb_object_agg(m, c), '{}'::jsonb) from (
        select coalesce(metodo, 'sin_metodo') as m, count(*)::int as c
        from rifa.numeros where estado='PAGADO' group by 1) t),
      'por_pais', (select coalesce(jsonb_object_agg(coalesce(pais,'?'), c), '{}'::jsonb) from (
        select c2.pais, count(*)::int as c
        from rifa.numeros n left join rifa.compradores c2 on c2.id = n.comprador_id
        where n.estado='PAGADO' group by 1) t),
      'con_vendedor', v_con_vendedor,
      'sin_vendedor', v_sin_vendedor,
      'caso_malo_cop', round(v_caso_malo)::bigint,
      'faltan_al_piso', v_faltan,
      'llego_al_piso', (v_caso_malo >= v_piso),
      'punto_control', v_pc_actual
    ),
    'proyeccion', jsonb_build_object(
      'ventas_ultimos_7d', v_ventas_7d,
      'dias_hasta_cierre', round(v_dias_restan, 1),
      'proy_vendidos_al_cierre', v_proy_vendidos,
      'al_ritmo_actual',   rifa.proyeccion_regla_premio(v_proy_vendidos),
      'al_nivel_del_piso', rifa.proyeccion_regla_premio(860),
      'al_nivel_de_meta',  rifa.proyeccion_regla_premio(900)
    )
  );
end $$;
grant execute on function public.estadisticas() to authenticated;

-- ────────── stats_vendedores ──────────
-- Ranking por ingresos. Con 35 de 43 ventas sin vendedor, el panel debe pintar el aviso.

create or replace function public.stats_vendedores() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  return jsonb_build_object(
    'con_vendedor', (select count(*) from rifa.numeros
                     where estado in ('PAGADO','APARTADO') and vendedor_id is not null),
    'sin_vendedor', (select count(*) from rifa.numeros
                     where estado in ('PAGADO','APARTADO') and vendedor_id is null),
    'ranking', (
      select coalesce(jsonb_agg(x order by (x->>'ingresos_cop')::bigint desc, x->>'codigo'), '[]'::jsonb)
      from (
        select jsonb_build_object(
          'id', v.id,
          'codigo', v.codigo,
          'nombre', v.nombre_completo,
          'tipo', v.tipo,
          'activo', v.activo,
          'pagados',    (select count(*) from rifa.numeros n where n.vendedor_id = v.id and n.estado='PAGADO'),
          'apartados',  (select count(*) from rifa.numeros n where n.vendedor_id = v.id and n.estado='APARTADO'),
          'compradores',(select count(distinct comprador_id) from rifa.numeros n
                         where n.vendedor_id = v.id and n.estado in ('PAGADO','APARTADO')),
          'ingresos_cop', coalesce((select sum(p.monto_cop) from rifa.pagos p where p.vendedor_id = v.id), 0)::bigint,
          'efectivo_pendiente_entregar', coalesce((select sum(p.monto_cop) from rifa.pagos p
                        where p.vendedor_id = v.id and p.tiene='VENDEDOR' and p.entregado_en is null), 0)::bigint
        ) as x
        from rifa.vendedores v
        where v.tipo <> 'ESPECIAL' and v.activo
      ) t
    )
  );
end $$;
grant execute on function public.stats_vendedores() to authenticated;
