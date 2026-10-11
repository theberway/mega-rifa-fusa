# Prompt para Claude en Chrome — montar el Sheet de la Mega Rifa Fusa

Este archivo es para **pegarle el texto de abajo a Claude cuando controla tu pantalla / Chrome**.
Tú solo le subes el archivo `MEGA-RIFA-FUSA-tablero.xlsx` (está en esta misma carpeta) y él hace
todo lo que yo no puedo hacer: entrar a tu cuenta de Google y configurar el Sheet.

**Antes de empezar, ten a la mano:**
1. El archivo `MEGA-RIFA-FUSA-tablero.xlsx`.
2. El archivo `script-tablero.gs` (esta misma carpeta): es el texto que se pega en Apps Script.
3. Estar con **una sola cuenta de Google** abierta en Chrome (la dueña del Sheet). Si tienes varias,
   abre una ventana de incógnito con esa sola cuenta — así Apps Script no arranca con la cuenta equivocada.

**Cuando termine, Claude te tiene que devolver UNA cosa: el link del CSV publicado de la hoja `NUMEROS`.**
Ese link me lo pasas a mí y yo conecto la web.

---

## COPIA DESDE AQUÍ 👇

Vas a configurar un Google Sheet para una rifa. Yo te subo un archivo de Excel; tú lo conviertes en
Sheet y lo dejas listo. Hazlo paso por paso y, al final, dame el link del CSV. **No hagas nada que
no esté en esta lista.** Si algo te pide permisos o no abre, dímelo y espera, no improvises.

1. **Sube el archivo** `MEGA-RIFA-FUSA-tablero.xlsx` a Google Drive (drive.google.com → Nuevo →
   Subir archivo). Cuando esté subido, ábrelo.

2. **Conviértelo en Sheet de verdad**: con el archivo abierto, menú **Archivo → Guardar como Hoja
   de cálculo de Google**. Se abre una versión nueva que ya es un Sheet (no un Excel). Trabaja sobre esa.

3. **Ajustes de cálculo** (sin esto los apartados no vencen solos): **Archivo → Configuración**:
   - pestaña **Cálculo → Recalcular: "Al cambiar y cada minuto"**.
   - **Zona horaria: (GMT-05:00) Bogotá**.
   - Guardar.

4. **Instala el script de la hora**: menú **Extensiones → Apps Script**. Si no abre y dice algo como
   "No se pudo abrir el archivo", es que hay varias cuentas de Google abiertas: entra a
   script.google.com con la cuenta dueña del Sheet, o abre el Sheet en una ventana de incógnito con
   esa sola cuenta, y vuelve a intentar.
   - Dentro de Apps Script, **borra lo que haya** y **pega todo el contenido del archivo
     `script-tablero.gs`** (te lo paso aparte).
   - **Guarda** (el disquete).
   - Arriba, escoge la función **`repararTodo`** y dale **Ejecutar**. La primera vez pide permiso:
     acepta (es tu propia cuenta escribiendo en tu propia hoja). Deja que termine.

5. **Comparte en Restringido** (que nadie entre por link): botón **Compartir** (arriba a la derecha)
   → **Acceso general → Restringido**. Que diga "Solo las personas con acceso pueden abrir".

6. **Publica solo la hoja NUMEROS como CSV**: menú **Archivo → Compartir → Publicar en la web**.
   - En el primer desplegable, escoge la pestaña **`NUMEROS`** (NO "Todo el documento").
   - En el segundo, escoge **`.csv`** (valores separados por comas).
   - Dale **Publicar** y confirma.
   - Copia el link que aparece. Se ve así:
     `https://docs.google.com/spreadsheets/d/e/2PACX-....../pub?gid=0&single=true&output=csv`

7. **Dame ese link del CSV.** Es lo único que necesito.

**Reglas que NO puedes romper:**
- **No compartas el archivo con ninguna persona ni correo.** Solo se publica la hoja NUMEROS como CSV.
- **No publiques ninguna otra hoja** (COMPRADORES, PAGOS, VENDEDORES tienen nombres y teléfonos).
- **No borres ni cambies datos** de las hojas. Solo configuras y publicas.
- Si un paso falla, **para y dime qué pasó**. No busques caminos alternos.

## COPIA HASTA AQUÍ 👆

---

## Checklist para ti, Santiago (que Claude lo haya hecho bien)
Cuando Claude diga que terminó, confirma que:
- [ ] El archivo quedó como **Hoja de cálculo de Google** (arriba dice el nombre sin "(.xlsx)").
- [ ] En **Archivo → Configuración → Cálculo** dice **"Al cambiar y cada minuto"** y zona **Bogotá**.
- [ ] En **Extensiones → Apps Script** está el script pegado y `repararTodo` corrió sin error.
- [ ] En **Compartir** dice **Acceso general: Restringido**.
- [ ] El link que te dio **termina en `output=csv`** y, al abrirlo, **se descarga/muestra un CSV** con
      filas tipo `000,LIBRE,...`.

Pásame ese link a **mí** (a Claude Code) y yo conecto la web y la redesplego.

> **Ojo con el link**: ese CSV es de la hoja NUMEROS, que es pública a propósito (solo lleva el
> número, el estado y el nombre acortado). Las demás hojas nunca se publican.
