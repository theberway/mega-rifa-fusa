# Plan: panel admin + base de datos + vendedores y referidos (Mega Rifa Fusa)

## Contexto

Hoy todo vive en el Google Sheet. Santiago lo edita desde el celular, y lo que pasa de verdad es esto (CSV público leído el 12 oct, 23:25):

- **31 pagados, 6 apartados, 963 libres**. Son 15 compradores distintos y uno de ellos tiene 10 números.
- **35 de los 37 nombres están completos** en `NUMEROS!E`. La web los acorta, pero el CSV público, cuyo link está en el código de la página, los muestra enteros. `COMPRADORES` casi seguro está vacía.
- **Los 6 apartados no tienen fecha válida** (`FALTA LA HORA` / `FALTA LA FECHA`), así que nunca vencen. El script de la hora no está instalado.
- **El vendedor se escribe a mano**: hay 2 ventas con alias («Mariajo» en el 575, «Tia July» en el 791), no con códigos.
- No hay registro de efectivo ni de consignación, ni auditoría de quién cambió qué.

Este pedido (`<ampliacion_vendedores>`) es la tercera parte del prompt unificado de la sesión anterior: base de datos y panel, referidos, y vendedores. Con tus respuestas de hoy, el alcance es el **plan completo por fases, sin afectar a nadie que ya compró**:

- **Sofía Montaña = la Sofía de NZ (N01)**.
- Alertas: **notificaciones en el celular (PWA)**.
- Sofía tiene **cuenta propia de turno**.
- **Mariajo → MARIAJOSE** y **Tia July → JULIANA**.

La base es el proyecto de Supabase que ya creaste: `oyvrdwkoorkidoadnzmc`, en Canadá, plan gratis y hoy vacío. Trae pg_cron, pg_net y unaccent. El despliegue va por la API REST de Vercel al proyecto `mega-rifa-fusa` (equipo `team_fDZUBDk4ynif732wPrTpXxQU`); comprobé que tengo acceso con el token del proxy.

## Tabla de links (ya funcionan hoy: la web acepta `?v=` desde el 10 oct)

| Vendedor | Código | Link |
|---|---|---|
| Andres Bernal | ANDRES | https://mega-rifa-fusa.vercel.app/?v=ANDRES |
| Ana Lucia Bello | ANALUCIA | https://mega-rifa-fusa.vercel.app/?v=ANALUCIA |
| Angelica Aranguren | ANGELICA | https://mega-rifa-fusa.vercel.app/?v=ANGELICA |
| Brayan Sarmiento | BRAYAN | https://mega-rifa-fusa.vercel.app/?v=BRAYAN |
| Cesar Casas | CESAR | https://mega-rifa-fusa.vercel.app/?v=CESAR |
| Gabriela Quitian | GABRIELA | https://mega-rifa-fusa.vercel.app/?v=GABRIELA |
| Juan Carlos Montaña | JUANCARLOS | https://mega-rifa-fusa.vercel.app/?v=JUANCARLOS |
| Juliana Gomez | JULIANA | https://mega-rifa-fusa.vercel.app/?v=JULIANA |
| Maria Jose Lozano | MARIAJOSE | https://mega-rifa-fusa.vercel.app/?v=MARIAJOSE |
| Paula Gomez | PAULAG | https://mega-rifa-fusa.vercel.app/?v=PAULAG |
| Paula Valencia | PAULAV | https://mega-rifa-fusa.vercel.app/?v=PAULAV |
| Sofia Montaña (NZ) | SOFIA | https://mega-rifa-fusa.vercel.app/?v=SOFIA (y `?v=N01` le sigue contando) |
| Sophia Moreno | SOPHIA | https://mega-rifa-fusa.vercel.app/?v=SOPHIA |
| Yolanda Bermudez | YOLANDA | https://mega-rifa-fusa.vercel.app/?v=YOLANDA |

Esta tabla se guarda en `06_Tablero-Web/codigos-de-vendedores.md` y sale como CSV desde el panel (`vendedores-links.csv`).

## Arquitectura

