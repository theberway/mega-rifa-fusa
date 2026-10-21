# Escribe copy.md de la tanda v2 nueva (24 oct – 2 nov) + NZ.
# Las piezas Gen. (25, 26, 28) usan el generador el día; su copy va aquí también.
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "mega-rifa-fusa.vercel.app"
FIRMA = "Organizada por Santiago · The Ber Way (@theberway) by Santiago (@santiagobermudezai)"
H = "#MegaRifaFusa #Fusagasugá #Fusa #Fusagasuga #Cundinamarca #Rifa #Sorteo"
HP = "#MegaRifaFusa #Fusagasugá #Rifa"
LINK_FB = f"*En FB el link sí se puede tocar: pegar `https://{URL}` completo en vez de \"link en la bio\".*"

def copy(titulo, piezas, hora, marca, personal, notas=None):
    s = f"# {titulo} — copy\n\n**Piezas:** {piezas}\n**Hora:** {hora}\n\n"
    s += f"## Cuenta de la rifa (@megarifafusa) — IG / FB\n{marca}\n\n{FIRMA}\n\n{H}\n\n{LINK_FB}\n\n"
    s += f"## Cuenta personal (@santiagobermudezai) — IG / FB\n{personal}\n\n{HP}\n"
    if notas:
        s += "\n## Antes de publicar\n" + "\n".join(f"- {n}" for n in notas) + "\n"
    return s

GEN = "del **generador** (`../../generador-contador.html`): `feed.png` e `historia.png` con el dato real del día"

T = {}

T["semana-3/24-oct-embrujado/copy.md"] = copy(
    "sáb 24 oct · Número embrujado (kickoff Halloween)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 10:00 a.m. · Historia 1:00 p.m.",
    f"Elige tu número embrujado 🎃 Entre el 000 y el 999, el tuyo te está esperando. $6.000 y quedas jugando por $2.000.000 el sáb 5 dic.\n\n👉 {URL} (link en la bio). Solo mayores de 18.",
    f"Arrancó la semana de Halloween en la rifa 🎃 Yo ya tengo mi número embrujado, ¿y ustedes? {URL} · @megarifafusa",
    notas=["Pieza decorativa con silueta de calabaza y murciélago en negro plano, sin naranja (fuera de paleta).",
           "Sin whisky de consolación, sin promesas falsas."])

T["semana-3/25-oct-pc2/copy.md"] = copy(
    "dom 25 oct · Punto de control 2 (recuento)",
    f"{GEN} → tipo **\"18 oct · Recuento\"** (mismo tipo, publicarlo con cifras de hoy)",
    "Feed 10:00 a.m. · Historia 1:00 p.m.",
    f"Vamos [VAN] de 1.000 🙌 Dos semanas moviendo la Mega Rifa Fusa. Quedan [QUEDAN] libres.\n\n👉 {URL} (link en la bio). Sorteo sáb 5 dic.",
    f"Dos semanas de la rifa y vamos [VAN] 🙌 Gracias a todos. Quedan [QUEDAN] en {URL} · @megarifafusa",
    notas=["[VAN] = **pagados** del tablero (no apartados). [QUEDAN] = número grande del contador.",
           "Si no llegamos a la meta interna del PC2, no se publica meta ni frustración. Solo el recuento real."])

T["semana-3/26-oct-descanso/copy.md"] = (
    "# lun 26 oct · Sin post de feed\n\n"
    "El calendario queda sin feed este día (post-fin-de-semana). No relleno con un post de más.\n\n"
    "**Opcional:** historia tipo **\"Cualquier día · Quedan X\"** del generador con el dato real:\n\n"
    f"> Quedan [QUEDAN] 🎟️ Míralos en {URL}\n")

T["semana-3/27-oct-sale-5-dic/copy.md"] = copy(
    "mar 27 oct · Sale el 5 dic (cuenta regresiva honesta)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Faltan 39 días para el sorteo 📅 Sábado 5 de diciembre, 10:30 p.m., Lotería de Boyacá. Si quieres estar jugando, hoy es un buen día para escoger el tuyo.\n\n👉 {URL} (link en la bio).",
    f"39 días para el sorteo de la Mega Rifa Fusa 🙌 Yo ya tengo el mío, ¿tú? {URL} · @megarifafusa",
    notas=["El contador 39 días es cifra real al 27-oct-2026. **Verificar el día de publicación** antes de subirlo.",
           "Si queda menos (p. ej. 37 o 38), **actualizar la pieza y la story**."])

