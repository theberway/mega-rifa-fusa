# Genera las piezas del QR de la web. Uso: python3 construir-qr.py  (después: NODE_PATH=/opt/node-tools/node_modules node exportar.js)
# Decisión 44: QR directo a la web (sin acortador ni parámetros), negro tinta sobre blanco, corrección H, borde de silencio de 4 módulos.
import segno, io, textwrap
URL = "https://mega-rifa-fusa.vercel.app"
q = segno.make(URL, error=segno.consts.ERROR_CORRECTION_LEVELS["H"] if hasattr(segno.consts,'ERROR_CORRECTION_LEVELS') else 'h', micro=False)
n = len(q.matrix); B = 4; T = n + 2*B
paths = []
for y,row in enumerate(q.matrix):
    x=0
    while x<n:
        if row[x]:
            s=x
            while x<n and row[x]: x+=1
            paths.append(f"M{s+B} {y+B}h{x-s}v1h-{x-s}z")
        else: x+=1
svg = f'<svg class="qr" viewBox="0 0 {T} {T}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges"><rect width="{T}" height="{T}" fill="#fff"/><path fill="#1A1A1A" d="{"".join(paths)}"/></svg>'
open("qr-web.svg","w").write(svg)
print("modulos",n,"version",q.version)

FONTS = "@import url('https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Archivo+Narrow:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');"
BASE = FONTS + """
:root{--crema:#FFF4D6;--rojo:#C1121F;--amarillo:#F2B705;--azul:#0A3D62;--negro:#1A1A1A}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Archivo Narrow',sans-serif;color:var(--negro);-webkit-font-smoothing:antialiased}
.slab{font-family:'Alfa Slab One',serif;font-weight:400}.mono{font-family:'Space Mono',monospace;font-weight:700}
.qr{display:block;width:100%;height:100%}
"""

