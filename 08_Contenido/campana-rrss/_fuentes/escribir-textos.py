# Escribe copy.md y reel.md de cada día (10–23 oct). El 13 oct ya tiene copy.md aprobado: no se toca.
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "mega-rifa-fusa.vercel.app"
FIRMA = "Organizada por Santiago · The Ber Way (@theberway) by Santiago (@santiagobermudezai)"
H = "#MegaRifaFusa #Fusagasugá #Fusa #Fusagasuga #Cundinamarca #Rifa #Sorteo"
HP = "#MegaRifaFusa #Fusagasugá #Rifa"
HT = "#MegaRifaFusa #Fusagasugá #Fusa #Rifa #Sorteo #Colombia"
AUDIO = ("Tu voz en off + una pista instrumental de la biblioteca de la app (Instagram/TikTok), bajita debajo de la voz. "
         "No sugiero canciones en tendencia: desde aquí no puedo verificar cuáles están vigentes ni si se pueden usar en cuentas de empresa.")
LINK_FB = f"*En FB el link sí se puede tocar: pegar `https://{URL}` completo en vez de \"link en la bio\".*"

def copy(titulo, piezas, hora, marca, personal, tiktok=None, notas=None):
    s = f"# {titulo} — copy\n\n**Piezas:** {piezas}\n**Hora:** {hora}\n\n"
    s += f"## Cuenta de la rifa (@megarifafusa) — IG / FB\n{marca}\n\n{FIRMA}\n\n{H}\n\n{LINK_FB}\n\n"
    s += f"## Cuenta personal (@santiagobermudezai) — IG / FB\n{personal}\n\n{HP}\n"
    if tiktok:
        s += f"\n## TikTok (@megarifafusa) — descripción del video (ver `reel.md`)\n{tiktok}\n\n{HT}\n"
    if notas:
        s += "\n## Antes de publicar\n" + "\n".join(f"- {n}" for n in notas) + "\n"
    return s

def reel(titulo, dur, idea, tomas, voz, textos, notas=None):
    s = f"# {titulo} — reel / TikTok\n\n**Duración:** {dur} · **Formato:** vertical 1080×1920 · **Cara:** no, solo voz y manos\n\n**Idea:** {idea}\n\n"
    s += "## Storyboard\n| Seg. | Qué se ve (cámara) | Texto en pantalla |\n|---|---|---|\n"
    s += "\n".join(f"| {a} | {b} | {c} |" for a, b, c in tomas) + "\n\n"
    s += "## Voz en off\n" + "\n".join(f"> {l}" for l in voz) + "\n\n"
    s += "## Rótulos (para escribirlos con el editor de la app)\n" + "\n".join(f"- {t}" for t in textos) + "\n\n"
    s += f"## Audio sugerido\n{AUDIO}\n"
    if notas:
        s += "\n## Ojo al grabar\n" + "\n".join(f"- {n}" for n in notas) + "\n"
    return s

GEN = "del **generador** (`../../generador-contador.html`): `feed.png` e `historia.png` con el dato real del día"
T = {}

# ---------------- Semana 0 ----------------
T["semana-0/10-oct-ya-esta/copy.md"] = copy(
    "sáb 10 oct · Ya está (preventa)", "`feed.png` (IG + FB) · `historia.png` (IG + FB)", "Hoy, apenas esté todo listo para la primera venta. Historia: a media tarde.",
    f"Ya está 🎟️ La Mega Rifa Fusa tiene 1.000 números, del 000 al 999, a $6.000 cada uno.\n\n💰 Premio: $2.000.000 en efectivo si el número ganador está vendido.\n🍀 Sorteo: sáb 5 de diciembre, 10:30 p.m., con las últimas 3 cifras del premio mayor de la Lotería de Boyacá.\n\nEscoge el tuyo en el tablero en vivo 👉 {URL} (link en la bio)\n\nSolo mayores de 18. Reglas: {URL}/reglamento",
    f"Les cuento algo: estoy organizando la Mega Rifa Fusa 🎟️ 1.000 números a $6.000 y un premio de $2.000.000 en efectivo. Sorteo el sáb 5 de diciembre con la Lotería de Boyacá.\n\nSi quieren el suyo, escríbanme o escójanlo en {URL} 🙌 Síganla en @megarifafusa",
    notas=["Es la preventa: el empujón real es 1 a 1 con familia y amigos (WhatsApp), no el post."])

