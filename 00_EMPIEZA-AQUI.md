# EMPIEZA AQUÍ — Mega Rifa Fusa

> Si eres una sesión nueva: lee este archivo, después `02_Decisiones/plan-maestro.md` completo y la memoria del proyecto (`MEMORY.md`, sobre todo `rifa-fusa-estado-2026-10-09` y `rifa-fusa-herramientas-y-despliegue`). Con eso tienes todo el contexto. **Estado al 2026-10-09: todo construido; falta que Santiago ejecute lo de "Siguiente paso" antes del sáb 10 oct.**

## 13 oct — Fase 3A: panel para vender + boleta en 4 toques

En la rama `claude/sweet-maxwell-bvoqti`. El panel `/admin` ahora tiene **Inicio · Vender · Números**: **Vender** registra una venta en 4 toques (pegar el mensaje de WhatsApp → nombre → chip de estado → Guardar) y emite la boleta reutilizando el generador privado. Estados: `APARTADO`, `PAGADO · Nu`, `PAGADO · Efectivo`, `Efectivo con vendedor (48 h)`, `Por verificar` y `PAGADO · NZ`; Sofía solo puede apartar, por verificar y PAGADO NZ (decisión 46). Botón **Deshacer la última** en Inicio.

Lo que todavía **no** entrega 3A (va en 3B/3C):
- Pestaña **Plata** (consignación, efectivo por vendedor), **estadísticas** con las fórmulas de `04_Finanzas/modelo-financiero.xlsx`, **auditoría** con lotes arbitrarios, **exportar CSV** y **respaldo diario**.
- **Push de la PWA** (decisión 57): se difiere hasta que Santiago genere la llave VAPID en Supabase e instale el panel como PWA en el iPhone. Las alertas de 24 h, 48 h y 3 h sí llegan al panel por dentro.
- Las **31 ventas viejas** del Sheet siguen sin vendedor ni método (decisión 56): se arreglan cuando lleguen los CSV privados.

La web pública **no se tocó**: `publicar/index.html` sigue byte-a-byte igual que la rama, con `SHEET_CSV` presente y cero menciones de `supabase`. Nadie que ya compró se vio afectado.

## 13 oct — Fase 2: panel admin con login + 2FA y gestión de vendedores
- **`/admin` en vivo**: https://mega-rifa-fusa.vercel.app/admin (`noindex`, `X-Frame-Options: DENY`, `no-store`, CSP estricta). Login con Supabase Auth + 2FA TOTP obligatorio para `admin`. Usuarios en la lista blanca: Santiago (`admin`, `f987cff5-…`) y Sofía (`turno`, `62b89bb4-…`).
- **Sección Vendedores**: lista con filtro (todos / activos / inactivos, por tipo), tarjetas con conteos (pagados, compradores distintos, apartados, cuánto le falta para el premio), botones «Copiar link» y «Compartir por WhatsApp», y para admin: Editar, Activar/Desactivar, + Alias y Detalle. Botón **«+ Agregar vendedor»** sugiere el código al escribir el nombre (mismas reglas del 10 oct) y da el link listo. **Descargar links (CSV)** en un botón.
- **Sección Pendientes**: cola «Otra persona…» para asignar un texto suelto a un vendedor (con un toque, con o sin crear alias). Si el panel aún no tiene pendientes, dice «Nada pendiente».
- **Mini-tarjeta `/v/CODIGO`** en vivo. Probado: `/v/JUANCARLOS` carga; códigos que no existen muestran el aviso dentro.
- **RPCs del panel**: `mi_perfil`, `listar_vendedores`, `crear_vendedor`, `editar_vendedor`, `cambiar_estado_vendedor`, `fusionar_alias`, `referidos_pendientes`, `resolver_referido`, `detalle_vendedor`, `sugerir_codigo` (puente). Todas revisan rol y 2FA en el servidor (`rifa.rol_actor()`). `turno` solo puede listar y pedir detalle; `admin` hace todo.
- **La web pública NO cambió**: sigue leyendo el Google Sheet. Fase 4 (cutover) la aprueba Santiago.

**Siguiente paso para ti:**
1. Entra a https://mega-rifa-fusa.vercel.app/admin con el correo y contraseña que creaste en Supabase.
2. La primera vez que entres el panel te muestra un QR para activar 2FA — escanéalo con Google Authenticator (o la app que uses), escribe los 6 dígitos y listo.
3. Ya adentro, verifica que la lista de vendedores sale completa (14 personas + 16 inactivos entre V01–T03/N02). Si quieres, agrega uno nuevo y mándale el link por WhatsApp desde el mismo panel.
4. Dile a Sofía su correo y contraseña (ella no necesita 2FA; entra directo).

**Lo que queda (Fase 3 en adelante):** panel de ventas (registrar venta en 4 toques + boleta), plata/consignación, estadísticas, auditoría con deshacer, respaldo diario, Edge Function de push + VAPID, y el cutover del tablero público (Fase 4). Detalle en `02_Decisiones/plan-panel-y-vendedores.md`.

