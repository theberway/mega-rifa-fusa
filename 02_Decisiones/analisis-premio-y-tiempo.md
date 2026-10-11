# Análisis: regla del número no vendido y fecha del sorteo

*2026-10-05/06. Lo pidió Santiago después de que le hicieran caer en cuenta de dos cosas. Fuentes: `plan-maestro.md`, `registro-de-decisiones.md`, `04_Finanzas/modelo-financiero.xlsx` (hoja nueva `REGLA-PREMIO`) y los informes 2 y 3 de `01_Investigacion/`.*

## Decisión final (2026-10-06)

**Sorteo el sáb 5 dic 2026** (decisión 15). Santiago comparó 21 nov, 5 dic y 19 dic con las cifras a la vista y escogió la intermedia: 57 días de venta (~15/día para el piso en vez de ~20), la moto antes de las fiestas y menos desgaste que el 19 dic. **Estimado realista con el 5 dic: centro ~700 vendidos → caso malo COP 2,05M, esperado 2,59M.** Santiago espera 100–200 números más que con el 21 nov; el estimado da +50 a +130, porque las dos semanas extra son sin U y con la semana de notas en medio. La comparación de fechas de abajo (12 y 19 dic) queda como registro.

## En corto

- **Regla nueva (decisión 37, ya tomada)**: el premio de **COP 2.000.000 no baja**. Se paga si las últimas 3 cifras de la Boyacá caen en un número **vendido**. Si caen en uno **sin vender**, no hay 2M: el **siguiente número vendido** se lleva un **premio de consolación de hasta COP 300.000**.
- **Lo que la regla hace**: baja mucho el riesgo de que Santiago ponga plata de su bolsillo y le da una probabilidad de quedarse con mucho más.
- **Lo que la regla no hace**: no cambia el caso malo. Si el número está vendido, el neto es exactamente el mismo de antes. **Para tener COP 3.000.000 seguros siguen haciendo falta ~860 números vendidos.**
- **Por eso la fecha es la otra mitad de la decisión**: con lo que hay hoy, el centro estimado al **21 nov es ~650 vendidos** (caso malo **COP 1,75M**); al **19 dic, ~800** (caso malo **COP 2,65M**). **La fecha sigue abierta: la decide Santiago.**

---

## 1. Lo que no se había mostrado antes

Dicho sin suavizar, porque Santiago tiene razón en que debió verse desde el principio:

1. **La capacidad que estimaba el plan no llegaba al piso.** La decisión 3 calculaba **600–800 números** antes de refuerzos, y el piso es **~860**. La diferencia quedó en manos de los refuerzos, cuyas cifras (+20 a +150 cada uno) son estimaciones sin datos: ninguna fuente de la investigación da tasas de conversión para rifas informales colombianas.
2. **Con la regla anterior, por debajo de ~359 vendidos Santiago ponía plata propia** (300 vendidos = −COP 350.000), y él no puede cubrir eso.
3. **El plan B estaba mal armado.** Una segunda rifa en diciembre lleva **otro premio de 2M**. Si la primera queda en 700, para sacar el millón que falta habría que vender ~525 números más en otra rifa; alargar esta pide ~160.
4. **No son "1.000 personas".** Son **~900 números ≈ 410–600 compradores** (de 1,5 a 2,2 números por persona), que a una conversión del 15% al 8% son **2.700–7.500 pedidos** (informe 3, C7) en 40 días de venta pública.

## 2. La regla nueva — decisión 37 (reemplaza la 7)

Escogida por Santiago el 2026-10-05:

1. Gana el número igual a las **últimas 3 cifras del premio mayor** del **sorteo ordinario de la Lotería de Boyacá** (4 cifras; no cuentan serie, ni secos, ni lanzamiento adicional, ni sorteos extraordinarios).
2. **Si ese número está PAGADO → COP 2.000.000.** Si el comprador está en NZ: NZD 1.000, con mínimo de COP 1.900.000 (decisión 25, sin cambios).
3. **Si no se vendió → premio de consolación de hasta COP 300.000** para **el siguiente número vendido** después del de la Boyacá (del 999 se pasa al 000).
4. **La Lotería del Cauca ya no es una segunda oportunidad para los 2M.** Queda solo como **respaldo si la Boyacá no juega o no publica su resultado** esa noche; en ese caso se aplica la misma regla con la Cauca (11:00 p.m.).

**Cerrado el 2026-10-08**: el premio de consolación es **un whisky Buchanan's Master 750 ml, COP 210.000** (Éxito), y los **COP 100.000 al vendedor aplican también con la consolación**. Antes de la primera venta (sáb 10 oct) se compra o se aparta la botella y se guarda el recibo. Lo que había quedado por definir:
- **Qué es exactamente el premio de consolación.** Un objeto concreto o un monto fijo, con valor máximo de COP 300.000. "Un whisky" sirve como idea, pero el reglamento tiene que nombrarlo.
- **El premio de COP 100.000 al vendedor.** Propuesta por defecto: **solo aplica cuando se pagan los 2M**. Si Santiago quiere pagarlo también con la consolación, se cambia la celda `REGLA-PREMIO!B5` del modelo.
- **Si la consolación cae en NZ**: Sofía compra allá algo equivalente (hasta ~NZD 160) y Santiago le devuelve en pesos por Bre-B, igual que en la decisión 25.