# ---------- 1. DIGITAL (1080x1080, para compartir) ----------
digital = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>QR digital — Mega Rifa Fusa</title><style>{BASE}
html,body{{background:var(--rojo)}}
.p{{position:relative;width:1080px;height:1080px;background:var(--rojo);overflow:hidden}}
.tag{{position:absolute;left:54px;top:50px;color:var(--crema);font-family:'Space Mono',monospace;font-weight:700;font-size:26px;letter-spacing:5px}}
.logo{{position:absolute;right:54px;top:34px;font-size:52px;line-height:.95;text-align:right;color:var(--crema);text-shadow:5px 5px 0 var(--negro)}}
.t{{position:absolute;left:54px;top:150px;width:560px;font-size:76px;line-height:1.02;color:var(--crema);text-shadow:6px 6px 0 var(--negro)}}
.qrbox{{position:absolute;left:54px;top:400px;width:520px;height:520px;background:#fff;border:10px solid var(--negro);padding:8px}}
.suta{{position:absolute;left:622px;top:150px;width:404px;height:770px;background:#F8EFDE;border:10px solid var(--negro);overflow:hidden}}
.suta img{{position:absolute;left:-30px;top:105px;width:440px;max-width:none}}
.flecha{{position:absolute;left:480px;top:300px;font-size:90px;color:var(--amarillo);text-shadow:4px 4px 0 var(--negro);transform:rotate(55deg)}}
.dato{{position:absolute;left:54px;right:54px;top:940px;height:88px;background:var(--amarillo);border:8px solid var(--negro);display:flex;align-items:center;justify-content:space-between;padding:0 24px}}
.dato b{{font-family:'Alfa Slab One',serif;font-weight:400;font-size:34px}}
.dato span{{font-weight:700;font-size:26px}}
.url{{position:absolute;left:54px;right:54px;bottom:10px;display:flex;justify-content:space-between;color:var(--crema);font-weight:700;font-size:22px}}
</style></head><body><div class="p" id="pieza">
<div class="tag">FUSAGASUGÁ · 2026</div>
<div class="logo slab">MEGA RIFA<br>FUSA</div>
<div class="t slab" style="top:170px;font-size:70px">ESCANEA Y ESCOGE TU NÚMERO</div>
<div class="qrbox">{svg}</div>
<div class="suta"><img src="suta-senalando.jpg" alt="Sutá"></div>
<div class="dato"><b>$2.000.000</b><span>1.000 números · $6.000 · Sorteo sáb 5 dic</span></div>
<div class="url"><span>Premio en efectivo si el número ganador está vendido</span><span class="mono">mega-rifa-fusa.vercel.app</span></div>
</div></body></html>"""
open("qr-digital.html","w",encoding="utf-8").write(digital)

# ---------- 2. CARTEL CARTA (imprimir) ----------
cartel = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>QR cartel carta — Mega Rifa Fusa</title><style>{BASE}
@page{{size:8.5in 11in;margin:0}}
html,body{{background:#fff}}
.h{{position:relative;width:816px;height:1056px;background:#fff;overflow:hidden;padding:36px}}
.marco{{position:relative;width:100%;height:100%;border:10px solid var(--negro);background:var(--crema);display:flex;flex-direction:column}}
.top{{background:var(--rojo);border-bottom:10px solid var(--negro);padding:16px 30px;display:flex;justify-content:space-between;align-items:center}}
.top .l{{font-size:58px;line-height:.95;color:var(--crema);text-shadow:5px 5px 0 var(--negro)}}
.top .f{{color:var(--crema);font-family:'Space Mono',monospace;font-weight:700;font-size:20px;letter-spacing:4px;text-align:right;line-height:1.5}}
.cta{{text-align:center;margin-top:18px;font-size:50px;line-height:1.04;color:var(--rojo)}}
.mid{{display:flex;justify-content:center;align-items:center;gap:22px;margin-top:18px}}
.qrbox{{width:410px;height:410px;background:#fff;border:10px solid var(--negro);padding:6px}}
.suta{{width:230px;height:410px;background:#F8EFDE;border:10px solid var(--negro);position:relative;overflow:hidden}}
.suta img{{position:absolute;left:-14px;top:52px;width:288px;max-width:none}}
.premio{{margin:18px 30px 0;background:var(--amarillo);border:8px solid var(--negro);padding:12px 22px;display:flex;justify-content:space-between;align-items:center}}
.premio .c{{font-size:46px;line-height:1;white-space:nowrap}}
.premio .d{{font-weight:700;font-size:21px;line-height:1.2;text-align:right;margin-left:16px}}
.premio small{{display:block;font-size:17px;font-weight:600}}
.pie{{margin-top:auto;padding:0 0 12px;text-align:center}}
.pie .u{{font-size:30px;color:var(--negro);line-height:1.1}}
.pie .o{{font-weight:700;font-size:18px;margin-top:4px}}
</style></head><body><div class="h"><div class="marco">
<div class="top"><div class="l slab">MEGA RIFA<br>FUSA</div><div class="f">FUSAGASUGÁ<br>2026</div></div>
<div class="cta slab">ESCANEA Y ESCOGE<br>TU NÚMERO</div>
<div class="mid"><div class="qrbox">{svg}</div><div class="suta"><img src="suta-senalando.jpg" alt=""></div></div>
<div class="premio"><div class="c slab">$2.000.000</div><div class="d">1.000 números a $6.000<small>Premio en efectivo si el número ganador está vendido · Sorteo sáb 5 dic, 10:30 p.m. · Lotería de Boyacá</small></div></div>
<div class="pie"><div class="u mono">mega-rifa-fusa.vercel.app</div><div class="o">Organizada por Santiago · The Ber Way · Solo mayores de 18</div></div>
</div></div></body></html>"""
open("qr-cartel-carta.html","w",encoding="utf-8").write(cartel)

# ---------- 3. HOJA DE STICKERS (6 por carta, 5 hojas = 30) ----------
card = f"""<div class="s"><div class="sh"><span class="slab">MEGA RIFA FUSA</span></div>
<div class="sb"><div class="q">{svg}</div></div>
<div class="sf"><div class="a slab">ESCANEA Y ESCOGE TU NÚMERO</div><div class="p"><b>$2.000.000</b> · 1.000 números a $6.000</div><div class="u mono">mega-rifa-fusa.vercel.app</div></div></div>"""
hojas = "".join(f'<section class="pg">{card*6}</section>' for _ in range(5))
stickers = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>QR stickers — Mega Rifa Fusa</title><style>{BASE}
@page{{size:8.5in 11in;margin:0}}
html,body{{background:#fff}}
.pg{{width:816px;height:1056px;padding:32px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,330px);page-break-after:always;break-after:page}}
.s{{border:1.5px dashed #888;display:flex;flex-direction:column;padding:7px;margin:0;overflow:hidden}}
.sb{{flex:1;display:flex;flex-direction:column;border:6px solid var(--negro);background:var(--crema);overflow:hidden}}
.sh{{background:var(--rojo);border:6px solid var(--negro);border-bottom:0;text-align:center;padding:3px 0 1px;color:var(--crema);font-size:23px;text-shadow:3px 3px 0 var(--negro)}}
.sb{{border-top:6px solid var(--negro);align-items:center;justify-content:center;padding:4px;background:#fff}}
.q{{width:184px;height:184px}}
.sf{{background:var(--amarillo);border:6px solid var(--negro);border-top:0;text-align:center;padding:4px 4px 5px}}
.a{{font-size:15.5px;line-height:1.1;color:var(--negro)}}
.p{{font-weight:700;font-size:14px;margin-top:2px}}
.u{{font-size:13px;margin-top:1px}}
</style></head><body>{hojas}</body></html>"""
open("qr-stickers-hoja.html","w",encoding="utf-8").write(stickers)
