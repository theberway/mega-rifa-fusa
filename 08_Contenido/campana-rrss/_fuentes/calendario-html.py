# Genera 08_Contenido/calendario-de-contenido.html desde calendario-de-contenido.md (con la marca).
import re, os, html
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
md = open(os.path.join(R, "calendario-de-contenido.md"), encoding="utf-8").read()
LISTOS = {10,11,12,13,14,15,16,17,18,19,20,21,22,23}  # oct con piezas en campana-rrss/
def inl(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", t)
semanas, notas = [], []
cur = None
for l in md.split("\n"):
    if l.startswith("## Semana"):
        cur = {"tit": l[3:], "meta": "", "filas": []}; semanas.append(cur)
    elif l.startswith("## Notas"):
        cur = None
    elif cur is not None and l.startswith("**") and not cur["meta"]:
        cur["meta"] = l
    elif cur is not None and l.startswith("| ") and not l.startswith("| Día") and not l.startswith("|---"):
        c = [x.strip() for x in l.strip("|").split("|")]
        cur["filas"].append(c)
    elif cur is None and l.startswith("- ") and semanas:
        notas.append(l[2:])
cards = []
for i, s in enumerate(semanas):
    filas = []
    for dia, que, copy in s["filas"]:
        fuerte = dia.startswith("**")
        dd = dia.strip("*")
        n = int(re.search(r"\d+", dd).group())
        listo = i <= 2 and n in LISTOS and "nov" not in dd
        badge = '<span class="listo">pieza lista</span>' if listo else ""
        filas.append(f'<div class="dia{" fuerte" if fuerte else ""}"><div class="fecha">{html.escape(dd)}</div>'
                     f'<div class="cuerpo"><div class="que">{inl(que)} {badge}</div><div class="copy">{inl(copy)}</div></div></div>')
    cards.append(f'<section class="semana"><h2>{inl(s["tit"])}</h2><p class="meta">{inl(s["meta"])}</p>{"".join(filas)}</section>')
out = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calendario de contenido · Mega Rifa Fusa</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Archivo+Narrow:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap">
<style>
:root{{--crema:#FFF4D6;--rojo:#C1121F;--amarillo:#F2B705;--azul:#0A3D62;--negro:#1A1A1A}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--crema);color:var(--negro);font:17px/1.45 'Archivo Narrow',sans-serif}}
header{{background:var(--rojo);border-bottom:7px solid var(--negro);padding:22px 16px}}
.logo{{font:400 44px/0.95 'Alfa Slab One',serif;color:var(--crema);text-shadow:4px 4px 0 var(--negro)}}
.sub{{font:700 14px 'Space Mono',monospace;letter-spacing:2px;color:var(--crema);margin-top:10px;text-transform:uppercase}}
main{{max-width:900px;margin:0 auto;padding:18px 16px 50px}}
.reglas{{background:var(--negro);color:var(--crema);border:5px solid var(--negro);padding:14px 16px;margin-bottom:22px}}
.reglas b{{color:var(--amarillo)}}
.semana{{border:5px solid var(--negro);background:#fff;margin-bottom:22px}}
.semana h2{{margin:0;background:var(--amarillo);border-bottom:5px solid var(--negro);padding:12px 14px;font:400 22px/1.15 'Alfa Slab One',serif}}
.meta{{margin:0;padding:10px 14px;background:var(--azul);color:var(--crema);font-weight:600}}
.dia{{display:flex;gap:12px;padding:12px 14px;border-top:2px solid #e5d9b8}}
.fecha{{flex:0 0 74px;font:700 15px 'Space Mono',monospace;text-transform:uppercase}}
.fuerte{{background:#fff7e0}} .fuerte .fecha{{color:var(--rojo)}}
.cuerpo{{min-width:0;overflow-wrap:anywhere}} .que{{font-weight:700}} .copy{{margin-top:3px;color:#333}}
.listo{{display:inline-block;font:700 11px 'Space Mono',monospace;background:var(--rojo);color:var(--crema);padding:2px 7px;margin-left:4px;letter-spacing:1px;text-transform:uppercase;vertical-align:2px}}
code{{color:var(--negro);font:13px 'Space Mono',monospace;background:var(--crema);padding:0 3px}}
footer{{text-align:center;font-weight:600;padding:20px 16px 30px}}
ul{{margin:6px 0 0;padding-left:20px}}
</style></head><body>
<header><div class="logo">MEGA RIFA<br>FUSA</div><div class="sub">Calendario de contenido · 9 oct → 6 dic 2026</div></header>
<main>
<div class="reglas"><b>Un post al día, 8:00 a.m.</b> Contador siempre <b>real</b> del Sheet. Nada de urgencia inventada ni "el 777 ya se fue" si no es cierto. La causa nunca va en público. <b>Pieza lista</b> = está en <code>campana-rrss/</code>.</div>
{"".join(cards)}
<section class="semana"><h2>Notas de producción</h2><div style="padding:6px 14px 14px"><ul>{"".join(f"<li>{inl(n)}</li>" for n in notas)}</ul></div></section>
</main><footer>Organizada por Santiago · The Ber Way</footer></body></html>"""
open(os.path.join(R, "calendario-de-contenido.html"), "w", encoding="utf-8").write(out)
print("ok", len(semanas), "semanas")
