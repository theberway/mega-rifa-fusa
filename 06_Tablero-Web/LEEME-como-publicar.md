# Cómo dejar el tablero funcionando

*Sesión 3, 2026-10-03. Son cuatro pasos. El 1 y el 2 los hacés vos; el 3 lo hago yo en cuanto me pases dos datos; el 4 es la prueba.*

## Qué hay en esta carpeta

| Archivo | Qué es |
|---|---|
| `index.html` | **La web.** Es un solo archivo: no necesita servidor, ni base de datos, ni instalar nada |
| `suta.webp`, `suta-boleta.jpg` | Sutá. Tienen que viajar junto al `index.html` |
| `demo.csv` | Tablero de mentiras para probar la web sin el Sheet. Se borra el día que entre el link real |
| `artifact.html` | La misma web, cortada para el lienzo de Claude. **No se edita a mano**: sale de `index.html` |
| **`MEGA-RIFA-FUSA-tablero.xlsx`** | **El Sheet ya armado.** 7 hojas, 1.000 filas, fórmulas, colores, listas y los 19 códigos. Solo falta subirlo |
| `esquema-google-sheet.md` | Qué hace cada hoja y cada fórmula, por si hay que tocarlas |
| `construir-tablero.py` | El script que generó el `.xlsx`. Si algo hay que rehacer, se corrige acá y se vuelve a correr |
| **`script-tablero.gs`** | El script del Sheet: pone la hora del apartado sola y, con `repararTodo()`, repone las fórmulas si alguien las pisa |
| `codigos-de-vendedores.md` | Los códigos ya asignados y para qué sirven |

**Sobre la tarjeta-boleta y quién puede generarla**: cualquiera puede escribir un número pagado y sacar su tarjeta. Se dejó así a propósito y la razón está en la decisión 36 del registro — en resumen, la tarjeta imprime el nombre del dueño que dice el Sheet, así que una tarjeta hecha por un tercero lo delata en vez de ayudarlo, y el premio es de quien diga el tablero.