## 12–13 oct — Fase 1 de la base de datos y vendedores lista
Santiago aprobó el plan `02_Decisiones/plan-panel-y-vendedores.md` (decisiones 45–55). Lo que quedó en pie:
- **Supabase conectado y poblado** (proyecto `oyvrdwkoorkidoadnzmc`): 1.000 números, 32 vendedores (14 cargados + SBG/DIR + los V01–T03 inactivos), 3 alias (N01→SOFIA, MARIAJO→MARIAJOSE, TIAJULY→JULIANA), cron de vencimientos cada 5 min.
- **Copia del tablero cargada** (31 pagados, 6 apartados, 963 libres, 15 compradores): la verificación 1:1 contra el CSV del Sheet pasa con cero diferencias. `cargar_copia` solo funciona en `modo='ensayo'`.
- **4 RPC públicas** (`tablero_publico`, `vendedores_selector`, `resolver_codigo`, `mini_tarjeta`) probadas con la llave publicable. Las tablas privadas (`rifa.*`) no se ven desde la API: 404.
- **Links listos** en `06_Tablero-Web/codigos-de-vendedores.md`. Los links viejos con `?v=N01` siguen contando (alias). Detalle completo en `06_Tablero-Web/base-de-datos.md`.
- **Mini-tarjeta `/v/CODIGO`** construida (`publicar/v.html` + rewrite en `vercel.json`). Pendiente de desplegar junto con el resto del cambio.
- **La web pública NO se tocó todavía**: sigue leyendo el Google Sheet. La Fase 4 (cambio) la aprueba Santiago.

**Siguiente paso (Fase 2 — panel admin con login y 2FA):**
1. En Supabase (Authentication → Users), crear tu usuario y el de Sofía con 2FA. Apagar «Allow new users to sign up».
2. Pasarme sus `user_id` (los copias del listado) para agregarlos a `rifa.usuarios_panel` (admin + turno).
3. En la próxima sesión se construyen las RPC del panel (`registrar_venta`, `marcar_pagado`, `liberar`, `dar_24h`, `crear_vendedor`, etc.), el panel `/admin` y la boleta.

## 11 oct — `SHEET_CSV` actualizado y web redesplegada
`index.html` y `publicar/index.html` ahora apuntan al Sheet `2PACX-1vSDP5V6…` (gid 540644959). Desplegado en producción (proyecto `mega-rifa-fusa`, dpl_2fr3fdETS3b9sqxVjiJemECjjd71) y verificado en vivo: la web muestra 998 libres, igual que el CSV (998 libres, 1 apartado, 1 pagado de prueba), sin errores. **Ojo:** el Sheet trae datos de prueba (002 apartado, 006 pagado); limpiarlos antes de vender.

## 12 oct — nombres automáticos, «Ocupado», lupa y WhatsApp con mensaje
- **Nombres**: en `NUMEROS!E` se puede escribir el nombre completo; la web lo acorta sola (`Juan Perez` → `Jua*** P.`, `Reservado` se respeta). Mismo criterio en `doGet` del script. **Ojo:** el CSV publicado sigue mostrando lo que se escriba en E a quien abra ese link; la web ya no, pero para que el CSV tampoco, hay que activar el servicio en vivo (`API_URL`).
- La web dice **«Ocupado»** (antes «Pagado») en leyenda, ventana del número y textos; en el Sheet el estado interno sigue siendo PAGADO.
- **Lupa «¡Busca si tu número está libre!»** entre el premio y «Así de fácil se paga»: libre → botón «¡Lo quiero!»; apartado u ocupado → 4 libres cercanos.
- **WhatsApp de la franja** abre con el mensaje «¡Hola! Quiero más información de la Mega Rifa Fusa 🎟️» (ES/EN).

## 11 oct (noche 5) — redes y contacto arriba en la web
Franja de 3 botones justo bajo el encabezado de la web: **Instagram @megarifafusa**, **WhatsApp 333 401 8903** (`wa.me/573334018903`) y **Canal de WhatsApp** (`whatsapp.com/channel/0029VbEFFEuHbFV0qQVLE00y`). ES/EN. Desplegado.

## 11 oct (noche 4) — generador privado: copiar / compartir la boleta
`06_Tablero-Web/generador-privado.html` ahora tiene tres botones bajo la boleta: **Copiar imagen** (portapapeles, para pegar en el chat), **Compartir** (menú del celular → WhatsApp; solo aparece donde el navegador lo permite) y **Guardar**. Además se arregló un fallo de fondo: Sutá se cargaba desde `suta-boleta.jpg` y el navegador marcaba el lienzo como «contaminado», así que no dejaba exportar la imagen; ahora Sutá va **incrustada** y el archivo funciona solo (se puede pasar al celular sin la imagen). Probado: copia un PNG de 880×520, comparte el archivo `boleta-NNN.png` y avisa si el navegador no soporta copiar.

## 11 oct (noche 3) — velocidad del tablero + ALERTA de nombres completos
- La web ahora relee cada **20 s** (antes 60) y al volver a la pestaña. El retraso grande es de Google ("Publicar en la web" tarda hasta ~5 min). **Solución lista, falta que Santiago la active:** `doGet` al final de `06_Tablero-Web/script-tablero.gs` (servicio en vivo, solo datos ya públicos) → publicarlo como aplicación web, pasar la URL `/exec` y ponerla en `API_URL` de `publicar/index.html`. Si falla, la web cae sola al CSV.
- **ALERTA (privacidad, decisión 35):** en `NUMEROS!E` (NOMBRE_PUBLICO) los números **575 y 718 tienen el nombre completo** escrito a mano y salen así en la web. Hay que restaurar la fórmula de E (ejecutar `repararTodo` en Apps Script, o copiar la fórmula de una fila vecina) y poner los nombres solo en `COMPRADORES`.

