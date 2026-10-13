# Handoff para la próxima sesión local — Mega Rifa Fusa

*Guardado el 2026-10-13. Rama: `claude/sweet-maxwell-bvoqti`. Fase 3A desplegada; siguiente sesión arranca en Fase 3B.*

## Qué está hecho

- **Fase 1** · Base de datos Supabase (proyecto `oyvrdwkoorkidoadnzmc`): esquema `rifa`, 1.000 números, 32 vendedores + alias, 4 RPC públicas, cron de vencimientos cada 5 min. Carga 1:1 del Sheet verificada con cero diferencias (31 pagados · 6 apartados · 963 libres · 15 compradores).
- **Fase 2** · Panel `/admin` en vivo con login + 2FA (TOTP) y pestañas **Vendedores** y **Pendientes**. Mini-tarjeta pública en `/v/CODIGO`.
- **Fase 3A** (13 oct) · **Ventas en 4 toques + boleta**, en vivo. Migraciones **006 / 006b / 006c** (`06_Tablero-Web/supabase/migraciones/006_rpcs_ventas.sql`). Panel con pestañas nuevas **Inicio · Vender · Números** y boleta reutilizando el generador privado (`publicar/admin/boleta.js`, oculta `SBG`/`DIR` y achica la letra si el código es largo). Decisiones 56–58.
- Lista blanca: Santiago (`admin`, `f987cff5-3429-4f01-a5f3-4d5adb1046dc`) y Sofía (`turno`, `62b89bb4-0fe3-4365-b675-24fabec11bd3`).
- La web pública **sigue leyendo el Google Sheet**. Nada le cambió a nadie que ya compró. `SHEET_CSV` sigue presente y no hay rastro de `supabase` en `publicar/index.html` (comprobado byte a byte).

## Qué falta (Fase 3B → Fase 5)

| Fase | Qué | Dónde escribirlo |
|---|---|---|
| **3B · Plata y estadísticas** | `entregar_efectivo`, `consignar`, `estadisticas`, `stats_vendedores`, pestaña **Plata** (solo admin). Las fórmulas vienen de `04_Finanzas/modelo-financiero.xlsx` (EMPIEZA!C8/C10/C12, REGLA-PREMIO). Separar `real` de `proyeccion` en el panel; con 35 de 37 ventas sin vendedor el desglose por vendedor sale casi vacío y hay que decirlo | `supabase/migraciones/007_plata_estadisticas.sql`, `publicar/admin/app.js` |
| **3C · Auditoría, exportar y respaldo** | `auditoria`, `deshacer_lote` arbitrario, `exportar()` → CSV con BOM (como `descargarCsv()` que ya existe), cron de respaldo diario a `rifa.respaldos`. Pestaña **Más** | `supabase/migraciones/008_auditoria_respaldo.sql`, `publicar/admin/app.js` |
| **4 · Cutover** · ⏸ aprobación | Encender `FUENTE="supabase"` en `publicar/index.html`, poner `rifa.config.modo='real'`, dejar el Sheet protegido. Antes: `verificar.py` da cero diferencias | `publicar/index.html`, SQL `update rifa.config set valor='"real"' where clave='modo'` |
| **5 · Retiro del Excel** | Actualizar `07_Kit-de-Ventas/05_guia-vendedores-y-tiendas.md`, `03_Hoja-de-ruta/rutina-diaria.md`, `codigos-de-vendedores.md` y `LEEME-como-publicar.md` | esos archivos |

**Push de la PWA (decisión 57):** se difiere hasta que Santiago genere e instale la llave VAPID en los secretos de Supabase y agregue el panel a la pantalla de inicio de su iPhone. Fase 3 entrega solo avisos dentro del panel.

**Plata vieja (decisión 56):** las 31 ventas que llegaron del Sheet quedan sin fila de pago y 35 de 37 sin vendedor. Se corrigen cuando lleguen los CSV privados y se vuelva a correr `importar.py`.

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
