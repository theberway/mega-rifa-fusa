# Esquema del Google Sheet — Mega Rifa Fusa

*Sesión 3. Fuente de verdad del dato de la rifa. La web solo lee de aquí.*

> **El archivo ya está armado: `MEGA-RIFA-FUSA-tablero.xlsx`, en esta misma carpeta.**
> Las 9 hojas, las 1.000 filas, las 4 fórmulas, los 3 colores del formato condicional, las listas desplegables y los 19 códigos de vendedor ya están adentro, y las fórmulas se verificaron **recalculando el archivo**, no solo escribiéndolas (los casos de prueba están al final).
>
> **Lo que falta hacer, y solo lo puedes hacer tú** (necesita tu cuenta de Google, y yo no entro a cuentas):
> 1. Subir el archivo a Google Drive.
> 2. Abrirlo y **Archivo → Guardar como Hoja de cálculo de Google**. Ahí deja de ser un Excel y se vuelve un Sheet de verdad.
> 3. **Archivo → Configuración → Cálculo → Recalcular: "Al cambiar y cada minuto"**, y **Zona horaria: (GMT-05:00) Bogotá**.
> 4. **Compartir → Acceso general → Restringido.**
> 5. **Archivo → Compartir → Publicar en la web → `NUMEROS` → `.csv` → Publicar**, y me pasás ese link.
>
> 6. **Instalar el script de la hora** (`script-tablero.gs`, en esta misma carpeta): Extensiones → Apps Script → pegar → guardar. Un minuto, sin permisos.
>
> El resto de este documento explica qué hace cada hoja y cada fórmula, por si alguna vez hay que tocarlas o rehacerlas.

El Sheet se llama **`MEGA RIFA FUSA — tablero`**. Nueve hojas, en este orden: `HOY`, `NUMEROS`, `COMPRADORES`, `PAGOS`, `VENDEDORES`, `GASTOS`, `NZ`, `RESUMEN`, `LEEME`.

**`HOY`** y **`LEEME`** son las dos hojas nuevas (9 oct): `HOY` es la pantalla del día (5 cifras grandes que lee de `RESUMEN` + los 3 pasos del día); `LEEME` explica en 12 renglones que solo se escribe en dos lugares. Las pestañas van con color: **verde = aquí se escribe** (`NUMEROS`, `COMPRADORES`, `PAGOS`, `VENDEDORES`, `GASTOS`, `NZ`), **gris = solo se mira** (`HOY`, `RESUMEN`, `LEEME`).

**Solo se publica `NUMEROS`.** Las otras ocho tienen nombres completos, cifras, teléfonos y plata, y no salen nunca del archivo. Por eso los nombres completos viven en `COMPRADORES` y lo único que llega a `NUMEROS` es el nombre ya acortado, calculado por fórmula.

Dos ajustes que si no se hacen, rompen el resto (son los pasos 3 de arriba):

1. **Archivo → Configuración → Cálculo → Recalcular: "Al cambiar y cada minuto"**. Sin esto la fórmula de vencimiento a 24 h se queda congelada y los apartados nunca se liberan.
2. **Archivo → Configuración → Zona horaria: (GMT-05:00) Bogotá**. Los apartados de Nueva Zelanda se registran en hora de Colombia, igual que todo lo demás, para que la cuenta de 24 h sea una sola.

Las fórmulas de abajo van con **coma** como separador, que es como quedaron escritas en el archivo y como las lee Google al convertirlo. Si alguna vez las escribes a mano en un Sheet configurado en español, puede pedirte `;` en vez de `,`.

Tampoco usan `LET` ni `SPLIT`, que son solo de Google: así el mismo archivo abre bien en Excel y en Sheets, y la conversión no las rompe.

---

## 1. Hoja `NUMEROS` — 1.000 filas, una por número

Fila 1 = encabezados. Filas 2 a 1001 = los números 000 a 999.

