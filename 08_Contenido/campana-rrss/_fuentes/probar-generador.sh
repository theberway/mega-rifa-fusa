#!/usr/bin/env bash
# Prueba el generador sin abrirlo: renderiza cada tipo con datos de ejemplo y arma una hoja.
# Uso (Git Bash): "$BASH" probar-generador.sh
set -euo pipefail
cd "$(dirname "$0")"
G="file:///$(cygpath -m "$(realpath ../generador-contador.html)")"
CH="/c/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
PY="/c/Users/Santiago/AppData/Local/Python/bin/python.exe"
mkdir -p prueba-generador
shot(){ "$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=10000 \
  --window-size=$3 --screenshot="$(cygpath -w "$(realpath -m "prueba-generador/$2")")" "$G?$1" 2>/dev/null; }
shot "tipo=vamos&libres=880&vendidos=112&fecha=2026-10-18&solo=feed" vamos-feed.png 1280,1380
shot "tipo=vamos&libres=880&vendidos=112&fecha=2026-10-18&solo=hist" vamos-hist.png 1280,2220
shot "tipo=busca-dueno&numero=314&libreok=1&fecha=2026-10-21&solo=feed" busca-feed.png 1280,1380
shot "tipo=busca-dueno&numero=314&libreok=1&fecha=2026-10-21&solo=hist" busca-hist.png 1280,2220
shot "tipo=ya-escogieron&libres=873&fecha=2026-10-12&solo=feed" escogieron-feed.png 1280,1380
shot "tipo=ya-escogieron&libres=873&fecha=2026-10-12&solo=hist" escogieron-hist.png 1280,2220
shot "tipo=prueba-social&libres=1000&fecha=2026-10-16" error-1000.png 1200,700
shot "tipo=vamos&libres=900&vendidos=200&fecha=2026-10-18" error-suma.png 1200,700
shot "tipo=busca-dueno&numero=314&fecha=2026-10-21" error-sin-check.png 1200,700
"$PY" - <<'PYEOF'
from PIL import Image
d='prueba-generador/'
fe=[Image.open(d+f).crop((0,0,1080,1080)) for f in ('vamos-feed.png','busca-feed.png','escogieron-feed.png')]
hi=[Image.open(d+f).crop((0,0,1080,1920)).resize((608,1080)) for f in ('vamos-hist.png','busca-hist.png','escogieron-hist.png')]
H=Image.new('RGB',(3*1080+3*608+120,1080),(60,60,60));x=0
for im in fe+hi: H.paste(im,(x,0)); x+=im.width+20
H.thumbnail((2400,2400)); H.save(d+'hoja.png'); print('hoja ok')
PYEOF