```
Panel /admin (PWA, celular y PC) ──RPC con sesión──▶ Supabase (Postgres + RLS)
Web pública / ──RPC anónima de solo lectura (cada 15 s)──▶ vistas mínimas
Mini-tarjeta /v/CODIGO ──RPC anónima──▶ solo conteos de ese código
pg_cron: vencimientos (5 min) · alertas → Edge Function → push (10 min) · respaldo diario
```

- **Sin paso de build.** Todo son archivos estáticos dentro de `06_Tablero-Web/publicar/`.
- El panel usa `supabase-js` v2 desde jsDelivr, con versión fija y SRI.
- La web pública no carga librerías: hace un `fetch` a `/rest/v1/rpc/...` con la clave publicable.
- `tablero_publico()` devuelve el mismo formato que ya entiende `cargarAPI()`: `{ok, t, v:[[n, estado, nombre]]}`. El cambio en la web es mínimo.

## Esquema de la base de datos (esquema `public`, RLS activado en todas las tablas)

**Tablas privadas.** Sin permisos para `anon` ni para `authenticated`; solo se tocan a través de las RPC.

- `usuarios_panel(user_id, rol 'admin'|'turno', nombre)`: la lista blanca. `admin` = Santiago; `turno` = Sofía.
- `vendedores(id, codigo único ^[A-Z0-9]{1,24}$, nombre_completo, nombre_norm, nombre_lista, tipo 'PERSONA'|'TIENDA'|'NZ'|'ESPECIAL', telefono, activo, creado_en)`. `SBG` y `DIR` son `ESPECIAL` y nunca salen en el selector.
- `vendedor_alias(alias_norm PK, vendedor_id)`: N01→SOFIA, MARIAJO→MARIAJOSE, TIA JULY→JULIANA, y los alias que se fusionen después.
- `compradores(id, nombre_completo, nombre_norm, telefono, sale_publico default true, quiere_tbw, pais 'CO'|'NZ')`.
- `numeros(numero char(3) PK, 1.000 filas fijas)`, con estas columnas:
  - `estado` (`LIBRE`, `APARTADO` o `PAGADO`), `comprador_id`, `vendedor_id`, `vendedor_texto` (lo que se dijo, sin tocar)
  - `apartado_en`, `vence_en` (null = no vence solo), `por_verificar` (el comprador dice que pagó y falta verlo en Nu), `pagado_en`
  - `metodo` (`NU`, `EFECTIVO`, `NZ` o null = sin dato)
- `pagos(id, numeros[], moneda, monto, monto_cop, medio, vendedor_id, tiene 'SANTIAGO'|'VENDEDOR', recibido_en, entregado_en, consignado_en, verificado_por)`.
- `referidos_pendientes(id, texto_original, texto_norm, numero, creado_en, resuelto_a, resuelto_en)`: la cola «Otra persona…».
- `auditoria(id, en, actor, accion, clave, antes jsonb, despues jsonb)`: **inmutable**. Un trigger bloquea UPDATE y DELETE. «Deshacer» escribe una entrada nueva inversa.
- `config(clave, valor)`, con valores tomados del modelo financiero:
  - precio 6.000, NZD 4, tasa 1.843, piso 3.000.000
  - premio 2.000.000, premio de vendedor 100.000, varios 50.000, tiendas 10 %, Tizumba 0/1
  - umbrales 24 h / 48 h, cierre 5 dic 18:00
  - metas de los puntos de control (120 · 230 · 320 · 420 · 500 · 600 · 690 · 750)
  - `modo` `ensayo` o `real`
- `push_suscripciones`, `alertas_enviadas` (para no repetir avisos) y `respaldos(fecha, jsonb)`.

**Funciones puras.** Las mismas reglas en SQL, JS y Apps Script; las pruebas comprueban que dan lo mismo:

