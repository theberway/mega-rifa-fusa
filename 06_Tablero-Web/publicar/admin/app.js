// Panel admin · Mega Rifa Fusa
// Usa supabase-js v2 (ESM) con versión fija. CSP permite el host de Supabase y jsDelivr.
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.46.1/+esm";
import { dibujarCuandoListo, obtenerBlob, serial } from "/admin/boleta.js";

const SUPA_URL = "https://oyvrdwkoorkidoadnzmc.supabase.co";
const SUPA_KEY = "sb_publishable_t_e7HPMI1g7rINUYIr0Ehg_OlzMMm3d";
const supabase = createClient(SUPA_URL, SUPA_KEY, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false }
});

const $ = (s) => document.querySelector(s);
const el = (t, p = {}, kids = []) => {
  const n = Object.assign(document.createElement(t), p);
  for (const k of [].concat(kids)) n.appendChild(typeof k === "string" ? document.createTextNode(k) : k);
  return n;
};
const txt = (s) => document.createTextNode(s);
const toast = (m, tipo = "verde") => {
  const t = el("div", { className: "toast " + tipo, textContent: m });
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2200);
};
const err = (e) => toast(String(e && e.message || e), "rojo");

async function rpc(fn, args = {}) {
  const { data, error } = await supabase.rpc(fn, args);
  if (error) throw error;
  return data;
}

// ---------- Sesión / 2FA ----------

async function usuarioActual() {
  const { data } = await supabase.auth.getUser();
  return data?.user || null;
}

async function nivelAal() {
  const { data } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
  return data || null; // { currentLevel, nextLevel, currentAuthenticationMethods }
}

async function arrancar() {
  const u = await usuarioActual();
  if (!u) return mostrarLogin();
  const aal = await nivelAal();
  const factores = await supabase.auth.mfa.listFactors();
  const totp = (factores?.data?.totp || []).find(f => f.status === "verified");
  // Si tiene MFA habilitado pero está en aal1, obliga a pasar el challenge
  if (totp && aal?.nextLevel === "aal2" && aal?.currentLevel !== "aal2") return mostrarMfa(totp);
  // Si NO tiene MFA aún: pide activarlo (admin solo). turno puede pasar sin 2FA.
  const yoRow = await cargarYo();
  if (!yoRow) return salir("Tu cuenta no está en la lista blanca del panel.");
  if (yoRow.rol === "admin" && !totp) return mostrarInscripcionMfa(yoRow);
  mostrarApp(yoRow);
}

async function cargarYo() {
  const u = (await usuarioActual()) || {};
  try {
    const r = await rpc("mi_perfil");
    if (!r || !r.ok) return null;
    return { email: u.email, nombre: r.nombre, rol: r.rol, exige2fa: !!r.exige_2fa };
  } catch (e) {
    return null;
  }
}

function mostrarLogin() {
  $("#login").hidden = false; $("#mfa").hidden = true; $("#app").hidden = true; $("#tabs").hidden = true;
  $("#yo").textContent = "";
  $("#fLogin").onsubmit = async (e) => {
    e.preventDefault();
    $("#errLogin").hidden = true;
    const correo = $("#iCorreo").value.trim();
    const pass = $("#iPass").value;
    try {
      const { error } = await supabase.auth.signInWithPassword({ email: correo, password: pass });
      if (error) throw error;
      arrancar();
    } catch (ex) {
      $("#errLogin").textContent = "No pudimos entrar: " + (ex.message || ex);
      $("#errLogin").hidden = false;
    }
  };
}

async function mostrarMfa(factor) {
  $("#login").hidden = true; $("#mfa").hidden = false; $("#app").hidden = true; $("#tabs").hidden = true;
  $("#fMfa").onsubmit = async (e) => {
    e.preventDefault();
    $("#errMfa").hidden = true;
    try {
      const code = $("#iMfa").value.replace(/\D/g, "");
      const { data: ch, error: e1 } = await supabase.auth.mfa.challenge({ factorId: factor.id });
      if (e1) throw e1;
      const { error: e2 } = await supabase.auth.mfa.verify({ factorId: factor.id, challengeId: ch.id, code });
      if (e2) throw e2;
      arrancar();
    } catch (ex) {
      $("#errMfa").textContent = "Código incorrecto o vencido.";
      $("#errMfa").hidden = false;
    }
  };
}

async function mostrarInscripcionMfa(yo) {
  $("#login").hidden = true; $("#mfa").hidden = false; $("#app").hidden = true; $("#tabs").hidden = true;
  const c = $("#mfa .card");
  c.innerHTML = '<h1>Activar 2FA</h1>' +
    '<p>Como <b>admin</b>, el panel exige 2FA (decisión 46). Es un paso de una vez.</p>' +
    '<ol><li>Abre tu app de autenticación (Google Authenticator o Microsoft Authenticator).</li>' +
    '<li>Escanea este QR o escribe el código a mano.</li>' +
    '<li>Escribe los 6 dígitos que aparecen y toca «Activar».</li></ol>' +
    '<div id="qr"></div><p id="codigo-txt" class="mono" style="font-family:Space Mono,monospace"></p>' +
    '<label>Código de 6 dígitos</label><input id="iCod" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" placeholder="000000">' +
    '<button id="bActivar">Activar</button><p class="err" id="errMfa" hidden></p>';
  try {
    const { data, error } = await supabase.auth.mfa.enroll({ factorType: "totp", friendlyName: "Mega Rifa Fusa" });
    if (error) throw error;
    const svg = data.totp.qr_code; // viene como URL svg data
    document.getElementById("qr").innerHTML = `<img alt="QR" style="width:200px;height:200px;background:#fff;padding:8px;border:3px solid var(--negro);border-radius:8px" src="${svg}">`;
    document.getElementById("codigo-txt").textContent = "Secreto: " + data.totp.secret;
    document.getElementById("bActivar").onclick = async () => {
      const code = document.getElementById("iCod").value.replace(/\D/g, "");
      try {
        const { data: ch, error: e1 } = await supabase.auth.mfa.challenge({ factorId: data.id });
        if (e1) throw e1;
        const { error: e2 } = await supabase.auth.mfa.verify({ factorId: data.id, challengeId: ch.id, code });
        if (e2) throw e2;
        toast("2FA activo", "verde"); arrancar();
      } catch (ex) {
        document.getElementById("errMfa").textContent = "No funcionó: " + (ex.message || ex);
        document.getElementById("errMfa").hidden = false;
      }
    };
  } catch (ex) {
    err(ex);
  }
}

async function salir(msg) {
  await supabase.auth.signOut();
  if (msg) alert(msg);
  location.reload();
}

// ---------- App ----------

let YO = null;
let VENDEDORES_CACHE = [];
let TAB_ACTUAL = "inicio";

async function mostrarApp(yo) {
  YO = yo;
  $("#login").hidden = true; $("#mfa").hidden = true; $("#app").hidden = false; $("#tabs").hidden = false;
  $("#yo").textContent = (yo.rol === "admin" ? "admin · " : "turno · ") + (yo.email || "");
  // Pestañas solo-admin
  for (const b of document.querySelectorAll(".tabs .solo-admin")) {
    b.hidden = (yo.rol !== "admin");
  }
  $$tabs();
  render();
}

function $$tabs() {
  for (const b of document.querySelectorAll(".tabs .tab")) {
    b.onclick = () => {
      if (b.dataset.tab === "salir") return salir();
      document.querySelectorAll(".tabs .tab").forEach(x => x.classList.remove("activo"));
      b.classList.add("activo");
      TAB_ACTUAL = b.dataset.tab;
      render();
    };
  }
}

async function render() {
  const app = $("#app");
  app.innerHTML = "";
  if (TAB_ACTUAL === "inicio")     return pantallaInicio(app);
  if (TAB_ACTUAL === "vender")     return pantallaVender(app);
  if (TAB_ACTUAL === "numeros")    return pantallaNumeros(app);
  if (TAB_ACTUAL === "vendedores") return pantallaVendedores(app);
  if (TAB_ACTUAL === "pendientes") return pantallaPendientes(app);
  if (TAB_ACTUAL === "plata")      return pantallaPlata(app);
  if (TAB_ACTUAL === "mas")        return pantallaMas(app);
}

// ────────── PLATA (solo admin) ──────────

const fmtCOP = (n) => new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(Number(n) || 0);
const fmtHoras = (h) => {
  const x = Number(h) || 0;
  if (x < 1) return Math.round(x * 60) + " min";
  if (x < 48) return x.toFixed(1) + " h";
  return Math.floor(x / 24) + " d " + Math.round(x % 24) + " h";
};

