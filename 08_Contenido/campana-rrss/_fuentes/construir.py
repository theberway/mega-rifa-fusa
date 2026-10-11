# Construye las piezas fijas de la campaña (feed 1080x1080 e historias 1080x1920) del 10 al 23 oct.
# Las piezas con contador NO están aquí: salen de ../generador-contador.html con el dato real del día.
# Uso (Git Bash):  /c/Users/Santiago/AppData/Local/Python/bin/python.exe construir.py [filtro]
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CHROME = r"C:/Users/Santiago/AppData/Local/ms-playwright/chromium-1217/chrome-win64/chrome.exe"
URL = "mega-rifa-fusa.vercel.app"
FIRMA = "Organizada por Santiago · The Ber Way"

CSS = """
.lienzo { padding: 44px; gap: 22px; }
.historia.lienzo { padding: 230px 60px 210px; gap: 30px; }
.rojo { background: var(--rojo); color: var(--crema); }
.amarillo { background: var(--amarillo); color: var(--negro); }
.crema { background: var(--crema); color: var(--negro); }
.azul { background: var(--azul); color: var(--crema); }
.tope { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.chip { font-family: 'Space Mono', monospace; font-weight: 700; font-size: 26px; letter-spacing: 3px; padding: 8px 18px; border: 6px solid var(--negro); background: var(--crema); color: var(--rojo); white-space: nowrap; }
.logoh { font-family: 'Alfa Slab One', serif; font-size: 36px; line-height: 1; white-space: nowrap; }
.rojo .logoh, .azul .logoh { color: var(--crema); text-shadow: 3px 3px 0 var(--negro); }
.amarillo .logoh, .crema .logoh { color: var(--rojo); text-shadow: 3px 3px 0 var(--negro); }
.titular { font-family: 'Alfa Slab One', serif; line-height: 0.98; }
.rojo .titular, .azul .titular { color: var(--crema); text-shadow: 6px 6px 0 var(--negro); }
.amarillo .titular { color: var(--negro); }
.crema .titular { color: var(--rojo); text-shadow: 6px 6px 0 var(--negro); }
.sub { font-size: 38px; font-weight: 600; line-height: 1.3; }
.panel { background: var(--crema); border: 8px solid var(--negro); position: relative; flex-shrink: 0; min-height: 200px; }
.panel img { position: absolute; left: 12px; top: 18px; width: calc(100% - 24px); height: calc(100% - 18px); object-fit: contain; object-position: center bottom; display: block; }
.banda { background: var(--negro); color: var(--crema); border: 8px solid var(--negro); padding: 14px 24px; }
.banda .slab { color: var(--amarillo); font-size: 46px; line-height: 1.1; }
.banda .linea { font-size: 30px; font-weight: 700; margin-top: 2px; }
.cta { background: var(--crema); border: 8px solid var(--negro); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.cta .slab { font-size: 38px; color: var(--rojo); white-space: nowrap; }
.cta .mono { font-size: 28px; color: var(--negro); white-space: nowrap; }
.historia .cta { flex-direction: column; align-items: flex-start; }
.historia .cta .slab { font-size: 54px; } .historia .cta .mono { font-size: 34px; }
.firma { font-size: 22px; font-weight: 600; text-align: center; letter-spacing: 1px; }
.historia .firma { font-size: 28px; }
.crece { flex: 1; min-height: 0; }
.fila { display: flex; gap: 24px; }
.col { display: flex; flex-direction: column; gap: 20px; }
"""

def doc(clase, cuerpo, extra=""):
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="marca.css"><style>{CSS}{extra}</style></head>
<body><div class="lienzo {clase}">{cuerpo}</div></body></html>"""

def cta(txt="ESCOGE EL TUYO →", url=URL):
    return f'<div class="cta"><span class="slab">{txt}</span><span class="mono">{url}</span></div>'

def firma(txt=FIRMA):
    return f'<div class="firma">{txt}</div>'

def datos(linea1="1.000 números · $6.000", linea2="Sorteo sáb 5 dic, 10:30 p.m. · Lotería de Boyacá"):
    return f'<div class="banda"><div class="slab">{linea1}</div><div class="linea">{linea2}</div></div>'

def suta(pose):
    ext = ".webp" if pose == "1-de-pie" else ".jpg"
    return f'<img src="../_assets/{pose}{ext}" alt="Sutá">'

# ---------- Layout "titular" ----------
def titular_feed(color, chip, tit, tam, sub, pose, banda=True, cta_txt="ESCOGE EL TUYO →"):
    cuerpo = f"""
