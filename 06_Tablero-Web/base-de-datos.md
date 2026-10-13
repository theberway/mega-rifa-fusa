# Base de datos — Mega Rifa Fusa (Supabase)

*Sesión del 12–13 oct 2026 · decisiones 45–55.*

Esta es la fuente de verdad DE LA FASE 1 del plan `02_Decisiones/plan-panel-y-vendedores.md`.
Hoy la base es una **copia** del Google Sheet: el Sheet sigue siendo lo que vende; la base se recarga con un comando. El cambio (Fase 4) solo se hace con tu aprobación.

## Proyecto

- **ID**: `oyvrdwkoorkidoadnzmc` · región `ca-central-1` · plan gratis.
- **URL**: `https://oyvrdwkoorkidoadnzmc.supabase.co`.
- **Llave publicable** (segura de poner en el HTML): `sb_publishable_t_e7HPMI1g7rINUYIr0Ehg_OlzMMm3d`.
- **Llave service_role**: solo tú la ves (Project settings → API). **Nunca** entra al repositorio.

## Esquema (resumen)

Todas las tablas viven en el esquema **`rifa`**, que la API de Supabase **no** expone. Además cada tabla tiene RLS activado y cero políticas, así que ni `anon` ni `authenticated` entran por la API; el único acceso público es a 4 funciones del esquema `public`.

- `rifa.vendedores` · 32 filas: 14 cargados + 2 especiales (SBG, DIR) + 16 viejos inactivos (V01–V12, T01–T03, N02).
- `rifa.vendedor_alias`: 3 (N01→SOFIA, MARIAJO→MARIAJOSE, TIAJULY→JULIANA). Mantienen vivos los links que ya circulan.
- `rifa.numeros` · 1.000 filas: estado efectivo, comprador y vendedor por número.
- `rifa.compradores`: nombre completo y teléfono (nunca sale a nadie).
- `rifa.pagos`: una fila por plata verificada.
- `rifa.referidos_pendientes`: cola «Otra persona…».
- `rifa.auditoria`: cada cambio, inmutable (un trigger bloquea UPDATE/DELETE).
- `rifa.config`: todos los números del modelo financiero (`SUPUESTOS`) y los puntos de control.
- `rifa.usuarios_panel`: lista blanca (admin / turno). Se llena manualmente al crear los dos usuarios de la Fase 2.
- `rifa.push_suscripciones`, `rifa.alertas_enviadas`, `rifa.respaldos`: Fase 3.

## Las 4 funciones públicas

Son las únicas callables sin login, y están diseñadas para devolver solo el mínimo. Reciben la llave publicable; cualquier otro endpoint devuelve 404.

| Función | Qué devuelve | Verifica |
|---|---|---|
| `tablero_publico()` | `[número, estado, nombre_acortado]` para los 37 que no están libres. Un apartado con `vence_en` ya pasado se devuelve como libre, sin esperar al cron | Nunca aparece un nombre completo ni un teléfono |
| `vendedores_selector()` | 14 pares `{c: código, n: etiqueta}` — vendedores activos no especiales, en orden alfabético | SBG y DIR y los V01–T03 inactivos NO salen |
| `resolver_codigo(c)` | Toma lo que venga en `?v=` o lo que escribió el comprador, aplica los alias y devuelve el código oficial y la etiqueta si el vendedor sigue activo | `?v=N01` resuelve a `SOFIA` |
| `mini_tarjeta(c)` | Solo conteos de un código: pagados, compradores distintos, apartados pendientes, cuánto le falta para el premio | No hay nombres de compradores, teléfonos ni dinero |

### Pruebas (12 oct)

- `tablero_publico()` → 37 filas (31 pagadas, 6 apartadas), nombres acortados. Comparado 1:1 contra el CSV del Sheet con `verificar.py`: **cero diferencias**.
- `vendedores_selector()` → 14, en orden alfabético, con `Paula V.`/`Paula G.` y `Sofia`.
- `resolver_codigo`: `N01`→`SOFIA`, `TIAJULY`→`JULIANA`, `MARIAJO`→`MARIAJOSE`, `JUANCARLOS` igual, `V03` devuelve el código sin etiqueta (inactivo) → la web lo mostrará como «te atiende V03».
- `mini_tarjeta`: funciona para los 14; `SBG`/`DIR` devuelven `ok:false` (especiales).
- `rifa.*` **no es accesible** desde la API (probado con la llave publicable: 404).