## 11 oct (noche 2) — historia «Premio 2M» y reorden de la web
- **Historia de Instagram/WhatsApp** (1080×1920, estilo de la web, zona segura respetada): `08_Contenido/historia-premio/` (`historia-premio.html` + `historia-premio.png`). Premio $2.000.000, boleta a $6.000, sorteo 5 dic, Sutá señalando, link. Sin whisky ni causa.
- **Web**: el bloque «Así de fácil se paga» ahora va **justo debajo del premio**, y entre él y el contador hay un botón amarillo con flechas **«¡ESCOGE TU NÚMERO AQUÍ ABAJO!»** que baja directo a la cuadrícula. Desplegado y probado en vivo.

## 11 oct (noche) — web: premio arriba + bloque de pago con botón de copiar
`06_Tablero-Web/publicar/index.html` (y copia en `06_Tablero-Web/index.html`): bloque **¡¡PREMIO DE $2.000.000!!** + «Boleta a $6.000» + «Se juega el 5 de diciembre» como **lo primero que se ve**, y debajo de la cuadrícula el bloque **«Así de fácil se paga»** (3 pasos, botón grande **COPIAR LLAVE @sbg884** con aviso «¡LLAVE COPIADA!», y Sutá señalando el botón; imagen `suta-senalando.webp`). ES y EN. Se arregló además un error de ortografía que estaba en vivo: **«Boyaquí» → «Boyacá»** (2 veces en la web). Desplegado y probado en vivo (copia la llave al portapapeles).

## Novedades del 11 oct — portada de Facebook y QR de la web
- **Portada de Facebook** (estilo de marca, 1640×624): `08_Contenido/banner-facebook/` (HTML + PNG). Reemplaza al `banner-facebook.html` viejo (negro, Arial Black), que sigue ahí sin usarse.
- **QR de la web** (**decisión 44**): `08_Contenido/qr/` (empezar por `00_LEEME.md`). Digital 1080×1080, cartel carta, **hoja de 6 stickers × 5 = 30** y SVG vectorial. Verificado: los 4 formatos leen `https://mega-rifa-fusa.vercel.app`. Imprimir en papel blanco, escala 100 %, adhesivo mate; **probar una hoja con dos celulares antes de pegar los 30**. **No cambiar el dominio después de imprimir.**
- La web ya lee el Sheet nuevo (`2PACX-1vSDP5V6…`, desplegada el 11 oct). **El Sheet trae datos de prueba (002 apartado, 006 pagado): limpiarlos antes de vender.**

## Novedades del 10 oct — campaña de redes (IG · FB · TikTok) LISTA

Todo en `08_Contenido/campana-rrss/` (empezar por `00_LEEME.md` y `calendario-publicacion.md`). Nada publicado: Santiago publica.
- **10 al 23 oct** (el 9 ya había pasado): 9 feeds y 10 historias listos en PNG (1080×1080 y 1080×1920), 1 carrusel de 4 láminas (11 oct), piezas de **NZ en inglés** (14 oct), `copy.md` por día (cuenta @megarifafusa, cuenta personal y TikTok, con hashtags) y **6 reels** con storyboard, voz en off y rótulos (11, 13, 14-NZ, 15, 20 y 22 oct; los graba Santiago, voz y manos).
- **Generador de contador** (`generador-contador.html`): las piezas con cifras (12, 16, 18 y 21 oct, y "Quedan X" cualquier día) salen de ahí con el dato real; no deja descargar si falta un dato o no cuadra. Probado con 3 casos buenos y 3 de error.
- **Decisión 43**: cuentas (@megarifafusa + personal) y **el whisky no va en las piezas ni en los captions**.
- Poses 2, 3 y 4 de Sutá **escaladas** a 1024 px (sin IA; banana no funciona aquí): sirven en redes, no para impresión grande.
- El calendario de contenido tiene los días de la semana 2 corridos (dice "lun 20", el 20 es martes). `calendario-publicacion.md` usa el día real; el 23 oct es **viernes**.

**Siguiente paso de contenido:** Santiago publica según `calendario-publicacion.md` y graba los reels. La próxima tanda (24 oct en adelante) se puede producir con el mismo sistema (`_fuentes/construir.py`) cuando haya datos del PC2 (dom 25).

## Novedades de la sesión del 9 oct (tarde)

Claude cerró los pedidos de Santiago. Lo construido/cambiado:
- **Decisiones 40, 41, 42** registradas (A y B firmes; whisky se compra al final; **se quitó el generador de tarjetas de la web**, lo genera Santiago con su generador privado).
- **Foto de perfil de WA**: 6 variantes en `05_Marca/WA-perfil/` + hoja de comparación a 48 px. **Descripción de WA**: 3 versiones de 139 caracteres o menos con emojis, y emojis en la bienvenida y `/pagado` (`07_Kit-de-Ventas/03_whatsapp-business-y-plantillas.md`).
- **Excel del tablero** regenerado y **simplificado**: hoja **HOY** (primera, una pantalla), hoja **LEEME**, orden nuevo, pestañas verde/gris, columnas de fórmula en gris, **columna QUIERE_TBW**, **link real de vendedores**, y el **bug del contador arreglado (21 nov -> 5 dic)**. 17 pruebas recalculadas, **todas pasan**.
- **Modelo financiero** simplificado: hoja **EMPIEZA**, ESCENARIOS agrupada, nota del whisky; **CASOS-PRUEBA = TODOS PASAN**.
- **Web**: quitado el generador y el **voseo -> español colombiano** (en `index.html`, `publicar/`, `artifact.html`). **Falta desplegar** (comando abajo); se junta con el `SHEET_CSV` nuevo.
- **Generador privado** de tarjetas: `06_Tablero-Web/generador-privado.html` (local, no se despliega).
- **Guías nuevas**: `06_Tablero-Web/PROMPT-claude-en-chrome.md` (para montar el Sheet), `07_Kit-de-Ventas/09_guia-de-arranque.html` (montaje + una venta de punta a punta), `07_Kit-de-Ventas/10_banco-nz-sofia.html` (banco NZ + giros + Binance).
- **S5 Contenido**: `08_Contenido/calendario-de-contenido.md`, `guion-de-lanzamiento.md`, y el **lienzo privado del celular**: https://claude.ai/artifact/1MYkZZYYzArwNFCvD3aUNU
- `01_Investigacion/guia-aplicada.html` marcado **histórico**.