<div class="tope"><span class="chip">{chip}</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="fila crece">
  <div class="col crece" style="justify-content:center">
    <div class="titular" style="font-size:{tam}px">{tit}</div>
    <div class="sub">{sub}</div>
  </div>
  <div class="panel" style="width:300px;padding:18px 14px 0">{suta(pose)}</div>
</div>
{datos() if banda else ''}{cta(cta_txt)}{firma()}"""
    return doc(f"feed {color}", cuerpo)

def titular_historia(color, chip, tit, tam, sub, pose, banda=True, cta_txt="ESCOGE EL TUYO →"):
    cuerpo = f"""
<div class="tope"><span class="chip">{chip}</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:{tam}px">{tit}</div>
<div class="sub" style="font-size:44px">{sub}</div>
<div class="panel crece" style="padding:30px 30px 0">{suta(pose)}</div>
{datos() if banda else ''}{cta(cta_txt)}{firma()}"""
    return doc(f"historia {color}", cuerpo)

# ---------- Layout "anuncio" (13 oct, aprobado) en historia ----------
def anuncio_historia(chip):
    cuerpo = f"""
<div class="tope"><span class="mono" style="font-size:28px;letter-spacing:4px">FUSAGASUGÁ · 2026</span><span class="chip">{chip}</span></div>
<div class="crema" style="border:8px solid var(--negro);padding:26px 30px 32px"><div class="slab" style="font-size:136px;line-height:0.95;color:var(--rojo);text-shadow:8px 8px 0 var(--negro)">MEGA RIFA<br>FUSA</div></div>
<div class="fila crece">
  <div class="col crece">
    <div class="amarillo" style="border:8px solid var(--negro);padding:20px 26px">
      <div class="caps" style="font-size:28px">Premio en efectivo</div>
      <div class="slab" style="font-size:84px;line-height:1.05;white-space:nowrap">$2.000.000</div>
      <div style="font-size:26px;font-weight:600">Si el número ganador está vendido.</div>
    </div>
    <div class="banda crece" style="display:flex;flex-direction:column;justify-content:center">
      <div class="slab" style="font-size:64px">1.000<br>números</div>
      <div class="slab" style="font-size:64px;margin-top:10px">$6.000</div>
      <div class="linea" style="font-size:34px;margin-top:14px">Sorteo sáb 5 dic<br>10:30 p.m.<br>Lotería de Boyacá</div>
    </div>
  </div>
  <div class="panel" style="width:330px;padding:24px 16px 0">{suta("4-senalando")}</div>
</div>
{cta()}{firma()}"""
    return doc("historia rojo", cuerpo, ".fila .col { min-width: 0; }")

# ---------- Carrusel "cómo funciona" (11 oct) ----------
PASOS = [
    ("1", "ESCOGE TU NÚMERO", "Entra al tablero en vivo y busca uno libre, del 000 al 999.", "4-senalando"),
    ("2", "APÁRTALO Y PAGA", "Toca “Lo quiero”, escríbenos por WhatsApp y paga $6.000 a la llave Bre-B @sbg884 o en efectivo.", "1-de-pie"),
    ("3", "TE LLEGA TU BOLETA", "Cuando la plata llega, tu número sale pagado en el tablero y te mandamos tu boleta.", "3-con-la-boleta"),
]

def paso_feed(n, tit, txt, pose, total=3):
    cuerpo = f"""
<div class="tope"><span class="chip">PASO {n} DE {total}</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="fila crece">
  <div class="col crece" style="justify-content:center;gap:26px">
    <div style="width:170px;height:170px;border-radius:50%;background:var(--rojo);border:8px solid var(--negro);display:flex;align-items:center;justify-content:center"><span class="slab" style="font-size:120px;color:var(--crema);text-shadow:5px 5px 0 var(--negro);line-height:1">{n}</span></div>
    <div class="titular" style="font-size:76px">{tit}</div>
    <div class="sub" style="font-size:40px">{txt}</div>
  </div>
  <div class="panel" style="width:290px;padding:18px 14px 0">{suta(pose)}</div>
</div>
{cta("DESLIZA →" if n != "3" else "ESCOGE EL TUYO →")}{firma()}"""
    return doc("feed crema", cuerpo)

def pasos_historia():
    filas = "".join(f"""
