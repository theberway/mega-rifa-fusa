-- 001_base.sql — esquema privado `rifa`, funciones puras, tablas, RLS y auditoría inmutable.
-- Las tablas viven en el esquema `rifa`, que la API de Supabase NO expone (solo expone `public`).
-- Aun así todas llevan RLS activado y sin políticas: ni anon ni authenticated tienen acceso directo.
-- Lo único alcanzable desde afuera son las funciones RPC de `public` (002 en adelante).

create schema if not exists rifa;
revoke all on schema rifa from public, anon, authenticated;
create extension if not exists unaccent with schema extensions;

-- ───────────── Funciones puras (misma regla que la web y el Apps Script) ─────────────

-- MAYÚSCULAS, sin tildes (ñ→N), espacios simples: «josé  PÉREZ» → «JOSE PEREZ»
create or replace function rifa.normalizar(t text) returns text
language sql stable set search_path = '' as $$
  select upper(btrim(regexp_replace(extensions.unaccent('extensions.unaccent', coalesce(t, '')), '\s+', ' ', 'g')))
$$;

-- Solo A-Z0-9: la forma en que la web limpia ?v= («Tia July» → «TIAJULY»)
create or replace function rifa.clave(t text) returns text
language sql stable set search_path = '' as $$
  select regexp_replace(rifa.normalizar(t), '[^A-Z0-9]', '', 'g')
$$;

-- «Juan Perez» → «Jua*** P.» (3 letras del nombre + *** + inicial de la 2.ª palabra). Idéntica a acortar() de la web.
create or replace function rifa.acortar(txt text) returns text
language plpgsql stable set search_path = '' as $$
declare t text; p text[]; w text; a text; b text;
begin
  t := btrim(regexp_replace(coalesce(txt, ''), '\s+', ' ', 'g'));
  if t ~* '^reservad[oa]$' then return 'Reservado'; end if;
  if t = '' or position('*' in t) > 0 then return t; end if;
  p := string_to_array(t, ' ');
  w := left(p[1], 3);
  a := upper(left(w, 1)) || lower(substr(w, 2));
  b := case when array_length(p, 1) >= 2 then ' ' || upper(left(p[2], 1)) || '.' else '' end;
  return a || '***' || b;
end $$;

-- Etiqueta por defecto del selector: con 3+ palabras las dos primeras («Juan Carlos»), si no la primera.
create or replace function rifa.etiqueta_base(n text) returns text
language plpgsql immutable set search_path = '' as $$
declare p text[];
begin
  p := string_to_array(btrim(regexp_replace(coalesce(n, ''), '\s+', ' ', 'g')), ' ');
  return case when array_length(p, 1) >= 3 then p[1] || ' ' || p[2] else p[1] end;
end $$;

-- ───────────── Tablas ─────────────

create table rifa.usuarios_panel (
  user_id uuid primary key references auth.users(id) on delete cascade,
  rol text not null check (rol in ('admin', 'turno')),
  nombre text not null
);

create table rifa.vendedores (
  id bigint generated always as identity primary key,
  codigo text not null unique check (codigo ~ '^[A-Z0-9]{1,24}$'),
  nombre_completo text not null,
  nombre_lista text,                       -- etiqueta pública; null = la por defecto (etiqueta_base)
  tipo text not null check (tipo in ('PERSONA', 'TIENDA', 'NZ', 'ESPECIAL')),
  telefono text,                           -- privado: nunca sale en una vista pública
  activo boolean not null default true,
  creado_en timestamptz not null default now()
);

create table rifa.vendedor_alias (
  alias_clave text primary key check (alias_clave ~ '^[A-Z0-9]{1,40}$'),
  vendedor_id bigint not null references rifa.vendedores(id)
);

create table rifa.compradores (
  id bigint generated always as identity primary key,
  nombre_completo text not null,
  nombre_norm text not null,
  telefono text,
  sale_publico boolean not null default true,
  quiere_tbw boolean,
  pais text not null default 'CO' check (pais in ('CO', 'NZ')),
  creado_en timestamptz not null default now()
);
create index on rifa.compradores (nombre_norm);

create table rifa.pagos (
  id bigint generated always as identity primary key,
  medio text not null check (medio in ('BRE-B', 'EFECTIVO', 'TIENDA', 'NZ')),
  moneda text not null default 'COP' check (moneda in ('COP', 'NZD')),
  monto numeric not null default 0,
  monto_cop numeric not null default 0,
  comprador_id bigint references rifa.compradores(id),
  vendedor_id bigint references rifa.vendedores(id),
  tiene text check (tiene in ('SANTIAGO', 'VENDEDOR')),   -- solo para efectivo: quién tiene la plata
  recibido_en timestamptz not null default now(),
  entregado_en timestamptz,                -- el vendedor se la dio a Santiago
  consignado_en timestamptz,               -- Santiago la consignó
  verificado_por uuid,
  creado_en timestamptz not null default now()
);

