/**
 * MEGA RIFA FUSA — script único del tablero.
 * Reemplaza a script-hora-apartado.gs: este hace eso y además repara la hoja.
 *
 * ── CÓMO SE INSTALA (una vez) ─────────────────────────────────────────────
 *  1. Abrí el Sheet con la cuenta megarifafusa@gmail.com
 *  2. Extensiones -> Apps Script
 *  3. Borrá lo que haya y pegá TODO este archivo
 *  4. Guardá (el disquete)
 *  5. Arriba, donde dice la lista de funciones, elegí "repararTodo" y dale Ejecutar
 *     (la primera vez pide permiso: Revisar permisos -> tu cuenta -> Configuración
 *      avanzada -> Ir a MEGA-RIFA-FUSA-tablero -> Permitir. Es tu propio archivo)
 *  6. Volvé al Sheet. Listo.
 *
 * ── QUÉ HACE ──────────────────────────────────────────────────────────────
 *  repararTodo()  — se corre a mano, cuando haga falta:
 *      · devuelve las fórmulas de E, F, G y H a las 1.000 filas
 *      · cuenta las horas mal escritas y te dice en cuáles están
 *
 *  onEdit()       — corre solo:
 *      En NUMEROS, al tocar la columna B (ESTADO_MANUAL):
 *      · APARTADO -> escribe fecha y hora completas en C (solo si estaba vacía)
 *      · LIBRE    -> borra C y D
 *      · PAGADO   -> no toca nada
 *
 *      En COMPRADORES, al llenar la columna D (SALE_PUBLICO), que es la última
 *      de la fila:
 *      · marca ese número como PAGADO en NUMEROS, solo
 *
 *      O sea: para vender no hay que ir a dos hojas. Se llena la fila en
 *      COMPRADORES y el tablero se pinta solo.
 *
 * ── LA REGLA QUE NO SE ROMPE ──────────────────────────────────────────────
 *  La columna E (NOMBRE_PUBLICO) es la ÚNICA columna pública que parece una
 *  celda normal. Lo que se escriba ahí sale publicado tal cual en la web.
 *  Los nombres completos van SIEMPRE en la hoja COMPRADORES, que no se publica.
 */

var HOJA   = 'NUMEROS';
var HOJA_C = 'COMPRADORES';
var FILAS  = 1000;
var FILA_1 = 2;

var COL_ESTADO = 2;   // B
var COL_HORA   = 3;   // C
var COL_VEND   = 4;   // D

// Las cuatro fórmulas. {f} se reemplaza por el número de fila.
var F_NOMBRE =
  '=IF($G{f}<>"PAGADO","",IFERROR(IF(VLOOKUP($A{f},COMPRADORES!$A:$D,4,FALSE)="NO","Reservado",' +
  'LEFT(VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE),3)&"***"&' +
  'IF(TRIM(MID(VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE)&" ",FIND(" ",VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE)&" ")+1,99))="","",' +
  '" "&LEFT(TRIM(MID(VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE)&" ",FIND(" ",VLOOKUP($A{f},COMPRADORES!$A:$D,2,FALSE)&" ")+1,99)),1)&".")),""))';

var F_SERIAL =
  '=IF($B{f}="PAGADO",MID("ABCDEFGHIJ",INT(VALUE($A{f})/100)+1,1)&"-"&$A{f},"")';

// Un apartado sin hora, o con una hora sin fecha, NO se suelta: queda apartado
// y la columna VENCE_A avisa qué le falta. Antes se soltaba en silencio.
var F_ESTADO =
  '=IF($B{f}="PAGADO","PAGADO",IF($B{f}="APARTADO",' +
  'IF(NOT(ISNUMBER($C{f})),"APARTADO",' +
  'IF($C{f}<1,"APARTADO",' +
  'IF(NOW()-$C{f}>1,"LIBRE","APARTADO"))),"LIBRE"))';

var F_VENCE =
  '=IF($G{f}<>"APARTADO","",IF(NOT(ISNUMBER($C{f})),"FALTA LA HORA",' +
  'IF($C{f}<1,"FALTA LA FECHA",TEXT($C{f}+1,"dd/mm hh:mm"))))';


