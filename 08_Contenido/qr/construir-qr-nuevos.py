# Genera dos piezas impresas nuevas, con el 2M dominante y layouts variados.
#   - qr-20-stickers.html  (4 hojas carta vertical, 20 stickers unicos)
#   - qr-6-media-hoja.html (3 hojas carta apaisada, 6 piezas verticales de 5.5x8.5 in)
# Reusa qr-web.svg (mismo QR que ya se imprimio: decision 44, directo a mega-rifa-fusa.vercel.app).
# No modifica construir-qr.py ni qr-stickers-30.pdf.
# Uso: python construir-qr-nuevos.py   (despues: render con Chromium headless; ver 00_LEEME.md)

from pathlib import Path

AQUI = Path(__file__).parent
SVG = (AQUI / "qr-web.svg").read_text(encoding="utf-8")

FONTS = "@import url('https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Archivo+Narrow:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');"

BASE = FONTS + """
:root{--crema:#FFF4D6;--rojo:#C1121F;--amarillo:#F2B705;--azul:#0A3D62;--negro:#1A1A1A}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;font-family:'Archivo Narrow',sans-serif;color:var(--negro);-webkit-font-smoothing:antialiased}
.slab{font-family:'Alfa Slab One',serif;font-weight:400}
.mono{font-family:'Space Mono',monospace;font-weight:700}
.qr svg,svg.qr{display:block;width:100%;height:100%}
"""

# Rutas de Suta relativas a 08_Contenido/qr/
POSES = {
    "senalando":  "suta-senalando.jpg",                      # ya esta en la carpeta qr
    "saludando":  "../campana-rrss/_assets/2-saludando.jpg",
    "boleta":     "../campana-rrss/_assets/3-con-la-boleta.jpg",
    "pulgar":     "../campana-rrss/_assets/5-pulgar-arriba.jpg",
    "celebrando": "../campana-rrss/_assets/6-celebrando.jpg",
    "depie":      "../campana-rrss/_assets/1-de-pie.webp",
}

TITULARES = [
    "ESCANEA Y ESCOGE",
    "TU NUMERO TE ESPERA",
    "1.000 NUMEROS · 1 GANADOR",
    "ESCANEA Y JUEGA",
    "AQUI ESCOGES TU NUMERO",
]

# ===================================================================
# 20 STICKERS — grid 2x3 por carta vertical (4 hojas: 6+6+6+2)
# ===================================================================
# Cada sticker vive dentro de una celda ~376x330 px.
# Diseños: el 2M siempre va grande; el QR siempre va; la frase "si el numero
# ganador esta vendido" va siempre pero chica. Varia layout, acento, pose, titular.