T["semana-3/28-oct-busca-dueno/copy.md"] = copy(
    "mié 28 oct · El [###] busca dueño",
    f"{GEN} → tipo **\"21 oct · El ### busca dueño\"** (igual que la anterior, con número libre del día)",
    "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"El [###] todavía busca dueño 🎟️ ¿Será el tuyo?\n\n👉 {URL} (link en la bio)\n\n$6.000 · premio $2.000.000 · sorteo sáb 5 dic.",
    f"El [###] sigue libre en la rifa 👀 {URL} · @megarifafusa",
    notas=["Escoger un número **libre ese día** (mirarlo en el tablero antes).",
           "Si alguien lo aparta durante el día, editar el post o borrarlo."])

T["semana-3/29-oct-regala/copy.md"] = copy(
    "jue 29 oct · Regala un número",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Regala el chance de ganar $2.000.000 🎁 Por $6.000 le pones el número a un amigo, mamá, pareja, hermanx. Si sale, es suyo.\n\n👉 {URL} (link en la bio). Sorteo sáb 5 dic.",
    f"Para regalar: un número de la rifa 🎁 $6.000 y le queda jugando por $2.000.000. {URL} · @megarifafusa",
    notas=["Al pagar, mandar WhatsApp con el nombre acortado de la persona a quien se le regala (o 'Reservado' si no quiere salir)."])

T["semana-3/30-oct-fin-de-mes/copy.md"] = copy(
    "vie 30 oct · Fin de mes = tu número",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Fin de mes 💸 Date el gusto de $6.000: tu número para el sáb 5 dic.\n\n1.000 números · premio $2.000.000 si el número ganador está vendido · Lotería de Boyacá.\n\n👉 {URL} (link en la bio). Solo mayores de 18.",
    f"Fin de mes y escogiendo mi segundo número 😄 $6.000 por una boleta más. {URL} · @megarifafusa",
    notas=["Igual que quincena: nada de saldos/cuentas/tarjetas en storias o fotos."])

T["semana-3/31-oct-suerte/copy.md"] = copy(
    "sáb 31 oct · Tu número de la suerte (Halloween pico)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 10:00 a.m. · Historia noche de Halloween (7-9 p.m.)",
    f"Noche de brujas, noche de suerte 🎃 Hoy escoges tu número para el sáb 5 dic. $6.000 · premio $2.000.000 si el número ganador está vendido.\n\n👉 {URL} (link en la bio).",
    f"Es Halloween y mi número de la suerte ya está pagado 🙌 ¿Y el tuyo? {URL} · @megarifafusa",
    notas=["Sin whisky, sin promesas de 'ganarás'. Solo el chance.",
           "La historia puede ir más tarde (noche de Halloween) con el gancho 'hoy sí'."])

T["semana-3/01-nov-frase/copy.md"] = copy(
    "dom 1 nov · Frase del día #2 (prueba social honesta)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 10:00 a.m. · Historia 1:00 p.m.",
    f"«Un número, un dueño. Nada de bombo: el tablero es la verdad.» 🎟️\n\nMíralo cuando quieras 👉 {URL} (link en la bio). Sorteo sáb 5 dic.",
    f"Lo que más me gusta de la Mega Rifa Fusa es que todo se puede revisar en el tablero 🙌 {URL} · @megarifafusa",
    notas=["Frase derivada del principio 'un número, un dueño'. No inventar números de ventas si no son reales."])

T["semana-3/02-nov-puente/copy.md"] = copy(
    "lun 2 nov · Puente para escoger (festivo de Difuntos)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Feed 10:00 a.m. · Historia 1:00 p.m.",
    f"Hoy es festivo (Difuntos — ley Emiliani) 🙏 Tómate 2 minutos: entra, escoge tu número para el sorteo del sáb 5 dic, páganos y listo.\n\n👉 {URL} (link en la bio). $6.000 · premio $2.000.000.",
    f"Festivo, buen día para escoger número de la rifa 😄 2 minutos y listo. {URL} · @megarifafusa",
    notas=["Mencionar que es festivo lun 2 nov (Difuntos — ley Emiliani), sin tono fúnebre.",
           "Es solo un día bueno para resolver — sin presión."])

T["semana-3/apoyo-1-error-404/copy.md"] = copy(
    "APOYO · ERROR 404 (meme técnico, sin fecha fija)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Publicar entre piezas, cuando queramos refuerzo o un día flojo.",
    f"**ERROR 404: tu número de la rifa no encontrado** 🤖\n\nSolución: entrar a {URL}, escoger uno libre y pagar $6.000.\n\nSorteo sáb 5 dic · premio $2.000.000 si el número ganador está vendido. Solo mayores de 18.",
    f"POV: tratando de verificar mi número de la rifa en memoria y el cerebro me da 404 🙃 {URL} · @megarifafusa",
    notas=["Pieza de refuerzo, no reemplaza al feed del día.",
           "El estilo 'terminal de código' funciona mejor en IG que en FB (público más joven)."])

T["semana-3/apoyo-2-pov-meme/copy.md"] = copy(
    "APOYO · POV: no escogiste y ganó el 234 (meme, sin fecha fija)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Publicar como refuerzo. Buena para fines de semana.",
    f"POV: no escogiste y ganó el 234 💀 (es ejemplo, el sorteo es el sáb 5 dic).\n\nTu número entre 1.000 por $6.000 👉 {URL} (link en la bio). Premio $2.000.000 si el número ganador está vendido.",
    f"Me da ansiedad pensar que ganó mi número favorito y no lo había comprado 💀 ya lo tengo apartado en @megarifafusa · {URL}",
    notas=["La palabra 'EJEMPLO' aparece visible en la pieza: no se puede inventar un ganador real.",
           "Reaccionar a los comentarios con humor."])

T["semana-3/apoyo-3-horoscopo/copy.md"] = copy(
    "APOYO · Horóscopo de rifa (listicle divertido, sin fecha fija)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Publicar como refuerzo. Alto engagement esperado por el tema zodiacal.",
    f"Horóscopo de rifa 🔮 Dinos qué signo eres en los comentarios y te decimos tu rango.\n\nAries 001–083 · Tauro 084–166 · Géminis 167–249 · Cáncer 250–332 · Leo 333–415 · Virgo 416–498 · Libra 499–581 · Escorpio 582–664 · Sagitario 665–747 · Capricornio 748–830 · Acuario 831–913 · Piscis 914–999\n\n* Es solo un juego: escoge el número que quieras 👉 {URL}",
    f"¿Soy la única que mira el horóscopo todos los días? Pues también tiene su rango de números en la Mega Rifa Fusa 🔮 {URL} · @megarifafusa",
    notas=["Los rangos salen de dividir 1.000 / 12 ≈ 83 números por signo. **No** hay base astrológica: es juego.",
           "No publicar en días cercanos al sorteo (mantener la jerarquía con los posts informativos)."])

T["semana-3/apoyo-4-mi-mama/copy.md"] = copy(
    "APOYO · Mi mamá: «no juegues» / Yo (meme POV, sin fecha fija)",
    "`feed.png` (IG + FB) · `historia.png`",
    "Publicar como refuerzo. Humor familiar colombiano.",
    f"— Mamá: no juegues.\n— Yo: *escoge el 777*\n\nMamá, son $6.000 por el chance de ganar $2.000.000. Igual: solo mayores de 18 😅\n\n👉 {URL} (link en la bio). Sorteo sáb 5 dic.",
    f"Mi mamá: «no juegues». Yo: *escogiendo mi número en {URL}* 😅 @megarifafusa",
    notas=["Humor familiar; no victimizar a nadie.",
           "Si una mamá real comenta, responder con respeto y el link al reglamento."])

T["semana-3/NZ-sofia/copy.md"] = (
    "# Fri 30 Oct (or earlier) · NZ second wave — copy (EN)\n\n"
    "**Pieces:** `feed-EN.png` (IG + FB) · `historia-EN.png` (story)\n"
    "**Who posts:** Sofía, on her accounts, on NZ time. Optional: @megarifafusa shares.\n"
    "**Time (NZ):** adjust to Sofía's audience.\n\n"
    "## Caption — IG / FB\n"
    "Second wave from Fusagasugá, Colombia 🇨🇴 the Mega Rifa Fusa 🎟️\n\n"
    "1,000 numbers · NZD 4 each\n"
    "💰 Cash prize: NZD 1,000 if the winning number was sold and paid here in NZ\n"
    "🍀 Draw: Sun 6 Dec, 4:30 p.m. NZ time, with the Lotería de Boyacá\n\n"
    f"Pick yours on the live board 👉 {URL}\n\n"
    "18+ only. Run by Santiago · The Ber Way (@theberway) · @megarifafusa\n\n"
    "#MegaRifaFusa #ColombiansInNZ #ColombianosEnNuevaZelanda #NewZealand #Raffle\n\n"
    "## Before posting\n- Payment details stay in private chat.\n- Pick a day Sofía's audience is active.\n")

for ruta, texto in T.items():
    p = os.path.join(R, ruta); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(texto); print("ok", ruta)
