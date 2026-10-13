-- 008_auditoria_respaldo.sql — Fase 3C
-- Auditoría consultable + deshacer de un lote arbitrario + exportar CSV + respaldo diario con cron.
-- Solo admin. Toca rifa.auditoria (lectura, nunca escribe ni cambia filas: trigger inmutable sigue en pie).

-- ────────── Auditoría (consulta con filtros) ──────────

create or replace function public.auditoria(
  p_desde timestamptz default now() - interval '7 days',
  p_hasta timestamptz default now(),
  p_accion text default null,
  p_actor uuid default null,
  p_clave text default null,
  p_limit int default 200
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_total int;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  if p_limit is null or p_limit <= 0 then p_limit := 200; end if;
  if p_limit > 2000 then p_limit := 2000; end if;

  select count(*) into v_total from rifa.auditoria a
   where a.en >= p_desde and a.en <= p_hasta
     and (p_accion is null or a.accion = p_accion)
     and (p_actor  is null or a.actor  = p_actor)
     and (p_clave  is null or a.clave  = p_clave);

  return jsonb_build_object(
    'total', v_total,
    'desde', p_desde,
    'hasta', p_hasta,
    'filas', (
      select coalesce(jsonb_agg(x order by (x->>'en') desc), '[]'::jsonb) from (
        select jsonb_build_object(
          'id', a.id,
          'en', a.en,
          'actor', a.actor,
          'actor_nombre', a.actor_nombre,
          'accion', a.accion,
          'clave', a.clave,
          'lote', a.lote,
          'deshace_lote', a.deshace_lote,
          'antes', a.antes,
          'despues', a.despues,
          'revertido', exists (select 1 from rifa.auditoria b where b.deshace_lote = a.lote)
        ) as x
        from rifa.auditoria a
        where a.en >= p_desde and a.en <= p_hasta
          and (p_accion is null or a.accion = p_accion)
          and (p_actor  is null or a.actor  = p_actor)
          and (p_clave  is null or a.clave  = p_clave)
        order by a.en desc
        limit p_limit
      ) t
    )
  );
end $$;
grant execute on function public.auditoria(timestamptz, timestamptz, text, uuid, text, int) to authenticated;

-- ────────── deshacer_lote (arbitrario: números y pagos) ──────────
-- Para lotes de números: restaura rifa.numeros desde `antes` (igual que deshacer_ultima de 006).
-- Para lotes de pagos (ENTREGAR_EFECTIVO, CONSIGNAR): restaura tiene / entregado_en / consignado_en.
-- Un lote mixto (nunca pasa hoy) procesa cada fila según el tipo de clave.

create or replace function public.deshacer_lote(p_lote uuid)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  rol text; v_nuevo uuid := gen_random_uuid();
  fila rifa.auditoria%rowtype; n_hechos int := 0;
  v_pago_id bigint;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede deshacer'; end if;
  if p_lote is null then raise exception 'falta el lote'; end if;
  if exists (select 1 from rifa.auditoria where deshace_lote = p_lote) then
    raise exception 'ese lote ya fue revertido';
  end if;
  if not exists (select 1 from rifa.auditoria where lote = p_lote) then
    raise exception 'lote % no existe', p_lote;
  end if;

  for fila in select * from rifa.auditoria where lote = p_lote order by id loop
    if fila.antes is null then continue; end if;
    if fila.clave ~ '^[0-9]{3}$' then
      -- Fila de rifa.numeros
      update rifa.numeros set
        estado         = (fila.antes->>'estado'),
        comprador_id   = nullif(fila.antes->>'comprador_id', '')::bigint,
        vendedor_id    = nullif(fila.antes->>'vendedor_id', '')::bigint,
        vendedor_texto = fila.antes->>'vendedor_texto',
        apartado_en    = nullif(fila.antes->>'apartado_en', '')::timestamptz,
        vence_en       = nullif(fila.antes->>'vence_en', '')::timestamptz,
        por_verificar  = coalesce((fila.antes->>'por_verificar')::boolean, false),
        pagado_en      = nullif(fila.antes->>'pagado_en', '')::timestamptz,
        metodo         = nullif(fila.antes->>'metodo', ''),
        pago_id        = nullif(fila.antes->>'pago_id', '')::bigint,
        notas          = nullif(fila.antes->>'notas', ''),
        actualizado_en = now()
       where numero = fila.clave;
    elsif fila.clave ~ '^[0-9]+$' then
      -- Fila de rifa.pagos (ENTREGAR_EFECTIVO / CONSIGNAR)
      v_pago_id := fila.clave::bigint;
      update rifa.pagos set
        tiene         = fila.antes->>'tiene',
        entregado_en  = nullif(fila.antes->>'entregado_en', '')::timestamptz,
        consignado_en = nullif(fila.antes->>'consignado_en', '')::timestamptz
       where id = v_pago_id;
    else
      continue;
    end if;
    perform rifa.auditar('DESHACER', fila.clave, fila.despues, fila.antes, v_nuevo, p_lote);
    n_hechos := n_hechos + 1;
  end loop;

  if n_hechos = 0 then raise exception 'ese lote no tiene nada que revertir'; end if;
  return jsonb_build_object('ok', true, 'lote_original', p_lote, 'lote_deshace', v_nuevo, 'cambios', n_hechos);
end $$;
grant execute on function public.deshacer_lote(uuid) to authenticated;

-- ────────── Exportar a CSV (admin) ──────────
-- Devuelve el CSV completo como texto. BOM UTF-8 al inicio para Excel.

create or replace function public.exportar(p_tabla text) returns text
language plpgsql security definer set search_path = '' as $$
declare rol text; v text; eol text := E'\r\n'; bom text := E'﻿';
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  if p_tabla not in ('numeros','pagos','compradores','vendedores') then
    raise exception 'tabla no exportable: %', p_tabla;
  end if;

  if p_tabla = 'numeros' then
    v := bom || 'numero,estado,metodo,por_verificar,comprador,vendedor,apartado_en,vence_en,pagado_en' || eol;
    select v || string_agg(
      quote_nullable(n.numero) || ',' ||
      quote_nullable(n.estado) || ',' ||
      quote_nullable(coalesce(n.metodo,'')) || ',' ||
      (case when n.por_verificar then '1' else '0' end) || ',' ||
      quote_nullable(coalesce(c.nombre_completo,'')) || ',' ||
      quote_nullable(coalesce(v2.codigo,'')) || ',' ||
      quote_nullable(coalesce(n.apartado_en::text,'')) || ',' ||
      quote_nullable(coalesce(n.vence_en::text,'')) || ',' ||
      quote_nullable(coalesce(n.pagado_en::text,'')),
      eol order by n.numero
    ) into v
    from rifa.numeros n
    left join rifa.compradores c  on c.id = n.comprador_id
    left join rifa.vendedores  v2 on v2.id = n.vendedor_id;
  elsif p_tabla = 'pagos' then
    v := bom || 'id,medio,moneda,monto,monto_cop,tiene,vendedor,recibido_en,entregado_en,consignado_en' || eol;
    select v || string_agg(
      p.id::text || ',' ||
      quote_nullable(p.medio) || ',' ||
      quote_nullable(p.moneda) || ',' ||
      p.monto::text || ',' ||
      p.monto_cop::text || ',' ||
      quote_nullable(coalesce(p.tiene,'')) || ',' ||
      quote_nullable(coalesce(v2.codigo,'')) || ',' ||
      quote_nullable(p.recibido_en::text) || ',' ||
      quote_nullable(coalesce(p.entregado_en::text,'')) || ',' ||
      quote_nullable(coalesce(p.consignado_en::text,'')),
      eol order by p.id
    ) into v
    from rifa.pagos p
    left join rifa.vendedores v2 on v2.id = p.vendedor_id;
  elsif p_tabla = 'compradores' then
    v := bom || 'id,nombre_completo,telefono,pais,sale_publico,quiere_tbw,numeros_vigentes' || eol;
    select v || string_agg(
      c.id::text || ',' ||
      quote_nullable(c.nombre_completo) || ',' ||
      quote_nullable(coalesce(c.telefono,'')) || ',' ||
      quote_nullable(coalesce(c.pais,'')) || ',' ||
      (case when c.sale_publico then '1' else '0' end) || ',' ||
      (case when c.quiere_tbw then '1' when c.quiere_tbw = false then '0' else '' end) || ',' ||
      (select count(*)::text from rifa.numeros n where n.comprador_id = c.id and n.estado <> 'LIBRE'),
      eol order by c.id
    ) into v
    from rifa.compradores c;
  elsif p_tabla = 'vendedores' then
    v := bom || 'codigo,nombre_completo,tipo,activo,telefono,pagados,apartados,compradores,ingresos_cop' || eol;
    select v || string_agg(
      quote_nullable(x.codigo) || ',' ||
      quote_nullable(x.nombre_completo) || ',' ||
      quote_nullable(x.tipo) || ',' ||
      (case when x.activo then '1' else '0' end) || ',' ||
      quote_nullable(coalesce(x.telefono,'')) || ',' ||
      x.pagados::text || ',' ||
      x.apartados::text || ',' ||
      x.compradores::text || ',' ||
      x.ingresos_cop::text,
      eol order by x.codigo
    ) into v
    from (
      select v2.codigo, v2.nombre_completo, v2.tipo, v2.activo, v2.telefono,
             (select count(*) from rifa.numeros n where n.vendedor_id = v2.id and n.estado='PAGADO') as pagados,
             (select count(*) from rifa.numeros n where n.vendedor_id = v2.id and n.estado='APARTADO') as apartados,
             (select count(distinct comprador_id) from rifa.numeros n
                where n.vendedor_id = v2.id and n.estado in ('PAGADO','APARTADO')) as compradores,
             coalesce((select sum(p.monto_cop) from rifa.pagos p where p.vendedor_id = v2.id), 0) as ingresos_cop
      from rifa.vendedores v2
    ) x;
  end if;

  return coalesce(v, bom);
end $$;
grant execute on function public.exportar(text) to authenticated;

-- ────────── Respaldo diario ──────────
-- Snapshot JSON de todo lo necesario para reconstruir el estado. Pisa el mismo día (upsert).
-- Se corre con pg_cron a las 08:00 UTC (03:00 Bogotá).

create or replace function rifa.respaldo_diario() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare v_datos jsonb; v_fecha date := current_date;
begin
  v_datos := jsonb_build_object(
    'generado_en', now(),
    'conteos', jsonb_build_object(
      'numeros', (select count(*) from rifa.numeros),
      'pagados', (select count(*) from rifa.numeros where estado='PAGADO'),
      'apartados', (select count(*) from rifa.numeros where estado='APARTADO'),
      'compradores', (select count(*) from rifa.compradores),
      'vendedores', (select count(*) from rifa.vendedores),
      'pagos', (select count(*) from rifa.pagos)
    ),
    'numeros',     (select coalesce(jsonb_agg(to_jsonb(n) order by n.numero), '[]'::jsonb) from rifa.numeros n where n.estado <> 'LIBRE'),
    'compradores', (select coalesce(jsonb_agg(to_jsonb(c) order by c.id), '[]'::jsonb) from rifa.compradores c),
    'vendedores',  (select coalesce(jsonb_agg(to_jsonb(v) order by v.id), '[]'::jsonb) from rifa.vendedores v),
    'pagos',       (select coalesce(jsonb_agg(to_jsonb(p) order by p.id), '[]'::jsonb) from rifa.pagos p)
  );

  insert into rifa.respaldos (fecha, datos, creado_en)
    values (v_fecha, v_datos, now())
    on conflict (fecha) do update set datos = excluded.datos, creado_en = excluded.creado_en;

  delete from rifa.respaldos where fecha < current_date - interval '30 days';

  return jsonb_build_object('ok', true, 'fecha', v_fecha, 'tamano_kb', round(length(v_datos::text)::numeric / 1024, 1));
end $$;

-- Lista de respaldos (admin)
create or replace function public.respaldos_lista() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  return (
    select coalesce(jsonb_agg(x order by (x->>'fecha') desc), '[]'::jsonb) from (
      select jsonb_build_object(
        'fecha', fecha,
        'creado_en', creado_en,
        'tamano_kb', round(length(datos::text)::numeric / 1024, 1),
        'pagados', (datos->'conteos'->>'pagados')::int,
        'apartados', (datos->'conteos'->>'apartados')::int,
        'pagos', (datos->'conteos'->>'pagos')::int
      ) as x from rifa.respaldos
    ) t
  );
end $$;
grant execute on function public.respaldos_lista() to authenticated;

-- Cron: respaldo diario a las 08:00 UTC = 03:00 Bogotá.
-- Si ya existe un job con el mismo nombre, se desprograma y se vuelve a crear.
do $$
begin
  perform cron.unschedule('respaldo_diario');
exception when others then null;
end $$;
select cron.schedule('respaldo_diario', '0 8 * * *', 'select rifa.respaldo_diario()');

-- Primer respaldo manual al aplicar la migración
select rifa.respaldo_diario();