**✅ Sheet nuevo conectado y web desplegada (10 oct):** **Cambio de la web (10 oct, tarde 2):** el tablero ahora muestra **solo QUEDAN LIBRES en grande** (se quitaron apartados y pagados) + un **banco de 50 frases rotatorias** (cada 20 min y al refrescar; las que llevan número muestran uno realmente libre del Sheet) + cuenta regresiva pequeña. **Favicon de Sutá** (variante roja). Desplegado y verificado en vivo. Se arregló además un voseo que quedaba en el modal ("Escogé"→"Escoge"). Santiago montó el Sheet con el prompt de Chrome; `SHEET_CSV` apunta al nuevo (gid 540644959). Web en vivo probada: 1.000 libres, 0 apartados, 0 pagados, sin generador, sin voseo, sin errores. El kit de 1 página del lienzo de marca también quedó sin la causa (moto).

## En una frase
Rifa informal de **1.000 números (000–999)** a **COP 6.000** (**NZD 4** en Nueva Zelanda), premio de **COP 2.000.000 en efectivo**, sorteo el **sábado 5 de diciembre de 2026 a las 10:30 p.m.** con las **últimas 3 cifras** del premio mayor de la **Lotería de Boyacá**. La meta es que Santiago reúna **COP 3.000.000 netos** para una moto.

## Números clave
| | |
|---|---|
| Piso | **COP 3.000.000 netos** ⇒ ~860–890 números |
| Meta | **900+ números** |
| Precio | COP 6.000 (Colombia) · NZD 4 (NZ, ≈ COP 7.372) |
| Premio | COP 2.000.000 · si gana en NZ: NZD 1.000, mínimo COP 1.900.000 |
| Costos | Premio 2M + 100k al vendedor + ~50k varios + 10% a tiendas + Tizumba opcional ~100k |
| Ritmo | ~15 números/día en promedio · ~18–25/día la última semana (57 días de venta). Centro estimado realista: ~700 |
| Pagos | Llave Bre-B de Nubank **`@sbg884`** + efectivo. PAGADO solo cuando la plata está en la app |
| Número no vendido | **Decisión 37**: si el número de la Boyacá no se vendió, no hay 2M; el siguiente número vendido gana un **premio de consolación: whisky Buchanan's Master 750 ml (COP 210.000)** |
| Respaldo del sorteo | Lotería del Cauca 11:00 p.m., **solo si la Boyacá no juega** (ya no es segunda oportunidad para los 2M) |

## Estado (2026-10-09)

**S4 Kit de ventas — ✅ ESCRITO el 8 oct (borrador para que Santiago lo revise antes del sáb 10).** `07_Kit-de-Ventas/`:
- [x] `01_reglamento.md` — completo en ES + resumen en EN. **Las 3 propuestas mías (A, B, C) están ahora en `01b_reglas-internas.md`; confirmarlas antes del sáb 10 oct**: (A) si ni Boyacá ni Cauca publican, se usa la Boyacá del sáb 12 dic; (B) 30 días para reclamar el premio; (C) **los datos de compradores se conservan** (decidido el 9 oct) y se usan para The Ber Way solo con SÍ del comprador
- [x] `02_frases-tarjeta.md` — 100 ES + 40 EN, con reglas de uso
- [x] `03_whatsapp-business-y-plantillas.md` — configuración, bienvenida y ausencia, 8 respuestas rápidas, 13 plantillas ES + 5 NZ
- [x] `04_causa-y-objeciones.md` — guion de la causa (solo 1 a 1) y 16 objeciones
- [x] `05_guia-vendedores-y-tiendas.md` — las 2 rutas, 6 reglas, acuerdo con tiendas listo para firmar
- [x] `06_manual-de-sofia.md` — turno, plata de NZ, el día del sorteo en hora de NZ
- [x] `07_brief-tizumba.md` — qué pedir, qué sí y qué no puede decir
- [x] `08_vendedores-confirmados.md` — qué cuenta como vendedor **fijo** (4 condiciones), tabla V01–V12 y T01–T03, conteo de fijos y cuánto significa para la capacidad, mensaje de confirmación y capacitación del vie 9. **Se cierra la lista de fijos el vie 9 oct, 6:00 p.m.**
- [x] **Decisiones 38 y 39 (9 oct)**: datos de compradores **se conservan** y se usan para The Ber Way solo con SÍ (columna nueva `QUIERE_TBW` en `COMPRADORES`; la pregunta va en el mensaje de pago); firma pública **The Ber Way (@theberway) by Santiago (@santiagobermudezai)** en el pie de la web y de /reglamento; la web dice "organizada por Santiago". Nota de estrategia: `00_Company\Strategy\Audience-from-Mega-Rifa-Fusa.md`
- [x] **Reglamento público simplificado (8 oct)**: https://mega-rifa-fusa.vercel.app/reglamento ahora son 9 reglas cortas, ES/EN, sin nada interno ni el nombre de Santiago. Lo interno (premio del vendedor, tiendas, Sofía, 48 h, datos, causa y las propuestas A, B y C) quedó en `07_Kit-de-Ventas/01b_reglas-internas.md`
- [ ] **Falta**: Santiago llena `08_vendedores-confirmados.md`, confirma las propuestas A–C (en `01b_reglas-internas.md`) y compra o aparta el whisky

