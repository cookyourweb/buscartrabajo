# Runbook. Cerrar la rotación de los webhooks

**Fecha:** 1 sep 2026 · **Issue:** #1 · **Relacionado:** [ADR-001](../adr/ADR-001-proteccion-de-los-webhooks.md)

Este documento cierra lo que ADR-001 dejó a medias. No decide nada nuevo: aplica
la decisión que ya está tomada.

---

## Qué pasaba, en una frase

Las rutas de los cuatro webhooks se rotaron y salieron del repositorio, pero
**los tres ficheros que arman los enlaces de los correos seguían con la ruta
vieja escrita a mano**, y `wf-join` los mete tal cual en el workflow que se
importa a n8n. El siguiente import habría devuelto a producción unos enlaces que
apuntan a rutas muertas.

ADR-001 avisó de la mitad del problema:

> Dos nodos de producción todavía construyen la URL con la ruta escrita a mano.
> Al rotar hay que sustituirla por una expresión, o la ruta nueva vuelve al repo
> en el siguiente `wf-split`.

La otra mitad, que no estaba anotada, es peor: **la ruta vieja vuelve a
producción**, y los correos de aprobar, descartar y enviar a empresa dejan de
funcionar. Nada avisaba, porque `check-secretos` solo buscaba las rutas VIVAS y
una ruta muerta no filtra nada.

---

## Lo que ya está arreglado en el repositorio

| Qué | Dónde |
|---|---|
| Los tres enlaces de correo usan `@@SECRET:<nodo>` en vez de la ruta | `workflows/PROD/nodes/code-preparar-email-notificacion.js`, `code-preparar-email-carta-cv.js` |
| `wf-join` resuelve los marcadores **dentro** del código de los nodos, no solo en `path` | `scripts/wf-join.mjs` |
| `wf-join` para con error si encuentra una ruta muerta o un marcador huérfano | `scripts/wf-join.mjs` |
| Comprobación 3: prohibida **cualquier** ruta literal, viva o muerta | `scripts/check-secretos.mjs` |
| Los dos documentos vivos usan el hueco `<RUTA>` | `docs/01-...`, `docs/19-...` |
| `npm test` vuelve a correr en Node 23 | `package.json` |

Los archivos congelados (`.archivo-historico-*`, `_archivo-exports-*`) quedan
fuera de la comprobación 3 a propósito: son un registro de lo que hubo y nadie
los importa a n8n. Sus rutas vivas las siguen mirando las comprobaciones 1 y 2.

Verificado de punta a punta: `wf-join` reconstruye los 50 nodos con **0
marcadores sin resolver, 0 rutas viejas**, y los tres enlaces de correo apuntando
a la ruta viva de su webhook.

---

## Lo que tienes que hacer tú, en este orden

### 1. Confirmar que n8n tiene las rutas nuevas

`workflows/PROD/secrets.local.json` tiene rutas de 25, 32, 39 y 34 caracteres, y
ninguna coincide con las publicadas. Todo apunta a que la rotación se hizo el
30 y 31 de agosto. **Confírmalo antes de seguir**: abre los cuatro nodos webhook
en n8n y compara su campo `path` con el fichero.

- Si coinciden: la rotación está hecha, sigue en el paso 2.
- Si no coinciden: las rutas del fichero son las nuevas y **no se han aplicado**.
  Aplícalas en n8n primero, y vuelve aquí.

### 2. Reimportar el workflow

```
npm run wf:join
```

Genera `workflows/PROD/_importar.json`, que está en `.gitignore`. Impórtalo en
n8n. Sin este paso, los correos que salgan siguen llevando la ruta vieja.

Si algo está mal, el comando para y lo dice: sale con código 3 si encuentra una
ruta muerta escrita a mano, y con 4 si hay un marcador cuyo nombre no está en el
fichero de secretos.

### 3. Actualizar los botones de Notion

Los tres webhooks que se invocan desde un botón de Notion abren una URL fija. Al
rotar, esa URL cambió. Revisa los botones de la base de ofertas y pon la ruta que
esté en `secrets.local.json`.

### 4. Avisar de los correos que ya salieron

**Este es el efecto que hay que tener en cuenta.** Los correos enviados antes de
la rotación llevan enlaces de aprobar y descartar que ya no responden. No hay
forma de arreglarlos: el enlace vive en un correo que ya está en una bandeja.

Las ofertas que estén esperando aprobación de uno de esos correos **se aprueban o
descartan desde Notion**, no desde el correo. Los correos nuevos, una vez hecho
el paso 2, funcionan.

### 5. Mergear la rama

`seguridad/webhooks-sin-auth` lleva fuera de `main` desde el 31 de agosto.
Cuando los pasos anteriores estén hechos, mergea.

Ojo con el tamaño: son 121 ficheros y unas 67.500 líneas, y casi todo son copias
de seguridad de workflows del verano que entraron en el mismo saco que el arreglo
de seguridad. Si el repositorio va a enseñarse, merece la pena separar las copias
en su propio commit antes de mergear.

---

## Cómo se rota la próxima vez

El orden de ADR-001 sigue siendo el bueno: **rotar, limpiar, publicar.**

1. Genera rutas nuevas, largas e impredecibles, y cámbialas en los cuatro nodos
   de n8n.
2. Exporta el workflow y pásalo por `npm run wf:split`. Las rutas salen solas a
   `secrets.local.json` y el código de los nodos queda con marcadores.
3. `npm run check:secretos`. Tiene que dar verde.
4. Actualiza los botones de Notion.
5. `npm run wf:join` y reimporta, para que los correos nuevos lleven la ruta viva.

Nunca escribas una ruta a mano en un fichero del repositorio. Ni siquiera una que
creas muerta: la comprobación 3 la rechaza, y tiene razón.

---

## Cuándo sobra todo esto

Cuando exista el frontend en Angular, según ADR-001. Una aplicación en el
navegador enseña la ruta en la pestaña de red, y la ruta impredecible deja de
proteger nada. En ese momento hace falta autenticación de verdad: un backend que
guarde el secreto y hable con n8n, o tokens por petición.

Es decir: **el frontend y la seguridad de estos webhooks son la misma tarea, no
dos.** Empezar el Angular sin resolver la autenticación empeora esto, no lo
arregla.
