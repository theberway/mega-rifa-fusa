-- 005_rpcs_panel.sql — RPCs del panel.
-- Todas se exponen en `public`, con SECURITY DEFINER. Antes de hacer nada verifican que
-- quien llama esté en `rifa.usuarios_panel` y tenga el rol que corresponde.
-- La auditoría registra actor, antes y después. «turno» (Sofía) tiene permisos acotados.

-- Guard: devuelve ('admin'|'turno') o rechaza. Exige aal2 solo para admin.
create or replace function rifa.rol_actor() returns text
language plpgsql security definer set search_path = '' as $$
declare r text; aal text;
begin
  if auth.uid() is null then raise exception 'sin sesión'; end if;
  select rol into r from rifa.usuarios_panel where user_id = auth.uid();
  if r is null then raise exception 'sin permiso'; end if;
  -- 2FA obligatorio para admin (decisión 46)
  if r = 'admin' then
    begin aal := coalesce((auth.jwt() -> 'aal')::text, '"aal1"'); exception when others then aal := '"aal1"'; end;
    if aal is distinct from '"aal2"' then
      -- se puede desactivar bajando config.exigir_2fa, para el día que estés sin tu teléfono
      if coalesce((select valor::text::boolean from rifa.config where clave = 'exigir_2fa'), true) then
        raise exception 'admin requiere 2FA (aal2)';
      end if;
    end if;
  end if;
  return r;
end $$;

grant execute on function rifa.rol_actor() to authenticated;

-- ──────────────── VENDEDORES ────────────────

create or replace function public.sugerir_codigo(p_nombre text) returns text
language plpgsql security definer set search_path = '' as $$
declare r text;
begin
  perform rifa.rol_actor();
  return rifa.sugerir_codigo(p_nombre);
end $$;
grant execute on function public.sugerir_codigo(text) to authenticated;

create or replace function public.listar_vendedores() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text;
begin
  rol := rifa.rol_actor();
  return (select coalesce(jsonb_agg(x order by codigo), '[]'::jsonb) from (
    select v.id, v.codigo, v.nombre_completo, v.tipo, v.activo,
           coalesce(v.nombre_lista, rifa.etiqueta_base(v.nombre_completo)) as etiqueta,
           case when rol = 'admin' then v.telefono else null end as telefono,
           (select count(*) from rifa.numeros n where n.vendedor_id = v.id and n.estado = 'PAGADO') as pagados,
           (select count(distinct n.comprador_id) from rifa.numeros n where n.vendedor_id = v.id and n.estado = 'PAGADO') as compradores,
           (select count(*) from rifa.numeros n where n.vendedor_id = v.id and n.estado = 'APARTADO'
                                                 and (n.vence_en is null or n.vence_en > now())) as apartados,
           case when rol = 'admin' then
             coalesce((select sum(monto_cop) from rifa.pagos p where p.vendedor_id = v.id and p.tiene = 'VENDEDOR'
                                                                 and p.entregado_en is null), 0)
             else null end as efectivo_pendiente_cop
    from rifa.vendedores v
    order by v.codigo) x);
end $$;
grant execute on function public.listar_vendedores() to authenticated;

