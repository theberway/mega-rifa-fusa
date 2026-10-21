# Construye las piezas v2 (2M dominante, menos texto, composicion asimetrica).
# Rutas v2:
#   Rediseño Fase A: pisa `semana-1/15-oct-quincena/`, `semana-1/17-oct-encuesta/`,
#     `semana-2/20-oct-como-se-gana/`, `semana-2/22-oct-como-se-verifica/`, `semana-2/23-oct-frase-del-dia/`
#   Nueva tanda Fase B: carpetas `semana-3/DD-{slug}/feed.png` + `historia.png`
#   NZ: `semana-3/NZ-sofia/feed-EN.png` + `historia-EN.png`
# Uso (Git Bash):  /c/Users/Santiago/AppData/Local/Python/bin/python.exe construir-v2.py [filtro]

import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CHROME = r"C:/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
URL = "mega-rifa-fusa.vercel.app"
FIRMA = "Organizada por Santiago · The Ber Way"
FIRMA_NZ = "Run by Santiago · The Ber Way · DM @megarifafusa"
COND = "Si el número ganador está vendido"
COND_EN = "If the winning number was sold and paid in NZ"

# ---------- CSS v2 ----------
CSS = r"""
/* v2: 2M dominante, borde negro grueso, sombras duras planas, composicion asimetrica */
.lienzo { padding: 40px; gap: 18px; position: relative; }
.historia.lienzo { padding: 60px 56px; gap: 24px; }
.bg-crema { background: var(--crema); color: var(--negro); }
.bg-rojo  { background: var(--rojo);  color: var(--crema); }
.bg-am    { background: var(--amarillo); color: var(--negro); }
.bg-azul  { background: var(--azul);  color: var(--crema); }
.bg-neg   { background: var(--negro); color: var(--crema); }

.tope { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.chip { font-family: 'Space Mono', monospace; font-weight: 700; font-size: 24px; letter-spacing: 3px; padding: 7px 16px; border: 5px solid var(--negro); background: var(--crema); color: var(--rojo); white-space: nowrap; }
.chip.oscuro { background: var(--negro); color: var(--amarillo); border-color: var(--negro); }
.logoh { font-family: 'Alfa Slab One', serif; font-size: 34px; line-height: 1; white-space: nowrap; }
.bg-rojo .logoh, .bg-azul .logoh, .bg-neg .logoh { color: var(--crema); text-shadow: 3px 3px 0 var(--negro); }
.bg-am .logoh, .bg-crema .logoh { color: var(--rojo); text-shadow: 3px 3px 0 var(--negro); }

/* === Bloque PREMIO (2M dominante) === */
.premio {
  border: 10px solid var(--negro);
  padding: 24px 30px 26px;
  display: flex; flex-direction: column; justify-content: center;
  box-shadow: 10px 10px 0 var(--negro);
}
.premio .eyebrow { font-family: 'Space Mono', monospace; font-weight: 700; font-size: 24px; letter-spacing: 4px; text-transform: uppercase; }
.premio .cifra { font-family: 'Alfa Slab One', serif; line-height: 0.95; white-space: nowrap; }
.premio .cond { font-weight: 700; margin-top: 10px; }
.premio.rojo { background: var(--rojo); color: var(--crema); }
.premio.rojo .cifra { color: var(--crema); text-shadow: 7px 7px 0 var(--negro); }
.premio.rojo .eyebrow { color: var(--amarillo); }
.premio.am { background: var(--amarillo); color: var(--negro); }
.premio.am .cifra { color: var(--negro); }
.premio.am .eyebrow { color: var(--negro); opacity: .78; }
.premio.azul { background: var(--azul); color: var(--crema); }
.premio.azul .cifra { color: var(--amarillo); text-shadow: 7px 7px 0 var(--negro); }
.premio.azul .eyebrow { color: var(--crema); opacity: .9; }

.rot-m3 { transform: rotate(-3deg); transform-origin: center; }
.rot-m5 { transform: rotate(-5deg); transform-origin: center; }
.rot-p2 { transform: rotate(2deg); transform-origin: center; }

/* QR stacked card (QR falso: cuadricula) */
.qr-stack { position: relative; width: 240px; height: 240px; flex-shrink: 0; }
.qr-stack::before, .qr-stack::after { content:""; position: absolute; inset: 0; border: 6px solid var(--negro); background: var(--crema); }
.qr-stack::before { transform: translate(14px, 14px); }
.qr-stack::after  { transform: translate(7px, 7px); }
.qr-stack .qr { position: relative; z-index: 2; width: 100%; height: 100%; border: 6px solid var(--negro); background:
  repeating-linear-gradient(0deg, var(--negro) 0 10px, transparent 10px 20px),
  repeating-linear-gradient(90deg, var(--negro) 0 10px, transparent 10px 20px), var(--crema);
  background-blend-mode: multiply;
}
.qr-stack.sm { width: 190px; height: 190px; }
.qr-stack.lg { width: 320px; height: 320px; }

/* panel Suta — imagen contain, centrada; para huecos usar aspect-ratio o panel más cuadrado */
.panel-suta { background: var(--crema); border: 8px solid var(--negro); position: relative; overflow: hidden; align-self: stretch; display: flex; align-items: center; justify-content: center; }
.panel-suta img { display: block; width: 100%; height: 100%; object-fit: contain; object-position: center center; }
.panel-suta.cover img { object-fit: cover; object-position: center top; }
.panel-suta.escape img { transform: scale(1.08); }
.panel-suta .flot { position: absolute; z-index: 3; }

/* banda inferior datos */
.datos { background: var(--negro); color: var(--crema); border: 8px solid var(--negro); padding: 12px 22px; text-align: center; }
.datos .slab { font-family: 'Alfa Slab One', serif; color: var(--amarillo); font-size: 30px; line-height: 1.0; }
.datos .mono { font-family: 'Space Mono', monospace; font-weight: 700; font-size: 18px; margin-top: 4px; }
.historia .datos .slab { font-size: 46px; }
.historia .datos .mono { font-size: 26px; }

/* CTA */
.cta { background: var(--crema); border: 8px solid var(--negro); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; gap: 16px; box-shadow: 8px 8px 0 var(--negro); }
.cta .slab { font-family: 'Alfa Slab One', serif; font-size: 34px; color: var(--rojo); white-space: nowrap; }
.cta .mono { font-family: 'Space Mono', monospace; font-weight: 700; font-size: 22px; color: var(--negro); white-space: nowrap; }
.historia .cta .slab { font-size: 42px; }
.historia .cta .mono { font-size: 26px; }

/* firma */
.firma { font-size: 22px; font-weight: 600; text-align: center; letter-spacing: 1px; }
.historia .firma { font-size: 28px; }

/* layout helpers */
.crece { flex: 1; min-height: 0; }
.fila { display: flex; gap: 20px; }
.col  { display: flex; flex-direction: column; gap: 18px; }

/* diagonal sash — centrado, rotación suave para no recortarse */
.sash { position: absolute; top: 48px; left: 0; width: 100%; padding: 18px 40px; transform: rotate(-3deg); transform-origin: center center; background: var(--rojo); color: var(--crema); border-top: 10px solid var(--negro); border-bottom: 10px solid var(--negro); text-align: center; font-family: 'Alfa Slab One', serif; letter-spacing: 2px; box-shadow: 0 8px 0 var(--negro); }

/* boleta troquelada */
.ticket {
  background: var(--crema); color: var(--negro); border: 10px solid var(--negro);
  background-image:
    radial-gradient(circle at 0 50%, transparent 18px, var(--negro) 18px, var(--negro) 24px, var(--crema) 24px),
    radial-gradient(circle at 100% 50%, transparent 18px, var(--negro) 18px, var(--negro) 24px, var(--crema) 24px);
  padding: 24px 40px 28px;
  position: relative;
  box-shadow: 10px 10px 0 var(--negro);
}
.ticket::before { content:""; position: absolute; left: 32%; top: 10%; bottom: 10%; width: 0; border-left: 6px dashed var(--negro); }

/* calabaza + murcielago siluetas (SVG embebido via mask) */
.pumpkin, .bat { pointer-events: none; }

/* titulares genericos */
.titular { font-family: 'Alfa Slab One', serif; line-height: 0.96; }
.titular.rojo-txt { color: var(--rojo); text-shadow: 6px 6px 0 var(--negro); }
.titular.crema-txt { color: var(--crema); text-shadow: 6px 6px 0 var(--negro); }
.titular.negro-txt { color: var(--negro); }
.sub { font-size: 34px; font-weight: 600; line-height: 1.3; }
.historia .sub { font-size: 44px; }
.caps { text-transform: uppercase; letter-spacing: 3px; font-weight: 700; }

/* comillas gigantes — SVG garantiza tamaño y forma */
.quote-svg { display: block; }

/* ficha ejemplo */
.ejemplo-tag { font-family: 'Space Mono', monospace; background: var(--rojo); color: var(--crema); border: 5px solid var(--negro); padding: 3px 14px; font-size: 22px; letter-spacing: 3px; }

/* digitos premio mayor */
.dig { border: 7px solid var(--negro); display: flex; align-items: center; justify-content: center; font-family: 'Space Mono', monospace; font-weight: 700; }

/* encuesta hueco */
.hueco-sticker { border: 6px dashed var(--negro); background: rgba(255,244,214,.5); color: var(--negro); padding: 18px 24px; text-align: center; font-family: 'Space Mono', monospace; font-size: 22px; letter-spacing: 2px; }

/* cinta "caution tape" diagonal (barra amarilla+negra con rotación) */
.caution-tape { position: absolute; top: 40px; left: -8%; width: 116%; padding: 18px 40px; transform: rotate(-4deg); transform-origin: center; font-family: 'Alfa Slab One', serif; letter-spacing: 2px; color: var(--negro); background: repeating-linear-gradient(45deg, var(--amarillo) 0 24px, var(--negro) 24px 36px, var(--amarillo) 36px 60px, var(--negro) 60px 72px); border-top: 8px solid var(--negro); border-bottom: 8px solid var(--negro); text-align: center; text-shadow: 2px 2px 0 var(--amarillo); box-shadow: 0 8px 0 rgba(0,0,0,.2); white-space: nowrap; overflow: hidden; }

/* sellos / badges rotados */
.sello { position: absolute; display: inline-flex; align-items: center; justify-content: center; text-align: center; font-family: 'Alfa Slab One', serif; border: 6px solid var(--negro); padding: 10px 18px; box-shadow: 6px 6px 0 var(--negro); z-index: 4; }

/* globos de doodle (speech bubble) */
.bocadillo { position: relative; background: var(--crema); border: 8px solid var(--negro); padding: 18px 24px; border-radius: 24px; font-family: 'Archivo Narrow', sans-serif; font-weight: 700; box-shadow: 8px 8px 0 var(--negro); }
.bocadillo::after { content:""; position: absolute; bottom: -22px; left: 50px; width: 30px; height: 30px; background: var(--crema); border-right: 8px solid var(--negro); border-bottom: 8px solid var(--negro); transform: rotate(45deg); }

/* pantalla error 404 */
.pantalla { background: var(--negro); color: var(--amarillo); border: 8px solid var(--negro); padding: 24px 28px; font-family: 'Space Mono', monospace; position: relative; box-shadow: 10px 10px 0 var(--rojo); }
.pantalla::before { content:""; position: absolute; top: 6px; left: 10px; display: flex; gap: 8px; }
.pantalla .barra { display: flex; gap: 6px; margin-bottom: 10px; }
.pantalla .dot { width: 14px; height: 14px; border-radius: 50%; }
.pantalla .d1 { background: var(--rojo); } .pantalla .d2 { background: var(--amarillo); } .pantalla .d3 { background: #4EC063; }

/* separador rayas de peligro vertical */
.rayas-v { background: repeating-linear-gradient(135deg, var(--negro) 0 14px, var(--amarillo) 14px 28px); height: 100%; width: 24px; }

/* zodiaco signo item */
.signo { display: flex; align-items: center; gap: 10px; background: var(--crema); border: 5px solid var(--negro); padding: 6px 12px; box-shadow: 4px 4px 0 var(--negro); }
.signo .glifo { font-family: 'Alfa Slab One', serif; font-size: 28px; color: var(--rojo); text-shadow: 2px 2px 0 var(--negro); line-height: 1; min-width: 32px; }
.signo .nombre { font-family: 'Space Mono', monospace; font-size: 13px; letter-spacing: 1.5px; font-weight: 700; text-transform: uppercase; }
.signo .numero { margin-left: auto; font-family: 'Alfa Slab One', serif; font-size: 22px; color: var(--rojo); line-height: 1; }
"""

