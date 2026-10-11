# Rutina diaria — durante la venta (10 oct – 5 dic 2026)

Hora Colombia (UTC−5). Nueva Zelanda va **+18 h**: las 12:00 de Colombia son las 6:00 del día siguiente en NZ.

**Las dos reglas que no se rompen**
1. **Un número queda PAGADO solo cuando la plata aparece en la app** (Nu para Santiago, el banco de Sofía para NZ). **Nunca con un pantallazo.**
2. **Solo la línea Business aparta números.** La personal invita y manda el link, nada más.

---

## Turnos

| Quién | Horario (CO) | Qué hace |
|---|---|---|
| **Santiago** | antes de las 12:00 | Verificación de pagos, apartados vencidos, imagen del tablero, mensajes de la noche |
| **Sofía** | 12:00 – 23:00 | Todos los chats de la Business, apartados, tarjetas-boleta, ventas en NZ, publicaciones en el Canal |
| **Santiago** | 12:30 · 6:00 p.m. · 10:00 p.m. | Ventanas de verificación de pagos |
| **Santiago** | 10:30 p.m. | Conciliación del día y copia de respaldo |

---

## Mañana — Santiago (antes de las 12:00)

1. **Abrir Nu y verificar los depósitos de la noche.** Por cada uno, cruzar **nombre, valor, hora y referencia** contra lo que dice el Sheet. Si cuadra → marcar **PAGADO**. Si no cuadra → etiqueta **Por verificar** y preguntar al comprador.
2. **Liberar los apartados de más de 24 horas.** Avisar al comprador con un mensaje amable antes de liberar ("tu apartado del 214 se vence hoy a las [hora]"). Liberado = vuelve a libre en el Sheet y en la web.
3. **Revisar los `VENTA · …` de los vendedores** (ruta 2, efectivo) que llegaron en la noche: apartar a nombre del vendedor y arrancar el reloj de **48 h** para que entregue la plata.
4. **Publicar la imagen del tablero** en el Canal y en los Estados, con el contador real ("quedan X de 1.000").
5. **Responder los mensajes que entraron después de las 23:00.**
6. **Pasar la reserva del premio**: mientras no se completen los primeros **COP 2.000.000**, todo lo que entre va a la cajita aparte. Esa plata no se toca.

## Tarde y noche — Sofía (12:00 – 23:00)

1. **Chats de la Business**: responder con las respuestas rápidas (`/precio` `/pago` `/reglas` `/tablero` `/nz`) y usar las etiquetas **Apartado / Por verificar / Pagado**.
2. **Apartar números**: confirmar en el Sheet que esté libre, apartarlo, poner la hora y avisar que el apartado dura **24 horas**.
3. **Mandar la tarjeta-boleta** solo cuando el número ya está **PAGADO**, con la frase chistosa que toque (nunca repetir la misma dos veces seguidas).
4. **Ventas en NZ**: cobrar en su cuenta, **verificar los NZD en su propia app**, anotar en la hoja NZ con **el número de la boleta como referencia del pago**, y mandar la tarjeta bilingüe.
5. **Publicar en el Canal**: prueba social, encuestas, micro-historias de los números, cuenta regresiva.
6. **Dejar en la libreta de NZ** lo recaudado del día, en NZD.

## Ventanas de verificación — Santiago (12:30 · 6:00 p.m. · 10:00 p.m.)

Las mismas tres revisiones cada vez, de 5 a 10 minutos:
- Depósitos nuevos en Nu → marcar PAGADO.
- Apartados que se vencen en la próxima hora → avisar.
- Efectivo recibido en persona → anotarlo en la libreta **el mismo día**, nunca después.

## Conciliación — 10:30 p.m. (Santiago)

Cuatro cosas tienen que cuadrar:

| Fuente | Qué se compara |
|---|---|
| **Google Sheet** | Números marcados PAGADO × COP 6.000 (Colombia) |
| **App de Nu** | Depósitos del día |
| **Libreta de efectivo** | Lo recibido en mano |
| **Libreta de NZ** | Números de NZ × NZD 4 |

Si no cuadra: **no se cierra el día hasta encontrar la diferencia.** Lo más común es un pantallazo que se tomó por pago, o un número apartado dos veces.

Después: **copia de respaldo del Sheet en `09_Operacion/`**, con el nombre `tablero-AAAA-MM-DD.csv`.

---

## Cada domingo

| Quién | Qué |
|---|---|
| Santiago | **Resumen semanal a cada vendedor**: cuántos números vendió, a cuántas personas distintas (va para el umbral de 25) y cuánta plata tiene pendiente de entregar |
| Santiago + Claude | **Revisión del punto de control** contra la meta → ¿se activa un refuerzo? (ver `puntos-de-control.md`) |
| Santiago | Refrescar el contenido de la semana |

---

## Cosas que nunca se hacen

- Aceptar un pantallazo como prueba de pago.
- Apartar un número desde la línea personal.
- Dar un número fiado.
- Vender a un menor de 18 años.
- Publicar el nombre completo o el teléfono de un comprador (en el tablero va `Dav*** G.`, o `Reservado` si no quiso salir).
- Publicar una foto con cara sin permiso.
- Decir que la rifa tiene permiso o autorización.
- Poner un contador que no sea real ("quedan 50" cuando quedan 300).
- Decir "el 777 ya se fue" si no se fue.
- Tocar la reserva del premio.
- Publicar cuánta plata hay en mano.

---

## Si algo se rompe

| Problema | Qué hacer |
|---|---|
| Un número aparece vendido dos veces | Manda el Sheet. El primero en quedar registrado se queda con el número; al segundo se le ofrece otro número **o la devolución completa**, a su elección, de inmediato |
| Un pago no aparece en Nu | Queda **Por verificar**, no PAGADO. El apartado sigue corriendo. Pedir al comprador la referencia y la hora exacta |
| Un vendedor no entrega la plata en 48 h | Los números se liberan y se le avisa. Sin excepciones, porque es la regla que protege a los compradores |
| Se bloquea una línea de WhatsApp | Pasar lo masivo al Canal, seguir 1 a 1 desde la otra línea, y avisar por Estados e Instagram |
| Borran una publicación en un grupo de Facebook | No reinsistir en ese grupo. Escribirle al admin |
| Santiago no puede cubrir la mañana | Sofía **no verifica pagos de Colombia**. Los depósitos quedan **Por verificar** hasta que Santiago abra Nu |

---

*Última actualización: 2026-10-02 (Sesión 1). Fuente: `02_Decisiones/plan-maestro.md`.*