function repararTodo() {
  var sh = SpreadsheetApp.getActive().getSheetByName(HOJA);
  if (!sh) { SpreadsheetApp.getUi().alert('No encuentro la hoja ' + HOJA); return; }

  var nombre = [], serial = [], estado = [], vence = [];
  for (var i = 0; i < FILAS; i++) {
    var f = i + FILA_1;
    nombre.push([F_NOMBRE.replace(/\{f\}/g, f)]);
    serial.push([F_SERIAL.replace(/\{f\}/g, f)]);
    estado.push([F_ESTADO.replace(/\{f\}/g, f)]);
    vence.push([F_VENCE.replace(/\{f\}/g, f)]);
  }

  sh.getRange(FILA_1, 5, FILAS, 1).setFormulas(nombre);   // E
  sh.getRange(FILA_1, 6, FILAS, 1).setFormulas(serial);   // F
  sh.getRange(FILA_1, 7, FILAS, 1).setFormulas(estado);   // G
  sh.getRange(FILA_1, 8, FILAS, 1).setFormulas(vence);    // H

  // La columna C tiene que guardar fecha Y hora.
  sh.getRange(FILA_1, COL_HORA, FILAS, 1).setNumberFormat('dd/mm/yyyy hh:mm');

  // Buscar las horas que quedaron sin fecha (el error de escribir "11:20" a secas).
  var numeros = sh.getRange(FILA_1, 1, FILAS, 1).getValues();
  var horas   = sh.getRange(FILA_1, COL_HORA, FILAS, 1).getValues();
  var malas = [];
  for (var j = 0; j < FILAS; j++) {
    var v = horas[j][0];
    if (v instanceof Date && v.getFullYear() < 2020) malas.push(numeros[j][0]);
  }

  SpreadsheetApp.flush();

  var msg = 'Fórmulas repuestas en E, F, G y H (1.000 filas).';
  if (malas.length) {
    msg += '\n\nHoras sin fecha, hay que rehacerlas: ' + malas.join(', ') +
           '\nEn cada una: poné LIBRE y después APARTADO otra vez. ' +
           'La hora se escribe sola y correcta.';
  } else {
    msg += '\n\nNinguna hora quedó mal escrita.';
  }
  SpreadsheetApp.getUi().alert('Tablero reparado', msg, SpreadsheetApp.getUi().ButtonSet.OK);
}


function onEdit(e) {
  if (!e || !e.range) return;

  var hoja = e.range.getSheet();
  if (hoja.getName() === HOJA_C) { alPagar_(e, hoja); return; }
  if (hoja.getName() !== HOJA) return;

  var primeraCol = e.range.getColumn();
  var ultimaCol  = primeraCol + e.range.getNumColumns() - 1;
  if (primeraCol > COL_ESTADO || ultimaCol < COL_ESTADO) return;

  var primeraFila = e.range.getRow();
  if (primeraFila < FILA_1) return;
  var filas = e.range.getNumRows();

  var estados = hoja.getRange(primeraFila, COL_ESTADO, filas, 1).getValues();
  var horas   = hoja.getRange(primeraFila, COL_HORA,   filas, 1).getValues();
  var vends   = hoja.getRange(primeraFila, COL_VEND,   filas, 1).getValues();

  var ahora = new Date();
  var cambio = false;

  for (var i = 0; i < filas; i++) {
    var est = String(estados[i][0]).trim().toUpperCase();
    var hora = horas[i][0];
    // Una hora de 1899 es una hora sin fecha: se trata como si no hubiera.
    var horaValida = (hora instanceof Date) && hora.getFullYear() >= 2020;

    if (est === 'APARTADO') {
      if (!horaValida) { horas[i][0] = ahora; cambio = true; }
    } else if (est === 'LIBRE') {
      if (hora || vends[i][0]) { horas[i][0] = ''; vends[i][0] = ''; cambio = true; }
    }
    // PAGADO: no se toca.
  }

  if (cambio) {
    hoja.getRange(primeraFila, COL_HORA, filas, 1).setValues(horas);
    hoja.getRange(primeraFila, COL_VEND, filas, 1).setValues(vends);
  }
}


/**
 * COMPRADORES: al llenar SALE_PUBLICO (columna D), el número queda PAGADO solo.
 * Se dispara con la D porque es la última celda de la fila: para entonces ya
 * están el número, el nombre y el teléfono.
 */