async function pantallaPlata(cont) {
  if (YO.rol !== "admin") { cont.appendChild(el("p", { className: "err", textContent: "Solo admin." })); return; }
  cont.appendChild(el("h1", { textContent: "Plata" }));
  const estado = el("p", { textContent: "Cargando…" }); cont.appendChild(estado);
  let d;
  try { d = await rpc("pagos_efectivo_pendientes"); }
  catch (e) { estado.className = "err"; estado.textContent = "No pudimos cargar: " + e.message; return; }
  estado.remove();

  const umbralEnt = d.umbral_entregar_h || 48;
  const umbralCon = d.umbral_consignar_h || 24;

  // Aviso de contexto
  const aviso = el("div", { className: "aviso-amarillo" });
  aviso.innerHTML = `El efectivo con vendedor se vuelve urgente a las <b>${umbralEnt} h</b>; lo tuyo sin consignar, a las <b>${umbralCon} h</b>.`;
  cont.appendChild(aviso);

  // Bloque 1: con vendedor
  const b1 = el("div", { className: "bloque-stats" });
  b1.appendChild(el("h2", { textContent: `Efectivo con vendedor (${(d.con_vendedor || []).length})` }));
  if (!d.con_vendedor.length) b1.appendChild(el("p", { className: "ok", textContent: "Nada pendiente. Buena." }));
  for (const p of (d.con_vendedor || [])) {
    const f = el("div", { className: "pago-fila" + (p.horas >= umbralEnt ? " urgente" : "") });
    const izq = el("div");
    izq.appendChild(el("div", { textContent: (p.codigo || "sin código") + " · " + (p.nombre || "") }));
    izq.appendChild(el("div", { className: "mono", textContent: `#${(p.numeros || []).join(", ") || "—"} · ${fmtHoras(p.horas)}` }));
    f.appendChild(izq);
    const der = el("div");
    der.appendChild(el("div", { className: "monto", textContent: fmtCOP(p.monto_cop) }));
    const bEnt = el("button", { className: "chico verde", textContent: "Me entregó" });
    bEnt.onclick = async () => {
      if (!confirm(`Marcar ${fmtCOP(p.monto_cop)} de ${p.codigo || "ese pago"} como recibido por ti?`)) return;
      try { await rpc("entregar_efectivo", { p_pago_id: p.pago_id }); toast("Entregado"); render(); }
      catch (e) { err(e); }
    };
    der.appendChild(bEnt);
    f.appendChild(der);
    b1.appendChild(f);
  }
  cont.appendChild(b1);

  // Bloque 2: sin consignar
  const b2 = el("div", { className: "bloque-stats" });
  b2.appendChild(el("h2", { textContent: `Tuyo sin consignar (${(d.sin_consignar || []).length})` }));
  if (!d.sin_consignar.length) b2.appendChild(el("p", { className: "ok", textContent: "Al día. Buena." }));
  const seleccion = new Set();
  const barraLote = el("div", { className: "acciones" });
  const bConsig = el("button", { className: "verde", textContent: "Consignar seleccionados" });
  bConsig.disabled = true;
  const info = el("span", { textContent: "0 seleccionados" });
  barraLote.appendChild(bConsig); barraLote.appendChild(info);
  b2.appendChild(barraLote);
  const refrescarSel = () => {
    info.textContent = seleccion.size + " seleccionados";
    bConsig.disabled = seleccion.size === 0;
  };
  for (const p of (d.sin_consignar || [])) {
    const f = el("div", { className: "pago-fila" + (p.horas >= umbralCon ? " urgente" : "") });
    const check = el("input", { type: "checkbox" });
    check.style.cssText = "width:auto;margin-right:8px";
    check.onchange = () => { if (check.checked) seleccion.add(p.pago_id); else seleccion.delete(p.pago_id); refrescarSel(); };
    const izq = el("div");
    izq.appendChild(check);
    const info2 = el("span");
    info2.innerHTML = `<b>${p.medio}</b>${p.codigo_vendedor ? " · " + p.codigo_vendedor : ""}<br><span class="mono">#${(p.numeros || []).join(", ") || "—"} · ${fmtHoras(p.horas)}</span>`;
    izq.appendChild(info2);
    f.appendChild(izq);
    f.appendChild(el("div", { className: "monto", textContent: fmtCOP(p.monto_cop) }));
    b2.appendChild(f);
  }
  bConsig.onclick = async () => {
    if (!seleccion.size) return;
    if (!confirm(`Marcar ${seleccion.size} pago(s) como consignados?`)) return;
    try {
      const r = await rpc("consignar", { p_pago_ids: Array.from(seleccion) });
      toast(`Consignados ${r.consignados}` + (r.omitidos ? ` (${r.omitidos} ya estaban)` : ""), "verde");
      render();
    } catch (e) { err(e); }
  };
  cont.appendChild(b2);
}

// ────────── MÁS (estadísticas + ranking) ──────────

