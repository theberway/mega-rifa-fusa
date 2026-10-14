# QR de la web — LÉEME

El QR apunta **directo** a `https://mega-rifa-fusa.vercel.app` (decisión 44). Está verificado: los 4 formatos se escanearon y leen exactamente esa dirección.

| Archivo | Para qué | Cómo se usa |
|---|---|---|
| `qr-digital.png` | Compartir por WhatsApp, estados, redes (1080×1080) | Mándalo como imagen. En el celular se escanea desde otro celular o se toca "buscar texto en la imagen" |
| `qr-cartel-carta.pdf` | Cartel para tiendas y vitrinas (carta, 1 por hoja) | Imprime en color o en blanco y negro. QR de ~11 cm: se lee a más de 1 m |
| `qr-stickers-30.pdf` | **5 hojas × 6 = 30 stickers** (carta) — todos iguales | Imprime las 5 hojas, corta por las líneas punteadas. QR de ~5 cm: se lee a ~50 cm, hay que pegarlo a la altura de los ojos |
| `qr-20-stickers.pdf` | **4 hojas × 6 = 20 stickers** (carta), **todos distintos** entre sí (6 layouts × varias combinaciones de color, pose de Sutá y titular). El 2M domina en cada uno. | Igual que arriba: imprime las 4 hojas, corta por las punteadas |
| `qr-6-media-hoja.pdf` | **3 hojas carta apaisada × 2 = 6 piezas** verticales de 5.5×8.5 in (media hoja carta). 2M dominante, QR grande (~7 cm), Sutá en diferentes poses. Entre vitrina y afiche chico. | Imprime en **horizontal** ("apaisado"), corta por la línea punteada vertical central → quedan 2 piezas verticales |
| `qr-web.svg` | El QR solo, vectorial | Para una imprenta o para meterlo en otra pieza |
| `qr-cartel-carta.png`, `qr-stickers-hoja-1.png`, `preview-stickers-pN.png`, `preview-mh-pN.png` | Vistas previas | Solo para mirar |

## Al imprimir
- **Papel blanco, escala 100 %** ("tamaño real", sin "ajustar a la página"). Las piezas llevan margen blanco: la impresora casera no imprime hasta el borde.
- Si imprimes en una papelería, mejor **adhesivo mate** (el brillante da reflejo y el celular no lee). Plastificado mate, si va a la intemperie.
- **No cambies el color del QR** (negro sobre blanco) ni lo estires, ni le pegues nada encima.
- Antes de pegar 30: imprime una hoja, **escanéala con tu celular y con otro de gama baja**, y mira que abra la web.
- El QR es **permanente**: si algún día cambia la dirección de la web, todo lo impreso deja de servir. Por eso no se cambia el dominio sin avisar (ver decisión 44).

## Regenerar

**Lo original** (digital, cartel, los 30 stickers iguales):
`python3 construir-qr.py` y después `NODE_PATH=/opt/node-tools/node_modules node exportar.js`. Necesita `pip install segno`.

**Lo nuevo** (20 stickers variados + 6 media hoja): no necesita `segno` porque reusa `qr-web.svg` ya generado. En Windows (Git Bash):
```
cd 08_Contenido/qr
/c/Users/Santiago/AppData/Local/Python/bin/python.exe construir-qr-nuevos.py
CHROME="C:/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
BASE='D:\Mis documentos\Documents\Work\The_Ber_Way\02_Clients\Santiago_Bermudez_Gomez\Mega-Rifa-Fusa\08_Contenido\qr'
HTML_ST="file:///D:/Mis%20documentos/Documents/Work/The_Ber_Way/02_Clients/Santiago_Bermudez_Gomez/Mega-Rifa-Fusa/08_Contenido/qr/qr-20-stickers.html"
HTML_MH="file:///D:/Mis%20documentos/Documents/Work/The_Ber_Way/02_Clients/Santiago_Bermudez_Gomez/Mega-Rifa-Fusa/08_Contenido/qr/qr-6-media-hoja.html"
"$CHROME" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf="$BASE\\qr-20-stickers.pdf" "$HTML_ST"
"$CHROME" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf="$BASE\\qr-6-media-hoja.pdf" "$HTML_MH"
```
La ruta de salida tiene que ir en formato Windows absoluto (con `\\`). Previews por pagina via `pymupdf`:
```
python -c "import pymupdf; [pymupdf.open(src).save or [p.get_pixmap(dpi=110).save(f'preview-{n}-p{i+1}.png') for i,p in enumerate(pymupdf.open(src))] for n,src in [('stickers','qr-20-stickers.pdf'),('mh','qr-6-media-hoja.pdf')]]"
```
