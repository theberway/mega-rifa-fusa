-- 003_semilla_vendedores.sql — los 14 vendedores de la carga inicial, los fijos y los códigos viejos conservados.
-- Pedido del 12 oct: código = nombre en MAYÚSCULAS sin tildes ni espacios (codigos-de-vendedores.md).

insert into rifa.vendedores (codigo, nombre_completo, nombre_lista, tipo, activo) values
  ('ANGELICA',   'Angelica Aranguren',  null,   'PERSONA', true),
  ('MARIAJOSE',  'Maria Jose Lozano',   null,   'PERSONA', true),
  ('JULIANA',    'Juliana Gomez',       null,   'PERSONA', true),
  ('JUANCARLOS', 'Juan Carlos Montaña', null,   'PERSONA', true),
  ('SOFIA',      'Sofia Montaña',       'Sofia','NZ',      true),   -- es la Sofía de Nueva Zelanda (N01), confirmado el 12 oct
  ('YOLANDA',    'Yolanda Bermudez',    null,   'PERSONA', true),
  ('ANDRES',     'Andres Bernal',       null,   'PERSONA', true),
  ('PAULAV',     'Paula Valencia',      'Paula','PERSONA', true),
  ('ANALUCIA',   'Ana Lucia Bello',     null,   'PERSONA', true),
  ('CESAR',      'Cesar Casas',         null,   'PERSONA', true),
  ('BRAYAN',     'Brayan Sarmiento',    null,   'PERSONA', true),
  ('GABRIELA',   'Gabriela Quitian',    null,   'PERSONA', true),
  ('SOPHIA',     'Sophia Moreno',       null,   'PERSONA', true),
  ('PAULAG',     'Paula Gomez',         'Paula','PERSONA', true);

-- Especiales: nunca salen en el selector ni tienen mini-tarjeta
insert into rifa.vendedores (codigo, nombre_completo, tipo, activo) values
  ('SBG', 'Santiago (venta directa)', 'ESPECIAL', true),
  ('DIR', 'Sin vendedor (llegó solo)', 'ESPECIAL', true);

-- Códigos viejos sin asignar (V01–V12, T01–T03, N02): se conservan inactivos por si algún link ya circula
insert into rifa.vendedores (codigo, nombre_completo, tipo, activo)
select 'V' || lpad(g::text, 2, '0'), 'Código reservado V' || lpad(g::text, 2, '0') || ' (sin asignar)', 'PERSONA', false
from generate_series(1, 12) g;
insert into rifa.vendedores (codigo, nombre_completo, tipo, activo)
select 'T' || lpad(g::text, 2, '0'), 'Código reservado T' || lpad(g::text, 2, '0') || ' (sin asignar)', 'TIENDA', false
from generate_series(1, 3) g;
insert into rifa.vendedores (codigo, nombre_completo, tipo, activo)
values ('N02', 'Código reservado N02 (reserva de Sofía)', 'NZ', false);

-- Alias: los links y textos ya emitidos siguen contando
insert into rifa.vendedor_alias (alias_clave, vendedor_id)
select a.alias, v.id from (values ('N01', 'SOFIA'), ('MARIAJO', 'MARIAJOSE'), ('TIAJULY', 'JULIANA')) as a(alias, cod)
join rifa.vendedores v on v.codigo = a.cod;