- `acortar(txt)`: copia exacta de la regla actual (`Juan Perez` → `Jua*** P.`; `Reservado` se respeta; lo que ya viene con `*` no se toca).
- `normalizar(txt)`: trim, espacios simples, sin tildes (ñ→N) y MAYÚSCULAS. Ejemplo: `josé  PÉREZ` → `JOSE PEREZ`.
- `sugerir_codigo(nombre)`:
  - Toma `nombre_lista` normalizado y sin espacios.
  - Si ya existe ese nombre de pila, agrega la inicial del apellido (`PAULAV` / `PAULAG`).
  - Si aun así choca, agrega un número (`ANGELICA2`). Máximo 24 caracteres.
- `nombre_lista` por defecto (editable): con 3 o más palabras, las dos primeras (`Juan Carlos`, `Maria Jose`, `Ana Lucia`); con 2, la primera. Los nombres repetidos llevan la inicial: `Paula V.` / `Paula G.`.

**RPC públicas (`anon`, `SECURITY DEFINER`, solo lectura, devuelven lo mínimo):**

- `tablero_publico()`: número, estado efectivo y nombre acortado (`Reservado` si no quiere salir).
  - Un apartado con `vence_en` ya pasado se devuelve como LIBRE en la misma consulta, sin esperar al cron.
  - Nunca devuelve el nombre completo ni el teléfono.
- `vendedores_selector()`: código y `nombre_lista`, solo de vendedores activos que no sean `ESPECIAL`, en orden alfabético.
- `resolver_codigo(c)`: aplica los alias (N01 → SOFIA). Devuelve la etiqueta solo si el vendedor está activo.
- `mini_tarjeta(c)`: pagados, compradores distintos, apartados pendientes y cuántos le faltan para pasar de 25. Nada de dinero ni de nombres.

**RPC del panel** (revisan rol y 2FA en el servidor, validan, bloquean las filas con `FOR UPDATE` y dejan auditoría):

- Ventas: `registrar_venta`, `marcar_pagado`, `marcar_por_verificar`, `liberar`, `dar_24h`, `deshacer_ultima`.
- Plata: `entregar_efectivo`, `consignar`.
- Vendedores: `crear_vendedor`, `editar_vendedor`, `activar` / `desactivar`, `fusionar_alias`, `resolver_referido`.
- Lectura y respaldo: `estadisticas`, `stats_vendedores`, `detalle_vendedor`, `exportar`.
- Lo que valida el servidor:
  - un número tiene un solo dueño;
  - máximo 20 números por comprador;
  - el rol `turno` solo aparta, registra «Por verificar», marca pagado con método NZ y saca boletas. No ve plata ni estadísticas de Colombia, no marca pagos de Colombia y no toca vendedores.
- Las funciones aceptan `p_ahora` para probar el vencimiento con un reloj simulado.

**Cron (pg_cron):**

- `liberar_vencidos()` cada 5 min: pasa a LIBRE, guarda la auditoría «VENCIÓ» y lo lista en «Se cayeron hoy» para volver a ofrecerlo.
- Alertas cada 10 min: pg_net llama a la Edge Function `alertas` con un secreto guardado en Vault.
- Respaldo diario a las 3:00 a.m. (hora Bogotá) en `respaldos`, que guarda los últimos 30 días.

## Web pública (Fase 4, detrás de la bandera `FUENTE`)

- **Lectura**: `FUENTE = "supabase"`, con refresco cada **15 s** (hoy es cada 20) y al volver a la pestaña.
  - Si Supabase falla, sale el aviso de siempre («escríbenos por WhatsApp»). **No vuelve al Sheet viejo**: mostraría como libres números ya vendidos.
- **Selector de referido.** Sale si no hay `?v=` ni `mrf_v` guardado, al tocar el WhatsApp de la franja o «Lo quiero» (desde la ventana, la lupa o los sugeridos):
  - Hoja inferior `<dialog>` con fondo crema y bordes negros de 2 px, sin animaciones. Texto de 20 px o más.
  - Título «¿Quién te compartió la rifa?». Píldoras en 2 columnas, en orden alfabético; lo tocado se marca en amarillo y sigue directo a WhatsApp, dentro del mismo toque.
  - Debajo, en texto discreto: «Nadie, llegué solo» y «Otra persona…» (campo corto + «Seguir»).
  - Se guarda en `mrf_ref` y no se vuelve a preguntar. En la ventana del número se ve «Te compartió: Juan Carlos · cambiar».
  - Un link `?v=` siempre gana sobre lo que se eligió en el selector.
