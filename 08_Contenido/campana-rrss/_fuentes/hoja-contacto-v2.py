# Hoja de contacto: grilla con todas las piezas v2 (feed + historia) para revisar de un vistazo.
# Salida: 08_Contenido/campana-rrss/hoja-contacto-v2.png
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# (etiqueta, ruta_feed, ruta_historia_opcional)
PIEZAS = [
    ("15-oct Quincena",           "semana-1/15-oct-quincena/feed.png",         "semana-1/15-oct-quincena/historia.png"),
    ("17-oct Encuesta",           "semana-1/17-oct-encuesta/feed.png",         "semana-1/17-oct-encuesta/historia.png"),
    ("20-oct Cómo se gana",       "semana-2/20-oct-como-se-gana/feed.png",     "semana-2/20-oct-como-se-gana/historia.png"),
    ("22-oct Cómo se verifica",   "semana-2/22-oct-como-se-verifica/feed.png", "semana-2/22-oct-como-se-verifica/historia.png"),
    ("23-oct Frase del día",      "semana-2/23-oct-frase-del-dia/feed.png",    "semana-2/23-oct-frase-del-dia/historia.png"),
    ("24-oct Embrujado 🎃",       "semana-3/24-oct-embrujado/feed.png",        "semana-3/24-oct-embrujado/historia.png"),
    ("27-oct Sale 5 dic",         "semana-3/27-oct-sale-5-dic/feed.png",       "semana-3/27-oct-sale-5-dic/historia.png"),
    ("29-oct Regala",             "semana-3/29-oct-regala/feed.png",           "semana-3/29-oct-regala/historia.png"),
    ("30-oct Fin de mes",         "semana-3/30-oct-fin-de-mes/feed.png",       "semana-3/30-oct-fin-de-mes/historia.png"),
    ("31-oct Suerte 🎃",          "semana-3/31-oct-suerte/feed.png",           "semana-3/31-oct-suerte/historia.png"),
    ("01-nov Frase",              "semana-3/01-nov-frase/feed.png",            "semana-3/01-nov-frase/historia.png"),
    ("02-nov Puente",             "semana-3/02-nov-puente/feed.png",           "semana-3/02-nov-puente/historia.png"),
    ("NZ Sofía (EN)",             "semana-3/NZ-sofia/feed-EN.png",             "semana-3/NZ-sofia/historia-EN.png"),
    ("APOYO · Error 404",         "semana-3/apoyo-1-error-404/feed.png",       "semana-3/apoyo-1-error-404/historia.png"),
    ("APOYO · POV meme",          "semana-3/apoyo-2-pov-meme/feed.png",        "semana-3/apoyo-2-pov-meme/historia.png"),
    ("APOYO · Horóscopo",         "semana-3/apoyo-3-horoscopo/feed.png",       "semana-3/apoyo-3-horoscopo/historia.png"),
    ("APOYO · Mi mamá vs yo",     "semana-3/apoyo-4-mi-mama/feed.png",         "semana-3/apoyo-4-mi-mama/historia.png"),
]

FEED_W, FEED_H = 360, 360
HIST_W, HIST_H = 220, 390
GAP_X, GAP_Y = 24, 46
PAD = 40
LABEL_H = 32
COLS = 4

# Calcular grid
TILE_W = FEED_W + GAP_X + HIST_W  # feed + hist side-by-side
TILE_H = max(FEED_H, HIST_H) + LABEL_H

rows = (len(PIEZAS) + COLS - 1) // COLS
canvas_w = PAD*2 + COLS*TILE_W + (COLS-1)*GAP_X
canvas_h = PAD*2 + 60 + rows*(TILE_H + GAP_Y) + 20

img = Image.new("RGB", (canvas_w, canvas_h), (255, 244, 214))  # crema
draw = ImageDraw.Draw(img)

# Titular
try:
    font_big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
    font_lbl = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
except Exception:
    font_big = ImageFont.load_default()
    font_lbl = ImageFont.load_default()

draw.text((PAD, PAD), "Hoja de contacto v2 — @megarifafusa (feed + historia)", fill=(26, 26, 26), font=font_big)

y0 = PAD + 60
for i, (etq, p_feed, p_hist) in enumerate(PIEZAS):
    row, col = divmod(i, COLS)
    x = PAD + col*(TILE_W + GAP_X)
    y = y0 + row*(TILE_H + GAP_Y)
    # label
    draw.rectangle([x, y, x + TILE_W, y + LABEL_H - 4], fill=(26, 26, 26))
    draw.text((x + 10, y + 4), etq, fill=(255, 244, 214), font=font_lbl)
    # feed
    try:
        feed_img = Image.open(os.path.join(RAIZ, p_feed)).convert("RGB")
        feed_img.thumbnail((FEED_W, FEED_H), Image.LANCZOS)
        img.paste(feed_img, (x, y + LABEL_H))
    except Exception as e:
        print("miss feed", p_feed, e)
    # historia
    if p_hist:
        try:
            hist_img = Image.open(os.path.join(RAIZ, p_hist)).convert("RGB")
            hist_img.thumbnail((HIST_W, HIST_H), Image.LANCZOS)
            img.paste(hist_img, (x + FEED_W + GAP_X, y + LABEL_H))
        except Exception as e:
            print("miss hist", p_hist, e)

out = os.path.join(RAIZ, "hoja-contacto-v2.png")
img.save(out, optimize=True)
print("ok", out, img.size)
