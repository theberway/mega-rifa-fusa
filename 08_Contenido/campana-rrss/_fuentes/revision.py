# Hojas de revisión (miniaturas) de todas las piezas. Uso: python revision.py
import glob, os
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def hoja(pat, out, tw, th, cols):
    fs = sorted(glob.glob(os.path.join(R, pat), recursive=True))
    if not fs: return
    rows = (len(fs) + cols - 1) // cols
    H = Image.new('RGB', (cols*(tw+10)+10, rows*(th+40)+10), (60, 60, 60)); d = ImageDraw.Draw(H)
    for i, f in enumerate(fs):
        im = Image.open(f); im.thumbnail((tw, th)); x = 10+(i % cols)*(tw+10); y = 10+(i//cols)*(th+40)
        H.paste(im, (x, y)); d.text((x, y+th+5), os.path.relpath(f, R).replace(os.sep, '/')[-60:], fill=(255, 255, 255))
    H.save(os.path.join(R, out)); print(out, len(fs))
hoja('semana-*/**/feed*.png', '_fuentes/revision-feeds.png', 420, 420, 4)
hoja('semana-*/**/carrusel*.png', '_fuentes/revision-carrusel.png', 420, 420, 4)
hoja('semana-*/**/historia*.png', '_fuentes/revision-historias.png', 300, 533, 6)
