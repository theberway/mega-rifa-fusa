#!/usr/bin/env bash
# Uso: "$BASH" render.sh <fuente.html> <salida.png> <ancho> <alto>
# HTML -> PNG con chromium headless. Renderiza en una ventana más grande y recorta al tamaño exacto
# (headless=new le quita unos px al viewport y recortaría la pieza).
set -euo pipefail
CHROME="/c/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
PY="/c/Users/Santiago/AppData/Local/Python/bin/python.exe"
src="$(cygpath -m "$(realpath "$1")")"
out="$(cygpath -w "$(realpath -m "$2")")"
tmp="${out%.png}.tmp.png"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=8000 --window-size="$(( $3 + 200 )),$(( $4 + 300 ))" --screenshot="$tmp" "file:///$src" 2>/dev/null
"$PY" -c "import sys;from PIL import Image;im=Image.open(sys.argv[1]).convert('RGB');im.crop((0,0,int(sys.argv[3]),int(sys.argv[4]))).save(sys.argv[2]);import os;os.remove(sys.argv[1])" "$tmp" "$out" "$3" "$4"
echo "ok $2"
