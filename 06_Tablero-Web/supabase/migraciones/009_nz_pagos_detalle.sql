-- 009 · Pagos de Nueva Zelanda (transferencia / efectivo), detalle de vendedor con nombres completos
--      y estadísticas NZ aparte. 14 oct 2026 (decisión 65).
--
-- · numeros.metodo y pagos.medio aceptan 'NZ_EFECTIVO' (NZ transferencia sigue siendo 'NZ').
-- · registrar_venta: nuevo estado PAGADO_NZ_EFECTIVO (admin y turno). El efectivo de NZ lo tiene Sofía
--   (tiene='VENDEDOR'); la transferencia de NZ queda verificada en su app (tiene='SANTIAGO'), como antes.
-- · marcar_pagado: acepta 'NZ_EFECTIVO'; turno puede marcar NZ y NZ_EFECTIVO.
-- · detalle_vendedor: al admin le da el nombre completo del comprador y el método de pago.
-- · estadisticas_nz(): ventas de Nueva Zelanda aparte (por vendedor tipo NZ o método NZ*) y pagos por medio.

alter table rifa.numeros drop constraint if exists numeros_metodo_check;
alter table rifa.numeros add constraint numeros_metodo_check
  check (metodo = any (array['NU','EFECTIVO','NZ','NZ_EFECTIVO']));
alter table rifa.pagos drop constraint if exists pagos_medio_check;
alter table rifa.pagos add constraint pagos_medio_check
  check (medio = any (array['BRE-B','EFECTIVO','TIENDA','NZ','NZ_EFECTIVO']));

create or replace function public.registrar_venta(
  p_numeros character[], p_nombre text, p_estado text, p_vendedor text default null,
  p_telefono text default null, p_sale_publico boolean default true, p_quiere_tbw boolean default null,
  p_pais text default null, p_nota text default null, p_ahora timestamptz default now()
) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  rol text; v_cid bigint; v_vid bigint; v_lote uuid := gen_random_uuid();
  v_horas_apartado int; v_horas_efvend int;
  v_precio_nzd numeric; v_tasa numeric; v_precio_cop numeric;
  n char(3); fila rifa.numeros%rowtype; antes rifa.numeros%rowtype;
  nuevo_estado text; nuevo_vence timestamptz; nuevo_metodo text;
  v_pago_id bigint; v_pago_medio text; v_pago_moneda text; v_pago_monto numeric; v_pago_cop numeric; v_pago_tiene text;
  cnt int;