T["semana-0/11-oct-como-funciona/copy.md"] = copy(
    "dom 11 oct · Cómo funciona en 3 pasos", "carrusel `carrusel-0-portada.png` → `carrusel-1/2/3-paso.png` (IG + FB, en ese orden) · `historia.png` · reel (`reel.md`)",
    "Carrusel 8:00 a.m. · Historia 12:30 p.m. · Reel 7:00 p.m.",
    f"Así de simple 👇\n\n1️⃣ Escoges tu número en el tablero en vivo (del 000 al 999)\n2️⃣ Lo apartas por WhatsApp y pagas $6.000 a la llave Bre-B @sbg884 o en efectivo\n3️⃣ Cuando la plata llega, tu número sale pagado en el tablero y te llega tu boleta\n\nUn número, un dueño. Todo a la vista 👉 {URL} (link en la bio)\n\nSorteo sáb 5 dic, 10:30 p.m., Lotería de Boyacá. Solo mayores de 18.",
    f"¿Cómo se compra un número de la rifa? En 3 pasos y sin enredos 👇 Escoges en {URL}, me escribes y pagas $6.000, y te llega tu boleta. Todo en @megarifafusa 🎟️",
    tiktok=f"Cómo conseguir tu número de la Mega Rifa Fusa en 3 pasos 🎟️ $6.000, premio $2.000.000, sorteo sáb 5 dic. Tablero en vivo: {URL} (link en el perfil)",
    notas=["En TikTok también se puede subir el carrusel en modo foto (opcional)."])
T["semana-0/11-oct-como-funciona/reel.md"] = reel(
    "dom 11 oct · Cómo funciona", "20–25 s", "Grabación de pantalla del celular usando el tablero de verdad, con tu voz encima.",
    [("0–3", "Sutá / logo en pantalla (puedes mostrar la `carrusel-0-portada.png`)", "¿Cómo consigo mi número?"),
     ("3–9", "Grabación de pantalla: bajas por la cuadrícula y tocas un número **libre** → se abre la ficha", "1. Escoge uno libre"),
     ("9–15", "Tocas \"Lo quiero\" → se abre WhatsApp con el mensaje listo (no lo envíes)", "2. Apártalo y paga $6.000"),
     ("15–21", "Vuelves al tablero y muestras el contador QUEDAN LIBRES", "3. Sale pagado y te llega tu boleta"),
     ("21–25", "Pantalla final: `carrusel-3-paso.png` o el link", URL)],
    ["¿Cómo consigues tu número de la Mega Rifa Fusa? Fácil.",
     "Uno: entras al tablero y escoges uno libre, del cero cero cero al nueve nueve nueve.",
     "Dos: tocas «Lo quiero», nos escribes y pagas seis mil pesos a la llave arroba ese-be-ge ocho-ocho-cuatro, o en efectivo.",
     "Tres: cuando la plata llega, tu número sale pagado en el tablero y te llega tu boleta.",
     "Sorteo el sábado 5 de diciembre. Escoge el tuyo en mega guion rifa guion fusa punto vercel punto app."],
    ["¿Cómo consigo mi número?", "1. Escoge uno libre", "2. Apártalo y paga $6.000", "3. Sale pagado y te llega tu boleta", URL],
    ["Antes de grabar, cierra notificaciones y que no salga ningún otro chat ni número de teléfono en pantalla.",
     "Si en el tablero ya hay números pagados, se ve el nombre acortado (Dav*** G.): eso está bien, es lo público."])

T["semana-0/12-oct-primeros-numeros/copy.md"] = copy(
    "lun 12 oct (festivo) · Ya escogieron los suyos", f"{GEN} → tipo **\"12 oct · Ya escogieron los suyos\"**", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Ya escogieron los suyos 🎟️ Quedan [QUEDAN] números libres de 1.000. ¿Cuál es el tuyo?\n\n👉 {URL} (link en la bio)\n\nPremio $2.000.000 · sorteo sáb 5 dic, 10:30 p.m., Lotería de Boyacá. Solo mayores de 18.",
    f"Gracias a los que ya escogieron su número 🙌 Quedan [QUEDAN] en la Mega Rifa Fusa. Míralos en {URL} o escríbeme. @megarifafusa",
    notas=["Reemplaza [QUEDAN] por el mismo número que pusiste en el generador.",
           "El calendario pedía un collage con fotos de compradores: **solo si hay fotos de manos con permiso**. Si no hay, va la pieza del generador.",
           "Si hoy no hay ningún número pagado, el generador no deja hacer esta pieza: publica `semana-0/11-oct-como-funciona/historia.png` en su lugar."])