**Análisis de riesgo — regla del premio y fecha (5–6 oct) — ✅ regla y fecha decididas.**
- [x] **Decisión 15: el sorteo pasa al sáb 5 dic 2026** (decidido el 6 oct, comparando 21 nov, 5 dic y 19 dic). Web en vivo, modelo (`B28` y `PUNTOS-CONTROL`), registro, plan maestro, hoja de ruta, puntos de control (7, metas 230 → 750 → 860), plan de sesiones y rutina, todo al 5 dic. Tizumba se decide el **dom 1 nov**. Ya no hay segunda rifa programada
- [x] **Decisión 37 (reemplaza la 7)**: si el número de la Boyacá no se vendió, **no hay 2M**; el siguiente número vendido gana un **premio de consolación: whisky Buchanan's Master 750 ml (COP 210.000)**. La Cauca queda solo como respaldo si la Boyacá no juega. El premio de 2M **no baja** (Santiago lo descartó)
- [x] `02_Decisiones/analisis-premio-y-tiempo.md` — por qué, cifras, capacidad realista, confianza, comparación de fechas y texto ES/EN para el reglamento
- [x] **Lo que no se había mostrado** (5 oct): la capacidad del propio plan (600–800) no llegaba al piso (~860). Con el sorteo del 5 dic el centro realista es **~700 vendidos → caso malo COP 2,05M** (número vendido); para 3M seguros siguen haciendo falta ~860. Es estimado, no hay datos de conversión de rifas informales
- [x] Modelo financiero: hoja nueva `REGLA-PREMIO` + 4 casos de prueba; **9 de 9 PASAN** recalculando con LibreOffice
- [x] Web en vivo actualizada (fila "Si el número no se vendió" y Cauca solo como respaldo, ES y EN), verificada sin errores
- [x] Registro, plan maestro, hoja de ruta, puntos de control, índice de investigación y memoria al día
- [x] **Lienzo de marca al día (8 oct)**: Estado, tarjetas ES y EN, kit del vendedor, feed y collages 1 y 5 dicen 5 dic y la regla del whisky. Los collages 3 y 9 y el tablero no mencionan fecha
- [x] `01_Investigacion/guia-aplicada.html` (sin dueño) **marcado como DOCUMENTO HISTÓRICO** el 9 oct (aviso rojo arriba): decía 21 nov y "siempre hay ganador", las dos ya no ciertas

**S3 Tablero web + Google Sheet — ✅ CONSTRUIDA, falta conectarla.**
- [x] **Decisión 33: los apartados vencen solos a las 24 h** por fórmula, no a mano
- [x] **Decisión 34: los códigos de vendedor** ya están asignados — `V01`–`V12`, `T01`–`T03`, `N01`–`N02`, `SBG`, `DIR`. Ver `06_Tablero-Web/codigos-de-vendedores.md`
- [x] `06_Tablero-Web/esquema-google-sheet.md` — las 6 hojas con fórmulas exactas, formato condicional, validación y cómo publicar el CSV
- [x] `06_Tablero-Web/index.html` — la web completa en un archivo: cuadrícula 000–999, contadores reales, cuenta regresiva, ficha por número, botón "Lo quiero" con el código del vendedor, links `?v=CODIGO` que se recuerdan, ES/EN y generador de tarjeta-boleta
- [x] Probada en pantalla de 375 px: sin desborde horizontal, el modal centra, el link de WhatsApp sale con el código, la tarjeta se genera solo si el número está PAGADO, y si el Sheet no responde los contadores quedan en `—` con un aviso (regla fija 3)
- [x] `06_Tablero-Web/LEEME-como-publicar.md` — los 4 pasos + tabla de fallas
- [x] Lienzo para probar desde el celular, **con datos de ejemplo y franja roja que lo avisa**: https://claude.ai/artifact/2MBAL5BcNprw8a9zeUaVNy

- [x] **Número de la Business puesto**: `3334018903`
- [x] **Decisión 35: en el tablero cada número pagado sale como `Dav*** G.`**, o `Reservado` si el comprador no quiso salir. El nombre completo y el teléfono viven en la hoja nueva `COMPRADORES`, que no se publica; `NUMEROS!E` lo acorta por fórmula
- [x] **Decisión 36: la prueba es el tablero, no la tarjeta.** La tarjeta-boleta imprime el nombre del dueño según el Sheet y dónde verificarlo

- [x] **El Sheet armado y verificado**: `06_Tablero-Web/MEGA-RIFA-FUSA-tablero.xlsx` — 7 hojas, 1.000 filas, 4 fórmulas, formato condicional, listas desplegables y los 19 códigos. Los 10 casos de prueba se corrieron **recalculando el archivo** con LibreOffice, no solo escribiendo las fórmulas (tabla al final de `esquema-google-sheet.md`)
- [x] `06_Tablero-Web/construir-tablero.py` — el script que lo genera, por si hay que rehacerlo

