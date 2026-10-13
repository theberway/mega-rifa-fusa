# Plan Fase 4 — cutover del tablero público

*Guardado el 2026-10-13. Rama de arranque: `claude/sweet-maxwell-bvoqti`. Base: Supabase `oyvrdwkoorkidoadnzmc`.*

Este archivo es el checklist ejecutable. Una sesión nueva puede arrancarlo sin más contexto: leer esto, confirmar pre-condiciones, ejecutar.

**Qué cambia**: la web pública deja de leer el Google Sheet y empieza a leer `tablero_publico()` de Supabase. Decisión 52 ya aprobada por Santiago.

**Qué NO cambia**: `/admin` (sigue como está), el generador privado, el Sheet queda archivado (no se borra).

## Pre-condiciones (verificar antes de tocar nada)

```sql
-- en Supabase SQL:
select (select valor from rifa.config where clave='modo') as modo,
       (select count(*) from rifa.numeros where estado='PAGADO') as pagados,
       (select count(*) from rifa.numeros where estado='APARTADO') as apartados;
```

- `modo` debe ser `ensayo` todavía.
- Pagados y apartados deben coincidir con lo que muestra la web pública en vivo (ventana nocturna → Santiago dejó de editar el Sheet).

```bash
# Hash de la web pública ANTES de tocar nada
md5sum 06_Tablero-Web/publicar/index.html
# Esperado: f41b42dc7becddbff1d2d7a06bc3431e (si Santiago no editó el Sheet entre tanto, 998 libres)
grep -c SHEET_CSV 06_Tablero-Web/publicar/index.html    # 4
grep -c supabase 06_Tablero-Web/publicar/index.html     # 0
grep -c FUENTE 06_Tablero-Web/publicar/index.html       # 0
```

Si la primera venta real ya pasó: avisar a Santiago y confirmar que esta es la ventana aprobada.

## Paso 1 — paridad 1:1

```bash
export SUPABASE_ANON_KEY="sb_publishable_t_e7HPMI1g7rINUYIr0Ehg_OlzMMm3d"
"/c/Users/Santiago/AppData/Local/Python/bin/python.exe" \
   06_Tablero-Web/migracion/verificar.py
```

Resultado requerido: **`Diferencias: 0`**. Si hay diferencias:

1. Si Santiago editó el Sheet en el ínterin: pedirle que detenga ediciones, exportar los CSV privados (`COMPRADORES`, `PAGOS`, `VENDEDORES`) y guardarlos en `06_Tablero-Web/_privado/` (ignorado por git).
2. Ejecutar `06_Tablero-Web/migracion/importar.py` para generar `payload.json`.
3. En Supabase SQL: `select rifa.cargar_copia('<payload.json>'::jsonb);` (solo funciona con `modo='ensayo'`).
4. Repetir `verificar.py` hasta que dé `0`.

**No seguir si no es 0.** Es la red de seguridad del cambio.

## Paso 2 — cambiar la fuente en la web

Editar `06_Tablero-Web/publicar/index.html`:

- Agregar bandera cerca de las constantes (línea ~355):
  ```js
  const FUENTE = "supabase"; // "supabase" | "sheet"
  const SUPA_URL = "https://oyvrdwkoorkidoadnzmc.supabase.co";
  const SUPA_KEY = "sb_publishable_t_e7HPMI1g7rINUYIr0Ehg_OlzMMm3d";
  ```
- Reemplazar `cargarAPI()` para que, cuando `FUENTE === "supabase"`, haga POST a `${SUPA_URL}/rest/v1/rpc/tablero_publico` con headers `apikey` y `Authorization: Bearer <SUPA_KEY>` y `Content-Type: application/json`, body `{}`. La respuesta ya viene con `{ok, t, v: [[n, estado, nombre], ...]}` → el formato que `pintar()` ya entiende.
- Si la llamada falla: NO caer al Sheet (regla fija 3: aviso honesto). Mostrar aviso con `sinDatos(...)`.
- Refresco cada **15 s** (hoy son 20): bajar `setInterval`/`timeout` a `15000`.
- Copiar `06_Tablero-Web/publicar/index.html` a `06_Tablero-Web/index.html` (deben quedar idénticos; `diff -q`).

**Lo que NO se debe tocar**: `SHEET_CSV` sigue como constante (no la borres: es la vía de rollback si por alguna razón hay que volver a leer el Sheet; nunca activa en producción tras el cutover, pero no estorba).

## Paso 3 — selector de referido y mensaje

(Opcional, lo deja limpio para Fase 5). Si `?v=` no viene y no hay `mrf_v` guardado: al tocar «Lo quiero» o WhatsApp, abrir un `<dialog>` con la lista de `vendedores_selector()` (RPC pública). Mensajes:

- Con vendedor: `🎉 Quiero el 607 de la Mega Rifa Fusa, me dijo Juan Carlos (JUANCARLOS)`.
- Nadie: sin «me dijo»; el panel lo asigna a DIR.
- Otra persona: `me dijo <texto>` (sin paréntesis).

