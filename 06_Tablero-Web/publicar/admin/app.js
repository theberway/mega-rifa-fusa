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
  let s, r;
  try {
    [s, r] = await Promise.all([rpc("estadisticas"), rpc("stats_vendedores")]);
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
    `<tr><td>Pagos registrados</td><td align="right"><b>${s.real.pagos_registrados}</b></td></tr>` +
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
  const umbral = 25;
  cifras.innerHTML =
    `<div><b>${v.pagados}</b><span>pagados</span></div>` +
    `<div><b>${v.compradores}</b><span>compradores</span></div>` +
    `<div><b>${v.apartados}</b><span>apartados</span></div>` +
    `<div><b>${Math.max(0, umbral + 1 - v.compradores)}</b><span>para premio</span></div>`;
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
    bDet.onclick = () => abrirDetalle(v); acc.appendChild(bDet);
    d.appendChild(acc);
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

async function abrirDetalle(v) {
  try {
    const d = await rpc("detalle_vendedor", { p_id: v.id });
    const body = el("div");
    const nums = d.numeros || [];
    const nAlias = (d.alias || []).length;
    body.innerHTML = `<p><b>${nums.length}</b> números a su nombre · <b>${nAlias}</b> alias.</p>`;
    if (nAlias) body.appendChild(el("p", { textContent: "Alias: " + d.alias.join(", ") }));
    const tbl = el("table"); tbl.style.cssText = "width:100%;font-size:13px;border-collapse:collapse;margin-top:8px";
    tbl.innerHTML = "<thead><tr><th style='text-align:left;border-bottom:1px solid #000'>Número</th><th style='text-align:left;border-bottom:1px solid #000'>Estado</th><th style='text-align:left;border-bottom:1px solid #000'>Comprador</th></tr></thead>";
    const tb = el("tbody");
    for (const n of nums) {
      const tr = el("tr");
      tr.innerHTML = `<td style='font-family:Space Mono,monospace'><b>${n.n}</b></td><td>${n.estado}</td><td>${n.comprador || ''}</td>`;
      tb.appendChild(tr);
    }
    tbl.appendChild(tb); body.appendChild(tbl);
    const dlg = dialogo("Detalle · " + v.codigo, body, [["Cerrar", () => dlg.remove(), "gris chico"]]);
    $("#app").appendChild(dlg);
  } catch (e) { err(e); }
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
// Ej.: "Quiero el 607 de la Mega Rifa Fusa, me dijo Juan Carlos (JUANCARLOS)"
function parsearMensaje(txt) {
  if (!txt) return { numeros: [], vendedor: null };
  const nums = (txt.match(/\b\d{3}\b/g) || []).map(x => x.padStart(3, "0"));
  const unicos = Array.from(new Set(nums));
  const m = txt.match(/\(([A-Z0-9]{1,24})\)/);
  const vendedor = m ? m[1] : null;
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
    `<label>Vendedor (código, se completa del mensaje)</label>` +
    `<input id="vVend" placeholder="JUANCARLOS · deja vacío si fue directa">`;
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
       ["POR_VERIFICAR", "Por verificar", "gris"]]
    : [["APARTADO", "Apartado", "gris"], ["POR_VERIFICAR", "Por verificar", "gris"],
       ["PAGADO_NZ", "Pagado · NZ", "verde"]];
  let estadoSel = null;
  for (const [k, lbl, cls] of opcs) {
    const b = el("button", { className: "chico " + cls, textContent: lbl });
    b.onclick = (e) => { e.preventDefault(); estadoSel = k;
      for (const x of chips.querySelectorAll("button")) x.style.outline = "";
      b.style.outline = "4px solid var(--rojo)";
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
  const txMsg = c1.querySelector("#vMsg"), txNums = c1.querySelector("#vNums"), txVend = c1.querySelector("#vVend");
  txMsg.oninput = () => {
    const r = parsearMensaje(txMsg.value);
    if (r.numeros.length && !txNums.value) txNums.value = r.numeros.join(", ");
    if (r.vendedor && !txVend.value) txVend.value = r.vendedor;
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
      const vend = (txVend.value || "").toUpperCase().replace(/[^A-Z0-9]/g, "") || null;
      const r = await rpc("registrar_venta", {
        p_numeros: nums, p_nombre: nombre, p_estado: estadoSel,
        p_vendedor: vend, p_telefono: c2.querySelector("#vTel").value || null,
        p_sale_publico: c2.querySelector("#vPub").checked,
        p_quiere_tbw: c2.querySelector("#vTbw").checked,
        p_pais: null, p_nota: null
      });
      if (r.vendedor_no_resuelto) toast("Vendedor «" + vend + "» quedó en Pendientes", "rojo");
      else toast("Guardado · " + r.estado_interno, "verde");
      await mostrarBoleta(nums[0], nombre, vend || "", nums.length);
    } catch (ex) { msg.textContent = String(ex.message || ex); msg.style.display = "block"; }
  };
}

async function mostrarBoleta(numero, nombre, vendedor, cantidad) {
  const dlg = el("div", { className: "card", id: "dlg-boleta" });
  dlg.appendChild(el("h2", { textContent: "Boleta de " + numero + (cantidad > 1 ? " (y " + (cantidad - 1) + " más)" : "") }));
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
  const bCerrar = el("button", { className: "chico gris", textContent: "Cerrar" });
  acc.appendChild(bCopiar); acc.appendChild(bCompartir); acc.appendChild(bGuardar); acc.appendChild(bCerrar);
  dlg.appendChild(acc);
  dlg.appendChild(el("p", { className: "nota", textContent: "Copiar queda en el portapapeles; en WhatsApp mantén presionado el cuadro y Pegar." }));
  $("#app").appendChild(dlg);

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
  bCerrar.onclick = () => dlg.remove();
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
        const bNZ = el("button", { className: "chico verde", textContent: "Pagado · NZ" });
        bNZ.onclick = () => rpc("marcar_pagado", { p_numeros: [d.numero], p_metodo: "NZ" }).then(() => { toast("Pagado"); cargar(); }).catch(err);
        acc.appendChild(bNZ);
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
      const bFicha = el("button", { className: "chico gris", textContent: "Ficha" });
      bFicha.onclick = async () => {
        try {
          const f = await rpc("ficha_numero", { p_numero: d.numero });
          const body = el("div");
          body.innerHTML = `<p><b>${f.numero}</b> · ${f.serial} · ${f.estado}${f.por_verificar ? " · por verificar" : ""}</p>`;
          if (f.comprador) body.innerHTML += `<p>Comprador: ${f.comprador.nombre}${f.comprador.telefono ? " · " + f.comprador.telefono : ""}</p>`;
          if (f.vendedor) body.innerHTML += `<p>Vendedor: ${f.vendedor.codigo} (${f.vendedor.nombre})</p>`;
          if (f.vendedor_texto && !f.vendedor) body.innerHTML += `<p>Vendedor (texto): «${f.vendedor_texto}»</p>`;
          if (f.vence_en) body.innerHTML += `<p>Vence: ${new Date(f.vence_en).toLocaleString("es-CO")}</p>`;
          if (f.pagado_en) body.innerHTML += `<p>Pagado: ${new Date(f.pagado_en).toLocaleString("es-CO")} · ${f.metodo}</p>`;
          if (f.notas) body.innerHTML += `<p>Notas: ${f.notas}</p>`;
          const dlg = dialogo("Ficha · " + f.numero, body, [["Cerrar", () => dlg.remove(), "gris chico"]]);
          $("#app").appendChild(dlg);
        } catch (e) { err(e); }
      };
      acc.appendChild(bFicha);
      t.appendChild(acc);
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