# ---------------- Semana 1 ----------------
T["semana-1/13-oct-lanzamiento/reel.md"] = reel(
    "mar 13 oct · Lanzamiento", "30–45 s", "El guion aprobado en `08_Contenido/guion-de-lanzamiento.md`, partido en tomas.",
    [("0–5", "Manos sosteniendo el celular con el tablero (la cuadrícula 000–999)", "Mega Rifa Fusa"),
     ("5–12", "Dedo bajando por la cuadrícula", "1.000 números · $6.000"),
     ("12–20", "Dedo toca un número **libre** → se abre la ficha", "Premio $2.000.000"),
     ("20–30", "La `feed.png` de hoy en pantalla (o Sutá impreso en la mano)", "Sorteo sáb 5 dic · Lotería de Boyacá"),
     ("30–40", "Cierre: logo y link", URL)],
    ["En Fusa hay algo nuevo: la Mega Rifa Fusa.",
     "Son mil números, del 000 al 999, a seis mil pesos cada uno.",
     "El premio: dos millones de pesos en efectivo.",
     "El sorteo es el sábado 5 de diciembre a las 10:30 de la noche, con las últimas tres cifras del premio mayor de la Lotería de Boyacá.",
     "Escoges tu número en el tablero —que puedes ver en vivo— pagas a la llave arroba ese-be-ge ocho-ocho-cuatro, y te llega tu boleta.",
     "Un número, un dueño. Todo a la vista.",
     "Escoge el tuyo en mega guion rifa guion fusa punto vercel punto app."],
    ["1.000 números · $6.000", "Premio $2.000.000", "Sorteo sáb 5 dic · Lotería de Boyacá", URL],
    ["Publícalo en la mañana (9:00 a.m.), después del feed de las 8:00, en IG Reels, FB Reels y TikTok."])
# el copy.md del 13 ya existe (aprobado); se le agrega la historia en el calendario

T["semana-1/14-oct-numeros-bonitos/copy.md"] = copy(
    "mié 14 oct · Números bonitos", "`feed.png` (IG + FB) · `historia.png`", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"¿Te late un número redondo? 🎯 El 000, el 100, el 500, el 777, el 999… o el de tu cumpleaños.\n\nMira en el tablero cuáles siguen libres: puede que alguno ya tenga dueño 👉 {URL} (link en la bio)\n\n$6.000 · premio $2.000.000 · sorteo sáb 5 dic, Lotería de Boyacá. Solo mayores de 18.",
    f"¿Cuál número escogerían ustedes? Yo ando viendo cuáles redondos siguen libres en {URL} 👀 @megarifafusa",
    notas=["No digas en ningún lado que uno de esos números está libre sin mirarlo antes en el tablero."])

T["semana-1/14-oct-NZ/copy.md"] = (
    "# Wed 14 Oct · New Zealand launch — copy (EN)\n\n"
    "**Pieces:** `feed-EN.png` (IG + FB) · `historia-EN.png` (story) · reel (`reel.md`)\n"
    "**Who posts:** Sofía, on her accounts, on NZ time. Optional: @megarifafusa shares her story.\n"
    "**Time (NZ):** feed 12:30 p.m. · story 12:35 p.m. · reel 7:00 p.m. (= Colombia: Tue 13, 6:30 p.m. and Wed 14, 1:00 a.m.)\n\n"
    "## Caption — IG / FB\n"
    "New from Fusagasugá, Colombia 🇨🇴 the Mega Rifa Fusa 🎟️\n\n"
    "1,000 numbers (000–999) · NZD 4 each\n"
    "💰 Cash prize: NZD 1,000 if the winning number was sold and paid here in NZ\n"
    "🍀 Draw: Sun 6 Dec, 4:30 p.m. NZ time, with the last 3 digits of Colombia's Lotería de Boyacá\n\n"
    f"Pick your number on the live board 👉 {URL} and send us a message. One number, one owner.\n\n"
    f"18+ only. Rules: {URL}/reglamento\n"
    "Run by Santiago · The Ber Way (@theberway) · @megarifafusa\n\n"
    "#MegaRifaFusa #ColombiansInNZ #ColombianosEnNuevaZelanda #NewZealand #Raffle #Colombia\n\n"
    "## TikTok / Reels description\n"
    f"1,000 numbers, NZD 4 each, NZD 1,000 cash prize 🎟️ Draw Sun 6 Dec, 4:30 p.m. NZ time. Pick yours: {URL}\n\n"
    "#MegaRifaFusa #ColombiansInNZ #NewZealand #Raffle\n\n"
    "## Before posting\n- How NZ buyers pay (bank transfer details) goes only in private chat, never in the post.\n")