ST_CSS = BASE + """
@page{size:8.5in 11in;margin:0}
.pg{width:816px;height:1056px;padding:28px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,328px);gap:0;page-break-after:always;break-after:page}
.pg:last-child{page-break-after:auto;break-after:auto}
.s{position:relative;border:1.5px dashed #999;margin:4px;overflow:hidden;background:var(--crema)}
.s .marco{position:absolute;inset:4px;border:5px solid var(--negro);overflow:hidden;display:flex;flex-direction:column}

/* --- Layout A: 2M arriba enorme en banda roja, QR centrado abajo con Suta chico --- */
.A .tope{background:var(--rojo);color:var(--crema);text-align:center;padding:6px 8px 10px;border-bottom:5px solid var(--negro)}
.A .tope .k{font-size:10.5px;letter-spacing:2.5px;font-weight:700}
.A .tope .big{font-size:46px;line-height:.95;text-shadow:3px 3px 0 var(--negro);margin-top:1px;white-space:nowrap}
.A .cuerpo{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:8px;background:var(--crema);position:relative}
.A .qr{width:132px;height:132px;background:#fff;border:4px solid var(--negro);padding:3px}
.A .suta{width:72px;height:132px;overflow:hidden;position:relative}
.A .suta img{position:absolute;left:-18px;top:0;height:132px;width:auto}
.A .cta{font-size:12.5px;line-height:1.08;font-weight:700;text-align:center;max-width:90px}
.A .pie{background:var(--amarillo);border-top:5px solid var(--negro);padding:5px 8px;text-align:center;font-size:9.5px;font-weight:700}
.A .pie b{font-weight:700}

/* --- Layout B: QR a la izquierda, 2M vertical a la derecha --- */
.B{display:flex;flex-direction:row !important;background:var(--crema)}
.B .qrcol{width:150px;background:#fff;border-right:5px solid var(--negro);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px}
.B .qrcol .qr{width:128px;height:128px}
.B .qrcol .lbl{font-size:9.5px;font-weight:700;text-align:center;margin-top:5px;letter-spacing:1.2px}
.B .right{flex:1;display:flex;flex-direction:column;min-width:0}
.B .pr{background:var(--amarillo);flex:1;padding:10px 6px;text-align:center;display:flex;flex-direction:column;justify-content:center;position:relative}
.B .pr .k{font-size:9.5px;letter-spacing:2px;font-weight:700;color:var(--negro)}
.B .pr .big{font-size:30px;line-height:.95;color:var(--negro);text-shadow:2px 2px 0 var(--crema);margin:2px 0;white-space:nowrap}
.B .pr .sub{font-size:9.5px;font-weight:700;line-height:1.15;margin-top:3px;padding:0 2px}
.B .foot{background:var(--rojo);color:var(--crema);text-align:center;padding:4px 2px;font-size:8.5px;font-weight:700;border-top:5px solid var(--negro);line-height:1.2}

/* --- Layout C: 2M como "sello" circular, QR debajo --- */
.C{background:var(--crema);text-align:center;padding:6px 8px;display:flex;flex-direction:column;align-items:center}
.C .sello{width:160px;height:160px;background:var(--amarillo);border:5px solid var(--negro);border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1;margin-top:4px;box-shadow:4px 4px 0 var(--negro)}
.C .sello .k{font-size:9.5px;letter-spacing:2.5px;font-weight:700;margin-bottom:1px}
.C .sello .big{font-size:26px;line-height:.95;color:var(--negro);white-space:nowrap}
.C .sello .sub{font-size:8.5px;font-weight:700;margin-top:2px;padding:0 14px;line-height:1.1}
.C .mid{display:flex;align-items:center;gap:6px;margin-top:4px}
.C .qr{width:100px;height:100px;background:#fff;border:4px solid var(--negro);padding:2px}
.C .cta{font-size:11px;font-weight:700;max-width:95px;line-height:1.1;text-align:left}
.C .foot{margin-top:auto;background:var(--rojo);color:var(--crema);width:100%;padding:4px;font-size:9px;font-weight:700;letter-spacing:1px;border-top:5px solid var(--negro);text-align:center}

/* --- Layout D: franja diagonal, 2M bien grande en centro, QR abajo-derecha --- */
.D{background:var(--amarillo);position:relative;overflow:hidden}
.D .diag{position:absolute;top:-26px;left:-40px;width:140%;height:46px;background:var(--rojo);transform:rotate(-10deg);border-bottom:4px solid var(--negro);border-top:4px solid var(--negro);display:flex;align-items:center;justify-content:center;color:var(--crema);font-size:11px;letter-spacing:3px;font-weight:700}
.D .big{position:absolute;top:46px;left:0;right:0;text-align:center;font-size:42px;line-height:.95;color:var(--negro);text-shadow:3px 3px 0 var(--crema);white-space:nowrap}
.D .sub{position:absolute;top:118px;left:0;right:0;text-align:center;font-size:11.5px;font-weight:700;line-height:1.15;padding:0 18px}
.D .qrbox{position:absolute;right:12px;bottom:12px;width:118px;height:118px;background:#fff;border:4px solid var(--negro);padding:3px}
.D .suta{position:absolute;left:10px;bottom:8px;width:120px;height:160px;overflow:hidden}
.D .suta img{position:absolute;left:-20px;bottom:-10px;width:160px}
.D .foot{position:absolute;left:14px;right:14px;bottom:134px;font-size:9.5px;font-weight:700;color:var(--negro);text-align:center;background:var(--crema);border:3px solid var(--negro);padding:2px 4px}

/* --- Layout E: 2M como texto suelto con sombra dura, QR a la izq, Suta a la der --- */
.E{background:var(--crema);padding:10px;display:flex;flex-direction:column}
.E .k{font-size:10px;letter-spacing:3px;font-weight:700;text-align:center}
.E .big{text-align:center;font-size:48px;line-height:.95;color:var(--rojo);text-shadow:4px 4px 0 var(--negro);margin:2px 0 4px;white-space:nowrap}
.E .cond{text-align:center;font-size:9.5px;font-weight:700;line-height:1.15;margin-bottom:6px}
.E .row{display:flex;align-items:center;gap:8px;flex:1}
.E .qr{width:115px;height:115px;background:#fff;border:4px solid var(--negro);padding:2px}
.E .suta{flex:1;height:115px;overflow:hidden;position:relative;border:3px solid var(--negro);background:#F8EFDE}
.E .suta img{position:absolute;left:50%;top:0;transform:translateX(-50%);height:135px;width:auto}
.E .cta{font-size:10.5px;font-weight:700;text-align:center;margin-top:5px;background:var(--amarillo);border:3px solid var(--negro);padding:3px 4px;line-height:1.1}

/* --- Layout F: fondo azul, 2M crema brillante centrado, QR abajo --- */
.F{background:var(--azul);color:var(--crema);text-align:center;padding:8px;display:flex;flex-direction:column;align-items:center}
.F .k{font-size:10.5px;letter-spacing:3px;font-weight:700;margin-top:2px}
.F .big{font-size:44px;line-height:.95;color:var(--amarillo);text-shadow:3px 3px 0 var(--negro);margin:2px 0 2px;white-space:nowrap}
.F .cond{font-size:9.5px;font-weight:700;line-height:1.15;color:var(--crema);margin-bottom:6px}
.F .qr{width:120px;height:120px;background:#fff;border:4px solid var(--negro);padding:3px}
.F .cta{margin-top:6px;background:var(--rojo);color:var(--crema);border:3px solid var(--negro);padding:3px 10px;font-size:11.5px;font-weight:700;letter-spacing:1.5px}
.F .url{margin-top:4px;font-size:9px;color:var(--crema);font-family:'Space Mono',monospace;font-weight:700;line-height:1.3}
"""

