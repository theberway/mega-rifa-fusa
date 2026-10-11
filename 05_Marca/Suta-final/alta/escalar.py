# Escala las poses de 200 px a 1024 px (sin IA: Lanczos por etapas + limpieza JPEG + enfoque)
# y quita el fondo crema para dejarlas transparentes. Uso: python escalar.py
import os, numpy as np
from PIL import Image, ImageFilter
AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(AQUI)
for f in ['2-saludando.jpg','3-con-la-boleta.jpg','4-senalando.jpg','5-pulgar-arriba.jpg','6-celebrando.jpg']:
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    im = im.filter(ImageFilter.MedianFilter(3))            # quita ruido de JPEG
    for s in (400, 800, 1024):                               # por etapas
        im = im.resize((s, s), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    a = np.asarray(im).astype(np.int16)
    fondo = np.median(np.concatenate([a[:8,:8].reshape(-1,3), a[:8,-8:].reshape(-1,3), a[-8:,:8].reshape(-1,3), a[-8:,-8:].reshape(-1,3)]), axis=0)
    d = np.sqrt(((a - fondo)**2).sum(axis=2))
    # alfa por distancia al color del fondo; solo el fondo conectado a los bordes
    from collections import deque
    mask = d < 28
    vis = np.zeros_like(mask); q = deque()
    h, w = mask.shape
    for y in range(h):
        for x in (0, w-1):
            if mask[y,x] and not vis[y,x]: vis[y,x]=True; q.append((y,x))
    for x in range(w):
        for y in (0, h-1):
            if mask[y,x] and not vis[y,x]: vis[y,x]=True; q.append((y,x))
    while q:
        y,x = q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx = y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not vis[ny,nx]:
                vis[ny,nx]=True; q.append((ny,nx))
    alpha = np.where(vis, 0, 255).astype(np.uint8)
    al = Image.fromarray(alpha).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert('RGBA'); out.putalpha(al)
    bbox = al.getbbox(); out = out.crop(bbox)
    out.save(os.path.join(AQUI, f.rsplit('.',1)[0] + '.png'))
    print(f, out.size)