async function pantallaMas(cont) {
  cont.appendChild(el("h1", { textContent: "Más" }));
  if (YO.rol !== "admin") {
    cont.appendChild(el("p", { textContent: "Solo admin puede ver estadísticas y ranking." }));
    return;
  }
  const estado = el("p", { textContent: "Cargando…" }); cont.appendChild(estado);
  let s, r, nz = null;
  try {
    [s, r, nz] = await Promise.all([rpc("estadisticas"), rpc("stats_vendedores"), rpc("estadisticas_nz").catch(() => null)]);
  } catch (e) { estado.className = "err"; estado.textContent = "No pudimos cargar: " + e.message; return; }
  estado.remove();

  // Aviso 35/43
  if ((s.real.sin_vendedor || 0) > 0) {
    const total = (s.real.con_vendedor || 0) + (s.real.sin_vendedor || 0);
    const aviso = el("div", { className: "aviso-amarillo" });
    aviso.innerHTML = `<b>${s.real.sin_vendedor} de ${total}</b> ventas no tienen vendedor asignado todavía (vienen del Sheet). El desglose por vendedor sale casi vacío hasta que lleguen los CSV privados.`;
    cont.appendChild(aviso);
  }

  // BLOQUE REAL
  const bR = el("div", { className: "bloque-stats" });
  bR.appendChild(el("h2", { textContent: "Real · lo que ya pasó" }));
  const grid = el("div", { className: "cifras" });
  grid.innerHTML =
    `<div><b>${s.real.pagados}</b><span>pagados</span></div>` +
    `<div><b>${s.real.apartados}</b><span>apartados</span></div>` +
    `<div><b>${s.real.libres}</b><span>libres</span></div>` +
    `<div><b>${s.real.compradores}</b><span>compradores</span></div>`;
  bR.appendChild(grid);
  const tR = el("table");
  const casoMalo = Number(s.real.caso_malo_cop);
  tR.innerHTML =
    `<tr><td>Ingresos cobrados</td><td align="right"><b>${fmtCOP(s.real.ingresos_cop)}</b></td></tr>` +
    `<tr><td>Pagos registrados</td><td align="right"><b>${s.real.pagos_registrados}</b>` +
      (nz && nz.por_medio ? `<br><small>${Object.entries(nz.por_medio).map(([k, v]) => `${{ "BRE-B": "Nu / Bre-B", EFECTIVO: "efectivo", NZ: "NZ transf.", NZ_EFECTIVO: "NZ efectivo", TIENDA: "tienda" }[k] || k} ${v}`).join(" · ")}</small>` : "") +
      `</td></tr>` +
    `<tr><td>Caso malo con hoy (EMPIEZA!C8)</td><td align="right"><b style="color:${casoMalo >= 0 ? 'var(--verde)' : 'var(--rojo)'}">${fmtCOP(casoMalo)}</b></td></tr>` +
    `<tr><td>Faltan al piso (EMPIEZA!C10)</td><td align="right"><b>${s.real.faltan_al_piso}</b> números</td></tr>` +
    `<tr><td>¿Llegó al piso? (EMPIEZA!C12)</td><td align="right"><b style="color:${s.real.llego_al_piso ? 'var(--verde)' : 'var(--rojo)'}">${s.real.llego_al_piso ? 'SÍ' : 'todavía no'}</b></td></tr>`;
  bR.appendChild(tR);

  // Por método (muy visible lo sin método)
  const porMetodo = s.real.por_metodo || {};
  const sinMet = porMetodo.sin_metodo || 0;
  const bMet = el("p");
  bMet.innerHTML = "<b>Pagados por método:</b> " +
    Object.entries(porMetodo).filter(([k]) => k !== "sin_metodo").map(([k, v]) => `${k} ${v}`).join(" · ") +
    (sinMet ? ` · <span style="color:var(--rojo);font-weight:700">sin método ${sinMet}</span>` : "");
  bR.appendChild(bMet);

  // Punto de control
  if (s.real.punto_control) {
    const pc = s.real.punto_control;
    bR.appendChild(el("p", { innerHTML: `<b>Punto de control:</b> meta ${pc.meta} para ${pc.fecha} · faltan ${pc.faltan_a_meta} · ${pc.pct}% cumplido` }));
  }
  cont.appendChild(bR);

  // BLOQUE NUEVA ZELANDA (ventas de Sofía, aparte)
  if (nz) {
    const bNZ = el("div", { className: "bloque-stats" });
    bNZ.appendChild(el("h2", { textContent: "Nueva Zelanda · ventas de Sofía" }));
    const gNZ = el("div", { className: "cifras" });
    gNZ.innerHTML =
      `<div><b>${nz.pagados}</b><span>pagados</span></div>` +
      `<div><b>${nz.apartados}</b><span>apartados</span></div>` +
      `<div><b>${nz.por_verificar}</b><span>por verificar</span></div>` +
      `<div><b>${nz.transferencia + nz.efectivo}</b><span>con pago NZ</span></div>`;
    bNZ.appendChild(gNZ);
    bNZ.appendChild(el("p", { innerHTML: `<b>Pagados en NZ:</b> transferencia ${nz.transferencia} · efectivo ${nz.efectivo}` +
      (nz.sin_clasificar ? ` · <span style="color:var(--rojo);font-weight:700">sin clasificar ${nz.sin_clasificar}</span>` : "") }));
    bNZ.appendChild(el("p", { textContent: `Cobrado en NZ: NZD ${Number(nz.ingresos_nzd).toLocaleString("es-CO")} (≈ ${fmtCOP(nz.ingresos_cop)}).` }));
    cont.appendChild(bNZ);
  }

  // BLOQUE PROYECCIÓN
  const bP = el("div", { className: "bloque-stats proy" });
  bP.appendChild(el("h2", { textContent: "Proyección · si el ritmo sigue igual" }));
  const p = s.proyeccion;
  bP.appendChild(el("p", { textContent: `Ritmo últimos 7 días: ${p.ventas_ultimos_7d} pagados · faltan ${p.dias_hasta_cierre} días para el cierre.` }));

  const bloqueCaso = (titulo, caso, color) => {
    const d = el("div", { style: "margin-top:10px;padding:10px;border-left:4px solid " + color + ";background:#fafafa" });
    d.innerHTML =
      `<div class="label">${titulo}</div>` +
      `<div class="cifra">${caso.vendidos} vendidos</div>` +
      `<table>` +
      `<tr><td>Esperado (REGLA-PREMIO)</td><td align="right"><b>${fmtCOP(caso.esperado)}</b></td></tr>` +
      `<tr><td>Neto si gana un vendido</td><td align="right">${fmtCOP(caso.neto_vendido)}</td></tr>` +
      `<tr><td>Neto si va consolación</td><td align="right">${fmtCOP(caso.neto_consolacion)}</td></tr>` +
      `</table>`;
    return d;
  };
  bP.appendChild(bloqueCaso("Al ritmo actual (proyección)", p.al_ritmo_actual, "var(--azul)"));
  bP.appendChild(bloqueCaso("Si llegas al piso (860)", p.al_nivel_del_piso, "var(--verde)"));
  bP.appendChild(bloqueCaso("Si llegas a la meta (900)", p.al_nivel_de_meta, "var(--amarillo)"));

  const esperado = Number(p.al_ritmo_actual.esperado);
  const piso = Number(s.real.pagados) * 6000; // referencia visual sencilla
  if (esperado < 3000000) {
    const f = el("div", { className: "franja-rojo" });
    f.textContent = `Alerta: la proyección actual (${fmtCOP(esperado)}) queda por debajo del piso de ${fmtCOP(3000000)}.`;
    bP.appendChild(f);
  }
  cont.appendChild(bP);

  // AUDITORÍA (dentro de Más)
  const bAud = el("div", { className: "bloque-stats" });
  bAud.appendChild(el("h2", { textContent: "Auditoría" }));
  const audFiltro = el("div", { className: "filtro" });
  audFiltro.innerHTML =
    `<select id="audAcc"><option value="">Toda acción</option>` +
    `<option>REGISTRAR_VENTA</option><option>MARCAR_PAGADO</option><option>MARCAR_POR_VERIFICAR</option>` +
    `<option>LIBERAR</option><option>DAR_24H</option><option>DESHACER</option>` +
    `<option>ENTREGAR_EFECTIVO</option><option>CONSIGNAR</option></select>` +
    `<input id="audClave" placeholder="Clave (número o id de pago)" style="max-width:200px">` +
    `<button class="chico" id="bAud">Buscar</button>`;
  bAud.appendChild(audFiltro);
  const audOut = el("div"); bAud.appendChild(audOut);
  const buscarAud = async () => {
    audOut.innerHTML = "Cargando…";
    try {
      const a = await rpc("auditoria", {
        p_accion: audFiltro.querySelector("#audAcc").value || null,
        p_clave: audFiltro.querySelector("#audClave").value.trim() || null,
        p_limit: 50
      });
      audOut.innerHTML = "";
      const info = el("p", { textContent: `${a.total} fila(s) totales · muestra: ${(a.filas || []).length}` });
      audOut.appendChild(info);
      const tbl = el("table");
      tbl.innerHTML = "<thead><tr><th align='left'>Cuándo</th><th>Acción</th><th>Clave</th><th>Lote</th><th></th></tr></thead>";
      const tb = el("tbody");
      const lotesVistos = new Set();
      for (const f of (a.filas || [])) {
        if (lotesVistos.has(f.lote)) continue;
        lotesVistos.add(f.lote);
        const tr = el("tr");
        const td1 = el("td", { textContent: new Date(f.en).toLocaleString("es-CO") });
        const td2 = el("td", { textContent: f.accion });
        const td3 = el("td", { className: "mono", textContent: f.clave });
        const td4 = el("td", { className: "mono", textContent: (f.lote || "").slice(0, 8) });
        const td5 = el("td");
        if (f.revertido || f.accion === "DESHACER") {
          td5.textContent = "revertido";
          td5.style.color = "var(--rojo)";
        } else {
          const b = el("button", { className: "chico rojo", textContent: "↩ Deshacer" });
          b.onclick = async () => {
            if (!confirm(`Deshacer el lote ${f.lote.slice(0,8)}… (${f.accion})?`)) return;
            try {
              const r = await rpc("deshacer_lote", { p_lote: f.lote });
              toast(`Deshecho · ${r.cambios} cambio(s)`, "verde");
              buscarAud();
            } catch (e) { err(e); }
          };
          td5.appendChild(b);
        }
        tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3); tr.appendChild(td4); tr.appendChild(td5);
        tb.appendChild(tr);
      }
      tbl.appendChild(tb); audOut.appendChild(tbl);
    } catch (e) { audOut.innerHTML = ""; audOut.appendChild(el("p", { className: "err", textContent: e.message })); }
  };
  audFiltro.querySelector("#bAud").onclick = buscarAud;
  cont.appendChild(bAud);
  buscarAud();

  // EXPORTAR
  const bEx = el("div", { className: "bloque-stats" });
  bEx.appendChild(el("h2", { textContent: "Exportar CSV" }));
  bEx.appendChild(el("p", { textContent: "Para auditar en el PC, pegar en Excel o guardar un respaldo externo." }));
  const exBox = el("div", { className: "filtro" });
  exBox.innerHTML = `<select id="exT"><option value="numeros">Números</option><option value="pagos">Pagos</option><option value="compradores">Compradores</option><option value="vendedores">Vendedores</option></select>`;
  const bDesc = el("button", { className: "chico verde", textContent: "Descargar" });
  bDesc.onclick = async () => {
    const t = exBox.querySelector("#exT").value;
    try {
      const csv = await rpc("exportar", { p_tabla: t });
      const u = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
      const a = el("a", { href: u, download: `mrf-${t}-${new Date().toISOString().slice(0,10)}.csv` });
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(u), 1000);
      toast("Descargado", "verde");
    } catch (e) { err(e); }
  };
  exBox.appendChild(bDesc);
  bEx.appendChild(exBox);
  cont.appendChild(bEx);

  // RESPALDOS
  const bResp = el("div", { className: "bloque-stats" });
  bResp.appendChild(el("h2", { textContent: "Respaldos diarios" }));
  bResp.appendChild(el("p", { textContent: "Snapshot JSON automático a las 3 a.m. (hora Bogotá). Se guardan los últimos 30 días." }));
  try {
    const resp = await rpc("respaldos_lista");
    if (!resp.length) bResp.appendChild(el("p", { className: "err", textContent: "Sin respaldos aún." }));
    else {
      const tbl = el("table");
      tbl.innerHTML = "<thead><tr><th align='left'>Fecha</th><th>Pagados</th><th>Pagos</th><th align='right'>Tamaño</th></tr></thead>";
      const tb = el("tbody");
      for (const r of resp) {
        const tr = el("tr");
        tr.innerHTML =
          `<td>${r.fecha}</td>` +
          `<td align="center">${r.pagados}</td>` +
          `<td align="center">${r.pagos}</td>` +
          `<td align="right">${r.tamano_kb} KB</td>`;
        tb.appendChild(tr);
      }
      tbl.appendChild(tb); bResp.appendChild(tbl);
    }
  } catch (e) { bResp.appendChild(el("p", { className: "err", textContent: e.message })); }
  cont.appendChild(bResp);

  // RANKING
  const bRk = el("div", { className: "bloque-stats" });
  bRk.appendChild(el("h2", { textContent: `Ranking de vendedores` }));
  const total = (r.con_vendedor || 0) + (r.sin_vendedor || 0);
  bRk.appendChild(el("p", { innerHTML: `<b>${r.con_vendedor}</b> ventas con vendedor · <b>${r.sin_vendedor}</b> sin vendedor (de ${total}).` }));
  if (r.con_vendedor < 10) {
    bRk.appendChild(el("p", { className: "err", textContent: "El ranking está casi vacío porque las ventas viejas del Sheet no tienen vendedor." }));
  }
  const tbl = el("table");
  tbl.innerHTML = "<thead><tr><th align='left'>Vendedor</th><th>Pag.</th><th>Comp.</th><th align='right'>Ingresos</th><th align='right'>Efectivo pend.</th></tr></thead>";
  const tb = el("tbody");
  for (const v of (r.ranking || [])) {
    const tr = el("tr");
    tr.innerHTML =
      `<td><b>${v.codigo}</b> · ${v.nombre}</td>` +
      `<td align="center">${v.pagados}</td>` +
      `<td align="center">${v.compradores}</td>` +
      `<td align="right">${fmtCOP(v.ingresos_cop)}</td>` +
      `<td align="right">${v.efectivo_pendiente_entregar ? '<span style="color:var(--rojo);font-weight:700">' + fmtCOP(v.efectivo_pendiente_entregar) + '</span>' : '—'}</td>`;
    tb.appendChild(tr);
  }
  tbl.appendChild(tb);
  bRk.appendChild(tbl);
  cont.appendChild(bRk);
}