def st_A(acento, titular, pose):
    # banda arriba usa 'acento' como color
    return f'''<div class="s"><div class="marco A" style="--acc:{acento}">
<div class="tope" style="background:{acento}"><div class="k">MEGA RIFA FUSA · FUSAGASUGA</div><div class="slab big">$2.000.000</div></div>
<div class="cuerpo"><div class="qr">{SVG}</div><div class="suta"><img src="{POSES[pose]}" alt=""></div><div class="cta slab">{titular}</div></div>
<div class="pie">Premio en efectivo si el numero ganador esta vendido · 1.000 numeros · $6.000 · <span class="mono">mega-rifa-fusa.vercel.app</span></div>
</div></div>'''

def st_B(acento, titular, pose):
    return f'''<div class="s"><div class="marco B">
<div class="qrcol"><div class="qr">{SVG}</div><div class="lbl slab">ESCANEA</div></div>
<div class="right"><div class="pr" style="background:{acento}"><div class="k">PREMIO EN EFECTIVO</div><div class="slab big">$2.000.000</div><div class="sub">Si el numero ganador esta vendido<br>1.000 numeros · $6.000 · Sorteo sab 5 dic</div></div>
<div class="foot">{titular} · <span class="mono">mega-rifa-fusa.vercel.app</span></div></div>
</div></div>'''

def st_C(acento, titular, pose):
    # sello usa acento
    return f'''<div class="s"><div class="marco C">
<div class="sello" style="background:{acento}"><div class="k">PREMIO</div><div class="slab big">$2.000.000</div><div class="sub">Si el numero ganador esta vendido</div></div>
<div class="mid"><div class="qr">{SVG}</div><div class="cta slab">{titular}</div></div>
<div class="foot">1.000 numeros · $6.000 · <span class="mono">mega-rifa-fusa.vercel.app</span></div>
</div></div>'''

