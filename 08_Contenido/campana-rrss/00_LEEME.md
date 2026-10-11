# Campaña de redes · 10–23 oct 2026 — LÉEME

Todo lo de las 2 primeras semanas para **Instagram, Facebook y TikTok**. Tú solo publicas; nada se ha publicado.

## Cómo se usa (cada día)
1. Abre `calendario-publicacion.md` y mira qué toca hoy.
2. Entra a la carpeta del día (`semana-X/DD-oct-.../`): ahí están los PNG, el `copy.md` (texto para @megarifafusa, para tu cuenta personal y para TikTok, con hashtags) y, si hay video, el `reel.md` (storyboard, voz en off y rótulos).
3. Si la pieza dice **Gen.**: abre `generador-contador.html` (doble clic, con internet para las fuentes), escoge la pieza, escribe el dato **real** del tablero de ese momento y descarga el feed y la historia. Guárdalos en la carpeta del día.
4. En el copy, reemplaza `[QUEDAN]`, `[VAN]` o `[###]` por **los mismos números** que pusiste en el generador.

## Carpetas
| | |
|---|---|
| `semana-0/` | 10–12 oct: preventa |
| `semana-1/` | 13–18 oct: lanzamiento, NZ, quincena, encuesta, PC1 |
| `semana-2/` | 19–23 oct |
| `generador-contador.html` | Piezas con cifras reales (no deja descargar si falta un dato o no cuadra) |
| `_assets/` | Sutá: pose 1 en alta + poses 2, 3 y 4 escaladas a 1024 px |
| `_fuentes/` | Para regenerar: `construir.py` (piezas fijas), `construir-generador.py`, `escribir-textos.py`, `render.sh`, `revision.py`, `probar-generador.sh` |

## Lo que ninguna pieza dice (revísalo antes de publicar algo que cambies)
- Que la rifa tiene permiso o autorización.
- La causa (para qué es la plata). En público solo va "organizada por Santiago".
- Un contador que no sea el real del día, "quedan pocos" o urgencia inventada. Tampoco que un número está libre sin haberlo mirado.
- Nombres completos, teléfonos o caras sin permiso. Fotos de compradores: solo manos y solo con permiso.
- El premio de consolación (whisky): **no va en las piezas ni en los captions** (decisión de Santiago, 10 oct). Está en el reglamento.
- Bajo el premio va siempre "si el número ganador está vendido": es la regla del premio, y es lo honesto.

## Datos fijos
1.000 números (000–999) · $6.000 (NZD 4 en NZ) · premio $2.000.000 (NZD 1.000 si se vendió en NZ) · sorteo **sáb 5 dic 2026, 10:30 p.m.**, últimas 3 cifras del premio mayor de la Lotería de Boyacá · tablero `mega-rifa-fusa.vercel.app` · reglas `mega-rifa-fusa.vercel.app/reglamento` · solo mayores de 18.

## Sutá
Las poses 2, 3 y 4 se **escalaron** de 200 a 1024 px, sin IA (no había forma de regenerarlas aquí). Al tamaño en que salen en las piezas se ven bien. **No sirven para impresión grande**; para eso hacen falta los originales en alta.

## Si quieres cambiar algo
- Un texto de una pieza fija: edítalo en `_fuentes/construir.py` y corre `python construir.py <parte-del-nombre>` (ej. `15-oct-quincena`). Después corre `python revision.py` y mira `_fuentes/revision-*.png`.
- Un caption: edita el `copy.md` directamente.