function alPagar_(e, hojaC) {
  var primeraCol = e.range.getColumn();
  var ultimaCol  = primeraCol + e.range.getNumColumns() - 1;
  if (primeraCol > 4 || ultimaCol < 4) return;

  var desde = e.range.getRow();
  if (desde < 2) return;
  var filas = e.range.getNumRows();

  var datos = hojaC.getRange(desde, 1, filas, 4).getValues();
  var hojaN = e.range.getSheet().getParent().getSheetByName(HOJA);
  if (!hojaN) return;

  for (var i = 0; i < filas; i++) {
    var num  = String(datos[i][0]).trim();
    var sale = String(datos[i][3]).trim().toUpperCase();
    if (sale !== 'SI' && sale !== 'NO') continue;
    if (!/^\d{1,3}$/.test(num)) continue;

    var fila = parseInt(num, 10) + FILA_1;            // 000 vive en la fila 2
    if (fila < FILA_1 || fila > FILA_1 + FILAS - 1) continue;

    // Se confirma contra la columna A antes de escribir nada.
    var enHoja = String(hojaN.getRange(fila, 1).getValue()).trim();
    if (enHoja !== num && enHoja !== ('000' + num).slice(-3)) continue;

    var celda = hojaN.getRange(fila, COL_ESTADO);
    if (String(celda.getValue()).trim().toUpperCase() !== 'PAGADO') {
      celda.setValue('PAGADO');
    }
  }
}


/**
 * ── SERVICIO EN VIVO PARA LA WEB (doGet) ──────────────────────────────────
 * La web lo llama cada 20 s. Responde en ~1 s con el estado REAL de la hoja, sin
 * esperar los ~5 min de "Publicar en la web". Solo entrega lo que ya es público:
 * número, estado y nombre acortado de los PAGADOS. Nada de COMPRADORES, teléfonos
 * ni plata. Guarda 5 s en memoria para aguantar muchas visitas.
 *
 * Cómo se publica (una vez): Implementar -> Nueva implementación -> tipo
 * "Aplicación web" -> Ejecutar como: Yo -> Quién tiene acceso: Cualquier persona
 * -> Implementar. Copiar la URL que termina en /exec y pasársela a Claude.
 * Si después se cambia este código: Implementar -> Administrar implementaciones
 * -> lápiz -> Versión nueva -> Implementar (la URL no cambia).
 */
function doGet() {
  var cache = CacheService.getScriptCache();
  var out = cache.get('tablero_v1');
  if (!out) {
    var sh = SpreadsheetApp.getActive().getSheetByName(HOJA);
    var vals = sh.getRange(1, 1, FILAS + 1, 9).getValues();
    var h = vals[0].map(function (x) { return String(x).trim().toUpperCase(); });
    var iN = h.indexOf('NUMERO'), iE = h.indexOf('ESTADO'), iM = h.indexOf('NOMBRE_PUBLICO');
    var filas = [];
    if (iN >= 0 && iE >= 0) {
      for (var i = 1; i < vals.length; i++) {
        var n = String(vals[i][iN]).trim();
        if (!/^\d{1,3}$/.test(n)) continue;
        n = ('000' + n).slice(-3);
        var est = String(vals[i][iE]).trim().toUpperCase();
        if (est !== 'PAGADO' && est !== 'APARTADO') continue;
        filas.push([n, est, (est === 'PAGADO' && iM >= 0) ? acortarNombre_(vals[i][iM]) : '']);
      }
      out = JSON.stringify({ ok: true, t: Date.now(), v: filas });
      cache.put('tablero_v1', out, 5);
    } else {
      out = JSON.stringify({ ok: false });
    }
  }
  return ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
}


/** "Juan Perez" -> "Jua*** P." (igual que la web). Si ya viene acortado o es "Reservado", lo deja igual. */
function acortarNombre_(txt) {
  var t = String(txt || '').replace(/\s+/g, ' ').trim();
  if (/^reservad[oa]$/i.test(t)) return 'Reservado';
  if (!t || t.indexOf('*') >= 0) return t;
  var p = t.split(' ');
  var cap = function (w) { return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase(); };
  return cap(p[0].slice(0, 3)) + '***' + (p[1] ? ' ' + p[1].charAt(0).toUpperCase() + '.' : '');
}
