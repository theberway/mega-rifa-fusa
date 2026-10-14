# Brief — Posts v2 de @megarifafusa (feed + historias)

**Fecha de este brief:** 2026-10-14
**Alcance:** rediseñar la próxima tanda de piezas de feed e historias con un estilo más creativo, disruptivo y con el premio de $2.000.000 dominante. No se rompe la marca aprobada.

## 1. Lo que pidió Santiago (verbatim)

- El **premio de $2.000.000 tiene que primar** visualmente en cada pieza.
- Debe ser **fácil de leer para todos, no mucho texto**.
- Los posts nuevos deben ser **más creativos, disruptivos, que impresionen a la gente**.
- Trigger explícito: `/high-end-visual-design` (skill de dirección visual).

## 2. Direccion creativa aprobada

Está escrita en: `08_Contenido/campana-rrss/_fuentes/direccion-creativa-v2.md`

Resumen:
- "$2.000.000" en Alfa Slab One, ocupando ≥40% del alto útil de la pieza, siempre en una banda de color plena con borde negro, con "si el número ganador está vendido" debajo (chico pero presente).
- **Una idea por pieza, un CTA, menos texto (−40%).**
- Mejor composición: asimetría, capas superpuestas, rotaciones leves (-3 a -5°), stacked cards. No todo centrado.
- **La marca intacta** (`05_Marca/sistema-de-marca.md`, decisión del 3-oct): paleta crema/rojo/amarillo/azul/negro, Alfa Slab One + Archivo Narrow + Space Mono, Sutá con respeto en sus 6 poses.

## 3. Reglas fijas (NO negociables)

De `08_Contenido/campana-rrss/00_LEEME.md` + decisiones:
- **Sin lenguaje legal / sin permiso / sin licencia.**
- **Sin whisky de consolación** en las piezas (solo vive en el reglamento).
- **Sin la causa** (moto, U, emprendimientos) — eso es 1-a-1. Firma pública: "Organizada por Santiago · The Ber Way".
- **Sin urgencia falsa ni contadores inventados.** Los contadores dinámicos (ya vendidos, quedan X, etc.) solo con dato real del tablero del día; para esto existe `generador-contador.html`.
- **Honestidad del premio**: bajo "$2.000.000" va siempre "Si el número ganador está vendido" (decisión 37).
- **Privacidad**: nombres cortados (`Dav*** G.`), fotos solo manos y con permiso.
- Datos duros fijos: 1.000 números (000–999) · $6.000 c/u · sorteo sáb 5 dic 2026, 10:30 p.m. · últimas 3 cifras del premio mayor de la Lotería de Boyacá.
- Idioma: español colombiano sin voseo. NZ (pieza con sufijo `-EN`) en inglés.
- Cuentas: **@megarifafusa** publica todo; **@santiagobermudezai** reposte con su propio texto.

## 4. Estado actual de la campaña

Carpetas: `08_Contenido/campana-rrss/semana-0/`, `semana-1/`, `semana-2/`
- Ya generadas (PNG renderizados desde HTML con Chromium headless): **9 feeds + 10 historias + 1 carrusel de 4 láminas**. Fechas: 10-oct, 11-oct, 13-oct, 14-oct (ES + NZ-EN), 15-oct, 17-oct, 20-oct, 22-oct, 23-oct.
- Dinámicas (se generan el día con cifra real del tablero, no están pre-renderizadas): 12-oct, 16-oct, 18-oct, 21-oct, "cualquier día / quedan X". Usan `generador-contador.html`.
- **Reels (6 guiones por grabar)**, están como `reel.md` en cada carpeta.
- Calendario corregido: `08_Contenido/campana-rrss/calendario-publicacion.md` (ignorar el `calendario-de-contenido.md` viejo).

Lo que queda por producir con estilo v2:
- Rediseñar las piezas ya hechas que no cumplan el estándar v2 (opcional, decidir con Santiago).
- Producir las piezas pendientes del calendario (semana-2 restante + semana-3+) directamente en v2.
- Carrusel adicional si el calendario lo pide.

## 5. Pipeline técnico (lo que funciona en esta máquina)

- **Fuentes HTML**: cada pieza es un HTML en `_fuentes/gen/` nombrado `semana-X__DD-oct-nombre__(feed|historia).html`. Se enlaza a `../marca.css` + estilos locales.
- **Script generador**: `_fuentes/construir.py` escribe los HTML; `_fuentes/escribir-textos.py` genera los `copy.md`/`reel.md`.
- **Render**: `_fuentes/render.sh` llama a Chromium y recorta con PIL. En Windows usar directamente:
  - Python: `C:/Users/Santiago/AppData/Local/Python/bin/python.exe` (3.14, tiene `openpyxl`, PyMuPDF)
  - Chromium headless: `C:/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe --headless=new --no-sandbox --disable-gpu`
  - Para screenshots: `--screenshot="<ruta Windows absoluta>" --window-size=W,H --hide-scrollbars`
  - **Trampa**: la ruta de salida tiene que ir en formato Windows absoluto con `\\`, no POSIX, o Chromium escribe en otro lado silenciosamente.
- **Dinámico**: `08_Contenido/campana-rrss/generador-contador.html` para piezas con cifras reales. 5 tipos. Validación estricta (no deja descargar sin dato verificado del tablero).

## 6. Assets de marca

- `05_Marca/sistema-de-marca.md` (guía completa).
- `05_Marca/Suta-final/` (6 poses .jpg/.webp + versiones alta 1024px en `alta/*.png` para impresión).
- `05_Marca/banner-facebook.png` (banner FB).
- `08_Contenido/campana-rrss/_assets/` (Sutá recortado para piezas).
- Referencias visuales de v2 ya aplicado (para mirar antes de empezar): `08_Contenido/qr/qr-6-media-hoja.pdf` (piezas MH-A, MH-B, MH-C) y `qr-20-stickers.pdf` (layouts A, E, F).

## 7. Lo que esta sesión ya dejó listo

Commit `d91b886` en `claude/sweet-maxwell-bvoqti` (ya pusheado):
- 20 QR stickers variados (`08_Contenido/qr/qr-20-stickers.pdf`).
- 6 QR media hoja (`08_Contenido/qr/qr-6-media-hoja.pdf`).
- Script `08_Contenido/qr/construir-qr-nuevos.py`.
- `08_Contenido/campana-rrss/_fuentes/direccion-creativa-v2.md` (principios).
- `08_Contenido/qr/00_LEEME.md` actualizado.

## 8. Checklist por pieza nueva (de direccion-creativa-v2.md)

- [ ] "$2.000.000" se lee en 1 segundo al escroll.
- [ ] "Si el número ganador está vendido" presente y legible.
- [ ] Un solo mensaje y un solo CTA por pieza.
- [ ] ¿Sobra texto que se puede quitar sin perder nada?
- [ ] Jerarquía clara, composición con intención, no todo centrado.
- [ ] Marca y Sutá respetados.