// ---------- Vendedores ----------

async function pantallaVendedores(cont) {
  cont.appendChild(el("h1", { textContent: "Vendedores" }));
  if (YO.rol === "admin") cont.appendChild(botonAgregar());
  cont.appendChild(filtro());
  const estado = el("p", { textContent: "Cargando…" });
  cont.appendChild(estado);

  try {
    VENDEDORES_CACHE = await rpc("listar_vendedores");
  } catch (e) {
    estado.className = "err";
    estado.textContent = "No pudimos cargar la lista: " + e.message;
    return;
  }
  estado.remove();
  pintarVendedores(cont, filtroActual());
}

function filtroActual() { return { texto: ($("#fTxt")?.value || "").trim(), tipo: $("#fTipo")?.value || "todos", mostrar: $("#fMostrar")?.value || "activos" }; }

function filtro() {
  const d = el("div", { className: "filtro" });
  d.innerHTML = '<input id="fTxt" placeholder="Buscar por nombre o código"><select id="fTipo"><option value="todos">Todos</option><option value="PERSONA">Personas</option><option value="TIENDA">Tiendas</option><option value="NZ">Nueva Zelanda</option></select><select id="fMostrar"><option value="activos">Activos</option><option value="todos">Todos</option><option value="inactivos">Inactivos</option></select>';
  setTimeout(() => {
    $("#fTxt").oninput = () => { const c = $("#app"); const lista = c.querySelector(".lista-vend"); if (lista) lista.remove(); pintarVendedores(c, filtroActual()); };
    $("#fTipo").onchange = $("#fMostrar").onchange = $("#fTxt").oninput;
  }, 0);
  return d;
}

function pintarVendedores(cont, f) {
  const lista = el("div", { className: "lista-vend" });
  const esp = v => v.tipo === "ESPECIAL";
  const txt = f.texto.toLowerCase();
  const vis = VENDEDORES_CACHE.filter(v => {
    if (esp(v)) return false; // SBG y DIR no se muestran
    if (f.tipo !== "todos" && v.tipo !== f.tipo) return false;
    if (f.mostrar === "activos" && !v.activo) return false;
    if (f.mostrar === "inactivos" && v.activo) return false;
    if (txt && !(v.codigo.toLowerCase().includes(txt) || v.nombre_completo.toLowerCase().includes(txt))) return false;
    return true;
  });
  lista.appendChild(el("p", { textContent: vis.length + " vendedores" }));
  for (const v of vis) lista.appendChild(tarjetaVendedor(v));
  cont.appendChild(lista);
}

function tarjetaVendedor(v) {
  const d = el("div", { className: "vend-tarjeta" + (v.activo ? "" : " inactivo") });
  const h = el("header");
  h.appendChild(el("span", { className: "nom", textContent: v.nombre_completo }));
  h.appendChild(el("span", { className: "tipo", textContent: v.tipo === "PERSONA" ? "persona" : (v.tipo === "TIENDA" ? "tienda" : "NZ") }));
  h.appendChild(el("span", { className: "cod", textContent: v.codigo }));
  d.appendChild(h);
  const cifras = el("div", { className: "cifras" });
  // Premio del vendedor (decisión 65): 25 boletas pagadas, aunque varias sean de la misma persona.
  const META_VENDEDOR = 25;
  cifras.innerHTML =
    `<div><b>${v.pagados}</b><span>pagados</span></div>` +
    `<div><b>${v.compradores}</b><span>compradores</span></div>` +
    `<div><b>${v.apartados}</b><span>apartados</span></div>` +
    `<div><b>${Math.max(0, META_VENDEDOR - v.pagados)}</b><span>para premio (${META_VENDEDOR})</span></div>`;
  d.appendChild(cifras);
  const link = `https://mega-rifa-fusa.vercel.app/?v=${v.codigo}`;
  const linkBox = el("div", { className: "link-box" });
  linkBox.innerHTML = `<code>${link}</code>`;
  const bCopiar = el("button", { className: "chico", textContent: "Copiar" });
  bCopiar.onclick = async () => { try { await navigator.clipboard.writeText(link); toast("Link copiado"); } catch { toast("No se pudo copiar", "rojo"); } };
  linkBox.appendChild(bCopiar);
  const bWa = el("button", { className: "chico verde", textContent: "WhatsApp" });
  bWa.onclick = () => {
    const msg = `¡Hola! Soy ${v.etiqueta} y estoy vendiendo boletas de la Mega Rifa Fusa (COP 6.000). Escoge tu número aquí 👉 ${link}`;
    window.open("https://wa.me/?text=" + encodeURIComponent(msg), "_blank", "noopener");
  };
  linkBox.appendChild(bWa);
  d.appendChild(linkBox);
  if (YO.rol === "admin") {
    const acc = el("div", { className: "acciones" });
    const bEd = el("button", { className: "chico gris", textContent: "Editar" });
    bEd.onclick = () => abrirEditar(v); acc.appendChild(bEd);
    const bAct = el("button", { className: "chico " + (v.activo ? "rojo" : "verde"), textContent: v.activo ? "Desactivar" : "Activar" });
    bAct.onclick = () => cambiarEstado(v);
    acc.appendChild(bAct);
    const bAl = el("button", { className: "chico gris", textContent: "+ Alias" });
    bAl.onclick = () => agregarAlias(v); acc.appendChild(bAl);
    const bDet = el("button", { className: "chico gris", textContent: "Detalle" });
    const detBox = el("div", { className: "ficha-inline" }); detBox.hidden = true;
    bDet.onclick = async () => {
      if (!detBox.hidden) { detBox.hidden = true; bDet.textContent = "Detalle"; return; }
      if (!detBox.dataset.listo) { if (!(await llenarDetalle(v, detBox))) return; detBox.dataset.listo = "1"; }
      detBox.hidden = false; bDet.textContent = "Cerrar detalle";
    };
    acc.appendChild(bDet);
    d.appendChild(acc);
    d.appendChild(detBox);
  }
  return d;
}

