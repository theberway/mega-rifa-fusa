-- 006_rpcs_ventas.sql — Fase 3A: ventas en 4 toques, boleta, pestañas Inicio/Vender/Números.
-- Todas las RPC públicas van en `public`, con security definer, search_path = '', y guardia rifa.rol_actor()
-- (ya existe en 005: exige aal2 al admin). Cada venta deja una fila de auditoría por número, todas con el mismo
-- `lote` para que `deshacer_ultima` las revierta como un bloque.
--
-- Mapeo de estado de UI → DB (la tabla rifa.numeros solo acepta LIBRE/APARTADO/PAGADO):
--   APARTADO          → estado=APARTADO,  vence_en=ahora+horas_apartado (24 h)
--   PAGADO_NU         → estado=PAGADO,    metodo=NU, pago(medio=BRE-B)
--   PAGADO_EFECTIVO   → estado=PAGADO,    metodo=EFECTIVO, pago(medio=EFECTIVO, tiene=SANTIAGO)
--   EFECTIVO_VENDEDOR → estado=APARTADO,  vence_en=ahora+horas_efectivo_vendedor (48 h), pago(medio=EFECTIVO, tiene=VENDEDOR)
--   POR_VERIFICAR     → estado=APARTADO,  por_verificar=true, vence_en=ahora+horas_apartado
--   PAGADO_NZ         → estado=PAGADO,    metodo=NZ, pago(medio=NZ, moneda=NZD, monto=precio_nzd, monto_cop=precio_nzd × tasa)

-- Convierte texto libre a vendedor_id. Si no resuelve y hay texto, el llamador encola en referidos_pendientes.
create or replace function rifa.resolver_vendedor_para_venta(p_texto text) returns bigint
language plpgsql security definer set search_path = '' as $$
declare v_id bigint;
begin
  if p_texto is null or btrim(p_texto) = '' then
    -- sin texto: va a DIR (regla fija: lo que no viene de un vendedor conocido es venta directa)
    select id into v_id from rifa.vendedores where codigo = 'DIR';
    return v_id;
  end if;
  return rifa.buscar_vendedor(p_texto);
end $$;

-- Busca por nombre_norm o crea. Es la única que escribe en rifa.compradores (fuera de la carga).
create or replace function rifa.comprador_para(p_nombre text, p_telefono text, p_sale_publico boolean,
                                                p_quiere_tbw boolean, p_pais text) returns bigint
language plpgsql security definer set search_path = '' as $$
declare r bigint; nom text := btrim(coalesce(p_nombre, '')); norm text;
begin
  if nom = '' then raise exception 'falta el nombre del comprador'; end if;
  if length(nom) > 100 then raise exception 'nombre muy largo'; end if;
  norm := rifa.normalizar(nom);
  select id into r from rifa.compradores where nombre_norm = norm limit 1;
  if r is not null then
    update rifa.compradores set
      telefono = coalesce(telefono, nullif(btrim(p_telefono), '')),
      sale_publico = coalesce(p_sale_publico, sale_publico),
      quiere_tbw = coalesce(quiere_tbw, p_quiere_tbw),
      pais = coalesce(pais, p_pais)
     where id = r;
    return r;
  end if;
  insert into rifa.compradores (nombre_completo, nombre_norm, telefono, sale_publico, quiere_tbw, pais)
    values (nom, norm, nullif(btrim(p_telefono), ''), coalesce(p_sale_publico, true),
            p_quiere_tbw, coalesce(nullif(p_pais, ''), 'CO'))
    returning id into r;
  return r;
end $$;

-- Devuelve 'A' + numero → 'A-000'. Ayuda a devolver el serial sin hacer substring[] en SQL puro.
create or replace function rifa.serial_de(p_numero char(3)) returns text
language sql immutable set search_path = '' as $$
  select substr('ABCDEFGHIJ', (ascii(substr(p_numero, 1, 1)) - 48) + 1, 1) || '-' || p_numero
$$;

-- ────────────── registrar_venta ──────────────