create table rifa.numeros (
  numero char(3) primary key check (numero ~ '^[0-9]{3}$'),
  estado text not null default 'LIBRE' check (estado in ('LIBRE', 'APARTADO', 'PAGADO')),
  comprador_id bigint references rifa.compradores(id),
  vendedor_id bigint references rifa.vendedores(id),
  vendedor_texto text,                     -- lo que dijo el comprador, sin tocar
  apartado_en timestamptz,
  vence_en timestamptz,                    -- null = no vence solo (apartados migrados sin fecha válida)
  por_verificar boolean not null default false,
  pagado_en timestamptz,
  metodo text check (metodo in ('NU', 'EFECTIVO', 'NZ')),
  pago_id bigint references rifa.pagos(id),
  notas text,
  actualizado_en timestamptz not null default now(),
  check (estado = 'LIBRE' or comprador_id is not null)
);
create index on rifa.numeros (estado);
create index on rifa.numeros (vendedor_id);
create index on rifa.numeros (comprador_id);

create table rifa.referidos_pendientes (
  id bigint generated always as identity primary key,
  texto_original text not null,
  texto_norm text not null,
  numero char(3),
  creado_en timestamptz not null default now(),
  resuelto_a bigint references rifa.vendedores(id),
  resuelto_en timestamptz
);

create table rifa.auditoria (
  id bigint generated always as identity primary key,
  en timestamptz not null default now(),
  actor uuid,
  actor_nombre text,
  accion text not null,
  clave text,                              -- p. ej. el número
  antes jsonb,
  despues jsonb,
  lote uuid not null default gen_random_uuid(),
  deshace_lote uuid                        -- si esta fila es un «deshacer», el lote que revierte
);
create index on rifa.auditoria (en desc);
create index on rifa.auditoria (lote);

create or replace function rifa.bloquear_cambios() returns trigger
language plpgsql set search_path = '' as $$
begin raise exception 'la auditoría es inmutable'; end $$;
create trigger auditoria_inmutable before update or delete on rifa.auditoria
  for each row execute function rifa.bloquear_cambios();
create trigger auditoria_sin_truncate before truncate on rifa.auditoria
  for each statement execute function rifa.bloquear_cambios();

create table rifa.config (
  clave text primary key,
  valor jsonb not null
);

create table rifa.push_suscripciones (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  creado_en timestamptz not null default now()
);

create table rifa.alertas_enviadas (
  clave text primary key,
  enviada_en timestamptz not null default now()
);

create table rifa.respaldos (
  fecha date primary key,
  datos jsonb not null,
  creado_en timestamptz not null default now()
);

-- RLS en todo, sin políticas = nadie entra por la API. Y sin permisos de tabla para los roles de la API.
alter table rifa.usuarios_panel enable row level security;
alter table rifa.vendedores enable row level security;
alter table rifa.vendedor_alias enable row level security;
alter table rifa.compradores enable row level security;
alter table rifa.pagos enable row level security;
alter table rifa.numeros enable row level security;
alter table rifa.referidos_pendientes enable row level security;
alter table rifa.auditoria enable row level security;
alter table rifa.config enable row level security;
alter table rifa.push_suscripciones enable row level security;
alter table rifa.alertas_enviadas enable row level security;
alter table rifa.respaldos enable row level security;
revoke all on all tables in schema rifa from public, anon, authenticated;
revoke all on all sequences in schema rifa from public, anon, authenticated;
revoke all on all functions in schema rifa from public, anon, authenticated;

-- Los 1.000 números, todos libres
insert into rifa.numeros (numero)
select lpad(g::text, 3, '0') from generate_series(0, 999) g;

-- Valores del modelo financiero (04_Finanzas/modelo-financiero.xlsx, hoja SUPUESTOS) y puntos de control
insert into rifa.config (clave, valor) values
  ('modo',                 '"ensayo"'),
  ('total_numeros',        '1000'),
  ('precio_cop',           '6000'),
  ('precio_nzd',           '4'),
  ('tasa_cop_nzd',         '1843'),
  ('piso_neto',            '3000000'),
  ('meta_numeros',         '900'),
  ('premio',               '2000000'),
  ('premio_vendedor',      '100000'),
  ('gastos_varios',        '50000'),
  ('comision_tienda',      '0.1'),
  ('tizumba',              '0'),
  ('tizumba_costo',        '100000'),
  ('consolacion',          '210000'),
  ('pct_nz',               '0.08'),
  ('pct_tiendas',          '0.10'),
  ('umbral_compradores',   '25'),
  ('horas_apartado',       '24'),
  ('horas_efectivo_vendedor', '48'),
  ('horas_consignar',      '24'),
  ('exigir_2fa',           'true'),
  ('cierre',               '"2026-12-05T18:00:00-05:00"'),
  ('puntos_control',       '[{"fecha":"2026-10-12","meta":120},{"fecha":"2026-10-18","meta":230},{"fecha":"2026-10-25","meta":320},{"fecha":"2026-11-01","meta":420},{"fecha":"2026-11-08","meta":500},{"fecha":"2026-11-15","meta":600},{"fecha":"2026-11-22","meta":690},{"fecha":"2026-11-29","meta":750}]');

-- Auditoría: una fila por cambio
create or replace function rifa.auditar(p_accion text, p_clave text, p_antes jsonb, p_despues jsonb,
                                         p_lote uuid default gen_random_uuid(), p_deshace uuid default null)
returns uuid language plpgsql security definer set search_path = '' as $$
declare v_nombre text;
begin
  select nombre into v_nombre from rifa.usuarios_panel where user_id = auth.uid();
  insert into rifa.auditoria (actor, actor_nombre, accion, clave, antes, despues, lote, deshace_lote)
  values (auth.uid(), v_nombre, p_accion, p_clave, p_antes, p_despues, p_lote, p_deshace);
  return p_lote;
end $$;
