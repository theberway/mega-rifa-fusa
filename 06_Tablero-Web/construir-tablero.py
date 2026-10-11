# -*- coding: utf-8 -*-
"""Construye MEGA-RIFA-FUSA-tablero.xlsx con sus hojas (esquema de S3, actualizado).

Sin funciones exclusivas de Google (nada de LET ni SPLIT): solo IF/IFERROR/
VLOOKUP/LEFT/MID/FIND/TRIM/COUNTIF, que sobreviven intactas al convertir
el .xlsx a Google Sheets.

Cambios 2026-10-09:
- Hoja HOY de primera: lo que se mira a diario, de una pantalla.
- Orden: HOY, NUMEROS, COMPRADORES, PAGOS, VENDEDORES, GASTOS, NZ, RESUMEN, LEEME.
- RESUMEN apunta al sorteo del 5 dic 2026 (antes 21 nov).
- COMPRADORES: columna nueva QUIERE_TBW (decisión 38).
- VENDEDORES!E: link real a la web.
- Colores de pestaña: verde = aquí se escribe; gris = solo se mira.
- NUMEROS: columnas de fórmula en gris claro (no se tocan); SERIAL queda a la vista
  (decisión 42: alimenta el generador privado de tarjetas).
- Texto de las notas en español colombiano (sin voseo).
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

CREMA, ROJO, AMARILLO, AZUL, NEGRO = "FFF4D6", "C1121F", "F2B705", "0A3D62", "1A1A1A"
VERDE, GRIS_TAB, GRIS_CELDA = "1E6F50", "9AA0A6", "EEEEEE"
SITIO = "mega-rifa-fusa.vercel.app"
N = 1000
FIN = N + 1  # última fila con datos

wb = openpyxl.Workbook()

hdr_font = Font(name="Arial", bold=True, color=CREMA, size=11)
hdr_fill = PatternFill("solid", fgColor=NEGRO)
gris_fill = PatternFill("solid", fgColor=GRIS_CELDA)
thin = Side(style="thin", color="BBBBBB")
borde = Border(bottom=thin)


def encabezados(ws, cols, anchos):
    for i, (c, a) in enumerate(zip(cols, anchos), start=1):
        cell = ws.cell(row=1, column=i, value=c)
        cell.font, cell.fill = hdr_font, hdr_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(i)].width = a
    ws.row_dimensions[1].height = 24
    ws.freeze_panes = "A2"


def nota(ws, fila, texto):
    c = ws.cell(row=fila, column=1, value=texto)
    c.font = Font(name="Arial", italic=True, size=9, color="777777")


# ─────────────────────────── HOY (de primera) ───────────────────────────
# Una pantalla con lo único que se mira cada día. Lee de RESUMEN (fuente única).
hoy = wb.active
hoy.title = "HOY"
hoy.sheet_properties.tabColor = GRIS_TAB
for col, w in zip("ABCD", [3, 30, 16, 48]):
    hoy.column_dimensions[col].width = w
hoy["B2"] = "MEGA RIFA FUSA · HOY"
hoy["B2"].font = Font(bold=True, size=20, color=ROJO)
hoy["B3"] = "Lo único que hay que mirar cada día. Todo se calcula solo."
hoy["B3"].font = Font(italic=True, size=10, color="777777")

kpis = [
    ("PAGADOS", "=RESUMEN!$B$3", "números con la plata verificada", AZUL),
    ("APARTADOS vivos", "=RESUMEN!$B$4", "aún no cumplen 24 h", AMARILLO),
    ("LIBRES", "=RESUMEN!$B$5", "lo que de verdad queda", VERDE),
    ("VENCIDOS por recuperar", "=RESUMEN!$B$6", "se cayeron solos: vuélvelos a ofrecer hoy", ROJO),
    ("RITMO por día", "=RESUMEN!$B$13", "para llegar al piso. Si pasa de 30, vas atrasado", NEGRO),
]
r = 5
for titulo, formula, desc, color in kpis:
    hoy.cell(row=r, column=2, value=titulo).font = Font(bold=True, size=13)
    c = hoy.cell(row=r, column=3, value=formula)
    c.font = Font(bold=True, size=22, color=color)
    c.number_format = "#,##0"
    c.alignment = Alignment(horizontal="center")
    hoy.cell(row=r, column=4, value=desc).font = Font(italic=True, size=10, color="777777")
    hoy.row_dimensions[r].height = 30
    r += 2

r += 1
hoy.cell(row=r, column=2, value="QUÉ HAGO HOY").font = Font(bold=True, size=13, color=ROJO)
pasos = [
    "1. Abro Nu y marco PAGADO lo que llegó: lleno una fila en COMPRADORES (número, nombre, teléfono, SI/NO, y SI/NO de The Ber Way).",
    "2. Reviso las filas ROJAS de NUMEROS (apartados vencidos): les escribo y, si no responden, pongo LIBRE.",
    "3. Publico la imagen del tablero con el contador real (lo de LIBRES de arriba).",
]
for i, p in enumerate(pasos):
    rr = r + 1 + i
    hoy.cell(row=rr, column=2, value=p).font = Font(size=11)
    hoy.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
    hoy.cell(row=rr, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    hoy.row_dimensions[rr].height = 30
nota(hoy, r + 5, "Para el detalle de la plata y las metas de cada domingo, mira la pestaña RESUMEN.")


# ─────────────────────────── NUMEROS ───────────────────────────
ws = wb.create_sheet("NUMEROS")
ws.sheet_properties.tabColor = VERDE
encabezados(
    ws,
    ["NUMERO", "ESTADO_MANUAL", "HORA_APARTADO", "VENDEDOR", "NOMBRE_PUBLICO",
     "SERIAL", "ESTADO", "VENCE_A", "NOTA"],
    [10, 16, 18, 12, 18, 11, 12, 14, 30],
)


def nom(f):
    return f'VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE)'


def resto(f):
    return f'TRIM(MID({nom(f)}&" ",FIND(" ",{nom(f)}&" ")+1,99))'


for i in range(N):
    f = i + 2
    ws.cell(row=f, column=1, value=f"{i:03d}").number_format = "@"
    ws.cell(row=f, column=2, value="LIBRE")
    ws.cell(row=f, column=3).number_format = "dd/mm/yyyy hh:mm"
    ws.cell(row=f, column=6,
            value=f'=IF($B{f}="PAGADO",MID("ABCDEFGHIJ",INT(VALUE($A{f})/100)+1,1)&"-"&$A{f},"")')
    ws.cell(row=f, column=7,
            value=f'=IF($B{f}="PAGADO","PAGADO",IF($B{f}="APARTADO",'
                  f'IF(NOT(ISNUMBER($C{f})),"APARTADO",'
                  f'IF($C{f}<1,"APARTADO",'
                  f'IF(NOW()-$C{f}>1,"LIBRE","APARTADO"))),"LIBRE"))')
    ws.cell(row=f, column=5,
            value=f'=IF($G{f}<>"PAGADO","",IFERROR('
                  f'IF(VLOOKUP($A{f},COMPRADORES!$A:$D,4,FALSE)="NO","Reservado",'
                  f'LEFT({nom(f)},3)&"***"&'
                  f'IF({resto(f)}="",""," "&LEFT({resto(f)},1)&".")'
                  f'),""))')
    ws.cell(row=f, column=8,
            value=f'=IF($G{f}<>"APARTADO","",'
                  f'IF(NOT(ISNUMBER($C{f})),"FALTA LA HORA",'
                  f'IF($C{f}<1,"FALTA LA FECHA",TEXT($C{f}+1,"dd/mm hh:mm"))))')
    for col in (1, 6, 7):
        ws.cell(row=f, column=col).alignment = Alignment(horizontal="center")
    # columnas de fórmula en gris claro: NO se tocan (E, F, G, H)
    for col in (5, 6, 7, 8):
        ws.cell(row=f, column=col).fill = gris_fill

rango = f"A2:I{FIN}"
ws.conditional_formatting.add(rango, FormulaRule(
    formula=[f'$G2="PAGADO"'], fill=PatternFill("solid", fgColor=AZUL),
    font=Font(color=CREMA, bold=True)))
ws.conditional_formatting.add(rango, FormulaRule(
    formula=[f'AND($B2="APARTADO",$G2="LIBRE")'], fill=PatternFill("solid", fgColor=ROJO),
    font=Font(color=CREMA, bold=True)))
ws.conditional_formatting.add(rango, FormulaRule(
    formula=[f'$G2="APARTADO"'], fill=PatternFill("solid", fgColor=AMARILLO),
    font=Font(color=NEGRO)))

nota(ws, FIN + 2, "NO ESCRIBAS EN LA COLUMNA E: es una fórmula. Los nombres van en la hoja COMPRADORES.")
nota(ws, FIN + 3, "Si escribes un nombre en E, ese nombre completo QUEDA PUBLICADO en la web.")
nota(ws, FIN + 4, "Columnas grises (E, F, G, H) = fórmulas, no se tocan. Solo escribes en B (estado), D (vendedor) y I (nota).")

dv = DataValidation(type="list", formula1='"LIBRE,APARTADO,PAGADO"', allow_blank=False)
dv.error = "Solo LIBRE, APARTADO o PAGADO."
dv.errorTitle = "Estado no válido"
ws.add_data_validation(dv)
dv.add(f"B2:B{FIN}")

dvv = DataValidation(type="list", formula1=f"=VENDEDORES!$A$2:$A$20", allow_blank=True)
dvv.error = "Ese código no está en la hoja VENDEDORES."
dvv.errorTitle = "Vendedor desconocido"
ws.add_data_validation(dvv)
dvv.add(f"D2:D{FIN}")

# ─────────────────────────── COMPRADORES ───────────────────────────
ws = wb.create_sheet("COMPRADORES")
ws.sheet_properties.tabColor = VERDE
encabezados(ws, ["NUMERO", "NOMBRE_COMPLETO", "TELEFONO", "SALE_PUBLICO", "QUIERE_TBW"],
            [10, 34, 16, 15, 14])
for f in range(2, 302):
    ws.cell(row=f, column=1).number_format = "@"
    ws.cell(row=f, column=3).number_format = "@"
dvs = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
ws.add_data_validation(dvs)
dvs.add("D2:D1001")
dvt = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
ws.add_data_validation(dvt)
dvt.add("E2:E1001")
nota(ws, 303, "ESTA HOJA NO SE PUBLICA NI SE COMPARTE. Es la única con nombres completos y teléfonos.")
nota(ws, 304, "SALE_PUBLICO = NO  ->  ese número se ve en el tablero como «Reservado», sin nombre.")
nota(ws, 305, "QUIERE_TBW = SI  ->  dijo que SÍ quiere saber de The Ber Way (decisión 38). Vacío o NO = no se le escribe.")

# ─────────────────────────── PAGOS ───────────────────────────
ws = wb.create_sheet("PAGOS")
ws.sheet_properties.tabColor = VERDE
encabezados(ws, ["FECHA_HORA", "NUMEROS", "CANTIDAD", "MONEDA", "MONTO",
                 "MONTO_COP", "MEDIO", "VENDEDOR", "VERIFICADO_POR", "COMPROBANTE"],
            [18, 22, 10, 10, 14, 14, 12, 12, 15, 30])
for f in range(2, 402):
    ws.cell(row=f, column=1).number_format = "dd/mm/yyyy hh:mm"
    ws.cell(row=f, column=6, value=f'=IF($E{f}="","",IF($D{f}="NZD",$E{f}*NZ!$B$1,$E{f}))')
    ws.cell(row=f, column=6).fill = gris_fill
    for c in (5, 6):
        ws.cell(row=f, column=c).number_format = '#,##0'
dvm = DataValidation(type="list", formula1='"COP,NZD"', allow_blank=True)
ws.add_data_validation(dvm); dvm.add("D2:D401")
dvmed = DataValidation(type="list", formula1='"BRE-B,EFECTIVO,TIENDA,NZ"', allow_blank=True)
ws.add_data_validation(dvmed); dvmed.add("G2:G401")
dvver = DataValidation(type="list", formula1='"SANTIAGO,SOFIA"', allow_blank=True)
ws.add_data_validation(dvver); dvver.add("I2:I401")
nota(ws, 403, "Una fila entra acá SOLO cuando la plata ya se ve dentro de la app que recibe.")
nota(ws, 404, "Un pantallazo de «enviado» no es un pago: mientras tanto el número sigue APARTADO y puede vencerse.")
nota(ws, 405, "La columna MONTO_COP (gris) es fórmula: convierte los NZD con la tasa de NZ!B1. No se escribe a mano.")

# ─────────────────────────── VENDEDORES ───────────────────────────
ws = wb.create_sheet("VENDEDORES")
ws.sheet_properties.tabColor = VERDE
encabezados(ws, ["CODIGO", "NOMBRE", "TIPO", "WHATSAPP", "LINK",
                 "VENDIDOS", "APARTADOS", "COMISION", "ESTADO"],
            [10, 26, 12, 16, 40, 11, 12, 13, 11])
codigos = ([(f"V{i:02d}", "VENDEDOR") for i in range(1, 13)]
           + [(f"T{i:02d}", "TIENDA") for i in range(1, 4)]
           + [("N01", "NZ"), ("N02", "NZ"), ("SBG", "VENDEDOR"), ("DIR", "VENDEDOR")])
for i, (cod, tipo) in enumerate(codigos):
    f = i + 2
    ws.cell(row=f, column=1, value=cod).font = Font(name="Consolas", bold=True)
    ws.cell(row=f, column=3, value=tipo)
    ws.cell(row=f, column=4).number_format = "@"
    ws.cell(row=f, column=5, value=f'="https://{SITIO}/?v=" & $A{f}')
    for col in (5, 6, 7, 8):
        ws.cell(row=f, column=col).fill = gris_fill
    ws.cell(row=f, column=6, value=f'=COUNTIFS(NUMEROS!$D:$D,$A{f},NUMEROS!$G:$G,"PAGADO")')
    ws.cell(row=f, column=7, value=f'=COUNTIFS(NUMEROS!$D:$D,$A{f},NUMEROS!$G:$G,"APARTADO")')
    ws.cell(row=f, column=8, value=f'=IF($C{f}="TIENDA",$F{f}*600,0)')
    ws.cell(row=f, column=8).number_format = '#,##0'
    ws.cell(row=f, column=9, value="ACTIVO")
ws.cell(row=17, column=2, value="Sofía")
ws.cell(row=18, column=2, value="Reserva de Sofía")
ws.cell(row=19, column=2, value="Santiago (venta directa)")
ws.cell(row=20, column=2, value="Sin vendedor (llegó por el Canal o un Estado)")
dve = DataValidation(type="list", formula1='"ACTIVO,INACTIVO"', allow_blank=True)
ws.add_data_validation(dve); dve.add("I2:I20")
nota(ws, 22, "ESTA HOJA NO SE PUBLICA: tiene nombres completos y teléfonos.")
nota(ws, 23, "La columna LINK ya trae el link real de cada vendedor. Solo llena NOMBRE y WHATSAPP.")
nota(ws, 25, "Puedes cambiar el código (V01) por el NOMBRE del vendedor, en MAYÚSCULAS, sin tildes ni espacios: ANGELICA, MARIAJOSE, JUANP. El link, los conteos y la lista del tablero se ajustan solos. Dos iguales: ANGELICA, ANGELICA2.")
nota(ws, 24, "Columnas grises (LINK, VENDIDOS, APARTADOS, COMISION) = fórmulas, no se tocan.")

# ─────────────────────────── GASTOS ───────────────────────────
ws = wb.create_sheet("GASTOS")
ws.sheet_properties.tabColor = VERDE
encabezados(ws, ["FECHA", "CONCEPTO", "MONTO_COP", "CATEGORIA", "PAGADO"],
            [14, 34, 14, 14, 10])
fijos = [("Premio en efectivo", 2000000, "PREMIO"),
         ("Bono al vendedor estrella", 100000, "VENDEDOR"),
         ("Varios (impresiones, transporte)", 50000, "VARIOS")]
for i, (con, monto, cat) in enumerate(fijos):
    f = i + 2
    ws.cell(row=f, column=1).number_format = "dd/mm/yyyy"
    ws.cell(row=f, column=2, value=con)
    ws.cell(row=f, column=3, value=monto).number_format = '#,##0'
    ws.cell(row=f, column=4, value=cat)
    ws.cell(row=f, column=5, value="NO")
for f in range(5, 102):
    ws.cell(row=f, column=1).number_format = "dd/mm/yyyy"
    ws.cell(row=f, column=3).number_format = '#,##0'
dvc = DataValidation(type="list", formula1='"PREMIO,VENDEDOR,TIENDAS,TIZUMBA,VARIOS"', allow_blank=True)
ws.add_data_validation(dvc); dvc.add("D2:D101")
dvp = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
ws.add_data_validation(dvp); dvp.add("E2:E101")

# ─────────────────────────── NZ ───────────────────────────
ws = wb.create_sheet("NZ")
ws.sheet_properties.tabColor = VERDE
ws["A1"] = "TASA COP POR NZD"
ws["A1"].font = Font(bold=True)
ws["B1"] = 1843
ws["B1"].font = Font(bold=True, size=14)
ws["B1"].fill = PatternFill("solid", fgColor=AMARILLO)
ws["C1"] = "Si se cambia, se anota en el registro de decisiones. PAGOS!F la lee de acá."
ws["C1"].font = Font(italic=True, size=9, color="777777")
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 12
ws.column_dimensions["C"].width = 60
for i, c in enumerate(["FECHA", "NUMEROS", "NZD", "COP_EQUIV", "EN_CUENTA_DE_SOFIA", "NOTA"], start=1):
    cell = ws.cell(row=3, column=i, value=c)
    cell.font, cell.fill = hdr_font, hdr_fill
    cell.alignment = Alignment(horizontal="center")
for w, col in zip([14, 22, 10, 14, 20, 30], "ABCDEF"):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A4"
for f in range(4, 204):
    ws.cell(row=f, column=1).number_format = "dd/mm/yyyy"
    ws.cell(row=f, column=4, value=f'=IF($C{f}="","",$C{f}*$B$1)')
    ws.cell(row=f, column=4).number_format = '#,##0'
    ws.cell(row=f, column=4).fill = gris_fill
dvnz = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
ws.add_data_validation(dvnz); dvnz.add("E4:E203")
nota(ws, 205, "La plata de NZ no viaja. Se queda en la cuenta de Sofía y entra al total como equivalente.")

# ─────────────────────────── RESUMEN ───────────────────────────
ws = wb.create_sheet("RESUMEN")
ws.sheet_properties.tabColor = GRIS_TAB
ws.column_dimensions["A"].width = 32
ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 54
ws["A1"] = "MEGA RIFA FUSA — resumen"
ws["A1"].font = Font(bold=True, size=16, color=ROJO)
filas = [
    ("Pagados", '=COUNTIF(NUMEROS!$G:$G,"PAGADO")', "Números con la plata ya verificada", '#,##0'),
    ("Apartados vivos", '=COUNTIF(NUMEROS!$G:$G,"APARTADO")', "Apartados que todavía no cumplen 24 h", '#,##0'),
    ("Libres", '=1000-$B$3-$B$4', "Lo que de verdad queda", '#,##0'),
    ("Vencidos por recuperar", '=COUNTIFS(NUMEROS!$B:$B,"APARTADO",NUMEROS!$G:$G,"LIBRE")', "Se cayeron solos: hay que volver a ofrecerlos hoy", '#,##0'),
    ("Plata recibida (COP)", '=SUM(PAGOS!$F:$F)', "Todo lo que entró, con NZ convertido", '"$"#,##0'),
    ("Gastos ya pagados", '=SUMIF(GASTOS!$E:$E,"SI",GASTOS!$C:$C)', "Solo los que dicen PAGADO = SI", '"$"#,##0'),
    ("Comisión de tiendas", '=SUM(VENDEDORES!$H:$H)', "10% = COP 600 por número de tienda", '"$"#,##0'),
    ("NETO PROYECTADO", '=$B$7-2000000-100000-50000-$B$9', "Lo que queda después del premio y los costos fijos", '"$"#,##0'),
    ("Faltan para el piso (3M)", '=MAX(0,3000000-$B$10)', "Si llega a 0, la moto está asegurada", '"$"#,##0'),
    ("Días para el sorteo", '=MAX(0,DATE(2026,12,5)-TODAY())', "Hasta el sáb 5 de diciembre", '#,##0'),
    ("RITMO NECESARIO POR DÍA", '=IF($B$12>0,ROUNDUP((860-$B$3)/$B$12,0),0)', "Si pasa de 30, la campaña va atrasada", '#,##0'),
]
for i, (k, f, nota_txt, fmt) in enumerate(filas):
    r = i + 3
    ws.cell(row=r, column=1, value=k).font = Font(bold=(k.isupper()), size=11)
    c = ws.cell(row=r, column=2, value=f)
    c.font = Font(bold=True, size=13)
    c.number_format = fmt
    c.alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=3, value=nota_txt).font = Font(italic=True, size=9, color="777777")
for r in (10, 13):
    ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=AMARILLO)
    ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=AMARILLO)
ws.freeze_panes = "A2"
nota(ws, 15, "El número que importa es el RITMO NECESARIO POR DÍA. Se mira cada domingo en el punto de control.")

# ─────────────────────────── LEEME (al final) ───────────────────────────
ws = wb.create_sheet("LEEME")
ws.sheet_properties.tabColor = GRIS_TAB
ws.column_dimensions["A"].width = 100
lineas = [
    ("MEGA RIFA FUSA — cómo se usa este archivo", True),
    ("", False),
    ("Solo escribes en DOS momentos:", True),
    ("1. Alguien aparta un número  ->  en NUMEROS, columna B, pones APARTADO. La hora se pone sola.", False),
    ("2. Llega la plata y la ves en la app  ->  en COMPRADORES llenas UNA fila:", False),
    ("     número, nombre completo, teléfono, SALE_PUBLICO (SI/NO) y QUIERE_TBW (SI/NO).", False),
    ("     Al llenar esa fila, el número queda PAGADO solo, con su nombre acortado y su serial.", False),
    ("", False),
    ("Y anotas la plata en PAGOS (una fila por pago que entró).", False),
    ("", False),
    ("Lo demás se calcula solo. Las columnas grises son fórmulas: NO se tocan.", True),
    ("La columna E de NUMEROS es la trampa: parece normal pero es fórmula y es la única pública.", False),
    ("Si escribes un nombre ahí, ese nombre completo queda publicado en la web.", False),
    ("", False),
    ("Pestañas verdes = aquí se escribe (NUMEROS, COMPRADORES, PAGOS, VENDEDORES, GASTOS, NZ).", False),
    ("Pestañas grises = solo se miran (HOY, RESUMEN, LEEME).", False),
    ("Cada mañana mira la pestaña HOY. Cada domingo, la pestaña RESUMEN.", False),
]
for i, (txt, bold) in enumerate(lineas, start=1):
    c = ws.cell(row=i, column=1, value=txt)
    c.font = Font(bold=bold, size=12 if bold else 11, color=(ROJO if (bold and i == 1) else NEGRO))
    c.alignment = Alignment(wrap_text=True, vertical="top")

wb.save("D:/Mis documentos/Documents/Work/The_Ber_Way/02_Clients/Santiago_Bermudez_Gomez/Mega-Rifa-Fusa/06_Tablero-Web/MEGA-RIFA-FUSA-tablero.xlsx")
print("listo")