function botonAgregar() {
  const d = el("div");
  const b = el("button", { textContent: "+ Agregar vendedor" });
  b.onclick = () => abrirCrear();
  d.appendChild(b);
  const bCsv = el("button", { className: "chico gris", textContent: "Descargar links (CSV)", style: "margin-left:8px" });
  bCsv.onclick = descargarCsv;
  d.appendChild(bCsv);
  return d;
}

function descargarCsv() {
  const rows = [["codigo", "nombre", "tipo", "activo", "link"]];
  for (const v of VENDEDORES_CACHE) {
    if (v.tipo === "ESPECIAL") continue;
    rows.push([v.codigo, v.nombre_completo, v.tipo, v.activo ? "SI" : "NO", `https://mega-rifa-fusa.vercel.app/?v=${v.codigo}`]);
  }
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
  const u = URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" }));
  const a = el("a", { href: u, download: "vendedores-links.csv" });
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 1000);
}

function dialogo(titulo, cuerpo, acciones) {
  const t = el("div", { className: "card" });
  t.appendChild(el("h2", { textContent: titulo }));
  if (typeof cuerpo === "string") t.appendChild(el("p", { textContent: cuerpo }));
  else t.appendChild(cuerpo);
  const bar = el("div", { className: "acciones" });
  for (const [etq, fn, cls] of acciones) {
    const b = el("button", { className: cls || "", textContent: etq });
    b.onclick = fn; bar.appendChild(b);
  }
  t.appendChild(bar);
  return t;
}

function abrirCrear() {
  const form = el("div");
  form.innerHTML =
    '<label>Nombre completo</label><input id="cNom" placeholder="Pedro Pérez">' +
    '<label>Tipo</label><select id="cTipo"><option value="PERSONA">Persona</option><option value="TIENDA">Tienda</option><option value="NZ">Nueva Zelanda</option></select>' +
    '<label>Código sugerido</label><input id="cCod" placeholder="se calcula al escribir el nombre">' +
    '<label>Teléfono (opcional, nunca público)</label><input id="cTel" inputmode="tel">';
  const d = dialogo("Nuevo vendedor", form, [
    ["Cancelar", () => d.remove(), "gris chico"],
    ["Crear", async () => {
      try {
        const r = await rpc("crear_vendedor", {
          p_nombre: form.querySelector("#cNom").value,
          p_tipo: form.querySelector("#cTipo").value,
          p_codigo: form.querySelector("#cCod").value || null,
          p_telefono: form.querySelector("#cTel").value || null
        });
        toast("Creado: " + r.codigo);
        d.remove();
        VENDEDORES_CACHE = await rpc("listar_vendedores");
        render();
      } catch (e) { err(e); }
    }, "verde"]
  ]);
  // sugerir código al escribir
  form.querySelector("#cNom").oninput = async () => {
    const n = form.querySelector("#cNom").value;
    const inp = form.querySelector("#cCod");
    if (inp.value && inp.dataset.manual) return;
    if (n.trim().length < 2) return;
    try { inp.value = await rpc("sugerir_codigo", { p_nombre: n }); } catch (_) {}
  };
  form.querySelector("#cCod").oninput = () => { form.querySelector("#cCod").dataset.manual = "1"; };
  $("#app").appendChild(d);
}

function abrirEditar(v) {
  const form = el("div");
  form.innerHTML =
    `<label>Nombre completo</label><input id="eNom" value="${v.nombre_completo}">` +
    `<label>Etiqueta pública (como sale en el selector)</label><input id="eEtq" value="${v.etiqueta}" placeholder="${v.etiqueta}">` +
    `<label>Tipo</label><select id="eTipo"><option value="PERSONA">Persona</option><option value="TIENDA">Tienda</option><option value="NZ">Nueva Zelanda</option></select>` +
    `<label>Teléfono (privado)</label><input id="eTel" value="${v.telefono || ''}">`;
  setTimeout(() => form.querySelector("#eTipo").value = v.tipo, 0);
  const d = dialogo("Editar " + v.codigo, form, [
    ["Cancelar", () => d.remove(), "gris chico"],
    ["Guardar", async () => {
      try {
        await rpc("editar_vendedor", {
          p_id: v.id,
          p_nombre: form.querySelector("#eNom").value,
          p_nombre_lista: form.querySelector("#eEtq").value,
          p_tipo: form.querySelector("#eTipo").value,
          p_telefono: form.querySelector("#eTel").value
        });
        toast("Guardado"); d.remove();
        VENDEDORES_CACHE = await rpc("listar_vendedores"); render();
      } catch (e) { err(e); }
    }, "verde"]
  ]);
  $("#app").appendChild(d);
}

async function cambiarEstado(v) {
  if (!confirm(`¿${v.activo ? "Desactivar" : "Activar"} ${v.codigo}? Esto ${v.activo ? "lo quita del selector público" : "lo vuelve a mostrar en el selector"}; el link y el historial siguen igual.`)) return;
  try {
    await rpc("cambiar_estado_vendedor", { p_id: v.id, p_activo: !v.activo });
    toast("Listo");
    VENDEDORES_CACHE = await rpc("listar_vendedores"); render();
  } catch (e) { err(e); }
}

function agregarAlias(v) {
  const alias = prompt(`Alias para ${v.codigo} (ej. "Juan Carlitos" o "JC"). Luego los mensajes con ese texto le cuentan a ${v.codigo}.`);
  if (!alias) return;
  rpc("fusionar_alias", { p_alias: alias, p_vendedor_id: v.id })
    .then(r => { toast("Alias creado: " + r.alias); render(); })
    .catch(err);
}

// Detalle de un vendedor, dentro de su propia tarjeta: a quién le ha vendido y cuáles números.
const ETQ_METODO = { NU: "Nu", EFECTIVO: "efectivo", NZ: "NZ transf.", NZ_EFECTIVO: "NZ efectivo" };
async function llenarDetalle(v, box) {
  try {
    const d = await rpc("detalle_vendedor", { p_id: v.id });
    const nums = d.numeros || [];
    const nAlias = (d.alias || []).length;
    const pag = nums.filter(n => n.estado === "PAGADO").length;
    const apa = nums.length - pag;
    box.appendChild(el("p", { textContent: `${pag} pagados · ${apa} apartados · ${nAlias} alias` + (nAlias ? " (" + d.alias.join(", ") + ")" : "") }));
    // Agrupado por comprador: «Claudia Hernandez · 10 boletas»
    const grupos = new Map();
    for (const n of nums) {
      const k = n.comprador_id || n.comprador || "—";
      if (!grupos.has(k)) grupos.set(k, { nombre: n.comprador || "—", items: [] });
      grupos.get(k).items.push(n);
    }
    box.appendChild(el("p", { className: "nota", textContent: grupos.size + " persona(s) a quienes les ha vendido" }));
    for (const g of grupos.values()) {
      const fila = el("div", { className: "det-persona" });
      const nPag = g.items.filter(i => i.estado === "PAGADO").length;
      fila.appendChild(el("div", { className: "det-nombre", textContent: `${g.nombre} · ${g.items.length} boleta${g.items.length > 1 ? "s" : ""}${nPag < g.items.length ? ` (${nPag} pagadas)` : ""}` }));
      const chips = el("div", { className: "det-chips" });
      for (const i of g.items) {
        const extra = i.estado === "PAGADO" ? (i.metodo ? " · " + (ETQ_METODO[i.metodo] || i.metodo) : "") : (i.por_verificar ? " · por verificar" : " · apartado");
        chips.appendChild(el("span", { className: "det-chip " + (i.estado === "PAGADO" ? "pag" : "apa"), textContent: i.n + extra }));
      }
      fila.appendChild(chips);
      box.appendChild(fila);
    }
    if (!nums.length) box.appendChild(el("p", { textContent: "Todavía no tiene ventas." }));
    return true;
  } catch (e) { err(e); return false; }
}

// ---------- Pendientes ----------