| Col | Encabezado | Quién lo llena | Qué es |
|---|---|---|---|
| A | `NUMERO` | se genera una vez | `000` a `999`, **como texto**, con los ceros adelante |
| B | `ESTADO_MANUAL` | el vendedor / Santiago | `LIBRE`, `APARTADO` o `PAGADO`. Lo único que se escribe a mano |
| C | `HORA_APARTADO` | **el script** | Fecha y hora en que se apartó. Se escribe sola al poner `APARTADO` en B |
| D | `VENDEDOR` | el vendedor / Santiago | Código de `VENDEDORES` (ej. `V01`) |
| E | `NOMBRE_PUBLICO` | **fórmula** | `Dav*** G.` o `Reservado`. Lo calcula desde `COMPRADORES`. ⚠️ **Acá no se escribe nada a mano: lo que se escriba acá queda publicado tal cual en la web** |
| F | `SERIAL` | fórmula | El folio de la tarjeta-boleta |
| G | `ESTADO` | **fórmula** | Lo que de verdad vale. Es lo que lee la web |
| H | `VENCE_A` | fórmula | A qué hora se suelta este apartado |
| I | `NOTA` | libre | "paga el viernes", "es de NZ", lo que sea |

### Las tres fórmulas (fila 2, y se arrastran hasta la 1001)

**F2 — serial.** Letra del bloque de cien + el número. El `000` da `A-000`, el `450` da `E-450`.

```
=IF($B2="PAGADO",MID("ABCDEFGHIJ",INT(VALUE($A2)/100)+1,1)&"-"&$A2,"")
```

**G2 — estado real, con el vencimiento automático a 24 h.** Decisión 33.

```
=IF($B2="PAGADO","PAGADO",IF($B2="APARTADO",IF(NOT(ISNUMBER($C2)),"APARTADO",IF($C2<1,"APARTADO",IF(NOW()-$C2>1,"LIBRE","APARTADO"))),"LIBRE"))
```

Se lee así: pagado manda siempre y no vence nunca. Un apartado con más de 24 h cumplidas **se muestra LIBRE**, aunque la columna B siga diciendo `APARTADO`.

Los otros dos casos son defensas que costaron un susto real el 5 de octubre:

- **Sin hora** → se trata como apartado. Un olvido no le regala el número a otro.
- **Hora sin fecha** (escribir `11:20` en vez de `05/10/2026 11:20`) → también apartado. Para Sheets, `11:20` solo es el **30 de diciembre de 1899** a las 11:20, así que la cuenta de 24 h da más de 46.000 días y el número se soltaba al instante. Antes eso pasaba en silencio; ahora el número se queda apartado y la columna `VENCE_A` dice **`FALTA LA FECHA`**.

**E2 — el nombre público, acortado.** Decisión 35. Busca el comprador en `COMPRADORES`, respeta el "no quiero salir" y devuelve las 3 primeras letras del nombre de pila + la inicial del apellido.

```
=IF($G2<>"PAGADO","",IFERROR(IF(VLOOKUP($A2,COMPRADORES!$A:$D,4,FALSE)="NO","Reservado",LEFT(VLOOKUP($A2,COMPRADORES!$A:$D,2,FALSE),3)&"***"&IF(TRIM(MID(VLOOKUP($A2,COMPRADORES!$A:$D,2,FALSE)&" ",FIND(" ",VLOOKUP($A2,COMPRADORES!$A:$D,2,FALSE)&" ")+1,99))="",""," "&LEFT(TRIM(MID(VLOOKUP($A2,COMPRADORES!$A:$D,2,FALSE)&" ",FIND(" ",VLOOKUP($A2,COMPRADORES!$A:$D,2,FALSE)&" ")+1,99)),1)&".")),""))
```

Es larga porque busca el nombre completo cuatro veces, pero no hace nada raro: corta las 3 primeras letras del nombre de pila, le pega `***`, y si hay un apellido le agrega su inicial.

Tres cosas que hace sola, y por eso no se escribe a mano: un número que no está pagado no muestra nombre; un comprador sin fila en `COMPRADORES` queda en blanco en vez de romper la hoja; y nadie puede escribir por error un nombre completo en la columna que **sí** se publica.

