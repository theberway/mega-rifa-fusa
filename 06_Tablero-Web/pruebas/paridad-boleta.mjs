// paridad-boleta.mjs — comprueba que el serial de boleta.js es el mismo que el del
// generador privado (`06_Tablero-Web/generador-privado.html` líneas 58-114) y el mismo
// que la fórmula server-side `rifa.serial_de()` (A..J + '-' + número).
// Node 20+: node 06_Tablero-Web/pruebas/paridad-boleta.mjs
import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
// Importa el serial del módulo del panel (ruta relativa; en Windows no se puede abusar de URL.pathname)
const boletaUrl = new URL("../publicar/admin/boleta.js", import.meta.url).href;
// `boleta.js` llama a `new Image()` en el preludio; en Node no existe. Lo stubbeo.
globalThis.Image = class { constructor() {} };
const mod = await import(boletaUrl);
const { serial } = mod;

// Serial del generador-privado.html (copia textual)
function serialGenerador(n) {
  return "ABCDEFGHIJ"[Math.floor(parseInt(n, 10) / 100)] + "-" + n;
}

const CASOS = ["000", "007", "099", "100", "250", "500", "750", "999"];
for (const n of CASOS) {
  const a = serial(n);
  const b = serialGenerador(n);
  assert.equal(a, b, `serial(${n}) debería coincidir con el generador: ${a} vs ${b}`);
}

// Serial server-side: A..J por centena. Compara contra la misma regla.
function serialSQL(n) {
  // Reproduce substr('ABCDEFGHIJ', (ascii(substr(n,1,1)) - 48) + 1, 1) || '-' || n
  const letras = "ABCDEFGHIJ";
  const idx = n.charCodeAt(0) - 48;
  return letras.charAt(idx) + "-" + n;
}
for (const n of CASOS) {
  assert.equal(serial(n), serialSQL(n), `serial(${n}) vs SQL`);
}

console.log("paridad boleta: PASA (", CASOS.length * 2, "casos )");