async function pantallaPendientes(cont) {
  cont.appendChild(el("h1", { textContent: "Referidos por resolver" }));
  cont.appendChild(el("p", { textContent: "Textos como «Otra persona…» que llegaron de la web y no se emparejaron a ningún vendedor. Asígnalos para que la venta cuente." }));
  const estado = el("p", { textContent: "Cargando…" }); cont.appendChild(estado);
  try {
    const [pend, lista] = await Promise.all([rpc("referidos_pendientes"), rpc("listar_vendedores")]);
    estado.remove();
    if (!pend.length) {
      cont.appendChild(el("p", { className: "ok", textContent: "Nada pendiente. Buena." }));
      return;
    }
    for (const p of pend) {
      const d = el("div", { className: "pendiente" });
      d.appendChild(el("div", { className: "t", textContent: `«${p.texto}»` }));
      d.appendChild(el("div", { className: "m", textContent: `Número ${p.numero || '—'} · ${new Date(p.creado_en).toLocaleString('es-CO')}` }));
      const f = el("div", { className: "f" });
      const sel = el("select");
      sel.appendChild(new Option("Escoge vendedor…", ""));
      for (const v of lista.filter(x => x.tipo !== "ESPECIAL" && x.activo)) {
        sel.appendChild(new Option(`${v.codigo} · ${v.nombre_completo}`, v.id));
      }
      f.appendChild(sel);
      const bOk = el("button", { className: "chico verde", textContent: "Asignar + alias" });
      bOk.onclick = async () => {
        if (!sel.value) return;
        try {
          await rpc("resolver_referido", { p_id: p.id, p_vendedor_id: parseInt(sel.value, 10), p_crear_alias: true });
          toast("Asignado"); render();
        } catch (ex) { err(ex); }
      };
      f.appendChild(bOk);
      const bSoloAsig = el("button", { className: "chico gris", textContent: "Solo esta venta" });
      bSoloAsig.onclick = async () => {
        if (!sel.value) return;
        try {
          await rpc("resolver_referido", { p_id: p.id, p_vendedor_id: parseInt(sel.value, 10), p_crear_alias: false });
          toast("Asignado"); render();
        } catch (ex) { err(ex); }
      };
      f.appendChild(bSoloAsig);
      d.appendChild(f);
      cont.appendChild(d);
    }
  } catch (e) {
    estado.className = "err"; estado.textContent = "No pudimos cargar: " + e.message;
  }
}

// ---------- Arranque ----------


// ────────── INICIO (home) ──────────

async function pantallaInicio(cont) {
  cont.appendChild(el("h1", { textContent: "Inicio" }));
  const estado = el("p", { textContent: "Cargando…" });
  cont.appendChild(estado);
  let c;
  try { c = await rpc("inicio_cifras"); } catch (e) {
    estado.className = "err"; estado.textContent = "No pudimos cargar: " + e.message; return;
  }
  estado.remove();

  // Alertas rojas (lo que requiere acción humana ahora)
  const alertas = [];
  if (c.vencen_pronto > 0)        alertas.push(c.vencen_pronto + " apartados vencen en menos de 3 h");
  if (c.por_verificar > 0)        alertas.push(c.por_verificar + " pago(s) por verificar en Nu");
  if (c.apartados_sin_fecha > 0)  alertas.push(c.apartados_sin_fecha + " apartados sin fecha (decide: dar 24 h o liberar)");
  if (c.referidos_pendientes > 0) alertas.push(c.referidos_pendientes + " referido(s) por resolver");
  if (alertas.length) {
    const box = el("div", { className: "pendiente" });
    box.appendChild(el("div", { className: "t", textContent: "Qué revisar hoy" }));
    for (const a of alertas) box.appendChild(el("div", { className: "m", textContent: "· " + a }));
    cont.appendChild(box);
  } else {
    cont.appendChild(el("p", { className: "ok", textContent: "Nada urgente ahora mismo." }));
  }

  // Cifras clave
  const cifras = el("div", { className: "vend-tarjeta" });
  const bloque = el("div", { className: "cifras" });
  bloque.innerHTML =
    `<div><b>${c.pagados}</b><span>pagados</span></div>` +
    `<div><b>${c.apartados}</b><span>apartados</span></div>` +
    `<div><b>${c.libres}</b><span>libres</span></div>` +
    `<div><b>${Math.max(0, 859 - c.pagados)}</b><span>faltan al piso</span></div>`;
  cifras.appendChild(el("header", {}, el("span", { className: "nom", textContent: "Hoy" })));
  cifras.appendChild(bloque);
  cont.appendChild(cifras);

  // Botón grande para registrar venta
  const b = el("button", { textContent: "+ Registrar venta", style: "width:100%;margin-top:16px;font-size:19px;padding:16px" });
  b.onclick = () => { TAB_ACTUAL = "vender"; marcarTab("vender"); render(); };
  cont.appendChild(b);

  // Botón discreto: deshacer la última acción mía
  const bU = el("button", { className: "chico gris", textContent: "↩ Deshacer la última", style: "margin-top:12px" });
  bU.onclick = deshacerUltima;
  cont.appendChild(bU);
}

function marcarTab(nombre) {
  for (const t of document.querySelectorAll(".tabs .tab")) {
    if (t.dataset.tab === nombre) t.classList.add("activo"); else t.classList.remove("activo");
  }
}

// ────────── VENDER (4 toques) ──────────