create or replace function public.crear_vendedor(p_nombre text, p_tipo text, p_codigo text default null, p_telefono text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; cod text; v_id bigint;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede crear vendedores'; end if;
  if p_tipo not in ('PERSONA', 'TIENDA', 'NZ') then raise exception 'tipo inválido'; end if;
  cod := coalesce(nullif(upper(regexp_replace(p_codigo, '[^A-Z0-9]', '', 'g')), ''),
                  rifa.sugerir_codigo(p_nombre));
  if length(cod) > 24 then raise exception 'código largo (máx 24)'; end if;
  if cod ~ '^(SBG|DIR)$' then raise exception 'código reservado'; end if;
  insert into rifa.vendedores (codigo, nombre_completo, tipo, telefono, activo)
    values (cod, btrim(p_nombre), p_tipo, nullif(btrim(p_telefono), ''), true)
    returning id into v_id;
  perform rifa.auditar('CREAR_VENDEDOR', cod, null, jsonb_build_object('id', v_id, 'nombre', p_nombre, 'tipo', p_tipo));
  return jsonb_build_object('ok', true, 'id', v_id, 'codigo', cod,
    'link', 'https://mega-rifa-fusa.vercel.app/?v=' || cod);
exception when unique_violation then
  raise exception 'ya existe un vendedor o alias con el código %', cod;
end $$;
grant execute on function public.crear_vendedor(text, text, text, text) to authenticated;

create or replace function public.editar_vendedor(p_id bigint, p_nombre text default null, p_nombre_lista text default null,
                                                    p_tipo text default null, p_telefono text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare rol text; antes rifa.vendedores%rowtype;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin puede editar vendedores'; end if;
  select * into antes from rifa.vendedores where id = p_id;
  if not found then raise exception 'no existe'; end if;
  update rifa.vendedores set
    nombre_completo = coalesce(nullif(btrim(p_nombre), ''), nombre_completo),
    nombre_lista = case when p_nombre_lista is null then nombre_lista
                        when btrim(p_nombre_lista) = '' then null
                        else btrim(p_nombre_lista) end,
    tipo = case when p_tipo is null then tipo
                when p_tipo in ('PERSONA', 'TIENDA', 'NZ', 'ESPECIAL') then p_tipo
                else tipo end,
    telefono = case when p_telefono is null then telefono
                    when btrim(p_telefono) = '' then null
                    else btrim(p_telefono) end
   where id = p_id;
  perform rifa.auditar('EDITAR_VENDEDOR', antes.codigo, to_jsonb(antes),
                       (select to_jsonb(v) from rifa.vendedores v where id = p_id));
  return jsonb_build_object('ok', true);
end $$;
grant execute on function public.editar_vendedor(bigint, text, text, text, text) to authenticated;

create or replace function public.cambiar_estado_vendedor(p_id bigint, p_activo boolean) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; antes rifa.vendedores%rowtype;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  select * into antes from rifa.vendedores where id = p_id;
  if not found then raise exception 'no existe'; end if;
  if antes.tipo = 'ESPECIAL' then raise exception 'SBG y DIR no se desactivan'; end if;
  update rifa.vendedores set activo = p_activo where id = p_id;
  perform rifa.auditar(case when p_activo then 'ACTIVAR_VENDEDOR' else 'DESACTIVAR_VENDEDOR' end,
                       antes.codigo, to_jsonb(antes),
                       jsonb_build_object('activo', p_activo));
  return jsonb_build_object('ok', true);
end $$;
grant execute on function public.cambiar_estado_vendedor(bigint, boolean) to authenticated;

create or replace function public.fusionar_alias(p_alias text, p_vendedor_id bigint) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; clv text; v_id bigint; existe int;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  clv := rifa.clave(p_alias);
  if clv = '' then raise exception 'alias vacío'; end if;
  if length(clv) > 40 then raise exception 'alias muy largo'; end if;
  select id into v_id from rifa.vendedores where id = p_vendedor_id;
  if v_id is null then raise exception 'vendedor inexistente'; end if;
  if exists (select 1 from rifa.vendedores where codigo = clv) then
    raise exception 'ese alias ya es un código existente';
  end if;
  insert into rifa.vendedor_alias (alias_clave, vendedor_id) values (clv, p_vendedor_id)
    on conflict (alias_clave) do update set vendedor_id = excluded.vendedor_id;
  -- Reasigna ventas pendientes de resolver con ese texto
  update rifa.numeros set vendedor_id = p_vendedor_id
   where vendedor_id is null and rifa.clave(vendedor_texto) = clv;
  update rifa.referidos_pendientes set resuelto_a = p_vendedor_id, resuelto_en = now()
   where resuelto_a is null and rifa.clave(texto_original) = clv;
  perform rifa.auditar('FUSIONAR_ALIAS', clv, null, jsonb_build_object('vendedor_id', p_vendedor_id));
  return jsonb_build_object('ok', true, 'alias', clv);
end $$;
grant execute on function public.fusionar_alias(text, bigint) to authenticated;

create or replace function public.referidos_pendientes() returns jsonb
language plpgsql security definer set search_path = '' as $$
begin
  perform rifa.rol_actor();
  return (select coalesce(jsonb_agg(jsonb_build_object(
    'id', id, 'texto', texto_original, 'texto_norm', texto_norm,
    'numero', numero, 'creado_en', creado_en) order by creado_en desc), '[]'::jsonb)
    from rifa.referidos_pendientes where resuelto_a is null);
end $$;
grant execute on function public.referidos_pendientes() to authenticated;

create or replace function public.resolver_referido(p_id bigint, p_vendedor_id bigint, p_crear_alias boolean default true) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; ref rifa.referidos_pendientes%rowtype; clv text;
begin
  rol := rifa.rol_actor();
  if rol <> 'admin' then raise exception 'solo admin'; end if;
  select * into ref from rifa.referidos_pendientes where id = p_id;
  if not found then raise exception 'no existe'; end if;
  update rifa.referidos_pendientes set resuelto_a = p_vendedor_id, resuelto_en = now() where id = p_id;
  update rifa.numeros set vendedor_id = p_vendedor_id
   where numero = ref.numero and vendedor_id is null;
  if p_crear_alias then
    clv := rifa.clave(ref.texto_original);
    if clv <> '' and not exists (select 1 from rifa.vendedores where codigo = clv) then
      insert into rifa.vendedor_alias (alias_clave, vendedor_id) values (clv, p_vendedor_id)
        on conflict (alias_clave) do update set vendedor_id = excluded.vendedor_id;
    end if;
  end if;
  perform rifa.auditar('RESOLVER_REFERIDO', ref.texto_original, to_jsonb(ref),
                       jsonb_build_object('vendedor_id', p_vendedor_id, 'crear_alias', p_crear_alias));
  return jsonb_build_object('ok', true);
end $$;
grant execute on function public.resolver_referido(bigint, bigint, boolean) to authenticated;

create or replace function public.detalle_vendedor(p_id bigint) returns jsonb
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
      'n', numero, 'estado', estado, 'comprador',
      case when c.sale_publico then rifa.acortar(c.nombre_completo) else 'Reservado' end,
      'fecha', coalesce(pagado_en, apartado_en)) order by numero), '[]'::jsonb)
      from rifa.numeros n left join rifa.compradores c on c.id = n.comprador_id
      where n.vendedor_id = v.id and n.estado in ('PAGADO', 'APARTADO')));
end $$;
grant execute on function public.detalle_vendedor(bigint) to authenticated;

create or replace function public.mi_perfil() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare rol text; nom text;
begin
  if auth.uid() is null then return jsonb_build_object('ok', false); end if;
  select u.rol, u.nombre into rol, nom from rifa.usuarios_panel u where u.user_id = auth.uid();
  if rol is null then return jsonb_build_object('ok', false, 'motivo', 'no en lista blanca'); end if;
  return jsonb_build_object('ok', true, 'rol', rol, 'nombre', nom, 'exige_2fa',
    coalesce((select valor::text::boolean from rifa.config where clave = 'exigir_2fa'), true));
end $$;
grant execute on function public.mi_perfil() to authenticated;