- [x] **Sheet creado, convertido y publicado por Santiago** el 4 oct. La web ya está conectada: `SHEET_CSV` apunta a la hoja `NUMEROS` publicada como CSV. Comprobado leyendo el CSV en vivo: 1.000 filas, encabezados correctos, ceros adelante intactos, fórmulas calculando
- [x] Probado con el Sheet real: **1.000 libres, 0 apartados, 0 pagados**, sin franja de datos de ejemplo y el botón "Lo quiero" abriendo `wa.me/573334018903`

- [x] **LA WEB ESTÁ EN VIVO: https://mega-rifa-fusa.vercel.app** — desplegada el 5 oct. Probada contra el Sheet real: 1.000 libres, sin franja de ejemplo, "Lo quiero" abriendo `wa.me/573334018903`, imágenes cargando, sin errores de consola
- [x] Sheet confirmado por Santiago en **Acceso general: Restringido**
- [x] **Arreglado el texto ilegible en modo oscuro** (lo encontró Santiago): el `<dialog>` tomaba el color del sistema en vez del de la página, así que en tema oscuro el texto salía blanco sobre crema. Pasaba en el navegador, no solo en el lienzo. Verificado forzando modo oscuro
- [x] `SITIO` puesto, así que la tarjeta-boleta ya imprime "verificá este número en mega-rifa-fusa.vercel.app"
- [x] `06_Tablero-Web/publicar/` — la carpeta que se despliega (3 archivos + `vercel.json`)

- [x] **Dos bugs que encontró Santiago probando con el 006 y el 007, ya arreglados** (5 oct):
  - En un número **PAGADO** el botón de WhatsApp seguía a la vista con el enlace del número anterior. Causa: `.btn` ponía `display:block` y le ganaba al atributo `hidden`. Solo pasaba en Vercel; en el lienzo no, porque ahí el visor agrega esa regla por su cuenta. Arreglado y verificado con el 006, el 007 y el 123
  - La **hora del apartado no se ponía sola**. Se resolvió con `06_Tablero-Web/script-tablero.gs`, un script de Apps Script. Una fórmula no sirve: `NOW()` se recalcula cada minuto y la hora se movería sola, así que el apartado no vencería nunca

- [x] **Tres bugs más, encontrados el 5 oct probando contra el Sheet real:**
  - **Cuatro nombres completos quedaron publicados** (`Jorge Perez` y otros tres) porque se escribieron encima de la fórmula de `NOMBRE_PUBLICO`, que es la única columna pública que parece una celda normal. Los nombres van en `COMPRADORES`
  - **Los apartados nacían vencidos**: una hora escrita como `11:20`, sin fecha, para Sheets es el 30/12/1899, así que la cuenta de 24 h daba 46.000 días. La fórmula lo dejaba pasar en silencio; ahora el número queda apartado y `VENCE_A` dice `FALTA LA FECHA`
  - `VENCE_A` mostraba `31/12 00:00` cuando no había hora; ahora dice `FALTA LA HORA`
- [x] Las 4 fórmulas corregidas y reprobadas con 8 casos recalculando el archivo. El `.xlsx` y `script-tablero.gs` quedaron con **las mismas fórmulas, verificado por comparación**

**Lo que falta de S3** (todo en el Sheet):
1. **Instalar y correr `06_Tablero-Web/script-tablero.gs`**: Extensiones → Apps Script, pegar, guardar, ejecutar `repararTodo`. Eso repone las fórmulas pisadas y deja la hora automática andando.
2. Rehacer los apartados con hora mala: poner `LIBRE` y después `APARTADO` otra vez.
3. Pasar los nombres completos a la hoja `COMPRADORES`.
4. Poner esta fórmula en `VENDEDORES!E2` y arrastrarla hasta la fila 20:

```
="https://mega-rifa-fusa.vercel.app/?v=" & $A2
```

**S2 Marca + kit para vendedores — ✅ TERMINADA.**
- [x] **Decisión 27 cerrada: estilo A · Rótulo + boleta**, escogido con los 9 bocetos a la vista (3 estilos × tarjeta-boleta, Estado y collage) → lienzo de bocetos: https://claude.ai/artifact/GPNxJxi4CbZ9b7JuAn1KuH
- [x] **Decisión 32 nueva: la mascota se llama Sutá** (del gentilicio *sutagao*, "hijos del sol")
- [x] **Sutá es una versión ilustrada del monumento al Indio Sutagao** de Fusa (L. H. Suárez, 1994): figura dorada con lanza. Seis poses, todas del mismo personaje. Archivos en `05_Marca/Suta-final/`
- [x] `05_Marca/sistema-de-marca.md` — colores con contraste medido, 3 tipografías, reglas del logo, origen y reglas de Sutá, inventario de piezas y qué falta
- [x] Lienzo con todo construido en estilo A: https://claude.ai/artifact/TF58pBayPvzBhPeqTJHmTq — logotipo (3 versiones), paleta, tipografías, **Sutá con 6 poses**, tarjeta-boleta ES, tarjeta-boleta NZ (EN, encabeza con NZD 1.000), **kit del vendedor de 1 página (carta, imprimible)**, Estado de lanzamiento, plantilla de feed, collages de 1/3/5/9 fotos y plantilla del tablero (10 × 100)
- [x] Registro de decisiones y plan maestro actualizados (32 decisiones, ninguna abierta)

