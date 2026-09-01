# El workflow de n8n, en git y verificable

## El problema que resuelve

El workflow vive en el servidor de n8n, no aquí. Se toca por la UI, y el export es un
JSON de 91k donde cada nodo de código está dentro de un string con `\n` escapados.

Consecuencia: **un cambio de tres líneas es invisible en `git diff`**. Por eso los
`BACKUP-*.json` de al lado son "antes de X" en vez de un histórico — solo servían para
restaurar entero, no para leer qué cambió.

Y sin diff legible no hay revisión. El 30-ago-2026, pegando a mano, el código de
`Formatear ofertas` acabó **también** dentro de `Code - Normalizar Modalidad`, que perdió
sus 100 líneas propias. Se cazó por casualidad. Eso es lo que este directorio evita.

## Qué hay aquí

```
workflow.json        estructura y conexiones. Los cuerpos largos son "@@FILE:nodes/…"
                     y los paths de webhook, "@@SECRET:<nodo>"
nodes/*.js           un fichero por nodo de código  -> git diff legible, node --check
nodes/*.body.txt     un fichero por cuerpo de petición (el prompt de Groq, por ejemplo)
secrets.local.json   los paths de webhook. NO ESTÁ EN GIT (.gitignore)
```

## Por qué los paths de webhook no se commitean

Desde el 30-ago-2026 el webhook de búsqueda se protege por un **path impredecible**:
el nombre viejo (`buscar-para-user`) estaba publicado en este repositorio y cualquiera
podía dispararlo — comprobado con `curl`, sin credenciales, HTTP 200.

Este repositorio es **público**. Si el path nuevo acabara en `workflow.json`, el primer
`git push` lo publicaría y la protección duraría lo que tarda un commit. Por eso
`wf-split` lo saca a `secrets.local.json`, que está en `.gitignore`, y `wf-check`
avisa si aparece un path sin redactar.

Si `secrets.local.json` se pierde, `wf-join` **para** y dice qué webhooks le faltan:
hay que recuperar esos paths de n8n. Es la contrapartida honesta de que el secreto
no viva en git.

## El ciclo

**Cuando el cambio sale de n8n** (alguien tocó la UI):

```bash
# 1. Exportar desde n8n:  menú "..." -> Download
node scripts/wf-check.mjs ~/Downloads/<export>.json     # ¿está sano?
node scripts/wf-split.mjs ~/Downloads/<export>.json workflows/PROD
git diff                                                # ahora SÍ se lee
git commit
```

**Cuando el cambio sale de aquí** (se edita el código en el editor):

```bash
node scripts/wf-join.mjs workflows/PROD workflows/PROD/_importar.json
node scripts/wf-check.mjs workflows/PROD/_importar.json  # verificar ANTES de importar
# importar en n8n DENTRO del workflow abierto: menú "..." -> Import from File
```

El viaje de ida y vuelta está comprobado: `split` + `join` devuelve un JSON **idéntico**
al original. Si algún día deja de serlo, es un bug del script, no del workflow.

## Importar sin romper nada

**Dentro del workflow abierto**, menú `...` -> *Import from File*. Desde la lista de
workflows crea uno NUEVO y sin credenciales.

## Las reglas de `wf-check.mjs`

Cada una existe porque algo se rompió de verdad. Ninguna depende de que nadie se acuerde.

| # | Regla | De dónde sale |
|---|-------|---------------|
| 1 | Dos nodos de código con roles distintos no pueden tener el mismo cuerpo | 30-ago: `Formatear ofertas` pisó a `Code - Normalizar Modalidad` |
| 2 | Todo nodo de código compila (`node --check`) | un error de sintaxis solo se ve al ejecutar |
| 3 | Todo `$('X')` apunta a un nodo que existe | renombrar un nodo deja colgadas las referencias |
| 4 | Groq: `max_tokens` ≤ 4096 y `reasoning_effort` si el modelo es `gpt-oss` | 30-ago: la cuenta tiene **8000 TPM** y `max_tokens` cuenta dentro; sin `reasoning_effort` el modelo razona y devuelve `content` vacío |
| 5 | Adzuna: sin `where=`, sin `app_key` en la URL, con `salary_min` | 30-ago: `where=Madrid` tiraba el 85% de España; la clave va por credencial de n8n |
| 6 | Lo que se calcula se devuelve, y lo que se devuelve se escribe | 30-ago: `ubic` se calculaba y se tiraba, y `Notion - Crear Oferta` ni tenía el campo |

Hermanos con el mismo cuerpo (`… Error` y `… Error1`, dos ramas que preparan el mismo
correo) salen como AVISO, no como fallo: eso es a propósito.

Cuando se arregle un bug nuevo, **la regla que lo habría cazado se añade aquí**. Es lo
que dice el proyecto en `POR_QUE_FALLA_LA_IA §3`: un control que depende de que alguien
se acuerde no es un control.

## Lo que este sistema NO hace

- No baja el workflow solo: el export es manual (haría falta la API key de n8n).
- No sabe qué hay **hoy** en producción. Solo lo que se exportó la última vez.
- No ejecuta los nodos. `node --check` dice que compilan, no que hagan lo correcto.