T["semana-1/14-oct-NZ/reel.md"] = (
    "# Wed 14 Oct · NZ reel (EN)\n\n**Length:** 20–30 s · vertical · voice + hands, no face\n\n"
    "## Storyboard\n| Sec. | On camera | On-screen text |\n|---|---|---|\n"
    "| 0–5 | Hands holding the phone with the live board | Mega Rifa Fusa · now in NZ |\n"
    "| 5–12 | Finger scrolling the 000–999 grid | 1,000 numbers · NZD 4 |\n"
    "| 12–20 | `feed-EN.png` on screen | Cash prize NZD 1,000 |\n"
    "| 20–28 | End card with the link | Draw: Sun 6 Dec, 4:30 p.m. NZ · " + URL + " |\n\n"
    "## Voice-over (from `guion-de-lanzamiento.md`, NZ version)\n"
    "> New from Fusagasugá, Colombia: the Mega Rifa Fusa.\n"
    "> 1,000 numbers, NZD 4 each. Prize: NZD 1,000 if the winning number was sold here in NZ.\n"
    "> Draw: Sunday 6 December, 4:30 p.m. New Zealand time, with the Lotería de Boyacá.\n"
    "> Pick your number on the live board and message us. One number, one owner.\n\n"
    "## Audio\nYour own voice-over + an instrumental track from the app's library, low under the voice.\n")

T["semana-1/15-oct-quincena/copy.md"] = copy(
    "jue 15 oct · Quincena #1", "`feed.png` (IG + FB) · `historia.png` · reel (`reel.md`)", "Feed 8:00 a.m. · Historia 12:30 p.m. · Reel 7:00 p.m.",
    f"Cayó la quincena 💸 Date el gusto de $6.000: tu número para el sorteo del sáb 5 de diciembre.\n\n1.000 números · premio $2.000.000 si el número ganador está vendido · Lotería de Boyacá.\n\n👉 {URL} (link en la bio). Solo mayores de 18.",
    f"Quincena = buen día para escoger tu número de la rifa 😄 $6.000 y quedas jugando por $2.000.000 el 5 de diciembre. {URL} · @megarifafusa",
    tiktok=f"Cayó la quincena 💸 $6.000 por tu número para el sáb 5 dic. Premio $2.000.000. {URL} (link en el perfil)")
T["semana-1/15-oct-quincena/reel.md"] = reel(
    "jue 15 oct · Quincena", "10–15 s", "Algo cotidiano: la plata de la quincena y $6.000 que se van para un número.",
    [("0–3", "Manos sacando billetes de la billetera (sin mostrar documentos ni tarjetas)", "Cayó la quincena 💸"),
     ("3–8", "Mano separa $6.000 (un billete de 5.000 y uno de 1.000, o la app de Nu abierta **sin saldo a la vista**)", "$6.000 = tu número"),
     ("8–12", "Celular con el tablero, dedo toca un número libre", "Premio $2.000.000 · sorteo 5 dic"),
     ("12–15", "`feed.png` de hoy o el link", URL)],
    ["Cayó la quincena.", "Con seis mil pesos tienes tu número para el sorteo del 5 de diciembre.",
     "Escoge el tuyo en mega guion rifa guion fusa punto vercel punto app."],
    ["Cayó la quincena 💸", "$6.000 = tu número", "Premio $2.000.000 · sorteo 5 dic", URL],
    ["Nada de saldos, números de cuenta ni tarjetas a la vista."])

T["semana-1/16-oct-prueba-social/copy.md"] = copy(
    "vie 16 oct · Ya tienen el suyo", f"{GEN} → tipo **\"16 oct · Ya tienen el suyo\"**", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Varios ya tienen el suyo 🎟️ Quedan [QUEDAN] libres de 1.000. ¿Y tú?\n\n👉 {URL} (link en la bio)\n\nSorteo sáb 5 dic, 10:30 p.m. · Lotería de Boyacá. Solo mayores de 18.",
    f"Semana Universitaria y la rifa moviéndose 🙌 Quedan [QUEDAN] números. {URL} · @megarifafusa",
    notas=["\"Varios\" tiene que ser cierto: úsala solo si hay **10 o más pagados**. Si hay menos, usa el tipo \"Quedan X\" del generador.",
           "El calendario decía \"varios de la U\": ponlo en el texto solo si de verdad hay compradores de la U. No nombres a nadie.",
           "Si hay fotos de manos con su boleta y permiso, se pueden subir como historia aparte."])

