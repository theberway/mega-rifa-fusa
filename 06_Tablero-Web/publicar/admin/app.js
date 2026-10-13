// Panel admin · Mega Rifa Fusa
// Usa supabase-js v2 (ESM) con versión fija. CSP permite el host de Supabase y jsDelivr.
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.46.1/+esm";

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
let TAB_ACTUAL = "vendedores";

async function mostrarApp(yo) {
  YO = yo;
  $("#login").hidden = true; $("#mfa").hidden = true; $("#app").hidden = false; $("#tabs").hidden = false;
  $("#yo").textContent = (yo.rol === "admin" ? "admin · " : "turno · ") + (yo.email || "");
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
  if (TAB_ACTUAL === "vendedores") return pantallaVendedores(app);
  if (TAB_ACTUAL === "pendientes") return pantallaPendientes(app);
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

supabase.auth.onAuthStateChange((event) => {
  if (event === "SIGNED_OUT") location.reload();
});
arrancar();