SVG_PUMPKIN = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width:100%;height:100%"><path fill="#1A1A1A" d="M50 15c-2 0-3 4-3 10v6c-10-4-24-2-30 7-7 11-3 32 8 42 7 7 17 10 25 10s18-3 25-10c11-10 15-31 8-42-6-9-20-11-30-7v-6c0-6-1-10-3-10zm-14 36c3-4 7-5 10-3-1 5-5 8-10 7v-4zm28 0v4c-5 1-9-2-10-7 3-2 7-1 10 3zm-14 10c4 0 7 2 7 5s-3 5-7 5-7-2-7-5 3-5 7-5z"/></svg>'
SVG_BAT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60" style="width:100%;height:100%"><path fill="#1A1A1A" d="M60 10c-3 0-5 2-6 5-4-6-12-10-20-10-4 0-8 1-12 3 3 1 6 4 7 8-5 1-9 5-9 10 4-2 9-2 13 1-3 4-4 10-2 15 4-6 11-10 19-10 6 0 10 3 10 6 0-3 4-6 10-6 8 0 15 4 19 10 2-5 1-11-2-15 4-3 9-3 13-1 0-5-4-9-9-10 1-4 4-7 7-8-4-2-8-3-12-3-8 0-16 4-20 10-1-3-3-5-6-5z"/></svg>'
SVG_RAYO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 100" style="width:100%;height:100%"><path fill="#F2B705" stroke="#1A1A1A" stroke-width="4" stroke-linejoin="round" d="M22 2 L4 54 L18 54 L10 98 L36 42 L22 42 Z"/></svg>'
SVG_ESTRELLA = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width:100%;height:100%"><path fill="#F2B705" stroke="#1A1A1A" stroke-width="5" stroke-linejoin="round" d="M50 4 L58 36 L92 36 L64 56 L74 90 L50 70 L26 90 L36 56 L8 36 L42 36 Z"/></svg>'
SVG_UFO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 90" style="width:100%;height:100%"><ellipse cx="70" cy="60" rx="60" ry="18" fill="#1A1A1A"/><ellipse cx="70" cy="56" rx="60" ry="14" fill="#C1121F" stroke="#1A1A1A" stroke-width="4"/><path d="M30 56 Q70 10 110 56" fill="#F2B705" stroke="#1A1A1A" stroke-width="4"/><circle cx="50" cy="38" r="4" fill="#1A1A1A"/><circle cx="70" cy="30" r="4" fill="#1A1A1A"/><circle cx="90" cy="38" r="4" fill="#1A1A1A"/></svg>'
SVG_ARANA = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width:100%;height:100%"><g stroke="#1A1A1A" stroke-width="5" fill="none" stroke-linecap="round"><path d="M50 50 L10 20"/><path d="M50 50 L10 40"/><path d="M50 50 L10 60"/><path d="M50 50 L10 80"/><path d="M50 50 L90 20"/><path d="M50 50 L90 40"/><path d="M50 50 L90 60"/><path d="M50 50 L90 80"/></g><circle cx="50" cy="50" r="22" fill="#1A1A1A"/><circle cx="44" cy="46" r="4" fill="#C1121F"/><circle cx="56" cy="46" r="4" fill="#C1121F"/></svg>'
SVG_SOMBRERO_BRUJA = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width:100%;height:100%"><path fill="#1A1A1A" d="M50 10 L72 80 L28 80 Z"/><ellipse cx="50" cy="80" rx="46" ry="10" fill="#1A1A1A"/><path d="M30 60 Q40 55 55 62" fill="none" stroke="#F2B705" stroke-width="4"/><circle cx="50" cy="30" r="5" fill="#F2B705"/></svg>'
SVG_LANA_FLECHA = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100" style="width:100%;height:100%"><path d="M20 50 Q60 10 100 40 Q140 70 180 30" fill="none" stroke="#1A1A1A" stroke-width="6" stroke-dasharray="4 8"/><polygon points="180,30 162,20 172,38" fill="#1A1A1A"/></svg>'