**Lo que queda suelto de S2** (nada bloquea el domingo 4):
1. La **variante de paleta**, si Santiago quiere mover algún color.
2. Las **poses 2 a 6 de Sutá están a 200 px**. La 1 está buena. Hay que reemplazarlas por originales de alta antes de imprimir.
3. Los lienzos son **privados**: para mandarle el kit a un vendedor hay que compartirlo desde el menú Share. Mostrarlo desde el celular de Santiago funciona sin hacer nada.
4. `01_Investigacion/guia-aplicada.html` sigue sin dueño: apareció con fecha del 3 oct, no lo creó ninguna sesión y Santiago no confirmó si es suyo. No está en el índice de investigación.

**S1 Cimientos — ✅ TERMINADA.**
- [x] Carpetas creadas (9 carpetas numeradas)
- [x] Plan maestro en `02_Decisiones/plan-maestro.md`
- [x] 4 informes de investigación en `01_Investigacion/` (en inglés, tal cual)
- [x] `01_Investigacion/00_LEEME-indice-y-resumenes.md` — índice + resumen en español de cada informe + tabla de "qué dijo la investigación que el plan NO siguió"
- [x] `02_Decisiones/registro-de-decisiones.md` — las 31 decisiones con estado, fecha y qué pasa si se cambian
- [x] `03_Hoja-de-ruta/`: `hoja-de-ruta.md`, `rutina-diaria.md`, `plan-de-sesiones.md`, `puntos-de-control.md`
- [x] `04_Finanzas/modelo-financiero.xlsx` — **los 5 casos de prueba pasan** (verificado recalculando el archivo)
- [x] Memoria del proyecto (5 memorias) + `MEMORY.md`
- [x] Verificación de S1 (abajo)

**Siguiente: S2 Marca + kit para vendedores (sáb 3 oct).**

## Siguiente paso (al 2026-10-09)

Santiago ejecuta estos 9 puntos para dejar todo listo (las reglas se congelan el sáb 10 oct con la primera venta). Marca el estado real al leer su respuesta:

| # | Qué | Para cuándo | Estado |
|---|---|---|---|
| 1 | **✅ HECHO (9 oct)**: A y B aprobadas (decisión 40), ya son reglas firmes en `01b_reglas-internas.md`. La C ya estaba resuelta | vie 9 oct | ✅ |
| 2 | **✅ RESUELTO (9 oct, decisión 41)**: el whisky se compra **después del sorteo**, solo si se activa la consolación. No se aparta plata (la reserva de 2M lo cubre). La captura del 8 oct queda de referencia | después del 5 dic | ✅ |
| 3 | Cerrar la lista de **vendedores fijos** en `07_Kit-de-Ventas/08_vendedores-confirmados.md` y capacitarlos (15–20 min cada uno). Pasar cuántos son fijos para recalcular capacidad | vie 9 oct, 6:00 p.m. | ⬜ |
| 4 | **Foto de perfil (6 variantes en `05_Marca/WA-perfil/`) y descripción (3 opciones) LISTAS (9 oct)**. Falta que Santiago escoja y configure WhatsApp Business según `03_whatsapp-business-y-plantillas.md` | antes del sáb 10 oct | 🟡 |
| 5 | Avisarles a los vendedores la **fecha nueva (5 dic)** y la **regla del whisky** (el kit que vieron decía 21 nov) | antes del sáb 10 oct | ⬜ |
| 6 | **Guía del banco NZ + giros LISTA (9 oct)**: `07_Kit-de-Ventas/10_banco-nz-sofia.html` (qué cuenta abrir, Remitly/OrbitRemit/Wise, Binance no vale la pena). Falta que Sofía revise reglas/visa y confirme cuenta | antes de vender en NZ | 🟡 |
| 7 | **✅ Santiago ya tiene Nequi**. Queda solo cotizar giros en vivo (ver guía NZ) | antes del mar 13 oct | ✅ |
| 8 | **Primera venta** (preventa a familia y amigos, meta 120 al lun 12). Reglas congeladas | sáb 10 oct | ⬜ |
| 9 | **Lanzamiento público** | mar 13 oct | ⬜ |

**Además, en el Sheet (solo lo puede hacer Santiago):** instalar y correr `06_Tablero-Web/script-tablero.gs` (sin él los apartados no vencen solos); agregar la columna `QUIERE_TBW` en `COMPRADORES`; pasar los nombres completos a `COMPRADORES`; poner la fórmula `="https://mega-rifa-fusa.vercel.app/?v=" & $A2` en `VENDEDORES!E2` hasta la fila 20; llenar los nombres junto a `V01`–`V12` y `T01`–`T03`.

**Lo que puede hacer Claude cuando Santiago lo pida:**
- **S5**: calendario de contenido del 9 oct al 6 dic y guion del lanzamiento (Santiago graba voz y manos).
- **Campaña de redes**: ✅ 10–23 oct hecha (ver arriba). Siguiente tanda: 24 oct en adelante, con el mismo sistema.
- **Ensayo de punta a punta**: venta falsa → pago → Sheet → web → tarjeta → Canal, antes de vender de verdad.
- Recalcular la capacidad con el número real de vendedores fijos.
- Cambiar cualquier regla pública antes del congelamiento: se edita `06_Tablero-Web/publicar/reglamento.html` (y `index.html`) y se despliega (ver `rifa-fusa-herramientas-y-despliegue`).

Los lienzos de marca son privados: Santiago los muestra desde el celular o los comparte desde Share.

## Dónde está todo

