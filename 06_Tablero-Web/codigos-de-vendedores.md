# Códigos de vendedores — cómo funcionan y cuáles son

*Sesión 3, 2026-10-03. Pediste que te ayudara con esto: acá está resuelto, los códigos ya están hechos y no hay que inventar nada el domingo.*

## Qué es un código de vendedor, en una frase

Es **un apodo corto de 3 caracteres** que identifica a cada persona que vende. Sirve para tres cosas y nada más:

1. **Saber quién vendió qué.** En la hoja `NUMEROS`, columna `VENDEDOR`, se escribe el código. Al final del día el Sheet cuenta solo: "V03 lleva 14 pagados".
2. **Darle a cada vendedor su propio link.** Si alguien entra por `...?v=V03`, el botón "Lo quiero" manda el mensaje a WhatsApp ya firmado con `V03`. Vos ves de quién vino sin preguntar.
3. **Pagar bien.** La comisión del 10% a tiendas sale de contar los pagados con el código de esa tienda. Sin código, la plata de las tiendas se calcula a ojo.

No es una clave ni un usuario. No da acceso a nada. Es público: puede ir en una tarjeta impresa sin problema.

## Actualización (10 oct): puedes usar el NOMBRE en vez de V01

Santiago prefirió códigos legibles. **Ya se puede.** En vez de `V01` puedes poner el **nombre del vendedor** en la columna `CODIGO` de la hoja `VENDEDORES`, con estas reglas:

- **MAYÚSCULAS, sin tildes ni espacios ni guiones**: `ANGELICA`, `MARIAJOSE`, `JUANP`. (El `?v=` de la web borra tildes, espacios y guiones, así que `V-Angelica` llegaría como `VANGELICA`; mejor escribirlo ya limpio.)
- **Dos personas con el mismo nombre**: `ANGELICA`, `ANGELICA2`.
- **El link, los conteos y la lista del tablero se ajustan solos** (son fórmulas sobre la columna `CODIGO`). Solo cambias esa celda.
- Los fijos especiales siguen igual: `SBG` (Santiago directo), `DIR` (sin vendedor), `N01`/`N02` (NZ).
- Tiendas: igual, el nombre de la tienda (`PAPELERIA`, `PANADERIA`) o deja `T01`. **Lo que lleva comisión del 10% es el `TIPO = TIENDA`**, no la letra del código, así que si usas nombres, pon el TIPO bien.

Lo de abajo (los `V01`…`T03`) queda como **ejemplo y respaldo**: si no quieres pensar en nombres, úsalos tal cual.

## Por qué son así y no de otra forma

Cuatro reglas de diseño, cada una por un motivo concreto:

- **3 caracteres: una letra de tipo + dos dígitos.** Corto para que entre en un link y en una tarjeta, pero suficiente para 99 personas por tipo. Más corto sería ambiguo; más largo lo copian mal.
- **La letra dice qué es:** `V` = vendedor persona, `T` = tienda, `N` = Nueva Zelanda. Mirás `T02` y sabés que lleva comisión del 10% sin consultar nada.
- **No llevan las iniciales del nombre.** Tentador, pero se rompe: dos Juan Pérez chocan, y si un vendedor se retira el código queda "manchado". Numerados secuenciales nunca chocan y se pueden reasignar.
- **Solo dígitos y mayúsculas, sin `O`, `I`, `0` ni `1` como letra.** `V01` tiene un cero porque va después de la `V` y nadie lo confunde con una letra.

## Los códigos, ya asignados

Están reservados. Vos solo escribís el nombre al lado cuando la persona confirme (eso es S4, martes 6).

### Vendedores persona (12 cupos — el plan pide 7 a 12)

| Código | Nombre | Link propio |
|---|---|---|
| `V01` | | `https://mega-rifa-fusa.vercel.app/?v=V01` |
| `V02` | | `https://mega-rifa-fusa.vercel.app/?v=V02` |
| `V03` | | `https://mega-rifa-fusa.vercel.app/?v=V03` |
| `V04` | | `https://mega-rifa-fusa.vercel.app/?v=V04` |
| `V05` | | `https://mega-rifa-fusa.vercel.app/?v=V05` |
| `V06` | | `https://mega-rifa-fusa.vercel.app/?v=V06` |
| `V07` | | `https://mega-rifa-fusa.vercel.app/?v=V07` |
| `V08` | | `https://mega-rifa-fusa.vercel.app/?v=V08` |
| `V09` | | `https://mega-rifa-fusa.vercel.app/?v=V09` |
| `V10` | | `https://mega-rifa-fusa.vercel.app/?v=V10` |
| `V11` | | `https://mega-rifa-fusa.vercel.app/?v=V11` |
| `V12` | | `https://mega-rifa-fusa.vercel.app/?v=V12` |

### Tiendas (3 cupos — el plan pide 1 a 3). Llevan 10% = COP 600 por número

| Código | Tienda | Link propio |
|---|---|---|
| `T01` | | `https://mega-rifa-fusa.vercel.app/?v=T01` |
| `T02` | | `https://mega-rifa-fusa.vercel.app/?v=T02` |
| `T03` | | `https://mega-rifa-fusa.vercel.app/?v=T03` |

### Nueva Zelanda

| Código | Quién | Link propio |
|---|---|---|
| `N01` | Sofía | `https://mega-rifa-fusa.vercel.app/?v=N01` |
| `N02` | (reserva, si Sofía recluta a alguien) | `https://mega-rifa-fusa.vercel.app/?v=N02` |

### Los dos especiales

| Código | Para qué |
|---|---|
| `SBG` | Vos. Todo lo que vendés directo. No lleva comisión |
| `DIR` | Llegó solo, por el Canal o por un Estado, sin link de nadie. Es el que mide cuánto vende la campaña por sí misma |

**Nunca se deja la columna `VENDEDOR` vacía.** Si no se sabe de dónde vino, se pone `DIR`. Una celda vacía es un dato perdido; `DIR` es un dato.

## El link de cada vendedor

La web ya está publicada en **mega-rifa-fusa.vercel.app**, así que el link de cada uno es la dirección de la web con `https://mega-rifa-fusa.vercel.app/?v=` y su código pegado al final:

```
https://mega-rifa-fusa.vercel.app/?v=V03
```

Qué pasa cuando alguien entra por ahí:

- La web se ve igual, pero arriba dice "te atiende V03".
- El código se guarda en el navegador de esa persona, así que si vuelve al otro día **sigue contando para V03**.
- Al tocar "Lo quiero" en el 450, se abre WhatsApp con el mensaje ya escrito: *"Hola, quiero el número 450 de la Mega Rifa Fusa. Vengo por V03."*
- Vos pegás ese `V03` en la columna `VENDEDOR` y listo.

Para que cada vendedor tenga su link a mano, en la hoja `VENDEDORES` la columna `E` lo arma sola:

```
="https://mega-rifa-fusa.vercel.app/?v=" & $A2
```

Cambiás la dirección una vez en esa fórmula y los 19 links quedan correctos.

## Lo que hay que decirle al vendedor (y lo que no)

**Sí:** "Este es tu código y este es tu link. Todo lo que entre por ahí queda a tu nombre."

**No** hace falta explicarle la fórmula ni el Sheet. Y ojo con una cosa, que es la que se desordena en la práctica: si un vendedor vende en persona, **igual tiene que decir su código** cuando reporta el número, porque ahí no hubo link. Esa es la única parte que depende de que la gente se acuerde, y por eso el código es de 3 caracteres.

---

*Los nombres se llenan en S4 (martes 6 de octubre), cuando estén los vendedores confirmados. Los códigos no cambian.*