def quote_svg(tam=200, color="#F2B705"):
    """Comilla doble gigante como SVG inline (dos trapecios sólidos), con sombra dura negra."""
    # Dos "lágrimas" sólidas con la forma clásica de comilla curva de slab-serif
    return f'''<svg class="quote-svg" width="{tam}" height="{int(tam*0.82)}" viewBox="0 0 200 164" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(10,10)"><path fill="#1A1A1A" d="M8 20 L48 20 L48 70 L28 140 L0 140 L18 80 L8 80 Z M78 20 L118 20 L118 70 L98 140 L70 140 L88 80 L78 80 Z"/></g>
  <path fill="{color}" stroke="#1A1A1A" stroke-width="5" stroke-linejoin="round" d="M8 20 L48 20 L48 70 L28 140 L0 140 L18 80 L8 80 Z M78 20 L118 20 L118 70 L98 140 L70 140 L88 80 L78 80 Z"/>
</svg>'''

# ---------- Helpers de contenido ----------
def doc(cuerpo, extra="", clase_lienzo="feed bg-crema"):
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="../marca.css"><style>{CSS}{extra}</style></head>
<body><div class="lienzo {clase_lienzo}">{cuerpo}</div></body></html>"""

def qr(tam="md"):
    cls = {"sm":"qr-stack sm","md":"qr-stack","lg":"qr-stack lg"}[tam]
    return f'<div class="{cls}"><div class="qr"></div></div>'

def suta(pose, cls="", estilo=""):
    ext = ".webp" if pose == "1-de-pie" else ".jpg"
    return f'<div class="panel-suta {cls}" style="{estilo}"><img src="../../_assets/{pose}{ext}" alt="Sutá"></div>'

def chip(txt, oscuro=False):
    return f'<span class="chip{" oscuro" if oscuro else ""}">{txt}</span>'

def logoh(txt="MEGA RIFA FUSA"):
    return f'<span class="logoh">{txt}</span>'

def tope(chip_txt, oscuro=False, logo="MEGA RIFA FUSA"):
    return f'<div class="tope">{chip(chip_txt, oscuro)}{logoh(logo)}</div>'

def tope_mono(mono_txt, chip_txt, oscuro=False):
    return f'<div class="tope"><span class="mono" style="font-family:\'Space Mono\',monospace;font-weight:700;font-size:24px;letter-spacing:4px">{mono_txt}</span>{chip(chip_txt, oscuro)}</div>'

def premio(color="rojo", tam_feed=False, tam=None, eyebrow="PREMIO EN EFECTIVO", cond=COND, rot=""):
    """Bloque dominante $2.000.000. Si tam=None, usa defaults seguros (ancho completo)."""
    f_cifra = tam or (140 if tam_feed else 150)
    f_eye = 22 if tam_feed else 28
    f_cond = 20 if tam_feed else 28
    return f"""<div class="premio {color} {rot}">
  <div class="eyebrow" style="font-size:{f_eye}px">{eyebrow}</div>
  <div class="cifra" style="font-size:{f_cifra}px">$2.000.000</div>
  <div class="cond" style="font-size:{f_cond}px">{cond}</div>
</div>"""

def premio_nz(color="rojo", tam_feed=False, tam=None, eyebrow="CASH PRIZE IN NZ"):
    f_cifra = tam or (140 if tam_feed else 150)
    f_eye = 22 if tam_feed else 28
    f_cond = 20 if tam_feed else 28
    cond = COND_EN
    return f"""<div class="premio {color}">
  <div class="eyebrow" style="font-size:{f_eye}px">{eyebrow}</div>
  <div class="cifra" style="font-size:{f_cifra}px">NZD 1,000</div>
  <div class="cond" style="font-size:{f_cond}px">{cond}</div>
</div>"""

def datos_pie(l1="1.000 números · $6.000", l2="Sorteo sáb 5 dic, 10:30 p.m. · Lotería de Boyacá"):
    return f'<div class="datos"><div class="slab">{l1}</div><div class="mono">{l2}</div></div>'

def cta(txt="ESCOGE EL TUYO →", url=URL):
    return f'<div class="cta"><span class="slab">{txt}</span><span class="mono">{url}</span></div>'

def firma(txt=None):
    return f'<div class="firma">{txt or FIRMA}</div>'

# =====================================================================
# LAYOUT L1 — Billboard (banda 2M arriba grande, Sutá + QR abajo)
# =====================================================================
def L1_feed(chip_txt, premio_bloque, cta_txt, pose="4-senalando", oscuro=False, firma_txt=None):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="fila crece" style="align-items:stretch;gap:18px">
  {suta(pose, cls="cover", estilo="width:360px")}
  <div class="col crece" style="justify-content:space-between">
    <div style="display:flex;justify-content:flex-end">{qr("md")}</div>
    {datos_pie()}
  </div>
</div>
{cta(cta_txt)}{firma(firma_txt)}"""
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def L1_historia(chip_txt, premio_bloque, cta_txt, pose="4-senalando", oscuro=False, firma_txt=None):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="fila crece" style="gap:22px;align-items:stretch">
  {suta(pose, cls="cover", estilo="flex:1")}
  <div class="col" style="width:340px;justify-content:center;align-items:center;gap:30px">
    {qr("lg")}
    <div style="font-family:'Alfa Slab One',serif;font-size:46px;color:var(--rojo);text-shadow:5px 5px 0 var(--negro);text-align:center;line-height:1">TU NÚMERO<br>TE ESPERA</div>
  </div>
</div>
{datos_pie()}{cta(cta_txt)}{firma(firma_txt)}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# =====================================================================
# LAYOUT L2 — Split editorial (premio arriba full-width, titular+Sutá abajo)
# =====================================================================
def L2_feed(chip_txt, premio_bloque, titular_html, pose="2-saludando", oscuro=False):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="fila crece" style="gap:18px">
  <div class="col crece" style="justify-content:center">{titular_html}</div>
  {suta(pose, cls="escape", estilo="width:300px;padding:14px 10px 0")}
</div>
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def L2_historia(chip_txt, premio_bloque, titular_html, pose="2-saludando", oscuro=False, extra_abajo=""):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="col" style="gap:14px">{titular_html}</div>
<div class="fila crece" style="gap:20px">
  {suta(pose, cls="escape", estilo="flex:1;padding:20px 14px 0")}
  <div class="col" style="width:340px;justify-content:space-between;align-items:center">
    {qr("lg")}
    {extra_abajo or '<div class="datos" style="width:100%"><div class="slab">1.000 números</div><div class="mono">$6.000 cada uno</div></div>'}
  </div>
</div>
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# =====================================================================
# LAYOUT L3 — Diagonal / Sash
# =====================================================================
def L3_feed(sash_txt, premio_bloque, cuerpo_centro, pose="6-celebrando"):
    cuerpo = f"""
<div class="sash" style="font-size:34px">{sash_txt}</div>
<div style="height:70px"></div>
{premio_bloque}
<div class="fila crece" style="gap:18px">
  <div class="col crece" style="justify-content:center">{cuerpo_centro}</div>
  {suta(pose, cls="escape", estilo="width:300px;padding:16px 10px 0")}
</div>
{datos_pie()}{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-am")

def L3_historia(sash_txt, premio_bloque, cuerpo_centro, pose="6-celebrando"):
    cuerpo = f"""
