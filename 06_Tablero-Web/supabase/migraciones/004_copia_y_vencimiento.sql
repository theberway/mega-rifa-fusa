-- 004_copia_y_vencimiento.sql — carga repetible de la COPIA del Sheet (solo en modo ensayo) y vencimiento automático.

-- Libera los apartados cuyo vencimiento ya pasó. p_ahora permite probar con reloj simulado.
-- Los apartados SIN vence_en (migrados sin fecha válida, decisión 51) nunca se tocan aquí.
create or replace function rifa.liberar_vencidos(p_ahora timestamptz default now()) returns int
language plpgsql security definer set search_path = '' as $$
declare r rifa.numeros%rowtype; n int := 0;
begin
  for r in select * from rifa.numeros
           where estado = 'APARTADO' and vence_en is not null and vence_en <= p_ahora for update loop
    perform rifa.auditar('VENCIO', r.numero, to_jsonb(r), jsonb_build_object('estado', 'LIBRE'));
    update rifa.numeros set estado = 'LIBRE', comprador_id = null, vendedor_id = null, vendedor_texto = null,
           apartado_en = null, vence_en = null, por_verificar = false, pagado_en = null, metodo = null,
           pago_id = null, notas = null, actualizado_en = now()
     where numero = r.numero;
    n := n + 1;
  end loop;
  return n;
end $$;

-- Carga la copia del Sheet. Entrada: [{n, estado, hora (ISO o null), vend, nombre, nota}, ...].
-- SOLO funciona en modo 'ensayo': después del cambio (Fase 4) se niega a borrar nada.
create or replace function rifa.cargar_copia(p jsonb) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  r jsonb; modo text; est text; nom text; cid bigint; vid bigint; hora timestamptz; horas int;
  v_txt text; reservado boolean; tot int := 0; pag int := 0; apa int := 0; sin_fecha int := 0; sin_vend int := 0;
  no_resueltos int := 0; blancos int := 0;
begin
  select valor #>> '{}' into modo from rifa.config where clave = 'modo';
  if modo is distinct from 'ensayo' then raise exception 'cargar_copia solo funciona en modo ensayo'; end if;
  select (valor #>> '{}')::int into horas from rifa.config where clave = 'horas_apartado';

  update rifa.numeros set estado = 'LIBRE', comprador_id = null, vendedor_id = null, vendedor_texto = null,
         apartado_en = null, vence_en = null, por_verificar = false, pagado_en = null, metodo = null,
         pago_id = null, notas = null, actualizado_en = now();
  delete from rifa.pagos;
  delete from rifa.referidos_pendientes;
  delete from rifa.compradores;

  for r in select * from jsonb_array_elements(p) loop
    est := upper(coalesce(r->>'estado', ''));
    if est not in ('PAGADO', 'APARTADO') then continue; end if;
    tot := tot + 1;
    nom := btrim(coalesce(r->>'nombre', ''));
    reservado := nom ~* '^reservad[oa]$';

    if nom = '' then
      blancos := blancos + 1;
      nom := 'Sin nombre (migrado)';
    end if;
    if reservado then   -- cada «Reservado» es una persona distinta: el nombre real llega con el CSV privado
      insert into rifa.compradores (nombre_completo, nombre_norm, sale_publico)
      values ('Reservado ' || (r->>'n'), rifa.normalizar('Reservado ' || (r->>'n')), false) returning id into cid;
    else
      select id into cid from rifa.compradores where nombre_norm = rifa.normalizar(nom) limit 1;
      if cid is null then
        insert into rifa.compradores (nombre_completo, nombre_norm) values (nom, rifa.normalizar(nom)) returning id into cid;
      end if;
    end if;

    -- hora del apartado: solo vale si trae fecha; «12:00» a secas no sirve (decisión 51)
    hora := null;
    begin hora := nullif(r->>'hora', '')::timestamptz; exception when others then hora := null; end;
    if est = 'APARTADO' and hora is null then sin_fecha := sin_fecha + 1; end if;

    v_txt := nullif(btrim(coalesce(r->>'vend', '')), '');
    vid := case when v_txt is null then null else rifa.buscar_vendedor(v_txt) end;
    if v_txt is null then sin_vend := sin_vend + 1;
    elsif vid is null then
      no_resueltos := no_resueltos + 1;
      insert into rifa.referidos_pendientes (texto_original, texto_norm, numero)
      values (v_txt, rifa.normalizar(v_txt), r->>'n');
    end if;

    update rifa.numeros set estado = est, comprador_id = cid, vendedor_id = vid, vendedor_texto = v_txt,
           apartado_en = case when est = 'APARTADO' then hora end,
           vence_en = case when est = 'APARTADO' and hora is not null then hora + make_interval(hours => horas) end,
           notas = nullif(btrim(coalesce(r->>'nota', '')), ''), actualizado_en = now()
     where numero = r->>'n';
    if not found then raise exception 'número inexistente: %', r->>'n'; end if;
    if est = 'PAGADO' then pag := pag + 1; else apa := apa + 1; end if;
  end loop;

  perform rifa.auditar('IMPORTAR_COPIA', null, null,
    jsonb_build_object('pagados', pag, 'apartados', apa, 'apartados_sin_fecha', sin_fecha,
                       'sin_vendedor', sin_vend, 'vendedor_no_resuelto', no_resueltos));
  return jsonb_build_object('filas', tot, 'pagados', pag, 'apartados', apa, 'apartados_sin_fecha', sin_fecha,
    'sin_vendedor', sin_vend, 'vendedor_no_resuelto', no_resueltos, 'nombres_en_blanco', blancos,
    'compradores', (select count(*) from rifa.compradores));
end $$;

-- Vencimiento cada 5 minutos
create extension if not exists pg_cron;
select cron.schedule('rifa-liberar-vencidos', '*/5 * * * *', $$select rifa.liberar_vencidos()$$);