- **Mensajes:**
  - Con número: «🎉 Quiero el 607 de la Mega Rifa Fusa, me dijo Juan Carlos (JUANCARLOS)».
  - Desde la franja: «🎉 ¡Hola! Quiero más información de la Mega Rifa Fusa, me dijo Juan Carlos (JUANCARLOS)».
  - En inglés: «🎉 I want number 607 in the Mega Rifa Fusa, Juan Carlos told me (JUANCARLOS)».
  - «Nadie»: no lleva «me dijo» (el panel pone DIR).
  - «Otra persona»: «me dijo Pedro», sin código.
  - Código desconocido o viejo: solo «(V03)», así no se pierde.
- El nombre del vendedor solo aparece en el selector y en el mensaje. La cabecera sigue mostrando el código, como hoy.

## Panel `/admin` (celular primero; también funciona en PC)

Pestañas abajo:

- **Inicio**: alertas en rojo, cifras clave y el botón grande «Registrar venta».
- **Vender**.
- **Números**: ficha de cada número, con recordatorio por WhatsApp prellenado y reenvío de la boleta.
- **Vendedores**.
- **Plata**: solo admin.
- **Más**: estadísticas, auditoría con «Deshacer», exportar, ajustes y avisos.

**Registrar una venta en 4 toques o menos:**

1. «Pegar mensaje». Lee los números y el código, o el «me dijo…».
2. Nombre, con autocompletado de compradores que ya existen.
3. Un chip de estado: «Apartado» · «Pagado · Nu» · «Pagado · Efectivo» · «Efectivo con vendedor (48 h)». Para Sofía: «Apartado» · «Por verificar» · «Pagado · NZ».
4. «Guardar».

El vendedor viene prellenado: el código del mensaje, o DIR si el mensaje no trae «me dijo». Si el texto no coincide con ningún vendedor, entra a la cola «por resolver». Teléfono, «sale en el tablero» (SÍ por defecto) y «The Ber Way» son opcionales.

**Boleta.** `admin/boleta.js` es el `dibujar()` de `generador-privado.html` copiado tal cual. El generador privado no se toca: sigue funcionando solo.

- Lleva el nombre como sale en el tablero.
- Se agregan dos ajustes: no imprime `SBG`/`DIR`, y achica la letra si el código es largo.
- Botones grandes: Copiar imagen / Compartir / Guardar, en español o inglés.

**Vendedores:**

- **«+ Agregar vendedor»**: nombre completo, tipo (Persona / Tienda / Nueva Zelanda) y teléfono opcional. Muestra la etiqueta y el código sugerido, los dos editables, y avisa al instante si el código está repetido.
- **Al guardar**: link + «Copiar link» + «Compartir por WhatsApp» con el mensaje de bienvenida y el link. Desde ese momento ya sale en el selector público.
- **Tarjetas** con:
  - pagados, compradores distintos con barra hacia «más de 25» y apartados pendientes;
  - efectivo sin entregar y su antigüedad (rojo desde las 48 h);
  - ingresos.
- También: editar, desactivar (conserva el historial y el link sigue contando), fusionar alias, la cola «por resolver», el ranking, el detalle (números, comprador y fecha) y la descarga de `vendedores-links.csv`.

**Plata:**

- Total de efectivo por consignar, desglosado por vendedor y por antigüedad.
- Botones «Ya me entregó» y «Ya consigné».
- Alertas: efectivo tuyo sin consignar después de 24 h, efectivo de un vendedor después de 48 h, apartados que vencen en menos de 3 h y la lista «Por verificar».

**Estadísticas** (con las fórmulas del modelo financiero, sin inventar cifras):

- **Conteos**: pagados, apartados, libres; vendidos hoy y ayer.
- **Plata contra la meta**: ingresos brutos y neto del caso malo (`EMPIEZA!C8`), y cuántos faltan para el piso (`859 − pagados`).
- **Ritmo**: necesario contra el real de 7 días, y «mañana hay que vender X».
- **Proyección** al 5 dic con los tres casos de REGLA-PREMIO (vendido, consolación y esperado), y el punto de control actual contra el 90 %.
- **Desgloses**: por vendedor, método y país; efectivo contra transferencia; premio de vendedor; números por centena.