<div class="sash" style="font-size:40px">{sash_txt}</div>
<div style="height:90px"></div>
{premio_bloque}
{cuerpo_centro}
{suta(pose, cls="crece escape", estilo="padding:20px 20px 0;min-height:400px")}
{datos_pie()}{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-am")

# =====================================================================
# LAYOUT L4 — Ticket troquelado (premio arriba full-width, boleta Nº abajo)
# =====================================================================
def L4_feed(chip_txt, numero_tit, premio_bloque, texto_abajo, pose="3-con-la-boleta", oscuro=False):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="ticket crece" style="display:flex;align-items:center;gap:20px">
  <div style="flex:0 0 38%;text-align:center">
    <div class="mono" style="font-size:22px;letter-spacing:3px">BOLETA Nº</div>
    <div class="slab" style="font-size:140px;line-height:1;color:var(--rojo);text-shadow:6px 6px 0 var(--negro)">{numero_tit}</div>
    <div class="mono" style="font-size:18px;margin-top:4px">tu número</div>
  </div>
  <div style="flex:1;font-size:26px;font-weight:600;line-height:1.3">{texto_abajo}</div>
</div>
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def L4_historia(chip_txt, numero_tit, premio_bloque, texto_abajo, pose="3-con-la-boleta", oscuro=False):
    cuerpo = f"""
{tope(chip_txt, oscuro)}
{premio_bloque}
<div class="ticket" style="padding:28px 50px 32px">
  <div class="mono" style="font-size:26px;letter-spacing:3px;text-align:center">BOLETA Nº</div>
  <div class="slab" style="font-size:190px;line-height:0.95;color:var(--rojo);text-shadow:9px 9px 0 var(--negro);text-align:center">{numero_tit}</div>
  <div class="mono" style="font-size:22px;text-align:center;margin-top:4px">tu número para el 5 de diciembre</div>
</div>
<div style="font-size:36px;font-weight:600;line-height:1.3;text-align:center">{texto_abajo}</div>
{suta(pose, cls="crece escape", estilo="padding:20px 20px 0;min-height:280px")}
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# =====================================================================
# HALLOWEEN — amarillo+negro de noche con calabazas/murcielagos en silueta
# =====================================================================
def HAL_adornos(pos_feed=True):
    """Decoraciones negras (calabaza, murciélagos) en esquinas"""
    if pos_feed:
        return f"""
<div style="position:absolute;top:420px;left:-20px;width:110px;height:110px;transform:rotate(-15deg);z-index:1">{SVG_PUMPKIN}</div>
<div style="position:absolute;top:480px;right:30px;width:140px;height:70px;transform:rotate(8deg);opacity:.9;z-index:1">{SVG_BAT}</div>
<div style="position:absolute;top:60px;right:-10px;width:80px;height:40px;transform:rotate(-10deg);opacity:.75;z-index:1">{SVG_BAT}</div>"""
    else:
        return f"""
<div style="position:absolute;top:260px;left:-30px;width:130px;height:130px;transform:rotate(-12deg);z-index:1">{SVG_PUMPKIN}</div>
<div style="position:absolute;top:340px;right:40px;width:180px;height:90px;transform:rotate(10deg);z-index:1">{SVG_BAT}</div>
<div style="position:absolute;top:900px;right:-20px;width:160px;height:80px;transform:rotate(-6deg);opacity:.85;z-index:1">{SVG_BAT}</div>
<div style="position:absolute;top:1200px;left:30px;width:110px;height:110px;transform:rotate(14deg);opacity:.85;z-index:1">{SVG_PUMPKIN}</div>"""

def HAL_feed(chip_txt, premio_bloque, titular_html, cta_txt="ESCOGE EL TUYO →"):
    cuerpo = f"""
{HAL_adornos(True)}
<div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:12px;flex:1">
  {tope(chip_txt, oscuro=True)}
  {titular_html}
  {premio_bloque}
  <div class="fila crece" style="gap:16px;align-items:stretch">
    {suta("4-senalando", cls="cover", estilo="width:300px")}
    <div class="col crece" style="justify-content:space-between;gap:12px">
      <div style="display:flex;justify-content:flex-end">{qr("sm")}</div>
      {datos_pie()}
    </div>
  </div>
  {cta(cta_txt)}{firma()}
</div>"""
    return doc(cuerpo, clase_lienzo="feed bg-am")

def HAL_historia(chip_txt, premio_bloque, titular_html, cta_txt="ESCOGE EL TUYO →"):
    cuerpo = f"""
{HAL_adornos(False)}
<div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:22px;flex:1">
  {tope(chip_txt, oscuro=True)}
  {titular_html}
  {premio_bloque}
  <div class="fila crece" style="gap:22px;align-items:stretch">
    {suta("6-celebrando", cls="cover", estilo="flex:1")}
    <div class="col" style="width:340px;justify-content:center;align-items:center;gap:28px">
      {qr("lg")}
      <div style="font-family:'Alfa Slab One',serif;font-size:46px;color:var(--rojo);text-shadow:5px 5px 0 var(--negro);text-align:center;line-height:1">TU NÚMERO<br>DE LA SUERTE</div>
    </div>
  </div>
  {datos_pie()}{cta(cta_txt)}{firma()}
</div>"""
    return doc(cuerpo, clase_lienzo="historia bg-am")

# =====================================================================
# PIEZAS — Fase A (rediseño 15–23 oct)
# =====================================================================

# ---------- 15-oct quincena (L1 billboard) ----------
def feed_15_quincena():
    return L1_feed("QUINCENA", premio("rojo", tam_feed=True), "DATE EL GUSTO →", pose="3-con-la-boleta")

def historia_15_quincena():
    return L1_historia("QUINCENA", premio("rojo"), "DATE EL GUSTO →", pose="3-con-la-boleta")

# ---------- 17-oct encuesta — VS pop-art, dos cards enfrentadas ----------
def vs_card(color_cls, titulo, sub, rot):
    return f'''<div class="{color_cls}" style="border:10px solid var(--negro);padding:28px 24px;box-shadow:10px 10px 0 var(--negro);transform:rotate({rot}deg);text-align:center;flex:1">
  <div style="font-family:'Space Mono',monospace;font-size:20px;letter-spacing:3px;font-weight:700;opacity:.8">{sub}</div>
  <div style="font-family:'Alfa Slab One',serif;font-size:76px;line-height:0.95;margin-top:8px">{titulo}</div>
</div>'''

def feed_17_encuesta():
    vs_block = f'''<div style="display:flex;gap:14px;align-items:center;justify-content:center">
  {vs_card("bg-am", "CUMPLE<br>AÑOS", "OPCIÓN A", -3)}
  <div style="font-family:'Alfa Slab One',serif;font-size:78px;color:var(--rojo);text-shadow:5px 5px 0 var(--negro);line-height:1">VS</div>
  {vs_card("bg-azul", "CÉ<br>DULA", "OPCIÓN B", 3)}
</div>'''
    cuerpo = f'''
{tope("ENCUESTA · VOTA YA")}
<div class="titular rojo-txt" style="font-size:84px;line-height:0.95">¿CON<br>QUÉ ESCOGES?</div>
{vs_block}
<div class="crece" style="display:flex;align-items:flex-end;gap:14px">
  <div class="sub crece" style="font-size:28px">Comenta <b>A</b> o <b>B</b>, dinos cuál. Y si todavía no tienes el tuyo…</div>
  {suta("2-saludando", cls="cover", estilo="width:180px;height:260px")}
</div>
{premio("rojo", tam_feed=True, tam=110)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_17_encuesta():
    vs_block = f'''<div style="display:flex;gap:14px;align-items:center;justify-content:center">
  {vs_card("bg-am", "CUMPLE<br>AÑOS", "OPCIÓN A", -3)}
  <div style="font-family:'Alfa Slab One',serif;font-size:96px;color:var(--rojo);text-shadow:6px 6px 0 var(--negro);line-height:1">VS</div>
  {vs_card("bg-azul", "CÉ<br>DULA", "OPCIÓN B", 3)}
</div>'''
    hueco = '<div class="hueco-sticker" style="width:100%">Pon aquí el sticker de encuesta de IG<br>«Mi cumpleaños» · «Mi cédula»</div>'
    cuerpo = f'''
{tope("ENCUESTA · VOTA YA")}
<div class="titular rojo-txt" style="font-size:120px;line-height:0.95">¿CON QUÉ<br>ESCOGES?</div>
{vs_block}
{hueco}
<div class="crece"></div>
{premio("rojo", tam=140)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- 20-oct cómo se gana (L2 azul con bloque ejemplo) ----------
def gana_bloque_v2(tam):
    digs = "".join(f'<div class="dig" style="width:{tam}px;height:{int(tam*1.25)}px;background:{"var(--amarillo)" if i else "var(--crema)"};font-size:{int(tam*0.78)}px;color:var(--negro)">{d}</div>' for i, d in enumerate("4217"))
    return f"""<div style="background:var(--crema);border:8px solid var(--negro);padding:22px 26px;position:relative;color:var(--negro);box-shadow:8px 8px 0 var(--negro)">
  <span class="ejemplo-tag" style="position:absolute;top:-20px;right:22px">EJEMPLO</span>
  <div class="caps" style="font-size:22px">Premio mayor de la Lotería de Boyacá</div>
  <div style="display:flex;gap:12px;margin-top:14px;align-items:center">
    {digs}
    <span class="slab" style="font-size:{int(tam*0.6)}px;color:var(--rojo);margin:0 10px">→</span>
    <div><div class="caps" style="font-size:20px">Gana el</div><div class="mono" style="font-size:{int(tam*0.95)}px;line-height:1;color:var(--rojo)">217</div></div>
  </div>
</div>"""

def feed_20_gana():
    tit = """<div class="titular rojo-txt" style="font-size:70px">ÚLTIMAS<br>3 CIFRAS</div>
<div class="sub" style="font-size:26px">Del premio mayor de la Lotería de Boyacá del sáb 5 dic. Transparente y público.</div>"""
    return L2_feed("CÓMO SE GANA", premio("azul", tam_feed=True), tit, pose="4-senalando")

def historia_20_gana():
    cuerpo_pre = """<div class="titular rojo-txt" style="font-size:100px">GANAN LAS<br>ÚLTIMAS<br>3 CIFRAS</div>
<div class="sub">Del premio mayor de la Lotería de Boyacá del sáb 5 dic. Transparente y público.</div>"""
    cuerpo = f"""
{tope("CÓMO SE GANA")}
{premio("azul", eyebrow="PREMIO EN EFECTIVO")}
{cuerpo_pre}
{gana_bloque_v2(120)}
<div class="crece"></div>
{datos_pie("Sáb 5 dic · 10:30 p.m.", "Premio $2.000.000 si el número ganador está vendido")}{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- 22-oct cómo se verifica (L1 billboard, azul, con ficha) ----------
def ficha_v2(tam):
    return f"""<div style="background:#fff;border:8px solid var(--negro);padding:22px 26px;position:relative;color:var(--negro);box-shadow:8px 8px 0 var(--negro)">
  <span class="ejemplo-tag" style="position:absolute;top:-20px;right:22px">EJEMPLO</span>
  <div style="display:flex;align-items:center;gap:24px">
    <div class="mono" style="font-size:{tam}px;line-height:1;color:var(--rojo)">214</div>
    <div><span class="mono" style="background:var(--azul);color:var(--crema);padding:6px 16px;font-size:{tam//4}px;letter-spacing:3px">PAGADO</span>
    <div style="font-size:{tam//3}px;font-weight:700;margin-top:12px">Dav*** G.</div></div>
  </div>
  <div style="font-size:24px;margin-top:12px;line-height:1.3">Quien no quiere salir aparece como <b>Reservado</b>. Nunca nombre completo ni teléfono.</div>
</div>"""

def feed_22_verifica():
    cuerpo = f"""
{tope("TODO A LA VISTA")}
{premio("azul", tam_feed=True, eyebrow="UN NÚMERO, UN DUEÑO")}
<div class="crece" style="display:flex;align-items:flex-end;gap:18px">
  <div style="flex:1">{ficha_v2(90)}</div>
  {suta("1-de-pie", cls="escape", estilo="width:220px;height:340px;padding:12px 8px 0")}
</div>
{cta("MÍRALO EN VIVO →")}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_22_verifica():
    cuerpo = f"""
{tope("TODO A LA VISTA")}
<div class="titular rojo-txt" style="font-size:120px">UN NÚMERO,<br>UN DUEÑO</div>
{premio("azul")}
{ficha_v2(130)}
{suta("4-senalando", cls="crece escape", estilo="padding:20px 20px 0;min-height:300px")}
{cta("MÍRALO EN VIVO →")}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- 23-oct frase del día — tarjeta subrayada con cinta "peligro" ----------
FRASE_23 = "1 entre 1.000: no es un plan de vida, pero sí un buen plan de sábado."
def feed_23_frase():
    cuerpo = f"""
<div class="caution-tape" style="font-size:28px">⚠ FRASE DEL DÍA ⚠ FRASE DEL DÍA ⚠ FRASE DEL DÍA ⚠</div>
<div style="height:70px"></div>
{premio("rojo", tam_feed=True)}
<div class="crece" style="display:flex;align-items:center;gap:14px">
  {quote_svg(130)}
  <div style="flex:1">
    <div class="titular negro-txt" style="font-size:40px;line-height:1.14">{FRASE_23}</div>
    <div style="height:12px;background:var(--rojo);width:60%;margin-top:12px;transform:rotate(-1deg)"></div>
    <div class="mono" style="font-size:20px;margin-top:14px;color:var(--rojo)">— @megarifafusa, siendo honesta</div>
  </div>
  {suta("3-con-la-boleta", estilo="width:180px;height:280px")}
</div>
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-am")

def historia_23_frase():
    cuerpo = f"""
<div class="caution-tape" style="font-size:34px">⚠ FRASE DEL DÍA ⚠ FRASE DEL DÍA ⚠</div>
<div style="height:100px"></div>
{premio("rojo")}
<div style="display:flex;align-items:flex-start;gap:16px;margin-top:4px">
  {quote_svg(200)}
  <div style="flex:1">
    <div class="titular negro-txt" style="font-size:60px;line-height:1.14">{FRASE_23}</div>
    <div style="height:16px;background:var(--rojo);width:70%;margin-top:16px;transform:rotate(-1deg)"></div>
    <div class="mono" style="font-size:26px;margin-top:16px;color:var(--rojo)">— @megarifafusa, siendo honesta</div>
  </div>
</div>
{suta("3-con-la-boleta", cls="crece", estilo="min-height:300px")}
{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-am")

# =====================================================================
# PIEZAS — Fase B (nueva tanda 24 oct – 2 nov)
# =====================================================================

# ---------- 24-oct Halloween kickoff: "NÚMERO EMBRUJADO" (más loco: araña, sombrero, sellos rotados) ----------
def hal_wild_adornos_feed():
    return f'''
<div style="position:absolute;top:-10px;left:-30px;width:160px;height:160px;transform:rotate(-18deg);z-index:1">{SVG_SOMBRERO_BRUJA}</div>
<div style="position:absolute;top:260px;right:-20px;width:120px;height:120px;transform:rotate(10deg);z-index:1">{SVG_ARANA}</div>
<div style="position:absolute;bottom:190px;left:-16px;width:120px;height:120px;transform:rotate(-14deg);z-index:1">{SVG_PUMPKIN}</div>
<div style="position:absolute;top:540px;right:60px;width:180px;height:90px;transform:rotate(16deg);opacity:.85;z-index:1">{SVG_BAT}</div>
<div class="sello bg-rojo" style="top:160px;right:30px;transform:rotate(14deg);font-size:22px;color:var(--crema);padding:12px 20px;letter-spacing:3px">🎃 BOO</div>
<div class="sello bg-crema" style="top:620px;left:12px;transform:rotate(-8deg);font-size:22px;color:var(--rojo);padding:12px 22px;letter-spacing:2px">¿O TE ASUSTA?</div>'''

def hal_wild_adornos_historia():
    return f'''
<div style="position:absolute;top:-20px;left:-30px;width:180px;height:180px;transform:rotate(-18deg);z-index:1">{SVG_SOMBRERO_BRUJA}</div>
<div style="position:absolute;top:320px;right:-20px;width:160px;height:160px;transform:rotate(10deg);z-index:1">{SVG_ARANA}</div>
<div style="position:absolute;top:680px;left:-10px;width:160px;height:160px;transform:rotate(-14deg);z-index:1">{SVG_PUMPKIN}</div>
<div style="position:absolute;top:1120px;right:-10px;width:200px;height:100px;transform:rotate(16deg);opacity:.85;z-index:1">{SVG_BAT}</div>
<div style="position:absolute;top:1400px;left:40px;width:150px;height:150px;transform:rotate(-6deg);opacity:.85;z-index:1">{SVG_PUMPKIN}</div>
<div class="sello bg-rojo" style="top:260px;right:40px;transform:rotate(14deg);font-size:30px;color:var(--crema);padding:14px 24px;letter-spacing:3px">🎃 BOO</div>
<div class="sello bg-crema" style="top:1100px;left:30px;transform:rotate(-8deg);font-size:28px;color:var(--rojo);padding:14px 26px;letter-spacing:2px">¿O TE ASUSTA?</div>'''

def feed_24_embrujado():
    cuerpo = f'''
{hal_wild_adornos_feed()}
<div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:12px;flex:1">
  {tope("HALLOWEEN · 24 OCT", oscuro=True)}
  <div style="position:relative">
    <div class="titular rojo-txt" style="font-size:72px;line-height:0.92;transform:rotate(-2deg)">NÚMERO<br>EM·BRU·JA·DO</div>
    <div style="font-family:'Space Mono',monospace;font-size:18px;letter-spacing:3px;color:var(--negro);margin-top:4px">adj. /em.bɾuˈxa.ðo/ · <b>el tuyo entre 1.000</b></div>
  </div>
  {premio("rojo", tam_feed=True, tam=120)}
  <div class="fila crece" style="gap:14px;align-items:stretch">
    {suta("4-senalando", cls="cover", estilo="width:280px")}
    <div class="col crece" style="justify-content:space-between;gap:10px">
      {datos_pie()}
      {qr("sm")}
    </div>
  </div>
  {cta()}{firma()}
</div>'''
    return doc(cuerpo, clase_lienzo="feed bg-am")

def historia_24_embrujado():
    cuerpo = f'''
{hal_wild_adornos_historia()}
<div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:20px;flex:1">
  {tope("HALLOWEEN · 24 OCT", oscuro=True)}
  <div class="titular rojo-txt" style="font-size:120px;line-height:0.92;transform:rotate(-2deg)">NÚMERO<br>EM·BRU·JA·DO</div>
  <div style="font-family:'Space Mono',monospace;font-size:22px;letter-spacing:3px;color:var(--negro);margin-top:-10px">adj. /em.bɾuˈxa.ðo/ · <b>el tuyo entre 1.000</b></div>
  {premio("rojo", tam=130)}
  <div class="fila crece" style="gap:22px;align-items:stretch">
    {suta("4-senalando", cls="cover", estilo="flex:1")}
    <div class="col" style="width:300px;justify-content:center;align-items:center;gap:24px">
      {qr("md")}
      <div style="font-family:'Alfa Slab One',serif;font-size:40px;color:var(--rojo);text-shadow:5px 5px 0 var(--negro);text-align:center;line-height:1">OJO:<br>HOY<br>ARRANCA</div>
    </div>
  </div>
  {datos_pie()}{cta()}{firma()}
</div>'''
    return doc(cuerpo, clase_lienzo="historia bg-am")

# =====================================================================
# PIEZAS DE APOYO — locas, meme-style, modernas, irreverentes (sin fecha fija)
# =====================================================================

# ---------- APOYO 1: ERROR 404 ----------
def feed_apoyo_404():
    pantalla = f'''<div class="pantalla crece" style="min-height:420px">
  <div class="barra"><span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span><span style="font-size:16px;color:var(--crema);opacity:.6;margin-left:12px">mega-rifa-fusa.vercel.app</span></div>
  <div style="font-size:84px;color:var(--amarillo);line-height:1;font-family:'Alfa Slab One',serif">ERROR</div>
  <div style="font-size:140px;color:var(--rojo);line-height:1;font-family:'Alfa Slab One',serif;letter-spacing:-4px">404</div>
  <div style="font-size:28px;color:var(--crema);line-height:1.2;margin-top:14px">tu_numero_de_la_rifa.exe<br><span style="color:var(--amarillo)">not found.</span></div>
  <div style="font-size:16px;color:var(--crema);opacity:.6;margin-top:14px">&gt; sugerencia: ir a mega-rifa-fusa.vercel.app</div>
</div>'''
    cuerpo = f'''
{tope("GLITCH DEL DÍA")}
<div class="fila" style="align-items:stretch;gap:16px">
  <div style="flex:1;display:flex;flex-direction:column;gap:14px">{pantalla}</div>
  {suta("4-senalando", cls="cover", estilo="width:260px")}
</div>
{premio("rojo", tam_feed=True, tam=110)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_apoyo_404():
    pantalla = f'''<div class="pantalla" style="padding:30px 36px">
  <div class="barra"><span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span><span style="font-size:20px;color:var(--crema);opacity:.6;margin-left:14px">mega-rifa-fusa.vercel.app</span></div>
  <div style="font-size:120px;color:var(--amarillo);line-height:1;font-family:'Alfa Slab One',serif">ERROR</div>
  <div style="font-size:260px;color:var(--rojo);line-height:0.9;font-family:'Alfa Slab One',serif;letter-spacing:-6px">404</div>
  <div style="font-size:36px;color:var(--crema);line-height:1.2;margin-top:18px">tu_numero_de_la_rifa.exe<br><span style="color:var(--amarillo)">not found.</span></div>
  <div style="font-size:22px;color:var(--crema);opacity:.6;margin-top:20px">&gt; sugerencia: entrar a {URL}<br>&gt; escoger uno libre antes del sáb 5 dic</div>
</div>'''
    cuerpo = f'''
{tope("GLITCH DEL DÍA")}
{pantalla}
{premio("rojo", tam=130)}
{suta("4-senalando", cls="crece cover", estilo="min-height:200px")}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- APOYO 2: POV meme ("cuando no escogiste y ganó el 234") ----------
def feed_apoyo_pov():
    cuerpo = f'''
{tope("P.O.V. · MEME")}
<div style="position:relative;background:var(--rojo);color:var(--crema);border:10px solid var(--negro);padding:28px 30px;box-shadow:10px 10px 0 var(--negro)">
  <div class="mono" style="font-size:22px;letter-spacing:4px;color:var(--amarillo)">POV:</div>
  <div class="titular" style="font-size:66px;line-height:1;text-shadow:5px 5px 0 var(--negro);margin-top:8px">NO ESCOGISTE<br>Y GANÓ EL 234</div>
  <div class="sello bg-am" style="top:-20px;right:-20px;transform:rotate(10deg);font-size:18px;letter-spacing:3px;color:var(--negro);padding:10px 18px">EJEMPLO</div>
</div>
<div class="fila crece" style="gap:14px;align-items:stretch">
  {suta("4-senalando", cls="cover", estilo="width:220px")}
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:12px">
    <div class="bocadillo" style="font-size:28px">¿No era <b>tu número</b> favorito?<br><span style="color:var(--rojo)">pues ya es de otrx 💀</span></div>
    <div class="mono" style="font-size:16px;color:var(--negro);padding-left:8px">* ejemplo, nadie ganó aún · sorteo sáb 5 dic</div>
  </div>
</div>
{premio("rojo", tam_feed=True, tam=110)}
{cta("ESCOGE EL TUYO ANTES →")}{firma()}'''
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_apoyo_pov():
    cuerpo = f'''
{tope("P.O.V. · MEME")}
<div style="position:relative;background:var(--rojo);color:var(--crema);border:10px solid var(--negro);padding:32px 36px;box-shadow:10px 10px 0 var(--negro)">
  <div class="mono" style="font-size:28px;letter-spacing:5px;color:var(--amarillo)">POV:</div>
  <div class="titular" style="font-size:92px;line-height:1;text-shadow:6px 6px 0 var(--negro);margin-top:10px">NO ESCOGISTE<br>Y GANÓ<br>EL 234</div>
  <div class="sello bg-am" style="top:-24px;right:-20px;transform:rotate(10deg);font-size:24px;letter-spacing:3px;color:var(--negro);padding:12px 22px">EJEMPLO</div>
</div>
<div class="bocadillo" style="font-size:38px">¿No era <b>tu número</b> favorito?<br><span style="color:var(--rojo)">pues ya es de otrx 💀</span></div>
{suta("4-senalando", cls="crece cover", estilo="min-height:400px")}
{premio("rojo", tam=130)}
{cta("ESCOGE EL TUYO ANTES →")}{firma()}'''
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- APOYO 3: HORÓSCOPO DE RIFA ----------
SIGNOS = [
    ("♈", "ARIES",       "001–083"),
    ("♉", "TAURO",       "084–166"),
    ("♊", "GÉMINIS",     "167–249"),
    ("♋", "CÁNCER",      "250–332"),
    ("♌", "LEO",         "333–415"),
    ("♍", "VIRGO",       "416–498"),
    ("♎", "LIBRA",       "499–581"),
    ("♏", "ESCORPIO",    "582–664"),
    ("♐", "SAGITARIO",   "665–747"),
    ("♑", "CAPRIC.",     "748–830"),
    ("♒", "ACUARIO",     "831–913"),
    ("♓", "PISCIS",      "914–999"),
]

def signo_html(glifo, nombre, rango, color_num="var(--rojo)"):
    return f'<div class="signo"><span class="glifo">{glifo}</span><span class="nombre">{nombre}</span><span class="numero" style="color:{color_num}">{rango}</span></div>'

def feed_apoyo_horoscopo():
    col1 = "".join(signo_html(*s) for s in SIGNOS[:6])
    col2 = "".join(signo_html(*s) for s in SIGNOS[6:])
    cuerpo = f'''
{tope("HORÓSCOPO DE RIFA")}
<div class="titular rojo-txt" style="font-size:50px;line-height:0.95">TU SIGNO · TU RANGO</div>
<div class="fila" style="gap:10px">
  <div class="col" style="flex:1;gap:6px">{col1}</div>
  <div class="col" style="flex:1;gap:6px">{col2}</div>
</div>
<div class="mono" style="font-size:13px;color:var(--negro);opacity:.7">* es solo un juego: escoge el que quieras · {URL}</div>
{premio("rojo", tam_feed=True, tam=100)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_apoyo_horoscopo():
    tods = "".join(signo_html(*s) for s in SIGNOS)
    cuerpo = f'''
{tope("HORÓSCOPO DE RIFA")}
<div class="titular rojo-txt" style="font-size:96px;line-height:0.95">TU SIGNO ·<br>TU RANGO</div>
<div class="col crece" style="gap:10px">{tods}</div>
<div class="mono" style="font-size:16px;color:var(--negro);opacity:.7">* es solo un juego: escoge el que quieras · {URL}</div>
{premio("rojo", tam=130)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# ---------- APOYO 4: MI MAMÁ VS YO (meme POV) ----------
def feed_apoyo_mama():
    cuerpo = f'''
{tope("DIÁLOGO FAMILIAR")}
<div class="fila" style="align-items:stretch;gap:16px">
  <div style="flex:1;background:var(--crema);border:10px solid var(--negro);padding:24px 26px;box-shadow:8px 8px 0 var(--negro);display:flex;flex-direction:column;gap:10px">
    <div class="mono" style="font-size:20px;letter-spacing:3px;color:var(--negro);opacity:.7">MI MAMÁ:</div>
    <div class="titular negro-txt" style="font-size:46px;line-height:1">«NO<br>JUEGUES»</div>
  </div>
  <div style="flex:1;background:var(--rojo);color:var(--crema);border:10px solid var(--negro);padding:24px 26px;box-shadow:8px 8px 0 var(--negro);display:flex;flex-direction:column;gap:10px;transform:rotate(2deg)">
    <div class="mono" style="font-size:20px;letter-spacing:3px;color:var(--amarillo)">YO:</div>
    <div class="titular crema-txt" style="font-size:46px;line-height:1">*ESCOGE<br>EL 777*</div>
  </div>
</div>
<div class="crece" style="display:flex;align-items:center;gap:14px">
  {suta("3-con-la-boleta", cls="cover", estilo="width:220px;height:280px")}
  <div class="bocadillo" style="font-size:24px;flex:1">Mamá, son <b>$6.000</b> por el chance de ganar <b>$2.000.000</b>.<br>Igual: solo mayores de 18 😅</div>
</div>
{premio("rojo", tam_feed=True, tam=110)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="feed bg-am")

def historia_apoyo_mama():
    cuerpo = f'''
{tope("DIÁLOGO FAMILIAR")}
<div class="col" style="gap:16px">
  <div style="background:var(--crema);border:10px solid var(--negro);padding:28px 30px;box-shadow:10px 10px 0 var(--negro);transform:rotate(-1deg)">
    <div class="mono" style="font-size:26px;letter-spacing:3px;color:var(--negro);opacity:.7">MI MAMÁ:</div>
    <div class="titular negro-txt" style="font-size:84px;line-height:1;margin-top:6px">«NO JUEGUES»</div>
  </div>
  <div style="background:var(--rojo);color:var(--crema);border:10px solid var(--negro);padding:28px 30px;box-shadow:10px 10px 0 var(--negro);transform:rotate(2deg)">
    <div class="mono" style="font-size:26px;letter-spacing:3px;color:var(--amarillo)">YO:</div>
    <div class="titular crema-txt" style="font-size:84px;line-height:1;margin-top:6px">*ESCOGE EL 777*</div>
  </div>
</div>
<div class="bocadillo" style="font-size:30px">Mamá: son <b>$6.000</b> por el chance de <b>$2.000.000</b>.<br>Igual: solo mayores de 18 😅</div>
{suta("3-con-la-boleta", cls="crece cover", estilo="min-height:260px")}
{premio("rojo", tam=130)}
{cta()}{firma()}'''
    return doc(cuerpo, clase_lienzo="historia bg-am")

# ---------- 27-oct "SALE EL 5 DIC" (L2 cuenta regresiva honesta) ----------
def feed_27_sale_5dic():
    tit = """<div class="titular rojo-txt" style="font-size:80px">SALE EL<br>5 DIC</div>
<div class="sub" style="font-size:26px">Sábado 5 de diciembre, 10:30 p.m. Últimas 3 cifras del premio mayor de la Lotería de Boyacá.</div>
<div class="mono" style="font-size:26px;padding:10px 18px;background:var(--negro);color:var(--amarillo);align-self:flex-start">39 días</div>"""
    return L2_feed("CUENTA REGRESIVA", premio("rojo", tam_feed=True), tit, pose="4-senalando")

def historia_27_sale_5dic():
    tit = """<div class="titular rojo-txt" style="font-size:130px">SALE EL<br>5 DIC</div>
<div class="sub">Sábado 5 de diciembre, 10:30 p.m. Últimas 3 cifras del premio mayor de la Lotería de Boyacá.</div>
<div class="mono" style="font-size:34px;padding:12px 22px;background:var(--negro);color:var(--amarillo);align-self:flex-start">39 días</div>"""
    return L2_historia("CUENTA REGRESIVA", premio("rojo"), tit, pose="4-senalando")

# ---------- 29-oct "REGALA UN NÚMERO" (L1, Sutá con boleta) ----------
def feed_29_regala():
    return L1_feed("REGALO", premio("am", tam_feed=True, eyebrow="REGALA EL CHANCE DE GANAR"),
                   "REGÁLALO →", pose="3-con-la-boleta")

def historia_29_regala():
    return L1_historia("REGALO", premio("am", eyebrow="REGALA EL CHANCE DE GANAR"),
                       "REGÁLALO →", pose="3-con-la-boleta")

# ---------- 30-oct "FIN DE MES = TU NÚMERO" (L3 sash sobre amarillo) ----------
def feed_30_fin_de_mes():
    centro = """<div class="titular rojo-txt" style="font-size:72px">FIN DE MES<br>=<br>TU NÚMERO</div>
<div class="sub" style="font-size:26px">$6.000 y quedas jugando por $2.000.000 el 5 de diciembre.</div>"""
    cuerpo = f"""
<div class="sash" style="font-size:30px">FIN DE MES · MEGA RIFA FUSA</div>
<div style="height:120px"></div>
{premio("rojo", tam_feed=True)}
<div class="fila crece" style="gap:18px">
  <div class="col crece" style="justify-content:center">{centro}</div>
  {suta("5-pulgar-arriba", estilo="width:240px")}
</div>
{datos_pie()}{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="feed bg-am")

def historia_30_fin_de_mes():
    centro = """<div class="titular rojo-txt" style="font-size:94px">FIN DE MES<br>=<br>TU NÚMERO</div>
<div class="sub">$6.000 y quedas jugando por $2.000.000 el 5 de diciembre.</div>"""
    cuerpo = f"""
<div class="sash" style="font-size:36px">FIN DE MES · MEGA RIFA FUSA</div>
<div style="height:140px"></div>
{premio("rojo")}
{centro}
{suta("5-pulgar-arriba", estilo="height:400px")}
{datos_pie()}{cta()}{firma()}"""
    return doc(cuerpo, clase_lienzo="historia bg-am")

# ---------- 31-oct Halloween pico: "TU NÚMERO DE LA SUERTE" ----------
def feed_31_suerte():
    tit = """<div class="titular rojo-txt" style="font-size:68px">TU NÚMERO<br>DE LA SUERTE</div>
<div class="sub" style="font-size:22px">Noche de brujas, noche de suerte. Hoy escoges el tuyo para el 5 dic.</div>"""
    return HAL_feed("ESTA NOCHE", premio("rojo", tam_feed=True, tam=120), tit)

def historia_31_suerte():
    tit = """<div class="titular rojo-txt" style="font-size:120px">TU NÚMERO<br>DE LA SUERTE</div>
<div class="sub">Noche de brujas, noche de suerte. Hoy escoges el tuyo para el 5 dic.</div>"""
    return HAL_historia("ESTA NOCHE", premio("rojo"), tit)

# ---------- 1-nov Frase del día #2 ----------
FRASE_01 = "Un número, un dueño. Nada de bombo: el tablero es la verdad."
def feed_01_frase():
    tit = f"""{quote_svg(150)}
<div class="titular rojo-txt" style="font-size:48px;line-height:1.1">{FRASE_01}</div>"""
    return L2_feed("FRASE DEL DÍA", premio("rojo", tam_feed=True), tit, pose="1-de-pie")

def historia_01_frase():
    tit = f"""{quote_svg(260)}
<div class="titular rojo-txt" style="font-size:70px;line-height:1.12">{FRASE_01}</div>"""
    return L2_historia("FRASE DEL DÍA", premio("rojo"), tit, pose="1-de-pie")

# ---------- 2-nov festivo: "PUENTE PARA ESCOGER" (L4 ticket) ----------
def feed_02_puente():
    return L4_feed("FESTIVO", "?", premio("am", tam_feed=True, eyebrow="PUENTE DE DIFUNTOS"),
                   "Hoy es festivo. Tómate 2 minutos y escoge tu número para el sorteo del sáb 5 dic.",
                   pose="3-con-la-boleta")

def historia_02_puente():
    return L4_historia("FESTIVO", "?", premio("am", eyebrow="PUENTE DE DIFUNTOS"),
                       "Hoy es festivo. Tómate 2 minutos y escoge tu número para el sorteo del sáb 5 dic.",
                       pose="3-con-la-boleta")

# ---------- NZ (Sofía) ----------
def feed_nz():
    cuerpo = f"""
{tope_mono("FROM COLOMBIA · 🇨🇴", "NOW IN NZ")}
{premio_nz("rojo", tam_feed=True, eyebrow="CASH PRIZE IN NZ")}
<div class="fila crece" style="align-items:stretch;gap:18px">
  {suta("2-saludando", cls="escape", estilo="width:340px;padding:14px 10px 0")}
  <div class="col crece" style="justify-content:space-between">
    <div style="display:flex;justify-content:flex-end">{qr("md")}</div>
    <div class="datos"><div class="slab">1,000 numbers · NZD 4</div><div class="mono">Draw: Sun 6 Dec, 4:30 p.m. NZ · Lotería de Boyacá</div></div>
  </div>
</div>
{cta("PICK YOURS →")}{firma(FIRMA_NZ)}"""
    return doc(cuerpo, clase_lienzo="feed bg-crema")

def historia_nz():
    cuerpo = f"""
{tope_mono("FROM COLOMBIA · 🇨🇴", "NOW IN NZ")}
{premio_nz("rojo", eyebrow="CASH PRIZE IN NZ")}
<div class="crece" style="display:flex;align-items:stretch;gap:22px">
  {suta("2-saludando", cls="escape", estilo="flex:1;padding:20px 14px 0")}
  <div class="col" style="width:360px;justify-content:space-between;align-items:center">
    {qr("lg")}
    <div style="font-family:'Alfa Slab One',serif;font-size:46px;color:var(--rojo);text-shadow:5px 5px 0 var(--negro);text-align:center;line-height:1">PICK<br>YOURS</div>
  </div>
</div>
<div class="datos"><div class="slab">1,000 numbers · NZD 4</div><div class="mono">Draw: Sun 6 Dec, 4:30 p.m. NZ · Lotería de Boyacá</div></div>
{cta("PICK YOURS →")}{firma(FIRMA_NZ)}"""
    return doc(cuerpo, clase_lienzo="historia bg-crema")

# =====================================================================
# Catálogo de piezas
# =====================================================================
PIEZAS = {
    # Fase A — rediseño
    "semana-1/15-oct-quincena/feed.png":                 (feed_15_quincena(),    1080, 1080),
    "semana-1/15-oct-quincena/historia.png":             (historia_15_quincena(),1080, 1920),
    "semana-1/17-oct-encuesta/feed.png":                 (feed_17_encuesta(),    1080, 1080),
    "semana-1/17-oct-encuesta/historia.png":             (historia_17_encuesta(),1080, 1920),
    "semana-2/20-oct-como-se-gana/feed.png":             (feed_20_gana(),        1080, 1080),
    "semana-2/20-oct-como-se-gana/historia.png":         (historia_20_gana(),    1080, 1920),
    "semana-2/22-oct-como-se-verifica/feed.png":         (feed_22_verifica(),    1080, 1080),
    "semana-2/22-oct-como-se-verifica/historia.png":     (historia_22_verifica(),1080, 1920),
    "semana-2/23-oct-frase-del-dia/feed.png":            (feed_23_frase(),       1080, 1080),
    "semana-2/23-oct-frase-del-dia/historia.png":        (historia_23_frase(),   1080, 1920),
    # Fase B — nueva tanda
    "semana-3/24-oct-embrujado/feed.png":                (feed_24_embrujado(),   1080, 1080),
    "semana-3/24-oct-embrujado/historia.png":            (historia_24_embrujado(),1080,1920),
    "semana-3/27-oct-sale-5-dic/feed.png":               (feed_27_sale_5dic(),   1080, 1080),
    "semana-3/27-oct-sale-5-dic/historia.png":           (historia_27_sale_5dic(),1080,1920),
    "semana-3/29-oct-regala/feed.png":                   (feed_29_regala(),      1080, 1080),
    "semana-3/29-oct-regala/historia.png":               (historia_29_regala(),  1080, 1920),
    "semana-3/30-oct-fin-de-mes/feed.png":               (feed_30_fin_de_mes(),  1080, 1080),
    "semana-3/30-oct-fin-de-mes/historia.png":           (historia_30_fin_de_mes(),1080,1920),
    "semana-3/31-oct-suerte/feed.png":                   (feed_31_suerte(),      1080, 1080),
    "semana-3/31-oct-suerte/historia.png":               (historia_31_suerte(),  1080, 1920),
    "semana-3/01-nov-frase/feed.png":                    (feed_01_frase(),       1080, 1080),
    "semana-3/01-nov-frase/historia.png":                (historia_01_frase(),   1080, 1920),
    "semana-3/02-nov-puente/feed.png":                   (feed_02_puente(),      1080, 1080),
    "semana-3/02-nov-puente/historia.png":               (historia_02_puente(),  1080, 1920),
    # NZ
    "semana-3/NZ-sofia/feed-EN.png":                     (feed_nz(),             1080, 1080),
    "semana-3/NZ-sofia/historia-EN.png":                 (historia_nz(),         1080, 1920),
    # Apoyo (sin fecha fija, publicar como refuerzo entre piezas)
    "semana-3/apoyo-1-error-404/feed.png":               (feed_apoyo_404(),      1080, 1080),
    "semana-3/apoyo-1-error-404/historia.png":           (historia_apoyo_404(),  1080, 1920),
    "semana-3/apoyo-2-pov-meme/feed.png":                (feed_apoyo_pov(),      1080, 1080),
    "semana-3/apoyo-2-pov-meme/historia.png":            (historia_apoyo_pov(),  1080, 1920),
    "semana-3/apoyo-3-horoscopo/feed.png":               (feed_apoyo_horoscopo(),1080, 1080),
    "semana-3/apoyo-3-horoscopo/historia.png":           (historia_apoyo_horoscopo(),1080,1920),
    "semana-3/apoyo-4-mi-mama/feed.png":                 (feed_apoyo_mama(),     1080, 1080),
    "semana-3/apoyo-4-mi-mama/historia.png":             (historia_apoyo_mama(), 1080, 1920),
}

# =====================================================================
# Render
# =====================================================================
def render(html, salida, w, h):
    from PIL import Image
    nombre = salida.replace("/", "__").replace(".png", ".html")
    fuente = os.path.join(AQUI, "gen-v2", nombre)
    os.makedirs(os.path.dirname(fuente), exist_ok=True)
    with open(fuente, "w", encoding="utf-8") as f:
        f.write(html)
    out = os.path.join(RAIZ, salida).replace("/", os.sep).replace("\\", os.sep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out[:-4] + ".tmp.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=8000",
                    f"--window-size={w+200},{h+300}", f"--screenshot={tmp}",
                    "file:///" + fuente.replace("\\", "/")], check=True, capture_output=True)
    Image.open(tmp).convert("RGB").crop((0, 0, w, h)).save(out)
    os.remove(tmp)
    print("ok", salida)

if __name__ == "__main__":
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    for salida, (html, w, h) in PIEZAS.items():
        if filtro in salida:
            render(html, salida, w, h)