T["semana-1/17-oct-encuesta/copy.md"] = copy(
    "sáb 17 oct · Encuesta", "`feed.png` (IG + FB) · `historia.png` **con sticker de encuesta**", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Pregunta seria 🤔 Si jugaras, ¿escogerías tu número por tu cumpleaños o por los últimos 3 de tu cédula? Te leemos 👇\n\n(Y si ya sabes cuál, míralo libre en {URL} 🎟️)",
    "Pregunta: ¿ustedes escogen número por fecha de cumpleaños o por la cédula? 😄 Voten en las historias de @megarifafusa",
    notas=["En la historia, agrega el **sticker de Encuesta** de IG en el espacio libre de arriba de Sutá, con las opciones **\"Mi cumpleaños\"** y **\"Mi cédula\"**.",
           "En FB las historias no tienen encuesta: publica la historia sin sticker o solo en IG.",
           "Al otro día, si quieres, comparte el resultado real (los porcentajes que dé IG)."])

T["semana-1/18-oct-pc1/copy.md"] = copy(
    "dom 18 oct · Recuento (punto de control 1)", f"{GEN} → tipo **\"18 oct · Recuento\"** (pagados + libres)", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"Vamos [VAN] de 1.000 🙌 Gracias a los que ya están. Quedan [QUEDAN] libres.\n\n👉 {URL} (link en la bio)\n\nSorteo sáb 5 dic, 10:30 p.m. · Lotería de Boyacá. Solo mayores de 18.",
    f"Primera semana de la rifa: vamos [VAN] de 1.000 🙌 Gracias, de verdad. Quedan [QUEDAN] en {URL} · @megarifafusa",
    notas=["[VAN] = **pagados** del Sheet (no apartados). [QUEDAN] = el número grande del tablero. Los mismos que pusiste en el generador.",
           "La meta interna del PC1 (230) **no se publica**. El post es un recuento, no una meta."])

T["semana-2/19-oct-descanso/copy.md"] = (
    "# lun 19 oct · Sin post de feed\n\n"
    "El calendario no tiene nada este día. No relleno con un post de más: descansa el feed.\n\n"
    "**Opcional:** una historia con el tipo **\"Cualquier día · Quedan X\"** del generador, con el dato real del día, y este texto:\n\n"
    f"> Quedan [QUEDAN] 🎟️ Míralos en {URL}\n")

# ---------------- Semana 2 ----------------
T["semana-2/20-oct-como-se-gana/copy.md"] = copy(
    "mar 20 oct · Cómo se gana", "`feed.png` (IG + FB) · `historia.png` · reel (`reel.md`)", "Feed 8:00 a.m. · Historia 12:30 p.m. · Reel 7:00 p.m.",
    f"¿Cómo se gana? 🍀 El sáb 5 de diciembre gana el número igual a las **últimas 3 cifras del premio mayor de la Lotería de Boyacá**.\n\nEjemplo: si el premio mayor fuera el 4217, ganaría el 217.\n\nTransparente y público: el resultado lo publica la lotería, no nosotros. Premio de $2.000.000 si el número ganador está vendido.\n\n👉 {URL} (link en la bio). Reglas: {URL}/reglamento",
    f"Por si alguien preguntaba cómo se gana: últimas 3 cifras del premio mayor de la Boyacá, sáb 5 dic 🍀 Tu número en {URL} · @megarifafusa",
    tiktok=f"¿Cómo se gana la Mega Rifa Fusa? Últimas 3 cifras del premio mayor de la Lotería de Boyacá, sáb 5 dic 🍀 {URL}")
T["semana-2/20-oct-como-se-gana/reel.md"] = reel(
    "mar 20 oct · Cómo se gana", "12–18 s", "Con papel y marcador: el número del premio mayor y cómo salen las 3 cifras.",
    [("0–3", "Mano escribe en un papel: 4 2 1 7", "¿Cómo se gana?"),
     ("3–8", "Un dedo tapa el 4", "Últimas 3 cifras del premio mayor"),
     ("8–12", "Encierra en un círculo el 217", "EJEMPLO: gana el 217"),
     ("12–18", "Celular con el tablero / `feed.png`", "Sorteo sáb 5 dic · Lotería de Boyacá")],
    ["¿Cómo se gana la Mega Rifa Fusa?", "El sábado 5 de diciembre juega la Lotería de Boyacá.",
     "Gana el número igual a las últimas tres cifras del premio mayor. Si sale el 4217, por ejemplo, gana el 217.",
     "Escoge el tuyo en mega guion rifa guion fusa punto vercel punto app."],
    ["¿Cómo se gana?", "Últimas 3 cifras del premio mayor", "EJEMPLO: gana el 217", "Sorteo sáb 5 dic · Lotería de Boyacá"],
    ["Que el rótulo diga **EJEMPLO**: el 4217 no es un resultado real."])

