# Códigos de vendedores — cómo funcionan y cuáles son

*Última actualización: 2026-10-12 — carga inicial de 14 vendedores en la base (decisión 47). Reemplaza la lista `V01–V12`/`T01–T03`, que queda inactiva como respaldo.*

## Qué es un código de vendedor, en una frase

Es **un apodo corto** que identifica a cada persona que vende. Sirve para:

1. **Saber quién vendió qué.** El panel suma solo: «JUANCARLOS lleva 14 pagados».
2. **Darle a cada vendedor su propio link.** `?v=JUANCARLOS` → el botón «Lo quiero» abre WhatsApp con ese código ya puesto.
3. **Mini-tarjeta propia.** Cada vendedor abre `mega-rifa-fusa.vercel.app/v/JUANCARLOS` y ve **solo sus** conteos: pagados, compradores distintos, apartados pendientes y cuánto le falta para el premio. **Nunca** ve nombres de otros compradores, ni teléfonos, ni dinero.

No es una clave ni un usuario. Es público: puede ir en una tarjeta impresa sin problema.

## Regla del código (decisión 34 ampliada el 10 oct, decisión 47 el 12 oct)

- **MAYÚSCULAS, sin tildes, espacios ni guiones.** `ANGELICA`, `MARIAJOSE`, `JUANCARLOS`.
- **Dos personas con el mismo nombre de pila**: se añade la inicial del apellido (`PAULAV` / `PAULAG`) o un número (`ANGELICA2`).
- **Máximo 24 caracteres.** La web limpia lo que viene en `?v=` a solo `A-Z0-9`.
- **Especiales que no cambian**: `SBG` (Santiago, no lleva comisión) y `DIR` (sin vendedor, llegó por el Canal o un Estado).
- **Alias**: `N01` sigue valiendo como `SOFIA` (es la Sofía de NZ, decisión 48). Mariajo y Tia July también quedan como alias.

## Los 14 cargados hoy (al 12 oct)

| Vendedor | Código | Link para compartir |
|---|---|---|
| Andres Bernal | `ANDRES` | https://mega-rifa-fusa.vercel.app/?v=ANDRES |
| Ana Lucia Bello | `ANALUCIA` | https://mega-rifa-fusa.vercel.app/?v=ANALUCIA |
| Angelica Aranguren | `ANGELICA` | https://mega-rifa-fusa.vercel.app/?v=ANGELICA |
| Brayan Sarmiento | `BRAYAN` | https://mega-rifa-fusa.vercel.app/?v=BRAYAN |
| Cesar Casas | `CESAR` | https://mega-rifa-fusa.vercel.app/?v=CESAR |
| Gabriela Quitian | `GABRIELA` | https://mega-rifa-fusa.vercel.app/?v=GABRIELA |
| Juan Carlos Montaña | `JUANCARLOS` | https://mega-rifa-fusa.vercel.app/?v=JUANCARLOS |
| Juliana Gomez | `JULIANA` | https://mega-rifa-fusa.vercel.app/?v=JULIANA |
| Maria Jose Lozano | `MARIAJOSE` | https://mega-rifa-fusa.vercel.app/?v=MARIAJOSE |
| Paula Gomez | `PAULAG` | https://mega-rifa-fusa.vercel.app/?v=PAULAG |
| Paula Valencia | `PAULAV` | https://mega-rifa-fusa.vercel.app/?v=PAULAV |
| Sofia Montaña (NZ) | `SOFIA` | https://mega-rifa-fusa.vercel.app/?v=SOFIA (y `?v=N01` también le cuenta) |
| Sophia Moreno | `SOPHIA` | https://mega-rifa-fusa.vercel.app/?v=SOPHIA |
| Yolanda Bermudez | `YOLANDA` | https://mega-rifa-fusa.vercel.app/?v=YOLANDA |

## Especiales y respaldo

| Código | Qué es |
|---|---|
| `SBG` | Santiago, venta directa. **No** aparece en el selector público ni en la mini-tarjeta |
| `DIR` | «Llegó solo» (por el Canal, un Estado o un QR). Mide cuánto vende la campaña por sí misma |
| `N01` | **Alias de `SOFIA`**: los links que ya circulan con `?v=N01` siguen contando para Sofía |
| `V01` a `V12`, `T01`, `T02`, `T03`, `N02` | Códigos viejos sin asignar. Quedan **inactivos**: no aparecen en el selector, pero si alguien ya tenía un link con esos códigos, el sistema no se rompe |

## Alias ya cargados (links viejos que siguen funcionando)

- `?v=N01` → cuenta para `SOFIA`.
- Un mensaje con «Mariajo» → el panel lo asigna a `MARIAJOSE`.
- Un mensaje con «Tia July» → el panel lo asigna a `JULIANA`.

En el panel se pueden agregar más alias con un toque («fusionar»).

## El link `?v=` y la web

- La web ya acepta `?v=CODIGO` (hasta 24 caracteres, se limpia a `A-Z0-9`) y lo guarda en `localStorage`.
- Al tocar «Lo quiero» en un número se abre WhatsApp con el mensaje escrito, incluyendo el código.
- En la cabecera dice «te atiende JUANCARLOS».

## Mini-tarjeta del vendedor

Cada vendedor abre su propia página de solo lectura, con botón para **copiar su link** y **compartirlo por WhatsApp** con un mensaje de bienvenida. No tiene clave ni login:

```
https://mega-rifa-fusa.vercel.app/v/JUANCARLOS
```

Muestra solo pagados, compradores distintos, apartados pendientes y cuánto le falta para el premio.

## Decisiones de referencia

Están en `02_Decisiones/registro-de-decisiones.md`: 34 (código = nombre, formato), 47 (14 vendedores cargados), 48 (Sofía = N01), 49 (selector y mensaje), 54 (mini-tarjeta `/v/CODIGO`). Y el plan completo en `02_Decisiones/plan-panel-y-vendedores.md`.