Lo que ves hoy en el lienzo (https://claude.ai/artifact/2MBAL5BcNprw8a9zeUaVNy) corre con `demo.csv` y lo avisa con una franja roja arriba: **los 706 libres y los 196 pagados son inventados**. Es para que pruebes la web en el celular, no para mostrárselo a nadie.

---

## Paso 1 — Subir el Sheet (ya está armado)

No hay que construir nada: `MEGA-RIFA-FUSA-tablero.xlsx` ya tiene las 7 hojas con todo adentro, y las fórmulas se verificaron recalculando el archivo (los casos de prueba están al final de `esquema-google-sheet.md`).

1. Subí el `.xlsx` a Google Drive.
2. Abrilo y **Archivo → Guardar como Hoja de cálculo de Google**. Ahí deja de ser un Excel.
3. **Archivo → Configuración → Cálculo → Recalcular: "Al cambiar y cada minuto"**. Sin esto los apartados no se vencen nunca.
4. **Archivo → Configuración → Zona horaria: (GMT-05:00) Bogotá.**
5. Borrá el `.xlsx` de Drive si querés: ya no se usa, el que manda es el Sheet.

Yo no puedo hacer estos pasos: necesitan tu cuenta de Google y no entro a cuentas.

Cuando esté, publicá **solo la pestaña `NUMEROS`** como `.csv`:

**Archivo → Compartir → Publicar en la web → `NUMEROS` → `.csv` → Publicar**

Copiás el link que sale. Termina en `output=csv`.

> **Publicar no es compartir el archivo.** Esto expone esa pestaña sola, de solo lectura. La hoja `VENDEDORES` tiene nombres completos y teléfonos y **no se publica nunca**.

## Paso 2 — Dejar el archivo restringido

**Compartir → Acceso general → Restringido.** Hoy está en "cualquiera con el enlace" y lo comprobé: el archivo se lee desde afuera sin abrir sesión. Hoy no importa porque está vacío, pero `COMPRADORES` y `VENDEDORES` van a tener nombres completos y teléfonos.

Publicar la pestaña `NUMEROS` **no** necesita que el archivo esté compartido: son dos cosas distintas y hay que hacer las dos.

## Paso 3 — Las líneas de configuración

Me pasás esos dos datos y los pongo. Son las líneas 2 y 3 del bloque de configuración, al final de `index.html`:

```js
const SHEET_CSV = "https://docs.google.com/...output=csv";   // ✅ ya está, conectado al Sheet
const WHATSAPP  = "573334018903";                            // ✅ ya está
const SITIO     = "mega-rifa-fusa.vercel.app";               // ✅ ya está
```

`SITIO` solo se imprime en la tarjeta-boleta, en la línea "verificá este número en…". Mientras esté vacío, la tarjeta simplemente no la lleva.

Si lo querés hacer vos: abrís `index.html` con el Bloc de notas, buscás `SHEET_CSV` y reemplazás. En cuanto deje de decir `demo.csv`, la franja roja de "datos de ejemplo" desaparece sola.

## ✅ Publicado

**La web está en vivo: https://mega-rifa-fusa.vercel.app**

Se desplegó el 5 de octubre con la CLI de Vercel, desde la carpeta `06_Tablero-Web/publicar/`. Para volver a desplegar después de cambiar `index.html`:

```bash
cd "06_Tablero-Web/publicar" && npx vercel deploy --prod --yes
```

(antes hay que copiar el `index.html` de la carpeta de arriba a `publicar/`).

## Paso 4 — Publicar la web

### Opción A — Vercel (la que queda de verdad)

1. Entrás a `vercel.com` y abrís sesión con GitHub o con el correo.
2. **Add New → Project → Deploy without Git** (o arrastrás la carpeta).
3. Arrastrás **el contenido** de `06_Tablero-Web/`: `index.html`, `suta.webp` y `suta-boleta.jpg`. Sin `demo.csv`, sin los `.md`, sin `artifact.html`.
4. Deploy. Sale una dirección tipo `mega-rifa-fusa.vercel.app`.

Esa dirección es la que va en el kit de los vendedores, en el Estado de lanzamiento y en la fórmula de la columna `LINK` de la hoja `VENDEDORES`.

Cuando cambie algo de la web, se vuelve a subir la carpeta. El Sheet **no** se vuelve a subir nunca: eso se actualiza solo.

### Opción B — GitHub Pages

Repo nuevo → subís los 3 archivos → Settings → Pages → Source: `main` / raíz. Queda en `usuario.github.io/repo`. Tarda unos minutos la primera vez.

### El lienzo de Claude: solo vista previa

**El lienzo no puede leer el Sheet.** Las páginas publicadas en Claude solo pueden pedir archivos propios: cualquier pedido a `docs.google.com` lo bloquea el navegador, sin mensaje de error. Comprobado.

Por eso el lienzo se quedó a propósito con `demo.csv` y una franja que dice *"vista previa con datos de ejemplo"*. Sirve para ver cómo se ve y para mostrarle el diseño a alguien, nada más.

**El tablero real tiene que ir en Vercel o en GitHub Pages.** No es opcional ni una preferencia: es el único sitio donde la web puede leer el Sheet.

Otra cosa del lienzo: adentro **el botón de bajar la tarjeta no funciona** — ahí se guarda manteniéndola presionada, como una foto de WhatsApp. En Vercel sí funciona.

---

## Lo que la web hace

| | |
|---|---|
| **Cuadrícula 000–999** | Blanco libre, amarillo apartado, azul pagado. Sale del Sheet |
| **Contadores** | Quedan libres, apartados, pagados y cuenta regresiva al cierre |
| **Tocar un número** | Abre una ficha con el estado y lo que significa |
| **"Lo quiero"** | Abre WhatsApp con el mensaje escrito y el código del vendedor pegado |
| **Links de vendedor** | `?v=V03`. Se guarda en el celular de quien entró: si vuelve otro día sigue contando para V03 |
| **ES/EN** | Botón arriba a la derecha. La versión en inglés encabeza el premio con NZD 1.000 |
| **Tarjeta-boleta** | Escribe su número y, **si ya está pagado**, genera la tarjeta de 880 × 520. La tarjeta sale **a nombre del dueño que dice el Sheet**, no de quien la genera |
| **Se refresca sola** | Cada 60 segundos relee el Sheet. Google guarda el CSV ~5 minutos, así que un cambio tarda hasta ~5 minutos en verse |

## Lo que la web no hace, a propósito

- **No muestra nombres completos ni teléfonos.** La cuadrícula solo muestra número y color. Al tocar un número pagado sale el nombre acortado (`Dav*** G.`) o `Reservado`, que es lo único que viaja en el CSV. El nombre completo vive en la hoja `COMPRADORES`, que no se publica.
- **No inventa un dato.** Si no logra leer el Sheet, los contadores quedan en `—`, la cuadrícula en blanco y sale un aviso que dice que escriban por WhatsApp. Nunca muestra un número que no sea real (regla fija 3).
- **No genera la tarjeta de un número que no esté pagado.** Dice que la tarjeta sale cuando el pago ya se vio en la app.
- **No vende.** No cobra, no reserva, no guarda nada. Toda venta pasa por WhatsApp y por el Sheet. La web solo muestra.
- **No dice que la rifa tiene permiso.** No aparece la palabra en ninguna parte.

## Si algo falla

| Qué ves | Qué pasó |
|---|---|
| "El tablero todavía no está conectado al Sheet" | `SHEET_CSV` está vacío. Falta el paso 3 |
| "No pudimos leer el tablero (404)" | El link del CSV está mal copiado, o se dejó de publicar la hoja |
| "faltan las columnas NUMERO o ESTADO" | La fila 1 de `NUMEROS` no dice exactamente `NUMERO` y `ESTADO` |
| La cuadrícula está toda blanca y hay números pagados en el Sheet | La columna `ESTADO` (la de la fórmula) está vacía. Revisá que `G2` esté arrastrada hasta la fila 1001 |
| Un cambio del Sheet no se ve | Esperá 5 minutos. Google cachea el CSV |
| Los apartados no se vencen | Falta el ajuste de **recalcular cada minuto** |
| Sutá no aparece | Las imágenes no se subieron junto al `index.html` |
| Funciona en Vercel pero no en el lienzo de Claude | Es lo esperado: el lienzo no puede leer Google. Ver arriba |
| Los números pagados salen sin nombre | Falta la columna `NOMBRE_PUBLICO` en `NUMEROS`, o la hoja `COMPRADORES` está vacía |

---

*Si cambia `index.html`, `artifact.html` se vuelve a generar a partir de él — no se editan los dos.*