T["semana-2/21-oct-busca-dueno/copy.md"] = copy(
    "mié 21 oct · El ### busca dueño", f"{GEN} → tipo **\"21 oct · El ### busca dueño\"** (número libre + casilla marcada)", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"El [###] todavía busca dueño 🎟️ ¿Será el tuyo?\n\n👉 {URL} (link en la bio)\n\n$6.000 · premio $2.000.000 · sorteo sáb 5 dic, Lotería de Boyacá. Solo mayores de 18.",
    f"El [###] sigue libre en la rifa 👀 ¿Alguien que lo quiera? {URL} · @megarifafusa",
    notas=["Escoge un número **que esté libre ese mismo día** (míralo en el tablero justo antes). Reemplaza [###] por ese número.",
           "Si alguien lo aparta durante el día, edita el post o bórralo: no dejes publicado un número que ya no está libre."])

T["semana-2/22-oct-como-se-verifica/copy.md"] = copy(
    "jue 22 oct · Cómo se verifica", "`feed.png` (IG + FB) · `historia.png` · reel (`reel.md`)", "Feed 8:00 a.m. · Historia 12:30 p.m. · Reel 7:00 p.m.",
    f"Un número, un dueño 🔎 Cada número pagado sale en el tablero con el nombre de su dueño acortado (así: Dav*** G.). Quien no quiere salir aparece como Reservado. Nunca nombre completo ni teléfono.\n\nMíralo cuando quieras 👉 {URL} (link en la bio)",
    f"Algo que me importa: que todo se pueda revisar. En {URL} ves qué números están pagados, sin datos personales. @megarifafusa",
    tiktok=f"Así se verifica cada número de la Mega Rifa Fusa: tablero en vivo, nombre acortado, sin teléfonos 🔎 {URL}")
T["semana-2/22-oct-como-se-verifica/reel.md"] = reel(
    "jue 22 oct · Cómo se verifica", "15–20 s", "Grabación de pantalla del tablero: tocar un número pagado y uno libre.",
    [("0–4", "Tablero completo en el celular", "¿Cómo sé que mi número es mío?"),
     ("4–10", "Tocas un número **pagado** → la ficha muestra el nombre acortado", "Sale pagado, con nombre acortado"),
     ("10–15", "Tocas un número **libre** → \"Lo quiero\"", "Los libres siguen libres"),
     ("15–20", "Contador QUEDAN LIBRES + link", URL)],
    ["¿Cómo sabes que tu número es tuyo?", "Cuando pagas, tu número sale pagado en el tablero, con tu nombre acortado. Nada de teléfonos ni nombres completos.",
     "Lo puedes revisar cuando quieras en mega guion rifa guion fusa punto vercel punto app."],
    ["¿Cómo sé que mi número es mío?", "Sale pagado, con nombre acortado", "Los libres siguen libres", URL],
    ["Muestra solo un número cuyo dueño salga acortado o como Reservado (eso ya es público). Si todavía no hay pagados, graba solo los libres y omite la toma 2."])

T["semana-2/23-oct-frase-del-dia/copy.md"] = copy(
    "vie 23 oct · Frase del día", "`feed.png` (IG + FB) · `historia.png`", "Feed 8:00 a.m. · Historia 12:30 p.m.",
    f"«1 entre 1.000: no es un plan de vida, pero sí un buen plan de sábado.» 🎟️\n\nEl sábado es el 5 de diciembre, 10:30 p.m., con la Lotería de Boyacá. Escoge el tuyo 👉 {URL} (link en la bio)",
    f"Frase del día de la rifa 😄 «1 entre 1.000: no es un plan de vida, pero sí un buen plan de sábado.» {URL} · @megarifafusa",
    notas=["La frase sale de `07_Kit-de-Ventas/02_frases-tarjeta.md` (n.º 3)."])

for ruta, texto in T.items():
    p = os.path.join(R, ruta); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(texto); print("ok", ruta)