<div class="fila" style="align-items:center;background:var(--crema);color:var(--negro);border:8px solid var(--negro);padding:22px 26px">
  <div style="width:130px;height:130px;flex-shrink:0;border-radius:50%;background:var(--rojo);border:7px solid var(--negro);display:flex;align-items:center;justify-content:center"><span class="slab" style="font-size:86px;color:var(--crema);text-shadow:4px 4px 0 var(--negro);line-height:1">{n}</span></div>
  <div><div class="slab" style="font-size:50px;line-height:1;color:var(--rojo)">{t}</div><div style="font-size:33px;font-weight:600;line-height:1.3;margin-top:8px">{x}</div></div>
</div>""" for n, t, x, _ in PASOS)
    cuerpo = f"""
<div class="tope"><span class="chip">CÓMO FUNCIONA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:118px">ASÍ DE<br>SIMPLE</div>
<div class="col crece" style="justify-content:center;gap:26px">{filas}</div>
{cta()}{firma()}"""
    return doc("historia amarillo", cuerpo)

# ---------- Números bonitos (14 oct) ----------
BOLETAS = ["000", "100", "500", "777", "999"]
def boleta(n, tam):
    return f'<div style="background:var(--crema);border:7px solid var(--negro);border-left:7px dashed var(--negro);padding:14px 10px;text-align:center"><div class="mono" style="font-size:{tam//4}px;letter-spacing:2px">Nº</div><div class="mono" style="font-size:{tam}px;line-height:1;color:var(--rojo)">{n}</div></div>'

def bonitos_feed():
    bols = "".join(boleta(n, 70) for n in BOLETAS)
    cuerpo = f"""
<div class="tope"><span class="chip">NÚMEROS BONITOS</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:96px">¿TE LATE UN<br>NÚMERO REDONDO?</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px">{bols}</div>
<div class="fila crece" style="align-items:flex-end">
  <div class="sub crece" style="align-self:center">¿Siguen libres? Míralo en el tablero:<br>puede que alguno ya tenga dueño.</div>
  <div class="panel" style="width:210px;height:100%;padding:12px 10px 0">{suta("2-saludando")}</div>
</div>
{cta("MÍRALOS EN VIVO →")}{firma()}"""
    return doc("feed amarillo", cuerpo)

def bonitos_historia():
    bols = "".join(boleta(n, 80) for n in BOLETAS)
    cuerpo = f"""
<div class="tope"><span class="chip">NÚMEROS BONITOS</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:112px">¿TE LATE UN NÚMERO REDONDO?</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px">{bols}</div>
<div class="sub" style="font-size:42px">¿Siguen libres? Míralo en el tablero: puede que alguno ya tenga dueño.</div>
<div class="panel crece">{suta("2-saludando")}</div>
{cta("MÍRALOS EN VIVO →")}{firma()}"""
    return doc("historia amarillo", cuerpo)

# ---------- NZ (14 oct, inglés) ----------
NZ_LINEAS = ("1,000 numbers · NZD 4", "Draw: Sun 6 Dec, 4:30 p.m. NZ time · Lotería de Boyacá (Colombia)")
def nz_feed():
    cuerpo = f"""
<div class="tope"><span class="mono" style="font-size:24px;letter-spacing:4px">FROM FUSAGASUGÁ, COLOMBIA</span><span class="chip">NOW IN NZ</span></div>
<div class="fila crece">
  <div class="col crece">
    <div class="crema" style="border:8px solid var(--negro);padding:20px 24px 26px;flex:1;display:flex;align-items:center"><div class="slab" style="font-size:98px;line-height:0.95;color:var(--rojo);text-shadow:7px 7px 0 var(--negro);white-space:nowrap">MEGA RIFA<br>FUSA</div></div>
    <div class="amarillo" style="border:8px solid var(--negro);padding:16px 24px 18px">
      <div class="caps" style="font-size:24px">Cash prize in New Zealand</div>
      <div class="slab" style="font-size:104px;line-height:1.02">NZD 1,000</div>
      <div style="font-size:21px;font-weight:600">If the winning number was sold and paid in NZ.</div>
    </div>
  </div>
  <div class="panel" style="width:270px;padding:20px 14px 0">{suta("2-saludando")}</div>
</div>
{datos(*NZ_LINEAS)}{cta("PICK YOURS →")}{firma("Run by Santiago · The Ber Way · DM @megarifafusa")}"""
    return doc("feed rojo", cuerpo)

def nz_historia():
    cuerpo = f"""