**H2 — a qué hora vence.**

```
=IF($G2<>"APARTADO","",IF(NOT(ISNUMBER($C2)),"FALTA LA HORA",IF($C2<1,"FALTA LA FECHA",TEXT($C2+1,"dd/mm hh:mm"))))
```

### Formato condicional (para leerlo de un vistazo)

Rango `$A$2:$I$1001`, tres reglas con **fórmula personalizada**:

| Regla | Fórmula | Relleno |
|---|---|---|
| Pagado | `=$G2="PAGADO"` | azul `#0A3D62`, texto crema |
| Apartado | `=$G2="APARTADO"` | amarillo `#F2B705`, texto negro |
| Vencido (atención) | `=AND($B2="APARTADO"; $G2="LIBRE")` | rojo `#C1121F`, texto crema |

La tercera es la importante: son los que se cayeron y hay que volver a ofrecer. Cada mañana se filtra por ella, se le escribe al que apartó y si no responde se cambia la B a `LIBRE`.

### Validación de datos

- **B**: lista desplegable `LIBRE`, `APARTADO`, `PAGADO`. Rechazar lo que no esté en la lista.
- **D**: lista desde un rango → `VENDEDORES!$A$2:$A$30`.
- **A, F**: formato **Texto sin formato**, si no Sheets borra los ceros de adelante.

### ⚠️ La columna E no se escribe a mano

Es la única columna pública que parece una celda normal, y por eso es la trampa del Sheet. Si alguien escribe `Jorge Perez` ahí:

1. Se borra la fórmula de esa fila, para siempre.
2. Ese nombre completo **sale publicado en el CSV y en la web**, visible para cualquiera.
3. Deja de limpiarse sola: si el número vuelve a `LIBRE`, el nombre se queda ahí.

Pasó el 5 de octubre en las pruebas, con cuatro nombres completos. Los nombres van **siempre** en la hoja `COMPRADORES`, que no se publica.

Vale la pena blindarla: **seleccionar `E2:E1001` → clic derecho → Ver más acciones → Proteger rango → Mostrar una advertencia al editar.** No lo impide, pero avisa antes.

### El script que pone la hora

Una fórmula **no puede** saber cuándo cambió una celda: `NOW()` se recalcula cada minuto, así que una hora puesta con fórmula se movería sola y el apartado no vencería jamás. Por eso la hora la escribe un script, no una fórmula.

Está en `script-tablero.gs`, que además trae `repararTodo()`: una función que se corre a mano y repone las fórmulas de `E`, `F`, `G` y `H` en las 1.000 filas, arregla el formato de la columna `C` y lista las horas que quedaron sin fecha. Es la red de seguridad para cuando alguien escriba encima de una fórmula.

Se instala una sola vez: **Extensiones → Apps Script**, pegar todo, guardar, y ejecutar `repararTodo` (pide permiso la primera vez, porque escribe en la hoja; `onEdit` después corre solo).

Qué hace al tocar la columna B de `NUMEROS`:

| Si se pone | Pasa |
|---|---|
| `APARTADO` | Escribe la fecha y hora en `C`, **solo si estaba vacía** — así corregir otra celda no reinicia el reloj de las 24 h |
| `LIBRE` | **Borra `C` y `D`.** El vendedor se borra a propósito: un código viejo le sumaría la venta a quien ya no tiene el número |
| `PAGADO` | No toca nada. Queda constancia de a qué hora se había apartado |

Funciona también si se pega un bloque de varias filas de una.

**Si Apps Script no abre** ("No se pudo abrir el archivo en este momento"), casi siempre es que el navegador tiene varias cuentas de Google abiertas y Apps Script arranca con la que no es dueña del Sheet. Se resuelve entrando a `script.google.com` con la cuenta correcta, o abriendo el Sheet en una ventana de incógnito con esa sola cuenta.

**Si de verdad no se puede usar Apps Script** (una cuenta institucional puede tenerlo bloqueado por el administrador), el plan B es escribir la hora a mano con **`Ctrl+Alt+Shift+;`** al poner `APARTADO`, más una alarma visual para que un olvido no pase desapercibido. Regla de formato condicional sobre `A2:I1001`, fórmula personalizada:

```
=AND($B2="APARTADO"; $C2="")
```

con relleno rojo. Esa fila queda gritando hasta que alguien le ponga la hora. Es peor que el script —depende de que alguien mire— pero evita que un número quede apartado para siempre en silencio.

---

## 2. Hoja `COMPRADORES` — **no se publica nunca**

Es la única hoja con nombres completos de compradores. Una fila por número vendido.

| Col | Encabezado | Qué es |
|---|---|---|
| A | `NUMERO` | El número, como texto con ceros. Es la llave que busca `NUMEROS!E` |
| B | `NOMBRE_COMPLETO` | Como lo dio la persona: `David Gómez Pérez` |
| C | `TELEFONO` | Para avisarle si gana y para el acta |
| D | `SALE_PUBLICO` | `SI` o `NO`. Lista desplegable. **`SI` por defecto** |
| E | `QUIERE_TBW` | `SI` o `NO`. Lista desplegable. **La respuesta del comprador a la pregunta de The Ber Way** (decisión 38). Vacío o `NO` = no se le escribe. No afecta el tablero |

`SALE_PUBLICO = NO` hace que el tablero muestre ese número como **`Reservado`**: se ve azul, se ve vendido, pero sin nombre. Nadie queda obligado a salir y el contador sigue siendo real.

Al vender, el vendedor pregunta una sola cosa, en una frase: *"¿Te molesta que tu número salga en el tablero como Dav*** G.?"*. Si dice que sí le molesta, `NO`.

**Esta hoja es la que se llena al vender.** Llenar la fila completa deja el número `PAGADO` solo: el script lo marca en `NUMEROS` apenas se escribe el `SI`/`NO`, que es la última celda de la fila. No hay que ir a `NUMEROS` a marcar nada.

Se dispara con la columna D a propósito: para cuando se escribe ahí, el número, el nombre y el teléfono ya están puestos. Si se escribe un número que no existe, no hace nada.

**Esta hoja no se publica, no se comparte y no se manda por chat.** Si alguien necesita ver el tablero, se le pasa la web, no el archivo.

---

## 3. Hoja `PAGOS` — un renglón por plata que entró

| Col | Encabezado | Qué es |
|---|---|---|
| A | `FECHA_HORA` | Cuándo **se vio la plata en la app**, no cuándo prometieron |
| B | `NUMEROS` | Los números que cubre, separados por coma: `045, 046` |
| C | `CANTIDAD` | Cuántos números |
| D | `MONEDA` | `COP` o `NZD` |
| E | `MONTO` | Lo que llegó, en esa moneda |
| F | `MONTO_COP` | `=IF($E2="","",IF($D2="NZD",$E2*NZ!$B$1,$E2))` — **lee la tasa de `NZ!B1`**, no un número duro |
| G | `MEDIO` | `BRE-B`, `EFECTIVO`, `TIENDA`, `NZ` |
| H | `VENDEDOR` | Código |
| I | `VERIFICADO_POR` | `SANTIAGO` o `SOFIA` |
| J | `COMPROBANTE` | Link a la captura, o `EFECTIVO EN MANO` |

**La regla que no se negocia (regla fija 4)**: una fila entra a `PAGOS` **solo** cuando la plata está dentro de la app que recibe. Un pantallazo de "enviado" no es un pago. Mientras no esté, el número sigue `APARTADO` y puede vencerse.

La tasa vive en **un solo lugar, `NZ!B1`** (hoy `1843`). `PAGOS!F` la lee de ahí, así que para cambiarla se toca una sola celda y se anota en el registro de decisiones.

---

## 4. Hoja `VENDEDORES`