begin
  rol := rifa.rol_actor();
  if p_estado not in ('APARTADO', 'PAGADO_NU', 'PAGADO_EFECTIVO', 'EFECTIVO_VENDEDOR', 'POR_VERIFICAR',
                      'PAGADO_NZ', 'PAGADO_NZ_EFECTIVO') then
    raise exception 'estado inválido: %', p_estado;
  end if;
  if rol = 'turno' and p_estado not in ('APARTADO', 'POR_VERIFICAR', 'PAGADO_NZ', 'PAGADO_NZ_EFECTIVO') then
    raise exception 'tu rol (turno) solo puede apartar, marcar «por verificar» o pagar en NZ';
  end if;
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'no viene ningún número'; end if;
  if array_length(p_numeros, 1) > 20 then raise exception 'máximo 20 números por venta'; end if;

  select (valor #>> '{}')::int into v_horas_apartado from rifa.config where clave = 'horas_apartado';
  select (valor #>> '{}')::int into v_horas_efvend from rifa.config where clave = 'horas_efectivo_vendedor';
  select (valor #>> '{}')::numeric into v_precio_nzd from rifa.config where clave = 'precio_nzd';
  select (valor #>> '{}')::numeric into v_tasa from rifa.config where clave = 'tasa_cop_nzd';
  select (valor #>> '{}')::numeric into v_precio_cop from rifa.config where clave = 'precio_cop';

  v_cid := rifa.comprador_para(p_nombre, p_telefono, p_sale_publico, p_quiere_tbw, coalesce(p_pais,
    case when p_estado in ('PAGADO_NZ', 'PAGADO_NZ_EFECTIVO') then 'NZ' else 'CO' end));
  v_vid := rifa.resolver_vendedor_para_venta(p_vendedor);
  if p_vendedor is not null and btrim(p_vendedor) <> '' and v_vid is null then
    insert into rifa.referidos_pendientes (texto_original, texto_norm, numero)
      values (btrim(p_vendedor), rifa.normalizar(p_vendedor), p_numeros[1]);
  end if;

  select count(*) into cnt from rifa.numeros where comprador_id = v_cid and estado <> 'LIBRE';
  if cnt + array_length(p_numeros, 1) > 20 then
    raise exception 'ese comprador ya tiene % número(s); máximo 20', cnt;
  end if;

  if p_estado = 'APARTADO' then
    nuevo_estado := 'APARTADO';  nuevo_vence := p_ahora + make_interval(hours => v_horas_apartado);
  elsif p_estado = 'POR_VERIFICAR' then
    nuevo_estado := 'APARTADO';  nuevo_vence := p_ahora + make_interval(hours => v_horas_apartado);
  elsif p_estado = 'EFECTIVO_VENDEDOR' then
    nuevo_estado := 'APARTADO';  nuevo_vence := p_ahora + make_interval(hours => v_horas_efvend);
    v_pago_medio := 'EFECTIVO'; v_pago_moneda := 'COP'; v_pago_monto := v_precio_cop * array_length(p_numeros, 1);
    v_pago_cop := v_pago_monto; v_pago_tiene := 'VENDEDOR';
  elsif p_estado = 'PAGADO_NU' then
    nuevo_estado := 'PAGADO'; nuevo_metodo := 'NU';
    v_pago_medio := 'BRE-B'; v_pago_moneda := 'COP'; v_pago_monto := v_precio_cop * array_length(p_numeros, 1);
    v_pago_cop := v_pago_monto; v_pago_tiene := 'SANTIAGO';
  elsif p_estado = 'PAGADO_EFECTIVO' then
    nuevo_estado := 'PAGADO'; nuevo_metodo := 'EFECTIVO';
    v_pago_medio := 'EFECTIVO'; v_pago_moneda := 'COP'; v_pago_monto := v_precio_cop * array_length(p_numeros, 1);
    v_pago_cop := v_pago_monto; v_pago_tiene := 'SANTIAGO';
  elsif p_estado = 'PAGADO_NZ' then
    nuevo_estado := 'PAGADO'; nuevo_metodo := 'NZ';
    v_pago_medio := 'NZ'; v_pago_moneda := 'NZD'; v_pago_monto := v_precio_nzd * array_length(p_numeros, 1);
    v_pago_cop := v_pago_monto * v_tasa; v_pago_tiene := 'SANTIAGO';
  elsif p_estado = 'PAGADO_NZ_EFECTIVO' then
    nuevo_estado := 'PAGADO'; nuevo_metodo := 'NZ_EFECTIVO';
    v_pago_medio := 'NZ_EFECTIVO'; v_pago_moneda := 'NZD'; v_pago_monto := v_precio_nzd * array_length(p_numeros, 1);
    v_pago_cop := v_pago_monto * v_tasa; v_pago_tiene := 'VENDEDOR';
  end if;

  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado <> 'LIBRE' then raise exception 'el número % ya está %', n, fila.estado; end if;
  end loop;

  if v_pago_medio is not null then
    insert into rifa.pagos (medio, moneda, monto, monto_cop, comprador_id, vendedor_id, tiene, recibido_en, verificado_por)
      values (v_pago_medio, v_pago_moneda, v_pago_monto, v_pago_cop, v_cid, v_vid, v_pago_tiene, p_ahora, auth.uid())
      returning id into v_pago_id;
  end if;

  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n;
    update rifa.numeros set
      estado = nuevo_estado, comprador_id = v_cid, vendedor_id = v_vid,
      vendedor_texto = nullif(btrim(coalesce(p_vendedor, '')), ''),
      apartado_en = case when nuevo_estado = 'APARTADO' then p_ahora else null end,
      vence_en = nuevo_vence,
      por_verificar = (p_estado = 'POR_VERIFICAR'),
      pagado_en = case when nuevo_estado = 'PAGADO' then p_ahora else null end,
      metodo = nuevo_metodo, pago_id = v_pago_id,
      notas = nullif(btrim(coalesce(p_nota, '')), ''),
      actualizado_en = p_ahora
     where numero = n;
    perform rifa.auditar('REGISTRAR_VENTA', n, to_jsonb(antes),
      (select to_jsonb(x) from rifa.numeros x where numero = n), v_lote);
  end loop;

  return jsonb_build_object('ok', true, 'lote', v_lote, 'comprador_id', v_cid, 'vendedor_id', v_vid,
    'pago_id', v_pago_id, 'estado_interno', nuevo_estado,
    'serial_primer_numero', rifa.serial_de(p_numeros[1]),
    'vendedor_no_resuelto', (p_vendedor is not null and btrim(p_vendedor) <> '' and v_vid is null));
end $$;

create or replace function public.marcar_pagado(p_numeros character[], p_metodo text, p_ahora timestamptz default now())
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); n char(3); fila rifa.numeros%rowtype; antes rifa.numeros%rowtype;
        v_precio numeric; v_precio_nzd numeric; v_tasa numeric;
        v_pago_id bigint; v_pago_medio text; v_pago_moneda text; v_pago_monto numeric; v_pago_cop numeric;
        pago_existente int; v_nz boolean;
begin
  rol := rifa.rol_actor();
  if p_metodo not in ('NU', 'EFECTIVO', 'NZ', 'NZ_EFECTIVO') then raise exception 'método inválido'; end if;
  if rol = 'turno' and p_metodo not in ('NZ', 'NZ_EFECTIVO') then raise exception 'tu rol (turno) solo marca pagado con método NZ'; end if;
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'faltan números'; end if;
  v_nz := p_metodo in ('NZ', 'NZ_EFECTIVO');
  select (valor #>> '{}')::numeric into v_precio from rifa.config where clave = 'precio_cop';
  select (valor #>> '{}')::numeric into v_precio_nzd from rifa.config where clave = 'precio_nzd';
  select (valor #>> '{}')::numeric into v_tasa from rifa.config where clave = 'tasa_cop_nzd';
  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado = 'PAGADO' then raise exception 'el número % ya está pagado', n; end if;
    if fila.estado = 'LIBRE' then raise exception 'el número % está libre; usa registrar_venta', n; end if;
  end loop;
  select count(distinct coalesce(pago_id, 0)) into pago_existente from rifa.numeros where numero = any(p_numeros);
  if pago_existente = 1 then
    select pago_id into v_pago_id from rifa.numeros where numero = p_numeros[1];
  end if;
  if v_pago_id is null then
    v_pago_medio := case p_metodo when 'NU' then 'BRE-B' else p_metodo end;
    v_pago_moneda := case when v_nz then 'NZD' else 'COP' end;
    v_pago_monto := case when v_nz then v_precio_nzd * array_length(p_numeros, 1)
                       else v_precio * array_length(p_numeros, 1) end;
    v_pago_cop := case when v_nz then v_pago_monto * v_tasa else v_pago_monto end;
    insert into rifa.pagos (medio, moneda, monto, monto_cop, comprador_id, vendedor_id, tiene, recibido_en, verificado_por)
      select v_pago_medio, v_pago_moneda, v_pago_monto, v_pago_cop,
             (select comprador_id from rifa.numeros where numero = p_numeros[1]),
             (select vendedor_id from rifa.numeros where numero = p_numeros[1]),
             case when p_metodo = 'NZ_EFECTIVO' then 'VENDEDOR' else 'SANTIAGO' end, p_ahora, auth.uid()
      returning id into v_pago_id;
  end if;
  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n;
    update rifa.numeros set
      estado = 'PAGADO', por_verificar = false, pagado_en = p_ahora, metodo = p_metodo,
      vence_en = null, pago_id = v_pago_id, actualizado_en = p_ahora
     where numero = n;
    perform rifa.auditar('MARCAR_PAGADO', n, to_jsonb(antes),
      (select to_jsonb(x) from rifa.numeros x where numero = n), v_lote);
  end loop;
  return jsonb_build_object('ok', true, 'lote', v_lote, 'pago_id', v_pago_id);
end $$;

-- Detalle de un vendedor: al admin, nombre completo del comprador, método y estado de cada número.
create or replace function public.detalle_vendedor(p_id bigint)
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; v rifa.vendedores%rowtype;
begin
  rol := rifa.rol_actor();
  select * into v from rifa.vendedores where id = p_id;
  if not found then raise exception 'no existe'; end if;
  return jsonb_build_object(
    'ok', true,
    'id', v.id, 'codigo', v.codigo, 'nombre', v.nombre_completo, 'tipo', v.tipo,
    'activo', v.activo, 'telefono', case when rol = 'admin' then v.telefono else null end,
    'etiqueta', coalesce(v.nombre_lista, rifa.etiqueta_base(v.nombre_completo)),
    'link', 'https://mega-rifa-fusa.vercel.app/?v=' || v.codigo,
    'alias', (select coalesce(jsonb_agg(alias_clave order by alias_clave), '[]'::jsonb)
              from rifa.vendedor_alias where vendedor_id = v.id),
    'numeros', (select coalesce(jsonb_agg(jsonb_build_object(
      'n', numero, 'estado', estado, 'metodo', n.metodo, 'por_verificar', n.por_verificar,
      'comprador_id', n.comprador_id,
      'comprador', case when rol = 'admin' then c.nombre_completo
                        when c.sale_publico then rifa.acortar(c.nombre_completo) else 'Reservado' end,
      'fecha', coalesce(pagado_en, apartado_en)) order by c.nombre_completo, numero), '[]'::jsonb)
      from rifa.numeros n left join rifa.compradores c on c.id = n.comprador_id
      where n.vendedor_id = v.id and n.estado in ('PAGADO', 'APARTADO')));
end $$;

-- Ventas de Nueva Zelanda aparte (vendedor tipo NZ o método NZ*) y pagos por medio.
create or replace function public.estadisticas_nz()
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  return (
    with nz as (
      select n.*, v.tipo as vtipo
      from rifa.numeros n left join rifa.vendedores v on v.id = n.vendedor_id
      where n.estado in ('PAGADO', 'APARTADO')
        and (v.tipo = 'NZ' or n.metodo in ('NZ', 'NZ_EFECTIVO'))
    )
    select jsonb_build_object(
      'pagados',        (select count(*) from nz where estado = 'PAGADO'),
      'apartados',      (select count(*) from nz where estado = 'APARTADO' and not por_verificar),
      'por_verificar',  (select count(*) from nz where estado = 'APARTADO' and por_verificar),
      'transferencia',  (select count(*) from nz where estado = 'PAGADO' and metodo = 'NZ'),
      'efectivo',       (select count(*) from nz where estado = 'PAGADO' and metodo = 'NZ_EFECTIVO'),
      'sin_clasificar', (select count(*) from nz where estado = 'PAGADO' and (metodo is null or metodo not in ('NZ','NZ_EFECTIVO'))),
      'ingresos_nzd',   coalesce((select sum(p.monto) from rifa.pagos p where p.moneda = 'NZD'), 0),
      'ingresos_cop',   coalesce((select sum(p.monto_cop) from rifa.pagos p where p.moneda = 'NZD'), 0)::bigint,
      'por_medio',      (select coalesce(jsonb_object_agg(medio, c), '{}'::jsonb)
                         from (select medio, count(*)::int c from rifa.pagos group by 1) t)
    )
  );
end $$;

revoke all on function public.estadisticas_nz() from public;
grant execute on function public.estadisticas_nz() to authenticated;

-- Decisión 65: el premio del vendedor se gana con 25 boletas PAGADAS (pueden ser varias a la misma persona).
-- La mini-tarjeta pública /v/CODIGO calculaba «faltan» con compradores distintos (umbral + 1 - compradores).
create or replace function public.mini_tarjeta(p_codigo text) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare r bigint; e record; umbral int; pag int; comp int; apar int;
begin
  r := rifa.buscar_vendedor(left(coalesce(p_codigo, ''), 60));
  select * into e from rifa.etiquetas() where vendedor_id = r;
  if r is null or e.tipo = 'ESPECIAL' then return jsonb_build_object('ok', false); end if;
  select (valor #>> '{}')::int into umbral from rifa.config where clave = 'umbral_compradores';
  select count(*) filter (where estado = 'PAGADO'),
         count(distinct comprador_id) filter (where estado = 'PAGADO'),
         count(*) filter (where estado = 'APARTADO' and (vence_en is null or vence_en > now()))
    into pag, comp, apar from rifa.numeros where vendedor_id = r;
  return jsonb_build_object('ok', true, 'codigo', e.codigo, 'etiqueta', e.etiqueta, 'activo', e.activo,
    'pagados', pag, 'compradores', comp, 'apartados', apar,
    'umbral', umbral, 'faltan', greatest(0, umbral - pag));
end $$;

-- Datos (14 oct 2026, hechos por SQL con auditoría, no son parte de la migración reutilizable):
--  · las 32 ventas viejas sin método quedaron como NU (Bre-B) con un pago por comprador y vendedor (acción COMPLETAR_PAGO_VIEJO);
--  · Ignacio Cobos y Sophia Moreno pasaron de DIR a SBG.