<div class="tope"><span class="mono" style="font-size:26px;letter-spacing:3px">FROM COLOMBIA</span><span class="chip">NOW IN NZ</span></div>
<div class="crema" style="border:8px solid var(--negro);padding:26px 30px 32px"><div class="slab" style="font-size:136px;line-height:0.95;color:var(--rojo);text-shadow:8px 8px 0 var(--negro)">MEGA RIFA<br>FUSA</div></div>
<div class="amarillo" style="border:8px solid var(--negro);padding:20px 26px">
  <div class="caps" style="font-size:28px">Cash prize in New Zealand</div>
  <div class="slab" style="font-size:120px;line-height:1.05">NZD 1,000</div>
  <div style="font-size:28px;font-weight:600">If the winning number was sold and paid in NZ.</div>
</div>
<div class="fila crece">
  <div class="banda crece" style="display:flex;flex-direction:column;justify-content:center">
    <div class="slab" style="font-size:62px">1,000 numbers<br>NZD 4 each</div>
    <div class="linea" style="font-size:34px;margin-top:14px">Draw: Sun 6 Dec<br>4:30 p.m. NZ time<br>Lotería de Boyacá</div>
  </div>
  <div class="panel" style="width:300px;padding:20px 14px 0">{suta("4-senalando")}</div>
</div>
{cta("PICK YOURS →")}{firma("Run by Santiago · The Ber Way · DM @megarifafusa")}"""
    return doc("historia rojo", cuerpo)

# ---------- Cómo se gana (20 oct) ----------
def gana_bloque(tam):
    dig = "".join(f'<div style="width:{tam}px;height:{int(tam*1.25)}px;border:7px solid var(--negro);background:{"var(--amarillo)" if i else "var(--crema)"};display:flex;align-items:center;justify-content:center"><span class="mono" style="font-size:{int(tam*0.8)}px;color:var(--negro)">{d}</span></div>' for i, d in enumerate("4217"))
    return f"""
<div class="crema" style="border:8px solid var(--negro);padding:22px 26px;position:relative">
  <span class="mono" style="position:absolute;top:-24px;right:22px;background:var(--rojo);color:var(--crema);border:5px solid var(--negro);padding:2px 14px;font-size:24px;letter-spacing:3px">EJEMPLO</span>
  <div style="font-size:28px;font-weight:700;letter-spacing:2px;text-transform:uppercase">Premio mayor de la Lotería de Boyacá</div>
  <div style="display:flex;gap:12px;margin-top:14px;align-items:center">{dig}
    <span class="slab" style="font-size:{int(tam*0.7)}px;color:var(--rojo);margin:0 10px">→</span>
    <div><div style="font-size:28px;font-weight:700;text-transform:uppercase;letter-spacing:2px">Gana el</div><div class="mono" style="font-size:{int(tam*0.9)}px;line-height:1;color:var(--rojo)">217</div></div>
  </div>
</div>"""

def gana_feed():
    cuerpo = f"""
<div class="tope"><span class="chip">CÓMO SE GANA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:84px">GANAN LAS ÚLTIMAS<br>3 CIFRAS</div>
<div class="sub" style="font-size:34px">Del premio mayor de la Lotería de Boyacá del sáb 5 dic. Transparente y público.</div>
{gana_bloque(104)}
<div class="crece"></div>
{datos("Sáb 5 dic · 10:30 p.m.", "Premio $2.000.000 si el número ganador está vendido")}{cta()}{firma()}"""
    return doc("feed azul", cuerpo)

def gana_historia():
    cuerpo = f"""
<div class="tope"><span class="chip">CÓMO SE GANA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:110px">GANAN LAS ÚLTIMAS 3 CIFRAS</div>
<div class="sub" style="font-size:44px">Del premio mayor de la Lotería de Boyacá del sáb 5 dic. Transparente y público.</div>
<div class="crece"></div>
{gana_bloque(130)}
<div class="crece"></div>
{datos("Sáb 5 dic · 10:30 p.m.", "Premio $2.000.000 si el número ganador está vendido")}{cta()}{firma()}"""
    return doc("historia azul", cuerpo)

# ---------- Cómo se verifica (22 oct) ----------
def ficha(tam):
    return f"""