| Col | Encabezado | Qué es |
|---|---|---|
| A | `CODIGO` | `V01`… ver `codigos-de-vendedores.md` |
| B | `NOMBRE` | Nombre completo — **esta hoja no se publica** |
| C | `TIPO` | `VENDEDOR`, `TIENDA`, `NZ` |
| D | `WHATSAPP` | Para escribirle |
| E | `LINK` | `=“https://…/?v=”&$A2` — su link propio |
| F | `VENDIDOS` | `=COUNTIFS(NUMEROS!$D:$D; $A2; NUMEROS!$G:$G; "PAGADO")` |
| G | `APARTADOS` | `=COUNTIFS(NUMEROS!$D:$D; $A2; NUMEROS!$G:$G; "APARTADO")` |
| H | `COMISION` | `=IF($C2="TIENDA"; $F2*600; 0)` — el 10% solo a tiendas |
| I | `ESTADO` | `ACTIVO` o `INACTIVO` |

---

## 5. Hoja `GASTOS`

| Col | Encabezado |
|---|---|
| A | `FECHA` |
| B | `CONCEPTO` |
| C | `MONTO_COP` |
| D | `CATEGORIA` — `PREMIO`, `VENDEDOR`, `TIENDAS`, `TIZUMBA`, `VARIOS` |
| E | `PAGADO` — `SI` / `NO` |

Arranca con tres filas fijas, que son los costos que ya se sabe que existen: premio `2.000.000`, vendedor estrella `100.000`, varios `50.000`.

---

## 6. Hoja `NZ`

`B1` = tasa COP por NZD: **1843**. Es la celda que `PAGOS!F` **ya lee**; para cambiar la tasa se cambia solo acá.

| Col | Encabezado |
|---|---|
| A | `FECHA` |
| B | `NUMEROS` |
| C | `NZD` |
| D | `COP_EQUIV` — `=$C2*$B$1` |
| E | `EN_CUENTA_DE_SOFIA` — `SI` / `NO` |
| F | `NOTA` |

La plata de NZ **no viaja**. Se queda en la cuenta de Sofía y entra al total como equivalente; si el número ganador se vendió allá, se paga allá (NZD 1.000, piso COP 1.900.000). Eso ya está decidido, acá solo se registra.

---

## 7. Hoja `RESUMEN` — lo que se mira cada día

| Celda | Qué | Fórmula |
|---|---|---|
| `B1` | Pagados | `=COUNTIF(NUMEROS!$G:$G; "PAGADO")` |
| `B2` | Apartados vivos | `=COUNTIF(NUMEROS!$G:$G; "APARTADO")` |
| `B3` | Libres | `=1000-$B$1-$B$2` |
| `B4` | Vencidos por recuperar | `=COUNTIFS(NUMEROS!$B:$B; "APARTADO"; NUMEROS!$G:$G; "LIBRE")` |
| `B5` | Plata recibida (COP) | `=SUM(PAGOS!$F:$F)` |
| `B6` | Gastos pagados | `=SUMIF(GASTOS!$E:$E; "SI"; GASTOS!$C:$C)` |
| `B7` | Comisión de tiendas | `=SUM(VENDEDORES!$H:$H)` |
| `B8` | **Neto proyectado** | `=$B$5-2000000-100000-50000-$B$7` |
| `B9` | Faltan para el piso | `=MAX(0; 3000000-$B$8)` |
| `B10` | Días para el sorteo | `=MAX(0,DATE(2026,12,5)-TODAY())` — **al sáb 5 dic** |
| `B11` | Ritmo necesario | `=IF($B$10>0; ROUNDUP((860-$B$1)/$B$10; 0); 0)` |

`B11` es el número que importa: **cuántos hay que vender por día desde hoy** para llegar al piso de 860. Si ese número pasa de 30, la campaña va atrasada y toca mover algo (ese es el criterio de los puntos de control del domingo).

---

## 8. Publicar para la web

La web lee **una sola cosa**: la hoja `NUMEROS` publicada como CSV.

**Archivo → Compartir → Publicar en la web** → pestaña **`NUMEROS`** → formato **`.csv`** → Publicar.

Sale un link así:

```
https://docs.google.com/spreadsheets/d/e/2PACX-xxxxxxxxxxxx/pub?gid=0&single=true&output=csv
```

Ese link va en `index.html`, en la constante `SHEET_CSV`.