## Migraciones y pruebas

- `supabase/migraciones/001_base.sql` → esquema, tablas, RLS, funciones puras (`acortar`, `normalizar`, `clave`, `etiqueta_base`), auditoría inmutable y `rifa.config`.
- `supabase/migraciones/002_vendedores_y_publico.sql` → `rifa.etiquetas`, `rifa.buscar_vendedor`, `rifa.sugerir_codigo` y las 4 RPC públicas.
- `supabase/migraciones/003_semilla_vendedores.sql` → 14 + especiales + viejos + alias.
- `supabase/migraciones/004_copia_y_vencimiento.sql` → `rifa.liberar_vencidos`, `rifa.cargar_copia` y el cron de 5 minutos.
- `supabase/pruebas/paridad.sql` → `acortar`, `normalizar` y vencimiento con reloj simulado.
- `pruebas/paridad.mjs` → la misma `acortar()` que la web, con los mismos casos.

## Cómo recargar la copia (durante Fase 1)

```bash
cd 06_Tablero-Web/migracion
python3 importar.py              # lee el CSV público, arma payload.json
# Después, en el panel SQL de Supabase:
#   select rifa.cargar_copia('<pega aquí el payload.json>'::jsonb);
```

Si quieres enriquecer con nombres completos (sin publicar nada), pon `compradores.csv` y `pagos.csv` en `06_Tablero-Web/_privado/` (está en `.gitignore`). `cargar_copia` **solo funciona en `modo='ensayo'`**: si alguien lo llama después del cambio, se niega.

## Verificar 1:1

```bash
export SUPABASE_ANON_KEY="sb_publishable_t_e7HPMI1g7rINUYIr0Ehg_OlzMMm3d"
python3 06_Tablero-Web/migracion/verificar.py
```

Debe decir «Diferencias: 0». Si no, no se hace el cambio.

## Lo que falta de las fases siguientes

| Fase | Qué queda | Dónde |
|---|---|---|
| **2 · Panel admin** | `/admin` con login + 2FA, roles, pestañas Vender · Números · Vendedores. También las RPC con `SECURITY DEFINER` del esquema `rifa` para registrar venta, marcar pagado, liberar, dar 24 h, crear vendedor, editar vendedor, activar/desactivar, fusionar alias y resolver referido. **PARADA**: antes de la Fase 2 tienes que crear los dos usuarios en Supabase (Authentication → Add user), apagar «Allow new users to sign up» y pasarme sus `user_id` para agregarlos a `rifa.usuarios_panel` | `publicar/admin/`, `supabase/migraciones/005_...sql` |
| **3 · Plata y alertas** | Efectivo con botones «Ya me entregó» / «Ya consigné», estadísticas (con las fórmulas del modelo), auditoría con deshacer, exportar CSV, respaldo diario (cron) y Edge Function de push + VAPID | `publicar/admin/`, `supabase/funciones/alertas/`, `supabase/migraciones/006_...sql` |
| **4 · Cambio del tablero** | Encender `FUENTE="supabase"` en la web, poner `rifa.config.modo='real'`, dejar el Sheet protegido y dejar de publicar su CSV | `publicar/index.html` |
| **5 · Mini-tarjetas y retiro del Excel** | `/v/CODIGO` ya construida en Fase 1; falta actualizar las guías de vendedores y la rutina diaria | `codigos-de-vendedores.md` ya actualizado; falta `07_Kit-de-Ventas/05_...md` y `03_Hoja-de-ruta/rutina-diaria.md` |

## Avisos de seguridad del linter (todos son a propósito)

- **12 × INFO «RLS Enabled No Policy»** en `rifa.*`: segunda defensa. Ni `anon` ni `authenticated` tienen `GRANT`; el esquema `rifa` no está expuesto.
- **4 × WARN «anon puede ejecutar SECURITY DEFINER»** y 4 × para `authenticated`: son las 4 RPC públicas, intencionales. Devuelven solo lo mínimo acortado.
