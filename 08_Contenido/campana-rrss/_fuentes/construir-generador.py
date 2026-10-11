# Mete las imágenes de Sutá (base64) en la plantilla y escribe ../generador-contador.html.
# Van incrustadas para que el lienzo no quede "contaminado" al abrir el archivo local (si no, no deja descargar el PNG).
import base64, io, os
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
def b64(nombre, alto=560):
    im = Image.open(os.path.join(RAIZ, "_assets", nombre)).convert("RGBA")
    im = im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True); return base64.b64encode(buf.getvalue()).decode()
html = open(os.path.join(AQUI, "generador-plantilla.html"), encoding="utf-8").read()
html = html.replace("__SUTA_4__", b64("suta-4-senalando.png")).replace("__SUTA_2__", b64("suta-2-saludando.png"))
open(os.path.join(RAIZ, "generador-contador.html"), "w", encoding="utf-8").write(html)
print("ok", round(len(html) / 1024), "KB")
