-- paridad.sql — pruebas de las funciones puras y del vencimiento. Imprime PASA / FALLA por caso.

-- acortar
with casos (entrada, esperado) as (values
  ('Juan Perez',                'Jua*** P.'),
  ('María de los Ángeles Ruiz', 'Mar*** D.'),
  ('Catalina',                  'Cat***'),
  ('Reservado',                 'Reservado'),
  ('reservada',                 'Reservado'),
  ('Jua*** P.',                 'Jua*** P.'),
  ('',                          ''))
select entrada, esperado, rifa.acortar(entrada) real,
       case when rifa.acortar(entrada) is not distinct from esperado then 'PASA' else 'FALLA' end v
from casos;

-- normalizar
with norm (entrada, esperado) as (values
  ('josé  PÉREZ',   'JOSE PEREZ'),
  ('  Muñoz  Ñero', 'MUNOZ NERO'),
  ('ana lucia',     'ANA LUCIA'))
select entrada, esperado, rifa.normalizar(entrada) real,
       case when rifa.normalizar(entrada) = esperado then 'PASA' else 'FALLA' end v
from norm;

-- sugerir_codigo cuando el vendedor es NUEVO (nombre no coincide con uno ya cargado).
-- Lo probamos usando una copia hipotética: creamos vendedores en un savepoint y lo revertimos.
begin;
savepoint s;
delete from rifa.vendedor_alias;
delete from rifa.vendedores;
-- primer "Paula ..." → PAULA; el segundo necesita la inicial del apellido
with t as (select rifa.sugerir_codigo('Paula Valencia') as c1)
insert into rifa.vendedores (codigo, nombre_completo, tipo) select c1, 'Paula Valencia', 'PERSONA' from t;
with t as (select rifa.sugerir_codigo('Paula Gomez')    as c2)
insert into rifa.vendedores (codigo, nombre_completo, tipo) select c2, 'Paula Gomez',    'PERSONA' from t;
with t as (select rifa.sugerir_codigo('Paula Rojas')    as c3)
insert into rifa.vendedores (codigo, nombre_completo, tipo) select c3, 'Paula Rojas',    'PERSONA' from t;
select 'reseed' as caso, codigo, nombre_completo from rifa.vendedores order by id;
rollback to savepoint s;
rollback;

-- vencimiento con reloj simulado: un apartado con fecha vieja se libera; uno sin fecha, no.
do $$
declare n_libre int; n_apart int;
begin
  update rifa.numeros set estado='APARTADO', comprador_id=(select id from rifa.compradores limit 1),
         apartado_en=now() - interval '25 hours',
         vence_en=(now() - interval '25 hours') + interval '24 hours'
   where numero='999';
  perform rifa.liberar_vencidos();
  select count(*) into n_libre from rifa.numeros where numero='999' and estado='LIBRE';
  if n_libre <> 1 then raise exception 'FALLA vencimiento 999'; end if;
  raise notice 'PASA: vencimiento 999';
  -- apartado sin fecha debe seguir en APARTADO
  select count(*) into n_apart from rifa.numeros where numero in ('007','042','444','607','822','873') and estado='APARTADO';
  if n_apart <> 6 then raise exception 'FALLA: apartados sin fecha % en APARTADO (esperaba 6)', n_apart; end if;
  raise notice 'PASA: apartados sin fecha preservados';
end $$;