def st_D(acento, titular, pose):
    # ignora acento (fondo amarillo fijo), usa pose
    return f'''<div class="s"><div class="marco D">
<div class="diag">MEGA RIFA FUSA · FUSAGASUGA 2026</div>
<div class="slab big">$2.000.000</div>
<div class="sub">Premio en efectivo si el numero<br>ganador esta vendido</div>
<div class="suta"><img src="{POSES[pose]}" alt=""></div>
<div class="foot">{titular} · <span class="mono">mega-rifa-fusa.vercel.app</span></div>
<div class="qrbox">{SVG}</div>
</div></div>'''

def st_E(acento, titular, pose):
    return f'''<div class="s"><div class="marco E">
<div class="k">PREMIO EN EFECTIVO</div>
<div class="slab big">$2.000.000</div>
<div class="cond">Si el numero ganador esta vendido · 1.000 numeros · $6.000</div>
<div class="row"><div class="qr">{SVG}</div><div class="suta"><img src="{POSES[pose]}" alt=""></div></div>
<div class="cta slab">{titular} · mega-rifa-fusa.vercel.app</div>
</div></div>'''

def st_F(acento, titular, pose):
    return f'''<div class="s"><div class="marco F">
<div class="k">MEGA RIFA FUSA · FUSAGASUGA</div>
<div class="slab big">$2.000.000</div>
<div class="cond">Si el numero ganador esta vendido · 1.000 numeros · $6.000</div>
<div class="qr">{SVG}</div>
<div class="cta slab">{titular}</div>
<div class="url">mega-rifa-fusa.vercel.app</div>
</div></div>'''

LAYOUTS = [st_A, st_B, st_C, st_D, st_E, st_F]
ACENTOS = ["var(--rojo)", "var(--amarillo)", "var(--azul)"]
POSE_LIST = list(POSES.keys())

# Elijo 20 combinaciones distintas (layout, acento, titular, pose) de forma deterministica
# que garantiza variedad: cada combinacion vecina difiere en al menos 2 ejes.
PLAN_20 = [
    (0, 0, 0, "senalando"),
    (1, 1, 1, "boleta"),
    (2, 2, 2, "pulgar"),
    (3, 0, 3, "celebrando"),
    (4, 1, 4, "saludando"),
    (5, 2, 0, "depie"),
    (0, 1, 1, "pulgar"),
    (1, 2, 2, "senalando"),
    (2, 0, 3, "saludando"),
    (3, 1, 4, "boleta"),
    (4, 2, 0, "celebrando"),
    (5, 0, 1, "senalando"),
    (0, 2, 2, "boleta"),
    (1, 0, 3, "depie"),
    (2, 1, 4, "celebrando"),
    (3, 2, 0, "pulgar"),
    (4, 0, 1, "senalando"),
    (5, 1, 2, "saludando"),
    (0, 2, 3, "saludando"),
    (1, 0, 4, "pulgar"),
]
assert len(PLAN_20) == 20
# chequeo de unicidad
assert len(set(PLAN_20)) == 20, "hay duplicados en PLAN_20"

cells = [LAYOUTS[L](ACENTOS[A], TITULARES[T], P) for (L, A, T, P) in PLAN_20]
# agrupar en paginas de 6 (ultima pagina queda con 2 celdas + 4 vacias)
paginas = []
for i in range(0, 20, 6):
    grupo = cells[i:i+6]
    while len(grupo) < 6:
        grupo.append('<div class="s" style="border:none;background:transparent"></div>')
    paginas.append('<section class="pg">' + "".join(grupo) + '</section>')
