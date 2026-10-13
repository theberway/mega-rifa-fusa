// paridad.mjs — misma regla de acortar() en JavaScript que en SQL y Apps Script.
// Node 20+: node 06_Tablero-Web/pruebas/paridad.mjs
import { strict as assert } from "node:assert";

function acortar(txt) {
  const t = String(txt || "").trim().replace(/\s+/g, " ");
  if (/^reservad[oa]$/i.test(t)) return "Reservado";
  if (!t || t.includes("*")) return t;
  const cap = w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
  const p = t.split(" ");
  const a = cap(Array.from(p[0]).slice(0, 3).join(""));
  const b = p[1] ? " " + Array.from(p[1])[0].toUpperCase() + "." : "";
  return a + "***" + b;
}

function normalizar(s) {
  return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/ñ/gi, m => (m === "ñ" ? "n" : "N"))
    .replace(/\s+/g, " ").trim().toUpperCase();
}

const CASOS = [
  ["Juan Perez", "Jua*** P."],
  ["María de los Ángeles Ruiz", "Mar*** D."],
  ["Catalina", "Cat***"],
  ["Reservado", "Reservado"],
  ["reservada", "Reservado"],
  ["Jua*** P.", "Jua*** P."],
  ["", ""],
];
for (const [in_, out] of CASOS) {
  assert.equal(acortar(in_), out, `acortar(${JSON.stringify(in_)})`);
}

const NORM = [
  ["josé  PÉREZ", "JOSE PEREZ"],
  ["  Muñoz  Ñero", "MUNOZ NERO"],
  ["ana lucia", "ANA LUCIA"],
];
for (const [in_, out] of NORM) assert.equal(normalizar(in_), out, `normalizar(${JSON.stringify(in_)})`);

console.log("paridad JS: PASA (", CASOS.length + NORM.length, "casos )");