**PWA:** manifest y service worker solo para push, con instrucciones «Agregar a pantalla de inicio». En iPhone las notificaciones exigen instalar el panel (iOS 16.4 o más reciente).

**Seguridad:**

- Supabase Auth con correo y contraseña, más **2FA con app autenticadora (TOTP)** obligatorio para el admin. El servidor exige `aal2`.
- Encabezados en `/admin`: `noindex`, CSP estricta (sin scripts en línea), `frame-ancestors 'none'` y `no-store`.
- Sin enlaces desde la web pública. Tras varios intentos fallidos, el panel hace esperar y se suma el límite de intentos de Supabase.
- Ningún nombre ni teléfono va a los logs.
- Para ser honesto: la API REST de Supabase no permite restringir CORS por dominio. La protección real está en RLS y en que `anon` no tiene permiso de escritura. La Edge Function sí queda restringida al dominio.

## Fases

| Fase | Qué se hace | Se acepta cuando | Cómo se deshace |
|---|---|---|---|
| **1 · Base y copia** | Migraciones SQL (guardadas en `06_Tablero-Web/supabase/`), RLS, funciones, carga de los 14 vendedores + SBG/DIR + los códigos viejos (V01–T03 y N02 sin asignar, inactivos) + alias. **⏸ PARADA**: me pasas `COMPRADORES`, `PAGOS` y `VENDEDORES` descargadas como CSV; las guardo en `06_Tablero-Web/_privado/` (en `.gitignore`). `migracion/importar.py` es repetible: lee el CSV público + esos 3 y carga la copia | Hay 1.000 números. Estado y nombre visible **idénticos número por número** a lo que muestra hoy la web. Los conteos y la suma de PAGOS coinciden. Mariajo/Tia July quedan atribuidos. Las pruebas de RLS y de paridad pasan | Borrar el esquema: nada público depende de él |
| **2 · Panel** | `/admin` con login + 2FA, roles, Vender + boleta, Números y Vendedores. **⏸ PARADA**: tú creas tu usuario y el de Sofía en el panel de Supabase (Authentication → Add user) y apagas «Allow new users to sign up»; yo los agrego a la lista blanca. Franja visible «MODO ENSAYO: lo real sigue en el Sheet» | Venta en 4 toques o menos a 390 px. La boleta se genera. Alta de vendedor → link → aparece en el selector. Sofía no ve Plata | Quitar `/admin` del despliegue |
| **3 · Plata, estadísticas y alertas** | Efectivo y consignación, estadísticas, auditoría + deshacer, exportar CSV, respaldo diario, Edge Function de push + VAPID (llave privada en los secretos de Supabase) | El total por consignar coincide con la suma a mano en un caso de prueba. La alerta llega al pasar el umbral (con reloj simulado). El push llega a un celular de prueba | Apagar los cron y la función |
| **4 · Cambio del tablero** **⏸ requiere tu aprobación** | Ventana nocturna de unos 15 min: dejas de editar el Sheet → última exportación → importar → verificar 1:1 → `modo='real'` → desplegar la web nueva (lectura de Supabase, selector y mensajes). El Sheet queda protegido de solo lectura y **dejas de publicar el CSV**, que hoy expone 35 nombres completos | La verificación 1:1 da cero diferencias **antes** de desplegar (si hay alguna, se cancela). La web en vivo refleja una venta del panel en 15 s o menos (medido). Ningún nombre completo ni teléfono en el HTML ni en las respuestas | **Un paso**: promover el despliegue anterior en Vercel. Además, el panel trae «Exportar para el Sheet» para volver a cargar lo vendido después del cambio |
| **5 · Mini-tarjetas y retiro del Excel** | `/v/CODIGO` (`v.html` + rewrite en `vercel.json`, `noindex`). Se actualizan la guía de vendedores, la rutina diaria, `LEEME-como-publicar.md` y el esquema. El Sheet queda como archivo congelado | `/v/ANGELICA` muestra solo sus conteos y su link con botón de copiar. Un código inexistente dice «no encontramos ese código» | Quitar `v.html` |