stickers_html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>20 QR stickers — Mega Rifa Fusa</title><style>{ST_CSS}</style></head><body>{"".join(paginas)}</body></html>"""
(AQUI / "qr-20-stickers.html").write_text(stickers_html, encoding="utf-8")
print("escrito qr-20-stickers.html (20 stickers, 4 hojas carta vertical)")

# ===================================================================
# 6 MEDIA HOJA — carta apaisada (11x8.5 in), partida en 2 verticales
# ===================================================================
# Cada pagina = 1056x816 px. Dos columnas de 528x816. Al cortar queda vertical 5.5x8.5 in.
MH_CSS = BASE + """
@page{size:11in 8.5in;margin:0}
.ph{width:1056px;height:816px;display:grid;grid-template-columns:528px 528px;position:relative;page-break-after:always;break-after:page}
.ph:last-child{page-break-after:auto;break-after:auto}
.ph .cut{position:absolute;left:528px;top:0;bottom:0;border-left:1.5px dashed #999}
.card{position:relative;overflow:hidden;padding:14px;height:816px}
.card .marco{position:absolute;inset:14px;border:7px solid var(--negro);overflow:hidden;display:flex;flex-direction:column}

/* --- MH-A: 2M dominante en banda superior roja, QR grande centrado, Suta a la derecha, pie amarillo --- */
.MA .top{background:var(--rojo);color:var(--crema);text-align:center;padding:10px 14px 14px;border-bottom:7px solid var(--negro)}
.MA .top .kick{font-size:15px;letter-spacing:4px;font-weight:700}
.MA .top .big{font-size:84px;line-height:.95;text-shadow:6px 6px 0 var(--negro);margin-top:2px;white-space:nowrap}
.MA .top .cond{font-size:15px;font-weight:700;letter-spacing:.5px;margin-top:3px}
.MA .mid{flex:1;display:flex;align-items:center;justify-content:center;gap:12px;padding:12px;background:var(--crema)}
.MA .qr{width:260px;height:260px;background:#fff;border:7px solid var(--negro);padding:7px}
.MA .suta{width:170px;height:280px;overflow:hidden;position:relative;background:#F8EFDE;border:5px solid var(--negro)}
.MA .suta img{position:absolute;left:-18px;top:0;height:280px;width:auto}
.MA .cta{text-align:center;font-size:26px;line-height:.98;color:var(--rojo);text-shadow:3px 3px 0 var(--negro);padding:4px 0}
.MA .pie{background:var(--amarillo);border-top:7px solid var(--negro);padding:8px 12px;text-align:center;font-size:13px;font-weight:700;letter-spacing:.8px}
.MA .pie .u{font-family:'Space Mono',monospace;font-size:15px}

/* --- MH-B: Fondo crema con banda amarilla, 2M en centro vertical con sombra crema sobre negro --- */
.MB{background:var(--crema)}
.MB .kick{text-align:center;background:var(--azul);color:var(--crema);padding:10px;letter-spacing:5px;font-weight:700;font-size:15px;border-bottom:7px solid var(--negro)}
.MB .hero{text-align:center;padding:28px 16px 10px;background:var(--amarillo);border-bottom:7px solid var(--negro)}
.MB .hero .mini{font-size:16px;font-weight:700;letter-spacing:3px}
.MB .hero .big{font-size:88px;line-height:.95;color:var(--negro);text-shadow:6px 6px 0 var(--crema);margin:4px 0 6px;white-space:nowrap}
.MB .hero .cond{font-size:15px;font-weight:700;line-height:1.2}
.MB .mid{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:14px;gap:10px;background:var(--crema)}
.MB .mid .qr{width:300px;height:300px;background:#fff;border:7px solid var(--negro);padding:6px}
.MB .mid .ctac{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center}
.MB .mid .ctac .cta{font-size:30px;line-height:.98;color:var(--rojo);text-shadow:3px 3px 0 var(--negro)}
.MB .mid .ctac .u{font-family:'Space Mono',monospace;font-size:17px;font-weight:700}
.MB .mid .ctac .data{font-size:13px;font-weight:700;line-height:1.3}
.MB .pie{background:var(--rojo);color:var(--crema);text-align:center;padding:8px;font-size:13px;font-weight:700;letter-spacing:1px;border-top:7px solid var(--negro)}

/* --- MH-C: 2M diagonal con Suta grande señalando, estilo cartel ruidoso --- */
.MC{background:var(--amarillo);position:relative}
.MC .brand{position:absolute;top:14px;left:0;right:0;text-align:center;font-size:14px;letter-spacing:4px;font-weight:700;color:var(--negro)}
.MC .big{position:absolute;top:52px;left:0;right:0;text-align:center;font-size:92px;line-height:.95;color:var(--rojo);text-shadow:7px 7px 0 var(--negro);transform:rotate(-3deg);white-space:nowrap}
.MC .cond{position:absolute;top:195px;left:0;right:0;text-align:center;font-size:14px;font-weight:700;line-height:1.2;padding:0 24px}
.MC .mid{position:absolute;top:245px;left:14px;right:14px;bottom:76px;display:flex;align-items:flex-end;gap:10px}
.MC .suta{flex:1;height:100%;overflow:hidden;position:relative}
.MC .suta img{position:absolute;left:50%;bottom:0;transform:translateX(-50%);height:112%;width:auto}
.MC .qrcol{display:flex;flex-direction:column;align-items:center;gap:6px}
.MC .qrcol .qr{width:220px;height:220px;background:#fff;border:7px solid var(--negro);padding:6px}
.MC .qrcol .lbl{background:var(--rojo);color:var(--crema);border:5px solid var(--negro);padding:4px 10px;font-size:18px;letter-spacing:2px}
.MC .pie{position:absolute;left:0;right:0;bottom:0;background:var(--negro);color:var(--crema);padding:10px;text-align:center;font-size:13px;font-weight:700;letter-spacing:1px}
.MC .pie .u{font-family:'Space Mono',monospace;font-size:16px}
"""

def mh_A(titular, pose):
    return f'''<div class="card"><div class="marco MA">
<div class="top"><div class="kick">PREMIO EN EFECTIVO</div><div class="slab big">$2.000.000</div><div class="cond">Si el numero ganador esta vendido</div></div>
<div class="mid"><div class="qr">{SVG}</div><div class="suta"><img src="{POSES[pose]}" alt=""></div></div>
<div class="cta slab" style="padding:8px">{titular}</div>
<div class="pie">1.000 numeros · $6.000 · Sorteo sab 5 dic · <span class="u">mega-rifa-fusa.vercel.app</span></div>
</div></div>'''

def mh_B(titular, pose):
    return f'''<div class="card"><div class="marco MB">
<div class="kick">MEGA RIFA FUSA · FUSAGASUGA 2026</div>
<div class="hero"><div class="mini">PREMIO EN EFECTIVO</div><div class="slab big">$2.000.000</div><div class="cond">Si el numero ganador esta vendido</div></div>
<div class="mid"><div class="qr">{SVG}</div><div class="ctac"><div class="cta slab">{titular}</div><div class="u">mega-rifa-fusa.vercel.app</div><div class="data">1.000 numeros · $6.000<br>Sorteo sab 5 dic, 10:30 p.m.<br>Loteria de Boyaca</div></div></div>
<div class="pie">Organizada por Santiago · The Ber Way · Solo mayores de 18</div>
</div></div>'''

def mh_C(titular, pose):
    return f'''<div class="card"><div class="marco MC">
<div class="brand">MEGA RIFA FUSA · FUSAGASUGA</div>
<div class="slab big">$2.000.000</div>
<div class="cond">Premio en efectivo si el numero ganador esta vendido<br>1.000 numeros · $6.000 · Sorteo sab 5 dic</div>
<div class="mid"><div class="suta"><img src="{POSES[pose]}" alt=""></div><div class="qrcol"><div class="qr">{SVG}</div><div class="lbl slab">{titular}</div></div></div>
<div class="pie"><span class="u">mega-rifa-fusa.vercel.app</span> · Organizada por Santiago · The Ber Way</div>
</div></div>'''

# 6 piezas unicas: 3 layouts x 2 poses/titulares distintos
PLAN_6 = [
    (mh_A, 0, "senalando"),
    (mh_B, 1, "boleta"),
    (mh_C, 2, "pulgar"),
    (mh_A, 3, "celebrando"),
    (mh_B, 4, "saludando"),
    (mh_C, 0, "depie"),
]
cards = [fn(TITULARES[t], p) for (fn, t, p) in PLAN_6]
paginas_mh = []
for i in range(0, 6, 2):
    izq, der = cards[i], cards[i+1]
    paginas_mh.append(f'<section class="ph">{izq}{der}<div class="cut"></div></section>')
mh_html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>6 QR media hoja — Mega Rifa Fusa</title><style>{MH_CSS}</style></head><body>{"".join(paginas_mh)}</body></html>"""
(AQUI / "qr-6-media-hoja.html").write_text(mh_html, encoding="utf-8")
print("escrito qr-6-media-hoja.html (6 piezas, 3 hojas carta apaisada)")