// Parsea el texto que llega por WhatsApp: números 3 cifras y, si viene, el código entre paréntesis.
// Ej.: "Hola, quiero el número 607 de la Mega Rifa Fusa, me dijo Juan Carlos (JUANCARLOS)."
// Si el comprador escogió «Otra persona» no hay código: "…, me dijo Pedro Perez." → el texto libre pasa como
// vendedor y, si no resuelve, queda en Pendientes. En inglés: "Juan Carlos told me about it (JUANCARLOS)."
function parsearMensaje(txt) {
  if (!txt) return { numeros: [], vendedor: null };
  const nums = (txt.match(/\b\d{3}\b/g) || []).map(x => x.padStart(3, "0"));
  const unicos = Array.from(new Set(nums));
  const m = txt.match(/\(([A-Z0-9]{1,24})\)/);
  let vendedor = m ? m[1] : null;
  if (!vendedor) {
    const t = txt.match(/me dijo\s+([^.\n(]{2,40})/i) || txt.match(/([^.\n(]{2,40}?)\s+told me about it/i);
    if (t) vendedor = t[1].trim();
  }
  return { numeros: unicos, vendedor };
}

async function pantallaVender(cont) {
  cont.appendChild(el("h1", { textContent: "Registrar venta" }));

  // Toque 1
  const c1 = el("div", { className: "card" });
  c1.innerHTML =
    `<label>1. Pegar el mensaje de WhatsApp (si viene)</label>` +
    `<textarea id="vMsg" rows="2" placeholder="Pega aquí lo que te mandó el comprador…" ` +
    `style="width:100%;font-family:inherit;font-size:16px;padding:10px;border:3px solid var(--negro);border-radius:8px"></textarea>` +
    `<label>Números (3 cifras, separa con espacios o comas)</label>` +
    `<input id="vNums" inputmode="numeric" placeholder="607, 123, 456">` +
    `<label>Vendedor (se completa solo si el mensaje lo trae)</label>` +
    `<select id="vVend"><option value="">Directa (sin vendedor)</option><option value="__otra">Otra persona (escribir)…</option></select>` +
    `<input id="vVendTxt" placeholder="Nombre de quien lo vendió" hidden style="margin-top:6px">`;
  cont.appendChild(c1);

  // Toque 2
  const c2 = el("div", { className: "card" });
  c2.innerHTML =
    `<label>2. Nombre del comprador</label>` +
    `<input id="vNom" placeholder="Nombre y apellido" autocomplete="off">` +
    `<div id="vSug" style="margin-top:4px;display:flex;gap:4px;flex-wrap:wrap"></div>` +
    `<label>Teléfono (opcional, nunca sale al tablero)</label>` +
    `<input id="vTel" inputmode="tel" placeholder="310…">` +
    `<label><input type="checkbox" id="vPub" checked style="width:auto;margin-right:6px">Mostrar en el tablero (si no: aparece como «Reservado»)</label>` +
    `<label><input type="checkbox" id="vTbw" style="width:auto;margin-right:6px">Dijo SÍ a recibir info de The Ber Way</label>`;
  cont.appendChild(c2);

  // Toque 3: chip de estado (según rol)
  const c3 = el("div", { className: "card" });
  c3.appendChild(el("label", { textContent: "3. Estado" }));
  const chips = el("div", { className: "acciones" });
  const opcs = YO.rol === "admin"
    ? [["APARTADO", "Apartado", "gris"], ["PAGADO_NU", "Pagado · Nu", "verde"],
       ["PAGADO_EFECTIVO", "Pagado · Efectivo", "verde"],
       ["EFECTIVO_VENDEDOR", "Efectivo con vendedor (48 h)", "gris"],
       ["POR_VERIFICAR", "Por verificar", "gris"],
       ["PAGADO_NZ", "Pagado · NZ · transferencia", "azul"], ["PAGADO_NZ_EFECTIVO", "Pagado · NZ · efectivo", "azul"]]
    : [["APARTADO", "Apartado", "gris"], ["POR_VERIFICAR", "Por verificar", "gris"],
       ["PAGADO_NZ", "Pagado · NZ · transferencia", "azul"], ["PAGADO_NZ_EFECTIVO", "Pagado · NZ · efectivo", "azul"]];
  let estadoSel = null;
  for (const [k, lbl, cls] of opcs) {
    const b = el("button", { className: "chico " + cls, textContent: lbl });
    b.onclick = (e) => { e.preventDefault(); estadoSel = k;
      for (const x of chips.querySelectorAll("button")) x.style.outline = "";
      b.style.outline = "4px solid var(--rojo)";
      // Venta de Nueva Zelanda: si no se puso vendedor, es de Sofía.
      if (k.startsWith("PAGADO_NZ") && !selVend.value && selVend.querySelector('option[value="SOFIA"]')) {
        selVend.value = "SOFIA"; selVend.onchange();
      }
    };
    chips.appendChild(b);
  }
  c3.appendChild(chips);
  cont.appendChild(c3);

  // Toque 4: Guardar
  const c4 = el("div", { className: "card" });
  const bGuardar = el("button", { className: "verde", textContent: "4. Guardar", style: "width:100%;font-size:19px;padding:16px" });
  const msg = el("p", { className: "err", id: "vErr" }); msg.style.display = "none";
  c4.appendChild(bGuardar); c4.appendChild(msg);
  cont.appendChild(c4);

  // Pegar mensaje → autollenar números y vendedor
  const txMsg = c1.querySelector("#vMsg"), txNums = c1.querySelector("#vNums");
  const selVend = c1.querySelector("#vVend"), txVendOtro = c1.querySelector("#vVendTxt");
  const limpiaCod = s => String(s || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  selVend.onchange = () => { txVendOtro.hidden = selVend.value !== "__otra"; if (!txVendOtro.hidden) txVendOtro.focus(); };
  // Menú de vendedores activos (los de la lista del panel). DIR es «Directa», o sea el vacío.
  const llenarVendedores = (lista) => {
    const otra = selVend.querySelector('option[value="__otra"]');
    for (const v of (lista || []).filter(x => x.activo && x.codigo !== "DIR")) {
      if (selVend.querySelector(`option[value="${v.codigo}"]`)) continue;
      const o = new Option(`${v.nombre_completo || v.etiqueta || v.codigo} (${v.codigo})`, v.codigo);
      selVend.insertBefore(o, otra);
    }
  };
  if (VENDEDORES_CACHE.length) llenarVendedores(VENDEDORES_CACHE);
  else rpc("listar_vendedores").then(l => { VENDEDORES_CACHE = l; llenarVendedores(l); }).catch(() => {});
  // Del mensaje de WhatsApp: si el código está en el menú se escoge; si no, queda como texto en «Otra persona».
  const escogerVendedor = (txt) => {
    const cod = limpiaCod(txt);
    if (!cod) return;
    if (selVend.querySelector(`option[value="${cod}"]`)) { selVend.value = cod; }
    else { selVend.value = "__otra"; txVendOtro.value = txt; }
    selVend.onchange();
  };
  txMsg.oninput = () => {
    const r = parsearMensaje(txMsg.value);
    if (r.numeros.length && !txNums.value) txNums.value = r.numeros.join(", ");
    if (r.vendedor && !selVend.value) escogerVendedor(r.vendedor);
  };

  // Autocompletado de comprador
  const nomInp = c2.querySelector("#vNom"), sugDiv = c2.querySelector("#vSug");
  let tDebounce;
  nomInp.oninput = () => {
    clearTimeout(tDebounce);
    const q = nomInp.value.trim();
    sugDiv.innerHTML = "";
    if (q.length < 2) return;
    tDebounce = setTimeout(async () => {
      try {
        const res = await rpc("buscar_comprador", { p_q: q });
        for (const c of (res || []).slice(0, 6)) {
          const chip = el("button", { className: "chico gris", textContent: c.nombre + (c.numeros_vigentes ? ` (${c.numeros_vigentes})` : "") });
          chip.onclick = (e) => { e.preventDefault(); nomInp.value = c.nombre; sugDiv.innerHTML = ""; };
          sugDiv.appendChild(chip);
        }
      } catch (_) {}
    }, 220);
  };

  // Guardar
  bGuardar.onclick = async (e) => {
    e.preventDefault(); msg.style.display = "none";
    try {
      const nums = txNums.value.split(/[^0-9]+/).filter(Boolean).map(x => x.padStart(3, "0"));
      if (!nums.length) throw new Error("Faltan los números");
      if (!estadoSel) throw new Error("Toca un estado");
      const nombre = nomInp.value.trim();
      if (!nombre) throw new Error("Falta el nombre");
      const vend = limpiaCod(selVend.value === "__otra" ? txVendOtro.value : selVend.value) || null;
      if (selVend.value === "__otra" && !vend) throw new Error("Escribe quién lo vendió o escoge «Directa»");
      const r = await rpc("registrar_venta", {
        p_numeros: nums, p_nombre: nombre, p_estado: estadoSel,
        p_vendedor: vend, p_telefono: c2.querySelector("#vTel").value || null,
        p_sale_publico: c2.querySelector("#vPub").checked,
        p_quiere_tbw: c2.querySelector("#vTbw").checked,
        p_pais: null, p_nota: null
      });
      if (r.vendedor_no_resuelto) toast("Vendedor «" + vend + "» quedó en Pendientes", "rojo");
      else toast("Guardado · " + r.estado_interno, "verde");
      await mostrarBoletas(nums, nombre, vend || "");
    } catch (ex) { msg.textContent = String(ex.message || ex); msg.style.display = "block"; }
  };
}

// Un bloque de boleta (imagen + idioma + copiar / compartir / guardar). Lo usan Vender (una por número) y la Ficha.
async function bloqueBoleta(numero, nombre, vendedor) {
  const dlg = el("div", { className: "boleta-bloque" });
  dlg.appendChild(el("h3", { textContent: "Boleta " + numero }));
  const sel = el("select");
  sel.innerHTML = '<option value="es">Español</option><option value="en">English</option>';
  dlg.appendChild(sel);
  const cv = el("canvas"); cv.width = 880; cv.height = 520;
  cv.style.cssText = "max-width:100%;height:auto;border:3px solid var(--negro);border-radius:8px;margin-top:12px;display:block";
  dlg.appendChild(cv);
  const acc = el("div", { className: "acciones" });
  const bCopiar = el("button", { className: "chico rojo", textContent: "📋 Copiar imagen" });
  const bCompartir = el("button", { className: "chico", textContent: "📤 Compartir" }); bCompartir.hidden = true;
  const bGuardar = el("a", { className: "chico verde", textContent: "💾 Guardar", download: "boleta-" + numero + ".png" });
  bGuardar.style.cssText = "text-decoration:none;display:inline-block;padding:6px 10px;font-weight:700;border:3px solid var(--negro);border-radius:8px;background:var(--verde);color:var(--crema)";
  acc.appendChild(bCopiar); acc.appendChild(bCompartir); acc.appendChild(bGuardar);
  dlg.appendChild(acc);
  dlg.appendChild(el("p", { className: "nota", textContent: "Copiar queda en el portapapeles; en WhatsApp mantén presionado el cuadro y Pegar." }));
  async function pintar() {
    await dibujarCuandoListo(cv, { numero, nombre, vendedor: vendedor || "", idioma: sel.value });
    bGuardar.href = cv.toDataURL("image/png");
  }
  await pintar();
  sel.onchange = pintar;

  try {
    const prueba = new File([new Blob(["x"], { type: "image/png" })], "x.png", { type: "image/png" });
    if (navigator.canShare && navigator.canShare({ files: [prueba] })) bCompartir.hidden = false;
  } catch {}

  bCopiar.onclick = async () => {
    try {
      if (!(navigator.clipboard && window.ClipboardItem)) throw new Error("sin-soporte");
      await navigator.clipboard.write([new ClipboardItem({ "image/png": obtenerBlob(cv) })]);
      bCopiar.textContent = "✅ ¡Copiada!";
      setTimeout(() => (bCopiar.textContent = "📋 Copiar imagen"), 2200);
    } catch { toast("No se pudo copiar. Usa Compartir o Guardar.", "rojo"); }
  };
  bCompartir.onclick = async () => {
    try {
      const b = await obtenerBlob(cv);
      const f = new File([b], "boleta-" + numero + ".png", { type: "image/png" });
      await navigator.share({ files: [f], title: "Mega Rifa Fusa " + numero });
    } catch { toast("No se pudo compartir", "rojo"); }
  };
  return dlg;
}

// Después de guardar una venta: una boleta por cada número, todas visibles para copiarlas una a una.
async function mostrarBoletas(numeros, nombre, vendedor) {
  for (const vieja of document.querySelectorAll("#dlg-boleta")) vieja.remove();
  const dlg = el("div", { className: "card", id: "dlg-boleta" });
  const varias = numeros.length > 1;
  dlg.appendChild(el("h2", { textContent: varias ? `${numeros.length} boletas de ${nombre}` : "Boleta de " + numeros[0] }));
  if (varias) dlg.appendChild(el("p", { className: "nota", textContent: "Números: " + numeros.join(", ") + ". Copia o guarda cada boleta por separado." }));
  $("#app").appendChild(dlg);
  for (const n of numeros) dlg.appendChild(await bloqueBoleta(n, nombre, vendedor));
  const acc = el("div", { className: "acciones" });
  const bCerrar = el("button", { className: "chico gris", textContent: "Cerrar" });
  bCerrar.onclick = () => dlg.remove();
  acc.appendChild(bCerrar); dlg.appendChild(acc);
  dlg.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ────────── NÚMEROS ──────────

async function pantallaNumeros(cont) {
  cont.appendChild(el("h1", { textContent: "Números" }));
  const filtros = el("div", { className: "filtro" });
  filtros.innerHTML =
    `<select id="fFil"><option value="todos">Todos</option><option value="pagados">Pagados</option>` +
    `<option value="apartados">Apartados</option><option value="por_verificar">Por verificar</option>` +
    `<option value="libres">Libres</option></select>` +
    `<input id="fBus" placeholder="Busca un número">`;
  cont.appendChild(filtros);
  const estado = el("p", { textContent: "Cargando…" });
  cont.appendChild(estado);

  const filtro = filtros.querySelector("#fFil"), busca = filtros.querySelector("#fBus");
  let datos = [];
  async function cargar() {
    try { datos = await rpc("tablero_admin", { p_filtro: filtro.value }); }
    catch (e) { estado.className = "err"; estado.textContent = e.message; return; }
    pintar();
  }
  function pintar() {
    const q = (busca.value || "").trim();
    for (const vieja of cont.querySelectorAll(".lista-num")) vieja.remove();
    try { estado.remove(); } catch {}
    const lista = el("div", { className: "lista-num" });
    const vis = datos.filter(d => !q || d.numero.includes(q));
    lista.appendChild(el("p", { textContent: vis.length + " números" }));
    for (const d of vis.slice(0, 300)) {
      const t = el("div", { className: "vend-tarjeta" });
      const h = el("header");
      h.appendChild(el("span", { className: "cod", textContent: d.numero }));
      h.appendChild(el("span", { className: "nom", textContent: d.estado + (d.por_verificar ? " · ⚠ por verificar" : "") }));
      if (d.vendedor) h.appendChild(el("span", { className: "tipo", textContent: d.vendedor }));
      t.appendChild(h);
      if (d.comprador) t.appendChild(el("p", { textContent: d.comprador }));
      const acc = el("div", { className: "acciones" });
      if (d.estado === "APARTADO") {
        if (YO.rol === "admin") {
          const bPag = el("button", { className: "chico verde", textContent: "Pagado · Nu" });
          bPag.onclick = () => confirmar("Marcar " + d.numero + " como PAGADO (Nu)?", () =>
            rpc("marcar_pagado", { p_numeros: [d.numero], p_metodo: "NU" }).then(() => { toast("Pagado"); cargar(); }).catch(err));
          acc.appendChild(bPag);
          const bPagEf = el("button", { className: "chico verde", textContent: "Pagado · Efectivo" });
          bPagEf.onclick = () => rpc("marcar_pagado", { p_numeros: [d.numero], p_metodo: "EFECTIVO" }).then(() => { toast("Pagado"); cargar(); }).catch(err);
          acc.appendChild(bPagEf);
        }
        const bNZ = el("button", { className: "chico verde", textContent: "Pagado · NZ transf." });
        bNZ.onclick = () => rpc("marcar_pagado", { p_numeros: [d.numero], p_metodo: "NZ" }).then(() => { toast("Pagado"); cargar(); }).catch(err);
        acc.appendChild(bNZ);
        const bNZe = el("button", { className: "chico verde", textContent: "Pagado · NZ efectivo" });
        bNZe.onclick = () => rpc("marcar_pagado", { p_numeros: [d.numero], p_metodo: "NZ_EFECTIVO" }).then(() => { toast("Pagado"); cargar(); }).catch(err);
        acc.appendChild(bNZe);
        const b24 = el("button", { className: "chico gris", textContent: "Darle 24 h" });
        b24.onclick = () => rpc("dar_24h", { p_numeros: [d.numero] }).then(() => { toast("24 h más"); cargar(); }).catch(err);
        acc.appendChild(b24);
        if (YO.rol === "admin") {
          const bLib = el("button", { className: "chico rojo", textContent: "Liberar" });
          bLib.onclick = () => confirmar("Liberar " + d.numero + " ahora?", () =>
            rpc("liberar", { p_numeros: [d.numero] }).then(() => { toast("Libre"); cargar(); }).catch(err));
          acc.appendChild(bLib);
        }
      }
      // Ficha: se despliega dentro de la misma tarjeta del número (no al final de la lista).
      const bFicha = el("button", { className: "chico gris", textContent: "Ficha" });
      const fichaBox = el("div", { className: "ficha-inline" }); fichaBox.hidden = true;
      bFicha.onclick = async () => {
        if (!fichaBox.hidden) { fichaBox.hidden = true; bFicha.textContent = "Ficha"; return; }
        try {
          if (!fichaBox.dataset.listo) {
            const f = await rpc("ficha_numero", { p_numero: d.numero });
            const linea = (txt) => fichaBox.appendChild(el("p", { textContent: txt }));
            linea(`${f.numero} · ${f.serial} · ${f.estado}${f.por_verificar ? " · por verificar" : ""}`);
            if (f.comprador) linea(`Comprador: ${f.comprador.nombre}${f.comprador.telefono ? " · " + f.comprador.telefono : ""}${f.comprador.pais === "NZ" ? " · NZ" : ""}`);
            if (f.vendedor) linea(`Vendedor: ${f.vendedor.codigo} (${f.vendedor.nombre})`);
            if (f.vendedor_texto && !f.vendedor) linea(`Vendedor (texto): «${f.vendedor_texto}»`);
            if (f.vence_en) linea("Vence: " + new Date(f.vence_en).toLocaleString("es-CO"));
            if (f.pagado_en) linea("Pagado: " + new Date(f.pagado_en).toLocaleString("es-CO") + " · " + (f.metodo || ""));
            else if (f.metodo) linea("Método: " + f.metodo);
            if (f.notas) linea("Notas: " + f.notas);
            // Boleta de nuevo, por si no se alcanzó a copiar al registrar la venta.
            if (f.comprador && f.estado !== "LIBRE") {
              const boletaBox = el("div"); boletaBox.hidden = true;
              const bBol = el("button", { className: "chico rojo", textContent: "🎟 Ver boleta" });
              bBol.onclick = async () => {
                if (!boletaBox.hidden) { boletaBox.hidden = true; bBol.textContent = "🎟 Ver boleta"; return; }
                if (!boletaBox.dataset.listo) {
                  bBol.disabled = true; bBol.textContent = "Generando…";
                  try { boletaBox.appendChild(await bloqueBoleta(f.numero, f.comprador.nombre, f.vendedor ? f.vendedor.codigo : "")); boletaBox.dataset.listo = "1"; }
                  catch (e) { err(e); bBol.disabled = false; bBol.textContent = "🎟 Ver boleta"; return; }
                  bBol.disabled = false;
                }
                boletaBox.hidden = false; bBol.textContent = "Ocultar boleta";
              };
              fichaBox.appendChild(bBol); fichaBox.appendChild(boletaBox);
            }
            fichaBox.dataset.listo = "1";
          }
          fichaBox.hidden = false; bFicha.textContent = "Cerrar ficha";
        } catch (e) { err(e); }
      };
      acc.appendChild(bFicha);
      t.appendChild(acc);
      t.appendChild(fichaBox);
      lista.appendChild(t);
    }
    cont.appendChild(lista);
  }
  filtro.onchange = cargar;
  busca.oninput = () => pintar();
  cargar();
}

function confirmar(txt, fn) { if (confirm(txt)) fn(); }

async function deshacerUltima() {
  try { const r = await rpc("deshacer_ultima", { p_lote: null }); toast("Deshecho · " + r.cambios + " cambio(s)", "verde"); render(); }
  catch (e) { err(e); }
}

supabase.auth.onAuthStateChange((event) => {
  if (event === "SIGNED_OUT") location.reload();
});
arrancar();