Tres cosas que hay que saber de esto:

- **Publicar ≠ compartir el archivo.** Publicar expone solo esa pestaña, de solo lectura, y nadie puede ver ni editar el resto.
- **Y hay que revisar aparte cómo está compartido el archivo**: Compartir → Acceso general → **Restringido**. Si queda en "Cualquier persona con el enlace", ese link entrega `COMPRADORES` y `VENDEDORES` enteras — nombres completos y teléfonos — aunque nunca se las publique.
- **Google guarda el CSV en caché unos 5 minutos.** Un cambio en el Sheet tarda hasta ~5 minutos en verse en la web; la web además se refresca sola cada 60 segundos. Lo prometido en el plan son 10 minutos, así que entra con margen.
- La columna `E` viaja en ese CSV y es pública. Por eso es una fórmula y no una celda para escribir: lo único que sale de ahí es `Dav*** G.`, `Reservado` o vacío. La cuadrícula no muestra ni eso — el nombre aparece solo al tocar un número pagado.

---

## 9. Cómo se usa en el día a día

| Momento | Qué se hace | Dónde |
|---|---|---|
| Alguien escoge un número | `APARTADO` en la columna B. La hora se pone sola | `NUMEROS` |
| **Llega la plata y se ve en la app** | **Una fila: número, nombre completo, teléfono, `SI`/`NO`.** Al poner el `SI`/`NO`, el número queda `PAGADO` solo, con su serial y su `Dav*** G.` | **`COMPRADORES`** |
| Y la plata se anota | Una fila en `PAGOS` | `PAGOS` |
| Cada mañana | Filtrar por la regla roja (vencidos), escribirle a cada uno, y a los que no responden poner B = `LIBRE` |
| Cada domingo | Leer `RESUMEN` y anotar el punto de control en `09_Operacion/` |

---

---

## 10. Casos de prueba (ya corridos sobre el archivo)

El archivo se llenó con casos a propósito, se **recalculó con LibreOffice** y se leyó con `openpyxl(data_only=True)`. **17 comprobaciones, todas pasan** (9 oct):

| Caso | Qué se puso | Qué dio | ✓ |
|---|---|---|---|
| Nombre normal | `000` PAGADO · David Gómez Pérez · SI | `Dav*** G.` · serial `A-000` | ✅ |
| No quiere salir | `001` PAGADO · Angela Rodríguez · **NO** | `Reservado` | ✅ |
| Un solo nombre | `002` PAGADO · Juan · SI | `Jua***`, sin espacio colgando | ✅ |
| Apartado fresco | `003` APARTADO hoy 10:00 | `APARTADO`, vence `05/10 10:00` | ✅ |
| Apartado viejo | `004` APARTADO hace 3 días | **`LIBRE`** — se venció solo | ✅ |
| Pagado sin ficha | `005` PAGADO, nadie en `COMPRADORES` | nombre en blanco, no se rompe | ✅ |
| Serial de otro bloque | `450` PAGADO · Sofía Bermúdez Gómez | `Sof*** B.` · serial `E-450` | ✅ |
| Plata de NZ | 1 pago de NZD 4 | `COP 7.372` (4 × 1.843) | ✅ |
| Contadores | 5 pagados, 1 apartado vivo, 1 vencido | Libres `994`, vencidos por recuperar `1` | ✅ |
| Ritmo | 5 pagados, 57 días al **5 dic** | **15 por día** — `ROUNDUP((860−5)/57)` | ✅ |
| `V01` vendidos | 000, 001, 002 pagados con `V01` | **3** | ✅ |
| `QUIERE_TBW` no rompe `NUMEROS!E` | 000 con `QUIERE_TBW=SI` | nombre sigue `Dav*** G.` | ✅ |

---

*Decisiones de esta sesión: **33** — los apartados vencen solos a las 24 horas, por fórmula en `NUMEROS!G`. **35** — en el tablero cada número pagado sale como `Dav*** G.`, calculado por fórmula desde `COMPRADORES`, con `Reservado` para quien no quiera salir.*