create or replace function public.registrar_venta(
  p_numeros char(3)[],
  p_nombre text,
  p_estado text,
  p_vendedor text default null,
  p_telefono text default null,
  p_sale_publico boolean default true,
  p_quiere_tbw boolean default null,
  p_pais text default null,
  p_nota text default null,
  p_ahora timestamptz default now()
) returns jsonb language plpgsql security definer set search_path = '' as $$
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

  -- Validación del estado y permisos por rol (decisión 46)
  if p_estado not in ('APARTADO', 'PAGADO_NU', 'PAGADO_EFECTIVO', 'EFECTIVO_VENDEDOR', 'POR_VERIFICAR', 'PAGADO_NZ') then
    raise exception 'estado inválido: %', p_estado;
  end if;
  if rol = 'turno' and p_estado not in ('APARTADO', 'POR_VERIFICAR', 'PAGADO_NZ') then
    raise exception 'tu rol (turno) solo puede apartar, marcar «por verificar» o pagar en NZ';
  end if;
  if p_numeros is null or array_length(p_numeros, 1) is null then
    raise exception 'no viene ningún número';
  end if;
  if array_length(p_numeros, 1) > 20 then
    raise exception 'máximo 20 números por venta';
  end if;

  -- Supuestos del modelo (modificables en rifa.config)
  select (valor #>> '{}')::int into v_horas_apartado from rifa.config where clave = 'horas_apartado';
  select (valor #>> '{}')::int into v_horas_efvend from rifa.config where clave = 'horas_efectivo_vendedor';
  select (valor #>> '{}')::numeric into v_precio_nzd from rifa.config where clave = 'precio_nzd';
  select (valor #>> '{}')::numeric into v_tasa from rifa.config where clave = 'tasa_cop_nzd';
  select (valor #>> '{}')::numeric into v_precio_cop from rifa.config where clave = 'precio_cop';

  -- Comprador y vendedor
  v_cid := rifa.comprador_para(p_nombre, p_telefono, p_sale_publico, p_quiere_tbw, coalesce(p_pais,
    case when p_estado = 'PAGADO_NZ' then 'NZ' else 'CO' end));
  v_vid := rifa.resolver_vendedor_para_venta(p_vendedor);
  if p_vendedor is not null and btrim(p_vendedor) <> '' and v_vid is null then
    insert into rifa.referidos_pendientes (texto_original, texto_norm, numero)
      values (btrim(p_vendedor), rifa.normalizar(p_vendedor), p_numeros[1]);
  end if;

  -- Tope de 20 por comprador (contando lo que ya tiene vigente)
  select count(*) into cnt from rifa.numeros
    where comprador_id = v_cid and estado <> 'LIBRE';
  if cnt + array_length(p_numeros, 1) > 20 then
    raise exception 'ese comprador ya tiene % número(s); máximo 20', cnt;
  end if;

  -- Mapeo de estado interno
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
  end if;

  -- Bloquea los números y verifica que todos estén LIBRE antes de tocar nada (ni pagos)
  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado <> 'LIBRE' then raise exception 'el número % ya está %', n, fila.estado; end if;
  end loop;

  -- Si hay plata, se crea la fila de pago (ya con el candado de los números)
  if v_pago_medio is not null then
    insert into rifa.pagos (medio, moneda, monto, monto_cop, comprador_id, vendedor_id, tiene, recibido_en, verificado_por)
      values (v_pago_medio, v_pago_moneda, v_pago_monto, v_pago_cop, v_cid, v_vid, v_pago_tiene, p_ahora, auth.uid())
      returning id into v_pago_id;
  end if;

  -- Aplica el cambio a cada número y audita (todos comparten el lote)
  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n;
    update rifa.numeros set
      estado = nuevo_estado,
      comprador_id = v_cid,
      vendedor_id = v_vid,
      vendedor_texto = nullif(btrim(coalesce(p_vendedor, '')), ''),
      apartado_en = case when nuevo_estado = 'APARTADO' then p_ahora else null end,
      vence_en = nuevo_vence,
      por_verificar = (p_estado = 'POR_VERIFICAR'),
      pagado_en = case when nuevo_estado = 'PAGADO' then p_ahora else null end,
      metodo = nuevo_metodo,
      pago_id = v_pago_id,
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
grant execute on function public.registrar_venta(char(3)[], text, text, text, text, boolean, boolean, text, text, timestamptz) to authenticated;

-- ────────────── marcar_pagado, marcar_por_verificar, liberar, dar_24h ──────────────

create or replace function public.marcar_pagado(p_numeros char(3)[], p_metodo text, p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); n char(3); fila rifa.numeros%rowtype; antes rifa.numeros%rowtype;
        v_precio numeric; v_precio_nzd numeric; v_tasa numeric;
        v_pago_id bigint; v_pago_medio text; v_pago_moneda text; v_pago_monto numeric; v_pago_cop numeric;
        pago_existente int;
begin
  rol := rifa.rol_actor();
  if p_metodo not in ('NU', 'EFECTIVO', 'NZ') then raise exception 'método inválido'; end if;
  if rol = 'turno' and p_metodo <> 'NZ' then
    raise exception 'tu rol (turno) solo marca pagado con método NZ';
  end if;
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'faltan números'; end if;

  select (valor #>> '{}')::numeric into v_precio from rifa.config where clave = 'precio_cop';
  select (valor #>> '{}')::numeric into v_precio_nzd from rifa.config where clave = 'precio_nzd';
  select (valor #>> '{}')::numeric into v_tasa from rifa.config where clave = 'tasa_cop_nzd';

  -- Bloqueo + verificación de estado
  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado = 'PAGADO' then raise exception 'el número % ya está pagado', n; end if;
    if fila.estado = 'LIBRE' then raise exception 'el número % está libre; usa registrar_venta', n; end if;
  end loop;

  -- Si todos los números apuntan al mismo pago_id (p. ej. EFECTIVO_VENDEDOR), se reutiliza.
  select count(distinct coalesce(pago_id, 0)) into pago_existente from rifa.numeros where numero = any(p_numeros);
  if pago_existente = 1 then
    select pago_id into v_pago_id from rifa.numeros where numero = p_numeros[1];
  end if;
  if v_pago_id is null then
    v_pago_medio := case p_metodo when 'NU' then 'BRE-B' when 'EFECTIVO' then 'EFECTIVO' else 'NZ' end;
    v_pago_moneda := case when p_metodo = 'NZ' then 'NZD' else 'COP' end;
    v_pago_monto := case when p_metodo = 'NZ' then v_precio_nzd * array_length(p_numeros, 1)
                       else v_precio * array_length(p_numeros, 1) end;
    v_pago_cop := case when p_metodo = 'NZ' then v_pago_monto * v_tasa else v_pago_monto end;
    insert into rifa.pagos (medio, moneda, monto, monto_cop, comprador_id, vendedor_id, tiene, recibido_en, verificado_por)
      select v_pago_medio, v_pago_moneda, v_pago_monto, v_pago_cop,
             (select comprador_id from rifa.numeros where numero = p_numeros[1]),
             (select vendedor_id from rifa.numeros where numero = p_numeros[1]),
             'SANTIAGO', p_ahora, auth.uid()
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
grant execute on function public.marcar_pagado(char(3)[], text, timestamptz) to authenticated;

create or replace function public.marcar_por_verificar(p_numeros char(3)[], p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); n char(3); antes rifa.numeros%rowtype; fila rifa.numeros%rowtype;
begin
  rol := rifa.rol_actor();
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'faltan números'; end if;
  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado <> 'APARTADO' then raise exception 'el número % no está apartado', n; end if;
  end loop;
  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n;
    update rifa.numeros set por_verificar = true, actualizado_en = p_ahora where numero = n;
    perform rifa.auditar('MARCAR_POR_VERIFICAR', n, to_jsonb(antes),
      (select to_jsonb(x) from rifa.numeros x where numero = n), v_lote);
  end loop;
  return jsonb_build_object('ok', true, 'lote', v_lote);
end $$;
grant execute on function public.marcar_por_verificar(char(3)[], timestamptz) to authenticated;

create or replace function public.liberar(p_numeros char(3)[], p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); n char(3); antes rifa.numeros%rowtype; fila rifa.numeros%rowtype;
        n_hechos int := 0;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede liberar manualmente'; end if;
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'faltan números'; end if;
  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if antes.estado = 'LIBRE' then continue; end if;
    update rifa.numeros set estado = 'LIBRE', comprador_id = null, vendedor_id = null, vendedor_texto = null,
           apartado_en = null, vence_en = null, por_verificar = false, pagado_en = null, metodo = null,
           pago_id = null, notas = null, actualizado_en = p_ahora
     where numero = n;
    perform rifa.auditar('LIBERAR', n, to_jsonb(antes),
      (select to_jsonb(x) from rifa.numeros x where numero = n), v_lote);
    n_hechos := n_hechos + 1;
  end loop;
  return jsonb_build_object('ok', true, 'lote', v_lote, 'cambios', n_hechos);
end $$;
grant execute on function public.liberar(char(3)[], timestamptz) to authenticated;

create or replace function public.dar_24h(p_numeros char(3)[], p_ahora timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; v_lote uuid := gen_random_uuid(); v_horas int; n char(3); antes rifa.numeros%rowtype; fila rifa.numeros%rowtype;
begin
  rol := rifa.rol_actor();
  if p_numeros is null or array_length(p_numeros, 1) is null then raise exception 'faltan números'; end if;
  select (valor #>> '{}')::int into v_horas from rifa.config where clave = 'horas_apartado';
  foreach n in array p_numeros loop
    select * into fila from rifa.numeros where numero = n for update;
    if not found then raise exception 'el número % no existe', n; end if;
    if fila.estado <> 'APARTADO' then raise exception 'el número % no está apartado', n; end if;
  end loop;
  foreach n in array p_numeros loop
    select * into antes from rifa.numeros where numero = n;
    update rifa.numeros set
      vence_en = p_ahora + make_interval(hours => v_horas),
      apartado_en = coalesce(apartado_en, p_ahora),
      actualizado_en = p_ahora
     where numero = n;
    perform rifa.auditar('DAR_24H', n, to_jsonb(antes),
      (select to_jsonb(x) from rifa.numeros x where numero = n), v_lote);
  end loop;
  return jsonb_build_object('ok', true, 'lote', v_lote);
end $$;
grant execute on function public.dar_24h(char(3)[], timestamptz) to authenticated;

-- ────────────── Deshacer el último lote (o uno dado) ──────────────

create or replace function public.deshacer_ultima(p_lote uuid default null) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  rol text; v_actor uuid := auth.uid(); v_lote uuid; v_nuevo uuid := gen_random_uuid();
  fila rifa.auditoria%rowtype; n_hechos int := 0;
begin
  rol := rifa.rol_actor();
  if p_lote is not null then
    v_lote := p_lote;
  else
    -- El lote más reciente del actor que aún no fue deshecho.
    select lote into v_lote from rifa.auditoria a
     where actor = v_actor
       and clave ~ '^[0-9]{3}$'
       and deshace_lote is null
       and not exists (select 1 from rifa.auditoria b where b.deshace_lote = a.lote)
     order by en desc limit 1;
    if v_lote is null then raise exception 'nada que deshacer'; end if;
  end if;

  -- Restaura cada número al estado `antes` del lote (lista explícita de campos).
  for fila in select * from rifa.auditoria where lote = v_lote and deshace_lote is null order by id loop
    if fila.clave is null or fila.clave !~ '^[0-9]{3}$' or fila.antes is null then continue; end if;
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
    perform rifa.auditar('DESHACER', fila.clave, fila.despues, fila.antes, v_nuevo, v_lote);
    n_hechos := n_hechos + 1;
  end loop;

  if n_hechos = 0 then raise exception 'ese lote no tenía nada que revertir'; end if;
  return jsonb_build_object('ok', true, 'lote_original', v_lote, 'lote_deshace', v_nuevo, 'cambios', n_hechos);
end $$;
grant execute on function public.deshacer_ultima(uuid) to authenticated;

-- ────────────── Lectura para el panel ──────────────

create or replace function public.buscar_comprador(p_q text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; q text := rifa.clave(p_q);
begin
  rol := rifa.rol_actor();
  if q = '' or length(q) < 2 then return '[]'::jsonb; end if;
  return (select coalesce(jsonb_agg(x order by x->>'nombre'), '[]'::jsonb) from (
    select jsonb_build_object(
      'id', c.id, 'nombre', c.nombre_completo, 'pais', c.pais,
      'telefono', case when rol = 'admin' then c.telefono else null end,
      'sale_publico', c.sale_publico, 'quiere_tbw', c.quiere_tbw,
      'numeros_vigentes', (select count(*) from rifa.numeros n where n.comprador_id = c.id and n.estado <> 'LIBRE')
    ) as x from rifa.compradores c
    where c.nombre_norm like '%' || q || '%' or rifa.clave(c.nombre_completo) like '%' || q || '%'
    limit 20) t);
end $$;
grant execute on function public.buscar_comprador(text) to authenticated;

create or replace function public.ficha_numero(p_numero char(3)) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; n rifa.numeros%rowtype; v rifa.vendedores%rowtype; c rifa.compradores%rowtype;
        wa text;
begin
  rol := rifa.rol_actor();
  select * into n from rifa.numeros where numero = p_numero;
  if not found then raise exception 'número % inexistente', p_numero; end if;
  if n.vendedor_id is not null then select * into v from rifa.vendedores where id = n.vendedor_id; end if;
  if n.comprador_id is not null then select * into c from rifa.compradores where id = n.comprador_id; end if;

  if c.telefono is not null and c.telefono <> '' and rol = 'admin' then
    wa := 'https://wa.me/' || regexp_replace(c.telefono, '[^0-9]', '', 'g');
  end if;

  return jsonb_build_object('ok', true,
    'numero', n.numero, 'serial', rifa.serial_de(n.numero), 'estado', n.estado,
    'apartado_en', n.apartado_en, 'vence_en', n.vence_en, 'pagado_en', n.pagado_en,
    'metodo', n.metodo, 'por_verificar', n.por_verificar, 'notas', n.notas,
    'comprador', case when c.id is not null then jsonb_build_object(
      'id', c.id, 'nombre', c.nombre_completo,
      'nombre_acortado', case when c.sale_publico then rifa.acortar(c.nombre_completo) else 'Reservado' end,
      'telefono', case when rol = 'admin' then c.telefono else null end,
      'sale_publico', c.sale_publico, 'quiere_tbw', c.quiere_tbw, 'pais', c.pais) end,
    'vendedor', case when v.id is not null then jsonb_build_object(
      'id', v.id, 'codigo', v.codigo, 'nombre', v.nombre_completo, 'tipo', v.tipo) end,
    'vendedor_texto', n.vendedor_texto,
    'wa_base', wa);
end $$;
grant execute on function public.ficha_numero(char(3)) to authenticated;

create or replace function public.tablero_admin(p_filtro text default 'todos') returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  return (select coalesce(jsonb_agg(x order by x->>'numero'), '[]'::jsonb) from (
    select jsonb_build_object(
      'numero', n.numero, 'estado', n.estado, 'por_verificar', n.por_verificar,
      'vence_en', n.vence_en, 'pagado_en', n.pagado_en, 'metodo', n.metodo,
      'comprador', case when c.id is not null then
        (case when rol = 'admin' then c.nombre_completo
              when c.sale_publico then rifa.acortar(c.nombre_completo) else 'Reservado' end) end,
      'vendedor', v.codigo
    ) as x
    from rifa.numeros n
    left join rifa.compradores c on c.id = n.comprador_id
    left join rifa.vendedores v on v.id = n.vendedor_id
    where (p_filtro = 'todos'
       or (p_filtro = 'pagados'   and n.estado = 'PAGADO')
       or (p_filtro = 'apartados' and n.estado = 'APARTADO')
       or (p_filtro = 'por_verificar' and n.por_verificar)
       or (p_filtro = 'libres'    and n.estado = 'LIBRE'))
  ) t);
end $$;
grant execute on function public.tablero_admin(text) to authenticated;

-- Resumen para la pestaña Inicio del panel
create or replace function public.inicio_cifras() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  return jsonb_build_object(
    'pagados',   (select count(*) from rifa.numeros where estado = 'PAGADO'),
    'apartados', (select count(*) from rifa.numeros where estado = 'APARTADO'),
    'libres',    (select count(*) from rifa.numeros where estado = 'LIBRE'),
    'por_verificar', (select count(*) from rifa.numeros where por_verificar),
    'vencen_pronto', (select count(*) from rifa.numeros
                        where estado = 'APARTADO' and vence_en is not null
                          and vence_en > now() and vence_en <= now() + interval '3 hours'),
    'apartados_sin_fecha', (select count(*) from rifa.numeros where estado='APARTADO' and vence_en is null),
    'referidos_pendientes', (select count(*) from rifa.referidos_pendientes where resuelto_a is null)
  );
end $$;
grant execute on function public.inicio_cifras() to authenticated;