| Carpeta | Qué hay | Cuándo se llena |
|---|---|---|
| `01_Investigacion/` | Los 4 informes + el índice con resúmenes en español | ✅ S1 |
| `02_Decisiones/` | `plan-maestro.md` (fuente de verdad) + `registro-de-decisiones.md` | ✅ S1 |
| `03_Hoja-de-ruta/` | Hoja de ruta, rutina diaria, plan de sesiones, puntos de control | ✅ S1 |
| `04_Finanzas/` | `modelo-financiero.xlsx` (7 hojas, con casos de prueba) | ✅ S1 |
| `05_Marca/` | `sistema-de-marca.md` + los dos lienzos (bocetos y piezas en estilo A) | ✅ S2 |
| `06_Tablero-Web/` | La web (en vivo en Vercel), el Sheet y los códigos de vendedor | ✅ S3 |
| `07_Kit-de-Ventas/` | `01_reglamento` (público) · `01b_reglas-internas` · `02_frases` · `03_whatsapp` · `04_causa-y-objeciones` · `05_guia-vendedores-y-tiendas` · `06_manual-de-sofia` · `07_brief-tizumba` · `08_vendedores-confirmados` | ✅ S4 (borrador del 8 oct) |
| `08_Contenido/` | Calendario de contenido, guion del lanzamiento y **`campana-rrss/`** (piezas 10–23 oct, generador, copys, reels) | ✅ S5 + campaña de redes (10 oct) |
| `09_Operacion/` | Copias diarias del tablero, reportes de los puntos de control, informe final | Durante la campaña |

## Las 7 reglas fijas (toda sesión, todo entregable)

1. **Idioma**: todo en español; las piezas de NZ, bilingües ES/EN.
2. **Nada de advertencias legales en el chat** (pedido de Santiago). La investigación legal queda en `01_Investigacion/` solo como referencia.
3. **Copy honesto**: nunca decir que la rifa tiene permiso o autorización; los contadores y los "quedan X" tienen que ser reales; frases como "el 777 ya se fue" solo si es cierto.
4. **Plata**: se verifica solo dentro de la app que recibe (Nu en Colombia, el banco de Sofía en NZ); primero se guarda la reserva del premio; conciliación diaria.
5. **Privacidad y permiso**: en lo público, un número pagado sale como **`Dav*** G.`** (nunca el nombre completo ni el teléfono), y quien no quiera salir aparece como **`Reservado`**; fotos de compradores solo con manos, salvo que pidan salir; historias solo con permiso. **Datos**: se conservan y solo se usan para The Ber Way con quien respondió SÍ (decisión 38).
6. **Respeto con la mascota**: un Sutagao orgulloso y amigable, sin caricaturizar rasgos étnicos ni usar disfraces genéricos; el humor sale de las situaciones, nunca de la etnia.
7. **Las reglas se congelan** antes de la primera venta (sáb 10 oct) y no se cambian después.

## Pendientes que no dependen de Claude

Ver la tabla de "Siguiente paso" arriba: son los mismos 9 puntos más lo del Sheet. No hay otros pendientes de terceros.

## Fechas que no se mueven

| Fecha | Qué |
|---|---|
| sáb 10 oct | **Primera venta** → las reglas quedan congeladas |
| **mar 13 oct** | **Lanzamiento público** (día 1 de la Semana Universitaria) |
| dom 25 oct | Punto de control 2 → meta 320. **Primer dato real de ritmo** |
| dom 1 nov | Punto de control 3 → meta 420 · **se decide Tizumba** |
| dom 15 nov | Punto de control 5 → meta 600 |
| jue 19 nov | Último día fuerte en la UdeC (la U se vacía desde el 20) |
| dom 29 nov | Punto de control 7 → meta 750. El más importante |
| lun 30 nov | Quincena #4 · arranca la última semana |
| **sáb 5 dic** | 6:00 p.m. cierre · 7:00 p.m. lista final · 10:30 p.m. sorteo (Boyacá ordinario) |
| dom 6 dic | Premio entregado (máx. 24 h) con video y acta |

---

## Verificación de S1 (del plan maestro)

| Criterio | Estado |
|---|---|
| Existen todas las carpetas y archivos | ✅ |
| Los informes están completos y tal cual, cada uno con su resumen en español | ✅ 4 informes intactos + `00_LEEME-indice-y-resumenes.md` |
| El registro de decisiones coincide con el plan | ✅ 31 decisiones + reglas por defecto |
| Cada fecha de la hoja de ruta tiene el día de la semana correcto | ✅ verificadas las 24 fechas de 2026 |
| 859 vendidos sin ventas de tiendas → neto ≥ COP 3.000.000 | ✅ **COP 3.004.000** |
| 700 vendidos → ≈ COP 2.050.000 | ✅ **COP 2.050.000** exacto |
| Los números de NZ se convierten a la tasa escogida | ✅ 100 números de NZ = COP 737.200 (NZD 4 × 1.843) |
| La memoria y su índice `MEMORY.md` están escritos | ✅ 5 memorias + índice |
| `CLAUDE.md` apunta a EMPIEZA-AQUÍ | ✅ |

Los casos de prueba se verificaron **recalculando el archivo de Excel**, no solo escribiendo las fórmulas. La hoja `CASOS-PRUEBA` dice **TODOS PASAN**.

---

*Última actualización: 2026-10-06: decisión 37 (regla del número no vendido) y decisión 15 (sorteo el sáb 5 dic). Ver `02_Decisiones/analisis-premio-y-tiempo.md`.*
