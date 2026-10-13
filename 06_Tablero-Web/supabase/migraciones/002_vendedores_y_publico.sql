-- 002_vendedores_y_publico.sql — ayudas de vendedores y las 4 RPC PÚBLICAS (solo lectura, mínimo expuesto).

-- Etiqueta pública de cada vendedor. Si dos activos comparten etiqueta, llevan la inicial del apellido
-- («Paula V.» / «Paula G.»). `visible` = activo y no especial: solo esos salen en el selector.
create or replace function rifa.etiquetas() returns table (
  vendedor_id bigint, codigo text, etiqueta text, visible boolean, activo boolean, tipo text)
language sql stable security definer set search_path = '' as $$
  with b as (
    select v.id, v.codigo, v.tipo, v.activo, v.nombre_completo,
           coalesce(nullif(btrim(v.nombre_lista), ''), rifa.etiqueta_base(v.nombre_completo)) as base,
           (v.activo and v.tipo <> 'ESPECIAL') as visible
    from rifa.vendedores v
  )
  select id, codigo,
         case when visible and count(*) over (partition by visible, rifa.normalizar(base)) > 1
              then base || ' ' || upper(left((regexp_match(btrim(nombre_completo), '(\S+)$'))[1], 1)) || '.'
              else base end,
         visible, activo, tipo
  from b
$$;

-- Texto libre / código / alias → id de vendedor (o null). Orden: código, alias, nombre completo, nombre de pila único.
create or replace function rifa.buscar_vendedor(p_texto text) returns bigint
language plpgsql stable security definer set search_path = '' as $$
declare k text := rifa.clave(p_texto); r bigint; n int;
begin
  if k = '' then return null; end if;
  select id into r from rifa.vendedores where codigo = k;                        if r is not null then return r; end if;
  select vendedor_id into r from rifa.vendedor_alias where alias_clave = k;       if r is not null then return r; end if;
  select id into r from rifa.vendedores where rifa.clave(nombre_completo) = k;    if r is not null then return r; end if;
  select count(*), min(id) into n, r from rifa.vendedores
   where rifa.clave(coalesce(nullif(btrim(nombre_lista), ''), rifa.etiqueta_base(nombre_completo))) = k and activo;
  if n = 1 then return r; end if;
  return null;
end $$;

-- Código sugerido para un nombre (regla del 10 oct): nombre de pila en MAYÚSCULAS sin tildes ni espacios;
-- si choca, + inicial del apellido (PAULAV/PAULAG); si aún choca (o es la misma persona), + número (ANGELICA2).
create or replace function rifa.sugerir_codigo(p_nombre text) returns text
language plpgsql stable security definer set search_path = '' as $$
declare base text; ini text; c text; i int := 2; misma boolean;
begin
  base := left(rifa.clave(rifa.etiqueta_base(p_nombre)), 22);
  if base = '' then raise exception 'el nombre no tiene letras'; end if;
  misma := exists (select 1 from rifa.vendedores where rifa.clave(nombre_completo) = rifa.clave(p_nombre));
  if not exists (select 1 from rifa.vendedores where codigo = base)
     and not exists (select 1 from rifa.vendedor_alias where alias_clave = base) then return base; end if;
  if not misma then
    ini := upper(left((regexp_match(rifa.normalizar(p_nombre), '(\S+)$'))[1], 1));
    c := base || ini;
    if ini ~ '^[A-Z0-9]$' and c <> base
       and not exists (select 1 from rifa.vendedores where codigo = c)
       and not exists (select 1 from rifa.vendedor_alias where alias_clave = c) then return c; end if;
  end if;
  loop
    c := base || i::text;
    exit when not exists (select 1 from rifa.vendedores where codigo = c)
          and not exists (select 1 from rifa.vendedor_alias where alias_clave = c);
    i := i + 1;
  end loop;
  return c;
end $$;

-- ───────────── RPC públicas ─────────────

-- El tablero: solo número, estado y nombre ACORTADO. Un apartado cuyo vencimiento ya pasó sale libre al instante.
create or replace function public.tablero_publico() returns jsonb
language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    'ok', true,
    't', (extract(epoch from clock_timestamp()) * 1000)::bigint,
    'v', coalesce(jsonb_agg(jsonb_build_array(
           n.numero, n.estado,
           case when n.estado = 'PAGADO'
                then case when c.sale_publico then rifa.acortar(c.nombre_completo) else 'Reservado' end
                else '' end) order by n.numero), '[]'::jsonb))
  from rifa.numeros n
  left join rifa.compradores c on c.id = n.comprador_id
  where n.estado = 'PAGADO'
     or (n.estado = 'APARTADO' and (n.vence_en is null or n.vence_en > now()))
$$;

-- El selector «¿Quién te compartió la rifa?»: solo etiqueta y código de vendedores ACTIVOS (nunca teléfono ni totales).
create or replace function public.vendedores_selector() returns jsonb
language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_agg(jsonb_build_object('c', codigo, 'n', etiqueta) order by rifa.normalizar(etiqueta), codigo), '[]'::jsonb)
  from rifa.etiquetas() where visible
$$;

-- ?v=CODIGO → código oficial (aplica alias: N01 → SOFIA) y etiqueta si el vendedor sigue activo.
create or replace function public.resolver_codigo(p_codigo text) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare r bigint; e record;
begin
  r := rifa.buscar_vendedor(left(coalesce(p_codigo, ''), 60));
  if r is null then return jsonb_build_object('ok', false); end if;
  select * into e from rifa.etiquetas() where vendedor_id = r;
  return jsonb_build_object('ok', true, 'codigo', e.codigo, 'etiqueta', case when e.visible then e.etiqueta else null end);
end $$;

-- Mini-tarjeta /v/CODIGO: SOLO conteos. Nunca nombres de compradores, teléfonos ni dinero.
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
    'umbral', umbral, 'faltan', greatest(0, umbral + 1 - comp));
end $$;

-- Permisos: solo estas 4 son públicas.
revoke all on function public.tablero_publico(), public.vendedores_selector(), public.resolver_codigo(text), public.mini_tarjeta(text) from public;
grant execute on function public.tablero_publico(), public.vendedores_selector(), public.resolver_codigo(text), public.mini_tarjeta(text) to anon, authenticated;
