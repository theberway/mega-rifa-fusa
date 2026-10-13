# Handoff para la próxima sesión local — Mega Rifa Fusa

*Guardado el 2026-10-13. Rama: `claude/sweet-maxwell-bvoqti`. Último commit: `dd7455b` (Fase 2).*

## Qué está hecho

- **Fase 1** · Base de datos Supabase (proyecto `oyvrdwkoorkidoadnzmc`): esquema `rifa`, 1.000 números, 32 vendedores + alias, 4 RPC públicas (`tablero_publico`, `vendedores_selector`, `resolver_codigo`, `mini_tarjeta`), cron de vencimientos cada 5 min, carga 1:1 del Sheet verificada con cero diferencias (31 pagados · 6 apartados · 963 libres · 15 compradores).
- **Fase 2** · Panel `/admin` en vivo en https://mega-rifa-fusa.vercel.app/admin con login + 2FA (TOTP) y pestañas **Vendedores** y **Pendientes**. Mini-tarjeta pública en `/v/CODIGO`.
- Lista blanca: Santiago (`admin`, `f987cff5-3429-4f01-a5f3-4d5adb1046dc`) y Sofía (`turno`, `62b89bb4-0fe3-4365-b675-24fabec11bd3`).
- La web pública **sigue leyendo el Google Sheet**. Nada le cambió a nadie que ya compró.

## Qué falta (Fase 3 → Fase 5)

| Fase | Qué | Dónde escribirlo |
|---|---|---|
| **3 · Ventas** | RPC `registrar_venta`, `marcar_pagado`, `marcar_por_verificar`, `liberar`, `dar_24h`, `deshacer_ultima` + pestaña Vender (4 toques) y generador de boleta reutilizando `generador-privado.html` | `06_Tablero-Web/supabase/migraciones/006_rpcs_ventas.sql`, `publicar/admin/boleta.js`, `publicar/admin/app.js` |
| **3 · Plata y auditoría** | `entregar_efectivo`, `consignar`, `estadisticas`, `stats_vendedores`, `deshacer_ultima`, `exportar`. Pestañas Plata y Más | `publicar/admin/app.js`, `supabase/migraciones/007_plata_estadisticas.sql` |
| **3 · Push + respaldo** | Edge Function `alertas` (con VAPID en Vault), cron de respaldo diario a `rifa.respaldos`, service worker en `publicar/admin/sw.js` | `supabase/funciones/alertas/`, `publicar/admin/sw.js`, `publicar/admin/manifest.webmanifest` |
| **4 · Cutover** · ⏸ aprobación | Encender `FUENTE="supabase"` en `publicar/index.html`, poner `rifa.config.modo='real'`, actualizar `publicar/vercel.json` para dejar de servir el Sheet. Antes: `verificar.py` da cero diferencias | `publicar/index.html`, SQL `update rifa.config set valor='"real"' where clave='modo'` |
| **5 · Retiro del Excel** | Actualizar `07_Kit-de-Ventas/05_guia-vendedores-y-tiendas.md`, `03_Hoja-de-ruta/rutina-diaria.md`, `codigos-de-vendedores.md` y `LEEME-como-publicar.md` para la nueva rutina | esos archivos |

Detalle completo en `02_Decisiones/plan-panel-y-vendedores.md`.

## Cómo arrancar la próxima sesión local

```bash
# 1. Clonar o actualizar
git clone https://github.com/theberway/mega-rifa-fusa.git
cd mega-rifa-fusa
git fetch origin
git checkout claude/sweet-maxwell-bvoqti
git pull origin claude/sweet-maxwell-bvoqti

# 2. Verificar que ves los commits
git log --oneline -3
# dd7455b  Panel admin (Fase 2): login + 2FA + Vendedores + Pendientes
# 78a6e93  Base de datos (Fase 1): Supabase + vendedores + mini-tarjeta
# ca741af  Web: nombres acortados automaticos, ...

# 3. Leer siempre en este orden:
#    CLAUDE.md  →  00_EMPIEZA-AQUI.md  →  02_Decisiones/plan-panel-y-vendedores.md
#               →  06_Tablero-Web/base-de-datos.md
```

Lo que la nueva sesión necesita en `local`:

- **Conector Supabase activo** (MCP de Supabase): el proyecto es `oyvrdwkoorkidoadnzmc`. Si lo tienes conectado en tu Claude.ai, la nueva sesión escribe directo a la base.
- **Conector Vercel activo** o `vercel` CLI: proyecto `mega-rifa-fusa`, team `team_fDZUBDk4ynif732wPrTpXxQU`.
- La **service_role key** y la **llave VAPID** nunca entran al repositorio. Si la Fase 3 necesita VAPID, se guarda en Vault de Supabase (no en código).
- Para probar el panel con tu cuenta ya tienes el user `financemaster66@gmail.com` como `admin` y Sofía como `turno`. Ambos están en `rifa.usuarios_panel`.

## Datos privados que NO están en el repo

- Nombres completos de los 15 compradores del Sheet (están en la base, no publicados).
- Teléfonos (los campos existen pero están vacíos; se llenarán al migrar `COMPRADORES.csv` desde el Sheet).
- `_privado/` siempre ignorado (`.gitignore` raíz).

## Prompt para arrancar la nueva sesión

Está en el PR (sección «Cómo seguir»). Lo pegas tal cual.