### Texto para el reglamento (S4)

> **ES** — Gana el número igual a las últimas 3 cifras del premio mayor del sorteo ordinario de la Lotería de Boyacá del [FECHA], 10:30 p.m. (no cuentan serie, secos, lanzamiento adicional ni sorteos extraordinarios). Si ese número está pagado, su dueño gana **COP 2.000.000**. Si ese número no se vendió, no hay premio de 2 millones: el **siguiente número vendido** (del 999 se pasa al 000) gana **[PREMIO DE CONSOLACIÓN]**. Si esa noche la Lotería de Boyacá no juega o no publica su resultado, se usa la Lotería del Cauca de las 11:00 p.m., con la misma regla.
>
> **EN** — The winning number is the last 3 digits of the top prize of the regular Lotería de Boyacá draw on [DATE], 10:30 p.m. Colombia time (series, minor prizes, extra draws and special draws don't count). If that number was sold, its owner wins **NZD 1,000** (or COP 2,000,000 in Colombia). If it wasn't sold, there is no big prize: the **next number sold** (999 wraps to 000) wins **[CONSOLATION PRIZE]**. If Lotería de Boyacá doesn't draw or publish that night, Lotería del Cauca at 11:00 p.m. is used, same rule.

## 3. Las cifras

Neto en millones de COP, todo venta directa, consolación de 300k y costos fijos de 150k (premio del vendedor 100k + varios 50k). La hoja `REGLA-PREMIO` del modelo hace lo mismo con la mezcla real (8% NZ, 10% tiendas); las cifras cambian unas decenas de miles.

| Vendidos | Número vendido: se pagan 2M | Número sin vender: consolación | Probabilidad de pagar los 2M | Neto esperado | Regla anterior |
|---|---|---|---|---|---|
| 300 | **−0,35** | 1,45 | 30% | 0,91 | −0,35 |
| 400 | 0,25 | 2,05 | 40% | 1,33 | 0,25 |
| 500 | 0,85 | 2,65 | 50% | 1,75 | 0,85 |
| **650** — centro, 21 nov | **1,75** | 3,55 | 65% | 2,38 | 1,75 |
| 700 | 2,05 | 3,85 | 70% | 2,59 | 2,05 |
| **800** — centro, 19 dic | **2,65** | 4,45 | 80% | 3,01 | 2,65 |
| **860** — piso | 3,01 | 4,81 | 86% | 3,26 | 3,01 |
| 900 | 3,25 | 5,05 | 90% | 3,43 | 3,25 |

Cómo leerla:
- **El caso malo es idéntico al de antes.** La regla no lo mejora; solo hace que pase menos veces.
- **Pérdida**: solo si se venden menos de ~360 **y** el número cae en uno vendido. Con 120 de meta en la preventa, 30–80 compradores comprometidos, 6–8 vendedores y 2–3 tiendas, quedar por debajo de 360 es poco probable, pero no imposible. No hay forma de dejarlo en cero sin bajar el premio, y Santiago descartó bajarlo.
- **Probabilidad de pagar los 2M = vendidos / 1.000.** Si se vende más, sube la probabilidad de pagar, pero suben más el neto del caso malo y el esperado: **cada número vendido sigue convenciendo**.

## 4. Confianza: el punto débil de la regla

El informe 2 (B.2) marca "el organizador se queda el premio si el número no se vendió" con **reacción negativa del comprador**: da la sospecha de que al organizador no le conviene vender todo, o de que esconde números. No se encontró ninguna fuente colombiana sobre cómo lo toma la gente aquí.

Lo que lo atenúa en esta rifa:
- **El tablero es público** y la **lista final se publica a las 7:00 p.m.**, tres horas y media antes del sorteo. Nadie puede esconder un número ni "venderlo" después del resultado.
- **Siempre hay un ganador de algo esa noche**, así que la frase "aquí siempre hay ganador" sigue siendo cierta. Para no rozar la regla fija 3 (copy honesto), en lo público se dice completa: *"Siempre hay ganador: 2 palos si el número de la Boyacá está vendido; si no, [premio de consolación] para el siguiente vendido."*
- **Se vuelve un argumento de venta honesto**: *"Entre más números se vendan, más seguro hay ganador de los 2 palos."* Es cierto (la probabilidad es lo vendido sobre 1.000) y vuelve a cada comprador un promotor.

## 5. Capacidad realista

Estimación con los datos que dio Santiago el 2026-10-05. Ninguna fuente da tasas de conversión para rifas informales, así que son rangos, no promesas.

| Fuente | Hasta el 21 nov | Lo que suma ir al 19 dic |
|---|---|---|
| Red directa (30–80 comprometidos × ~1,8 + el resto de la red) | 150–250 | +30–80 (prima, novenas) |
| 6–8 vendedores × 25–50 números (mitad estudiantes, mitad familia/adultos) | 150–400 | +40–120 (los de familia/adultos siguen; los estudiantes caen con la U vacía) |
| 2–3 tiendas × 20–40 | 40–120 | +20–60 |
| NZ | 50–100 | ~0 (allá empieza el verano) |
| **Total** | **390–870 · centro ~650** | **+90–260 · centro ~800** |

## 6. La fecha (abierta: la decide Santiago)

Comprobado en el informe 2 (calendario Coljuegos 2026): la Boyacá juega su **sorteo ordinario todos los sábados a las 10:30 p.m. sin ningún cambio en el trimestre**, incluidos el 12 y el 19 dic, y la Cauca igual a las 11:00 p.m. Cada fecha tiene un extraordinario de otra lotería ese mismo día (21 nov Medellín, 12 dic Quindío, 19 dic Bogotá 8:20 p.m.); por eso el reglamento dice **"sorteo ordinario de la Lotería de Boyacá"**. El Extraordinario de la Boyacá es el **jue 24 dic**, no un sábado.

| | **Sáb 21 nov** (hoy) | **Sáb 12 dic** | **Sáb 19 dic** (recomendada) |
|---|---|---|---|
| Días de venta desde el 10 oct | 43 | 64 | 71 |
| Ritmo para llegar a 860 | ~20/día | ~13/día | ~12/día |
| Quincenas | 15 oct, 30 oct, 13 nov | + 30 nov | + 30 nov y 15 dic |
| Prima (mitad de diciembre) | no | casi nada | en parte (quien la recibe el 15) |
| Novenas | no | no | 16–19 dic |
| Empujón en la U | antes del 19 nov | igual | igual |
| Centro estimado | ~650 | ~720 | ~800 |
| Caso malo (número vendido) | **COP 1,75M** | **~COP 2,17M** | **COP 2,65M** |
| Moto | fin de noviembre | antes de las fiestas | después del 20 dic |
| Plan B (segunda rifa) | sigue en pie | desaparece | desaparece |

**Por qué 19 dic**: es la fecha que más sube el caso malo (+COP 0,9M frente al 21 nov) y la única en la que llegar a 860 entra en el rango estimado. Suma dos quincenas, parte de la prima y tres noches de novena, que son justo los momentos de reunión familiar donde vende la mitad de los vendedores que no es estudiante. La investigación ya lo sugería (informe 3, B: "sortear alrededor del 14–19 dic, antes del choque con las rifas de Navidad").

**Lo que cuesta, sin suavizar**:
- **10 semanas de campaña en vez de 6.** Más cansancio para Santiago, Sofía y los vendedores, y un bajón a mitad de campaña más largo. Hay que planear un relanzamiento a la vuelta de la U (22–30 nov).
- **El cierre del semestre** (notas del 23 al 28 nov) cae en plena campaña.
- **La moto se compra en temporada de fiestas**: oficinas de tránsito más lentas para el traspaso y vendedores particulares de viaje. Santiago dijo que puede esperar a mitad o fin de diciembre, así que cabe, pero sin margen.
- **La urgencia del 21 nov se pierde.** Con la U empujando hasta el 19 nov y el cierre real un mes después, el mensaje de "últimas horas" llega cuando los estudiantes ya no están.
- **Los 6–8 vendedores ya vieron el kit con el 21 nov**: hay que avisarles antes de la preventa.

**Sáb 12 dic** es la alternativa si Santiago quiere la moto antes de las fiestas con margen: suma la quincena del 30 nov pero pierde la del 15 dic, la prima y las novenas.

## 7. Qué cambió en los archivos (decisión 37)

| Archivo | Cambio |
|---|---|
| `02_Decisiones/registro-de-decisiones.md` | Decisión 37 nueva; la 7 queda reemplazada; historial |
| `02_Decisiones/plan-maestro.md` | Tabla de decisiones y números clave |
| `04_Finanzas/modelo-financiero.xlsx` | Hoja `REGLA-PREMIO`, 4 casos de prueba nuevos (9 en total, **TODOS PASAN** recalculando con LibreOffice), notas de `LEEME`, `SUPUESTOS` y `ESCENARIOS` |
| `06_Tablero-Web/index.html` y `publicar/` | Fila nueva "Si el número no se vendió" y la Cauca solo como respaldo, en ES y EN; redeploy |
| `03_Hoja-de-ruta/` | Guion de la noche del sorteo y "Lo que no se mueve" |
| `00_EMPIEZA-AQUI.md`, `01_Investigacion/00_LEEME…`, memorias | Al día con la regla nueva |

**Si Santiago mueve la fecha**, falta: las decisiones 15 y 19 en el registro, la cuenta regresiva y las fechas de la web y de la tarjeta-boleta, la hoja de ruta, los puntos de control (metas nuevas por domingo hasta el 13 dic), el plan de sesiones y `ESCENARIOS!B28` del modelo.