**Mientras duran las fases 1 a 3 sigues vendiendo con el Sheet.** La base es una copia que se vuelve a cargar con `importar.py` cada vez que hace falta: no hay sincronización viva que pueda descuadrarse. La fuente cambia una sola vez, en la Fase 4. **A ningún comprador le llega nada automático. Las boletas ya enviadas siguen valiendo**: el serial es el mismo y el nombre acortado es el mismo.

## Decisiones que anoto en el registro (desde la 45) y después en el plan maestro

- **45** Base Supabase (proyecto existente) + panel `/admin` estático, instalable como PWA. Una sola fuente de verdad desde el cambio. ⚑
- **46** Roles: Santiago `admin` con 2FA obligatorio ⚑; Sofía `turno` con permisos limitados (respuesta tuya).
- **47** Vendedores en la base:
  - el código es el nombre (regla del 10 oct) y los alias mantienen vivos los links viejos;
  - desactivar no borra;
  - los códigos viejos sin asignar se conservan inactivos;
  - Mariajo→MARIAJOSE y Tia July→JULIANA.
- **48** Sofía Montaña = Sofía de NZ: código `SOFIA` tipo NZ, con `N01` como alias (respuesta tuya).
- **49** Selector de referido y formato del mensaje:
  - «Nadie» = DIR;
  - «Otra persona» viaja en el mensaje y se resuelve en el panel (la web pública nunca escribe en la base);
  - el link `?v=` gana sobre el selector;
  - en la lista se ve el nombre de pila, escrito tal como me lo diste (sin tildes; se puede editar).
- **50** Efectivo:
  - efectivo con vendedor = apartado de 48 h hasta que lo entrega (decisión 28);
  - tú consignas, con alerta a las 24 h;
  - «Por verificar» = pago reportado que todavía no se ve en Nu.
- **51** Los 6 apartados migrados sin fecha válida **no vencen solos**: quedan arriba en el panel con «Pagado / Darle 24 h / Liberar» hasta que los revises. ⚑
- **52** El tablero público se refresca cada 15 s. Después del cambio no vuelve a leer el Sheet, y el rollback es el despliegue anterior. ⚑
- **53** Alertas: aviso dentro del panel + notificaciones push de la PWA (respuesta tuya).
- **54** Mini-tarjeta `/v/CODIGO` con solo conteos (incluida por defecto).
- **55** Respaldos: CSV con un botón + copia diaria dentro de la base (30 días). Ningún dato de compradores entra al repositorio.

**⚑ Lo que requiere tu aprobación:**

1. Usar el proyecto de Supabase que ya existe (gratis, Canadá).
2. Los 6 apartados sin fecha no vencen solos.
3. Exigir 2FA en tu cuenta.
4. El cambio de la Fase 4: la fecha se aprueba ese día, la web no vuelve al Sheet y se deja de publicar el CSV.

## Riesgos y cómo se manejan

- **Divergencia Sheet ↔ base**: la copia se recarga cada vez y el cambio solo se hace si la verificación 1:1 da cero diferencias.
- **Un número vendido dos veces el día del cambio**: la ventana es corta y nocturna, y en la base el número es la llave única, con bloqueo de filas.
- **Supabase caído después del cambio**: la web muestra el aviso honesto (regla fija 3) y el rollback es de un paso. El plan gratis se pausa con 7 días sin uso, pero la web lo usa todo el tiempo.
- **Perder el 2FA**: lo reseteo por SQL desde esta conexión.
- **Push en iPhone**: solo con la PWA instalada. El aviso dentro del panel siempre está.
- **Que alguien consulte conteos de cualquier código en `/v/`**: los códigos ya son públicos y no se muestra dinero ni nombres.
- **Hoy, el CSV público expone nombres completos.** Se corrige con el cambio: dejas de publicarlo. Si lo quieres antes, son 2 minutos tuyos, y la web no lo necesita una vez instalado el servicio en vivo (`API_URL`).