<div style="background:#fff;border:8px solid var(--negro);padding:24px 28px;position:relative;color:var(--negro)">
  <span class="mono" style="position:absolute;top:-24px;right:22px;background:var(--rojo);color:var(--crema);border:5px solid var(--negro);padding:2px 14px;font-size:24px;letter-spacing:3px">EJEMPLO</span>
  <div style="display:flex;align-items:center;gap:24px">
    <div class="mono" style="font-size:{tam}px;line-height:1">214</div>
    <div><span class="mono" style="background:var(--azul);color:var(--crema);padding:6px 16px;font-size:{tam//4}px;letter-spacing:3px">PAGADO</span>
    <div style="font-size:{tam//3}px;font-weight:700;margin-top:12px">Dav*** G.</div></div>
  </div>
  <div style="font-size:26px;margin-top:14px;line-height:1.35">Quien no quiere salir aparece como <b>Reservado</b>. Nunca nombre completo ni teléfono.</div>
</div>"""

def verifica_feed():
    cuerpo = f"""
<div class="tope"><span class="chip">TODO A LA VISTA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="fila crece">
  <div class="col crece" style="justify-content:center">
    <div class="titular" style="font-size:86px">UN NÚMERO,<br>UN DUEÑO</div>
    <div class="sub" style="font-size:34px">Cada número pagado sale en el tablero con el nombre de su dueño acortado.</div>
    {ficha(110)}
  </div>
  <div class="panel" style="width:250px;padding:16px 12px 0">{suta("1-de-pie")}</div>
</div>
{cta("MÍRALO EN VIVO →")}{firma()}"""
    return doc("feed crema", cuerpo)

def verifica_historia():
    cuerpo = f"""
<div class="tope"><span class="chip">TODO A LA VISTA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:126px">UN NÚMERO,<br>UN DUEÑO</div>
<div class="sub" style="font-size:44px">Cada número pagado sale en el tablero con el nombre de su dueño acortado. Míralo cuando quieras.</div>
{ficha(150)}
<div class="panel crece" style="padding:24px 24px 0">{suta("4-senalando")}</div>
{cta("MÍRALO EN VIVO →")}{firma()}"""
    return doc("historia crema", cuerpo)

# ---------- Frase del día (23 oct) ----------
FRASE = "1 entre 1.000: no es un plan de vida, pero sí un buen plan de sábado."
def frase_feed():
    cuerpo = f"""
<div class="tope"><span class="chip">FRASE DEL DÍA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="fila crece">
  <div class="col crece" style="justify-content:center">
    <div class="slab" style="font-size:180px;line-height:0.6;color:var(--amarillo);text-shadow:6px 6px 0 var(--negro)">“</div>
    <div class="titular" style="font-size:72px;line-height:1.08">{FRASE}</div>
  </div>
  <div class="panel" style="width:270px;padding:18px 14px 0">{suta("3-con-la-boleta")}</div>
</div>
{datos()}{cta()}{firma()}"""
    return doc("feed rojo", cuerpo)

def frase_historia():
    cuerpo = f"""
<div class="tope"><span class="chip">FRASE DEL DÍA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="slab" style="font-size:240px;line-height:0.6;color:var(--amarillo);text-shadow:7px 7px 0 var(--negro);margin-top:40px">“</div>
<div class="titular" style="font-size:96px;line-height:1.08">{FRASE}</div>
<div class="panel crece" style="padding:24px 24px 0">{suta("3-con-la-boleta")}</div>
{datos()}{cta()}{firma()}"""
    return doc("historia rojo", cuerpo)

# ---------- Encuesta (17 oct): historia con espacio libre para el sticker ----------
def encuesta_historia():
    cuerpo = f"""
<div class="tope"><span class="chip">ENCUESTA</span><span class="logoh">MEGA RIFA FUSA</span></div>
<div class="titular" style="font-size:118px">SI JUGARAS…</div>
<div class="sub" style="font-size:52px">¿Escogerías tu número por tu cumpleaños o por los últimos 3 de tu cédula?</div>
<div class="crece"></div>
<div class="fila" style="align-items:flex-end">
  <div class="panel" style="width:360px;height:520px;padding:24px 16px 0">{suta("2-saludando")}</div>
  <div class="sub crece" style="font-size:40px;align-self:center">Vota aquí arriba y mira qué escogió la gente.</div>