Guardar la elección en `localStorage.mrf_ref`. Un `?v=` siempre gana sobre lo guardado.

Si el alcance es mucho para la ventana: entregarlo con Fase 5 y en Fase 4 dejar solo el cambio de fuente.

## Paso 4 — pasar la base a modo real

```sql
update rifa.config set valor = '"real"' where clave = 'modo';
```

Esto bloquea `rifa.cargar_copia()` (negará si no es ensayo). Verificar:

```sql
select rifa.cargar_copia('{}'::jsonb);  -- debe fallar con 'solo en modo ensayo'
```

## Paso 5 — desplegar

```bash
cd 06_Tablero-Web/publicar
PATH="/c/nvm4w/nodejs:$PATH" /c/nvm4w/nodejs/npx.cmd vercel deploy --prod --yes
```

Verificar en vivo:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://mega-rifa-fusa.vercel.app
# El md5 de la home YA DEBE cambiar (es el objetivo del cutover)
curl -s https://mega-rifa-fusa.vercel.app -o /tmp/mrf-vivo.html
grep -c FUENTE /tmp/mrf-vivo.html   # 1 o más (ya no es 0)
grep -c supabase /tmp/mrf-vivo.html # 1 o más
```

En el navegador: abrir https://mega-rifa-fusa.vercel.app, abrir devtools → Network, confirmar que hay una llamada a `/rest/v1/rpc/tablero_publico` y que NO hay llamada a `docs.google.com`.

## Paso 6 — prueba de latencia

En `/admin`, registrar una venta de prueba (apartar un número que no esté usado). En paralelo mirar la web pública: el número debe cambiar a «Ocupado» en **15 s o menos**. Después de la prueba: deshacer la última desde el panel para no dejar el apartado.

## Paso 7 — qué hace Santiago (manual, no Claude)

1. En Google Sheets → Archivo → Compartir → **Publicar en la web** → **Detener publicación**. Esto deja de exponer el CSV con 35 nombres completos.
2. En Google Sheets → Compartir → **Acceso general: Restringido** (solo él). El Sheet queda archivado como respaldo histórico.
3. Confirmar en el panel que todo sigue vendiendo normal.

## Rollback (si algo sale mal en los primeros minutos)

**Opción A** (ventana corta, un paso): en Vercel → el proyecto → Deployments → el deployment anterior → **Promote to Production**. Vuelve a la web vieja (lee el Sheet). Si el Sheet ya quedó sin publicar su CSV: Santiago vuelve a publicarlo mientras se resuelve.

**Opción B** (si Supabase falla después): la web pública muestra el aviso honesto («no pudimos cargar ahora; escríbenos por WhatsApp»). No volver al Sheet silenciosamente.

**Volver `modo='real'` a `'ensayo'`** si hay que recargar la copia:
```sql
update rifa.config set valor = '"ensayo"' where clave='modo';
```

## Paso 8 — decisiones y docs

Después del cutover exitoso:

- Decisión nueva **63**: cutover al modo real, con hora de corte y resultado de la prueba de latencia.
- Actualizar `02_Decisiones/registro-de-decisiones.md`, `plan-maestro.md`, `06_Tablero-Web/base-de-datos.md`, `00_EMPIEZA-AQUI.md`, `HANDOFF-sesion-local.md`.
- Memoria: actualizar `rifa-fusa-tablero-y-sheet` para decir que la web lee Supabase.

## Fase 5 (sigue a 4, no bloquea el cutover)

- `/v/CODIGO` ya está en vivo desde Fase 1 (verificar que sigue respondiendo).
- Actualizar `07_Kit-de-Ventas/05_guia-vendedores-y-tiendas.md`, `03_Hoja-de-ruta/rutina-diaria.md`, `06_Tablero-Web/codigos-de-vendedores.md`, `06_Tablero-Web/LEEME-como-publicar.md` para decir que la fuente es Supabase.
- El Sheet queda como archivo histórico; nadie lo edita más.

## Lo que NO se toca en Fase 4

- `/admin` y las 3 fases ya desplegadas (3A, 3B, 3C).
- El generador privado (`generador-privado.html`).
- Las boletas ya enviadas (el serial y el nombre acortado no cambian).
- Las decisiones congeladas de ventas pasadas.

## Checklist resumen (pegar en el commit)

```
[ ] 1. Pre-condiciones verificadas (modo=ensayo, md5 web intacto)
[ ] 2. verificar.py → Diferencias: 0
[ ] 3. Editado publicar/index.html + copia a 06_Tablero-Web/index.html
[ ] 4. (opcional) selector de referido + mensaje con «me dijo (CODIGO)»
[ ] 5. UPDATE rifa.config SET valor='"real"' WHERE clave='modo'
[ ] 6. vercel deploy --prod --yes
[ ] 7. Verificado en vivo: FUENTE y supabase en el HTML; call a /rpc/tablero_publico
[ ] 8. Prueba de latencia: venta en panel ≤15 s en la web
[ ] 9. Santiago: detener publicación del CSV + restringir acceso al Sheet
[ ] 10. Decisión 63 + docs
```