## Archivos

- **Nuevos**:
  - `06_Tablero-Web/supabase/` (migraciones `00x_*.sql`, `pruebas/*.sql`, `funciones/alertas/index.ts`)
  - `06_Tablero-Web/migracion/` (`importar.py`, `verificar.py`)
  - `06_Tablero-Web/publicar/admin/` (`index.html`, `app.js`, `boleta.js`, `manifest.webmanifest`, `sw.js`, iconos)
  - `06_Tablero-Web/publicar/v.html`
  - `06_Tablero-Web/pruebas/e2e/*.mjs`
  - `06_Tablero-Web/base-de-datos.md`
  - `.gitignore` en la raíz (`06_Tablero-Web/_privado/`)
- **Cambian**:
  - `06_Tablero-Web/publicar/index.html` y su copia `06_Tablero-Web/index.html`: bandera `FUENTE`, `cargarAPI` con encabezado `apikey`, selector y mensajes. Se reutilizan `acortar()`, `abrirModal()` y `setIdioma()`.
  - `publicar/vercel.json` (encabezados de `/admin` y `/v`, rewrite `/v/:codigo`).
  - `06_Tablero-Web/script-tablero.gs` (solo si hace falta para la paridad de `acortar`).
  - En la Fase 5: `codigos-de-vendedores.md`, `07_Kit-de-Ventas/05_guia-vendedores-y-tiendas.md` y `03_Hoja-de-ruta/rutina-diaria.md`.
  - Siempre: `registro-de-decisiones.md`, `plan-maestro.md` y `00_EMPIEZA-AQUI.md` al cerrar cada sesión.
- **Copia del plan aprobado**: `02_Decisiones/plan-panel-y-vendedores.md`.

## Verificación (pasa o no pasa)

1. **Paridad**:
   - `acortar` da lo mismo en JS, SQL y Apps Script con «Juan Perez», «María de los Ángeles Ruiz», «Catalina», «Reservado» y uno ya acortado.
   - `normalizar` da lo mismo en JS y SQL («josé  PÉREZ» → «JOSE PEREZ», «Muñoz» → «MUNOZ»).
   - `sugerir_codigo` reproduce los 14 códigos de la tabla y da `ANGELICA2` al repetir.
2. **RLS** (pruebas SQL con `set role`):
   - `anon` no lee ninguna tabla privada, no escribe y no llama RPC del panel;
   - un usuario autenticado que no está en la lista blanca recibe «sin permiso»;
   - `turno` no lee Plata ni marca pagos de Colombia.
3. **Migración**: comparación de los 1.000 números (estado + nombre visible) entre el CSV del Sheet pasado por `acortar()` y `tablero_publico()`, con cero diferencias. También se comparan conteos por estado, compradores distintos (15 hoy) y sumas de PAGOS.
4. **Vencimiento**: con `p_ahora + 25 h`, un apartado normal se libera y un apartado migrado sin fecha no.
5. **Plata**: un caso con 3 ventas en efectivo da el total esperado. La alerta de 48 h aparece al cruzar el umbral.
6. **Playwright a 390 px y 1280 px** (Chromium de `/opt/pw-browsers`):
   - sin `?v=` la pregunta sale una sola vez y el `wa.me` lleva el mensaje exacto;
   - con `?v=JUANCARLOS` no pregunta y dice «me dijo Juan Carlos (JUANCARLOS)»;
   - con `?v=N01` dice «Sofia (SOFIA)»;
   - el HTML y las respuestas públicas no tienen ningún nombre completo de comprador ni teléfono;
   - una venta en el panel en 4 toques o menos aparece en la web en 15 s o menos (medido).
   - Para las pruebas de UI del panel uso un usuario de prueba temporal, que se borra antes del cambio. Una prueba comprueba que la lista blanca quede solo con Santiago y Sofía.
7. Después de cada despliegue: revisión en vivo de https://mega-rifa-fusa.vercel.app y del aviso de seguridad de Supabase (`get_advisors`) sin hallazgos.