</div>
{cta()}{firma()}"""
    return doc("historia amarillo", cuerpo)

# ---------- Catálogo de piezas ----------
S0, S1, S2 = "semana-0", "semana-1", "semana-2"
PIEZAS = {
    f"{S0}/10-oct-ya-esta/feed.png": (titular_feed("rojo", "YA ESTÁ", "1.000<br>NÚMEROS<br>A $6.000", 104,
        "Premio de $2.000.000 en efectivo si el número ganador está vendido.", "2-saludando", banda=False), 1080, 1080),
    f"{S0}/10-oct-ya-esta/historia.png": (titular_historia("rojo", "YA ESTÁ", "1.000 NÚMEROS A $6.000", 124,
        "Premio de $2.000.000 en efectivo si el número ganador está vendido.", "2-saludando"), 1080, 1920),
    f"{S0}/11-oct-como-funciona/carrusel-0-portada.png": (titular_feed("amarillo", "CÓMO FUNCIONA", "ASÍ DE<br>SIMPLE", 130,
        "Tu número en 3 pasos. Desliza →", "4-senalando"), 1080, 1080),
    f"{S0}/11-oct-como-funciona/historia.png": (pasos_historia(), 1080, 1920),
    f"{S1}/13-oct-lanzamiento/historia.png": (anuncio_historia("HOY ARRANCA"), 1080, 1920),
    f"{S1}/14-oct-numeros-bonitos/feed.png": (bonitos_feed(), 1080, 1080),
    f"{S1}/14-oct-numeros-bonitos/historia.png": (bonitos_historia(), 1080, 1920),
    f"{S1}/14-oct-NZ/feed-EN.png": (nz_feed(), 1080, 1080),
    f"{S1}/14-oct-NZ/historia-EN.png": (nz_historia(), 1080, 1920),
    f"{S1}/15-oct-quincena/feed.png": (titular_feed("amarillo", "QUINCENA", "CAYÓ LA<br>QUINCENA", 100,
        "Date el gusto de $6.000: tu número para el sáb 5 dic.", "3-con-la-boleta"), 1080, 1080),
    f"{S1}/15-oct-quincena/historia.png": (titular_historia("amarillo", "QUINCENA", "CAYÓ LA QUINCENA", 140,
        "Date el gusto de $6.000: tu número para el sáb 5 dic.", "3-con-la-boleta"), 1080, 1920),
    f"{S1}/17-oct-encuesta/feed.png": (titular_feed("crema", "PREGUNTA DEL DÍA", '<span style="display:block;line-height:1.18">¿CUMPLEAÑOS<br>O CÉDULA?</span>', 68,
        "Si jugaras, ¿escogerías el número por tu cumpleaños o por los últimos 3 de tu cédula? Te leemos en los comentarios.", "2-saludando", banda=False), 1080, 1080),
    f"{S1}/17-oct-encuesta/historia.png": (encuesta_historia(), 1080, 1920),
    f"{S2}/20-oct-como-se-gana/feed.png": (gana_feed(), 1080, 1080),
    f"{S2}/20-oct-como-se-gana/historia.png": (gana_historia(), 1080, 1920),
    f"{S2}/22-oct-como-se-verifica/feed.png": (verifica_feed(), 1080, 1080),
    f"{S2}/22-oct-como-se-verifica/historia.png": (verifica_historia(), 1080, 1920),
    f"{S2}/23-oct-frase-del-dia/feed.png": (frase_feed(), 1080, 1080),
    f"{S2}/23-oct-frase-del-dia/historia.png": (frase_historia(), 1080, 1920),
}
for i, p in enumerate(PASOS, 1):
    PIEZAS[f"{S0}/11-oct-como-funciona/carrusel-{i}-paso.png"] = (paso_feed(*p), 1080, 1080)

def render(html, salida, w, h):
    from PIL import Image
    nombre = salida.replace("/", "__").replace(".png", ".html")
    fuente = os.path.join(AQUI, "gen", nombre)
    os.makedirs(os.path.dirname(fuente), exist_ok=True)
    # gen/ queda un nivel más abajo: corregir rutas relativas
    html = html.replace('href="marca.css"', 'href="../marca.css"').replace('src="../_assets/', 'src="../../_assets/')
    with open(fuente, "w", encoding="utf-8") as f:
        f.write(html)
    out = os.path.join(RAIZ, salida).replace("/", os.sep).replace("\\", os.sep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out[:-4] + ".tmp.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--virtual-time-budget=8000", f"--window-size={w+200},{h+300}", f"--screenshot={tmp}",
                    "file:///" + fuente.replace("\\", "/")], check=True, capture_output=True)
    Image.open(tmp).convert("RGB").crop((0, 0, w, h)).save(out)
    os.remove(tmp)
    print("ok", salida)

if __name__ == "__main__":
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    for salida, (html, w, h) in PIEZAS.items():
        if filtro in salida:
            render(html, salida, w, h)
