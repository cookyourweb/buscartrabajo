# BuscarTrabajo · cómo se trabaja aquí

Las reglas del proyecto. Valen igual para una persona que llega al repositorio
y para un agente: **no dependen de qué herramienta las lea.** Los ficheros que
las cargan (`AGENTS.md`, `CLAUDE.md`) solo apuntan aquí, y son desechables.

Lo que esté aquí se cumple; lo que esté en `docs/` hay que ir a buscarlo, y por
eso se olvida.

**Este repositorio es PÚBLICO.** Antes de escribir cualquier cosa, asumir que la
va a leer alguien que no eres tú.

---

## 1. Qué es esto

Un sistema que capta ofertas de trabajo y las lleva hasta un CV enviado. Tres
piezas, y solo la primera vive aquí:

```
n8n (este repo)          capta la oferta, la filtra con un LLM, la escribe en Notion
cv-server (otro repo)    genera el CV y la carta, los sube a Drive
Notion                   es el estado: lo que hay pendiente, aprobado y enviado
```

El corazón es **un workflow de n8n de 50 nodos**, no una aplicación. Aquí no hay
`src/`, y `package.json` no tiene ni una dependencia. Es deliberado: lo que se
versiona es la automatización, más los scripts que la rodean.

- `workflows/PROD/` el workflow, partido en piezas que git puede diffear
- `scripts/` herramientas de Node (partir, unir, comprobar) y de Python (Notion, Drive)
- `tests/` `node --test`, sin framework
- `docs/` runbooks fechados y ADRs

---

## 2. Ninguna ruta de webhook entra en el repositorio

**Esta es la regla que más duele y la que más importa.**

El workflow expone cuatro webhooks. Tres ejecutan acciones con efectos externos
irreversibles y **no piden ninguna credencial**. Lo único que los separa de
cualquiera que sepa leer el repositorio es que su ruta sea impredecible. El
porqué, y por qué no se usa autenticación por cabecera, está en
[ADR-001](docs/adr/ADR-001-proteccion-de-los-webhooks.md).

Consecuencia práctica, y no admite excepción:

| Dónde | Qué se escribe |
|---|---|
| Campo `path` de un nodo webhook | `@@SECRET:<nombre del nodo>` |
| Dentro del código de un nodo (enlaces de correo) | `@@SECRET:<nombre del nodo>` |
| Documentación | el hueco `<RUTA>` |
| `workflows/PROD/secrets.local.json` | la ruta viva, y ese fichero no está en git |

**No escribas nunca una ruta a mano, ni siquiera una que creas muerta.** El
1-sep-2026 tres rutas ya rotadas sobrevivieron meses en el código de los nodos
que arman los correos. No filtraban nada, y por eso nadie las miraba. El daño
era el contrario: `wf-join` las devolvía a producción y los botones de aprobar y
descartar de los correos llevaban a un 404.

`scripts/check-secretos.mjs` lo comprueba en el hook de pre-commit y en CI. Una
prohibición escrita no es un control; un control es código que falla.

---

## 3. Los workflows: solo se versiona `PROD/`

n8n exporta un JSON de 46 KB en una sola línea, ilegible en un diff. Por eso
existe `wf-split`, que lo parte: cada nodo de código sale a su fichero, y las
rutas a `secrets.local.json`.

El ciclo, siempre en este orden:

```
n8n  →  exportar  →  npm run wf:split  →  editar el .js  →  npm run wf:join  →  importar
```

Se edita el fichero del nodo en el editor, **nunca en la interfaz de n8n**. Así
el cambio pasa por git antes que por producción.

`wf-join` para con error si encuentra una ruta escrita a mano (código 3) o un
marcador cuyo nombre no está en el fichero de secretos (código 4).

**Todo lo que hay bajo `workflows/` que no sea `PROD/` está ignorado.** El
1-sep-2026 se sacaron 47 exports del mismo workflow que ocupaban 38.000 líneas.
Git ya es la copia de seguridad: un fichero llamado `antes-fix-adzuna.json`
guarda en el nombre justo lo que va en un mensaje de commit. Para recuperar uno,
`git log --all -- 'workflows/BACKUP-*'`.

---

## 4. Antes de decir que está

```
npm test              22 tests, node --test, sin framework
npm run check:secretos ninguna ruta en el repositorio
npm run wf:check      avisos del workflow
npm run hooks         instala el pre-commit (una vez por clon)
```

El pre-commit corre las dos primeras y no deja commitear si fallan.

Node 20 o superior. CI fija Node 20; el desarrollo suele ir por Node 23, así que
el script de test usa `tests/*.test.mjs` y no `tests/`, que en Node 22 y
posteriores revienta con `MODULE_NOT_FOUND`.

Los tests nuevos van con la prueba primero. Rojo, verde, refactor, y ver el rojo
fallar por el motivo correcto.

---

## 5. Deuda conocida y declarada

**Las reglas de negocio del filtro viven dentro del prompt.** El suelo de 60.000
euros, la restricción de remoto a España, Europa o EMEA, y la prioridad de las
ofertas de IA están escritas en el texto de
`workflows/PROD/nodes/groq-generar-ofertas.body.txt`. No hay ningún test que las
cubra: se cambia una coma y nada se pone en rojo.

Está anotado aquí a propósito, porque es lo primero que pregunta quien abre ese
fichero. Lo que decide una regla no debería decidirlo un modelo: los filtros
duros son código. Cuando se toque, salen a un módulo con tests y el prompt se
queda con lo que solo un modelo puede hacer.

---

**Los tests cubren una pieza de diecinueve.** Las 22 pruebas y el badge verde son
todas de `scripts/lib/secretos.mjs`. Los cuatro `wf-*.mjs` no tienen pruebas
propias, y los 14 ficheros de Python (2.116 líneas, Notion y Drive) no tienen
ninguna ni las ejecuta CI, que corre solo sobre Node 20.

Se eligió cubrir secretos primero porque es la única pieza cuyo fallo es
irreversible: una ruta publicada ya no se despublica. El resto falla de forma
ruidosa y recuperable. Está escrito aquí y en el README para que un badge verde no
diga más de lo que cubre.

## 6. Lo que no se cambia sin un ADR

- Cómo se protegen los webhooks ([ADR-001](docs/adr/ADR-001-proteccion-de-los-webhooks.md))
- Qué framework usa el frontend cuando exista
- Que `secrets.local.json` no entre en git

ADR-001 **caduca cuando exista el frontend**: una aplicación en el navegador
enseña la ruta en la pestaña de red, y la ruta impredecible deja de proteger
nada. El frontend obliga a autenticación de verdad, con un backend que guarde el
secreto. El frontend y la seguridad de estos webhooks son la misma tarea, no dos.
