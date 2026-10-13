# QR de la web — LÉEME

El QR apunta **directo** a `https://mega-rifa-fusa.vercel.app` (decisión 44). Está verificado: los 4 formatos se escanearon y leen exactamente esa dirección.

| Archivo | Para qué | Cómo se usa |
|---|---|---|
| `qr-digital.png` | Compartir por WhatsApp, estados, redes (1080×1080) | Mándalo como imagen. En el celular se escanea desde otro celular o se toca "buscar texto en la imagen" |
| `qr-cartel-carta.pdf` | Cartel para tiendas y vitrinas (carta, 1 por hoja) | Imprime en color o en blanco y negro. QR de ~11 cm: se lee a más de 1 m |
| `qr-stickers-30.pdf` | **5 hojas × 6 = 30 stickers** (carta) | Imprime las 5 hojas, corta por las líneas punteadas. QR de ~5 cm: se lee a ~50 cm, hay que pegarlo a la altura de los ojos |
| `qr-web.svg` | El QR solo, vectorial | Para una imprenta o para meterlo en otra pieza |
| `qr-cartel-carta.png`, `qr-stickers-hoja-1.png` | Vistas previas | Solo para mirar |

## Al imprimir
- **Papel blanco, escala 100 %** ("tamaño real", sin "ajustar a la página"). Las piezas llevan margen blanco: la impresora casera no imprime hasta el borde.
- Si imprimes en una papelería, mejor **adhesivo mate** (el brillante da reflejo y el celular no lee). Plastificado mate, si va a la intemperie.
- **No cambies el color del QR** (negro sobre blanco) ni lo estires, ni le pegues nada encima.
- Antes de pegar 30: imprime una hoja, **escanéala con tu celular y con otro de gama baja**, y mira que abra la web.
- El QR es **permanente**: si algún día cambia la dirección de la web, todo lo impreso deja de servir. Por eso no se cambia el dominio sin avisar (ver decisión 44).

## Regenerar
`python3 construir-qr.py` y después `NODE_PATH=/opt/node-tools/node_modules node exportar.js`. Necesita `pip install segno`.
