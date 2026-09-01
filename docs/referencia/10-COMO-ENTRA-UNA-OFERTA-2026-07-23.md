# Cómo entra una oferta al sistema

> Escrito el 23 de julio de 2026. Todo lo que hay aquí está verificado contra el código,
> contra el schema real de Notion y contra PROD. Lo que no se pudo verificar está marcado
> como tal.

## La regla que manda sobre todas las demás

**El CV lo escribe el prompt. Nunca Claude a mano en el chat.**

El 23 de julio se generó el CV de Tenth Revolution corrigiendo a mano, en la conversación,
cada fallo que iba saliendo. Salió un buen CV y el sistema quedó igual de roto: el prompt
no aprendió nada, y la siguiente oferta habría vuelto a colar PHP y a meter verbos de
liderazgo.

Cuando el CV generado tiene un fallo, se arregla **el prompt del cv-server**, no el CV.
Corregir el resultado a mano esconde el problema y garantiza repetirlo.

El papel de Claude en una oferta de contacto directo es meterla en Notion. Nada más.

## Los tres caminos por los que entra una oferta

| | De dónde | Quién la trae | Escribe en |
|---|---|---|---|
| 1 | Tecnoempleo, Adzuna, Remotive, Indeed | n8n, workflows programados | Ofertas de Trabajo |
| 2 | LinkedIn | Tarea programada de Claude cowork | Ofertas de Trabajo |
| 3 | LinkedIn o correo, te escriben a ti | Verónica, contándoselo a Claude | Ofertas de Trabajo |

Los caminos 1 y 2 producen lo mismo: **una oferta detectada**, que puede no interesar. El
camino 3 no: cuando alguien te escribe, la decisión de que interesa ya está tomada.

> **Sin verificar:** los exports de `workflows/` no contienen ningún nodo de Indeed. Solo
> aparecen Tecnoempleo, Adzuna y Remotive en `OVoFiXTQwXmiyMfW`. Los exports son de julio y
> están incompletos, así que eso no prueba nada: el workflow de Indeed puede existir en n8n
> sin estar exportado. Para saberlo hay que mirar n8n, no el repo.

## El origen no es un estado

Cuando entra una oferta de contacto directo, la tentación es añadir un estado nuevo,
"Me han contactado", al principio del ciclo. **No sirve.**

`Estado` responde a *dónde está esto ahora*. El origen responde a *cómo llegó esto*. El
estado cambia constantemente; el origen no cambia nunca. Metiendo el origen dentro del
estado se pierde el dato en cuanto la candidatura avanza: al pasar a `Entrevista` ya nadie
sabe que vinieron a buscarte.

Y ese dato vale. "De todo lo que me llega, cuánto viene sin que yo lo busque" es la medida
de si el perfil de LinkedIn y el CV están funcionando. Si vive en `Estado`, la pregunta no
se puede contestar.

Si se quiere registrar, va en una propiedad propia. No en `Estado`.

## Una oferta de contacto directo entra por el final

El recorrido normal es: el bot busca, filtra, avisa por correo, esperas, apruebas, se
genera CV y carta.

Cuando te contactan a ti, los cuatro primeros pasos no existen. No hay nada que buscar ni
que decidir. Por eso no hace falta un estado *antes* de `Pendiente`: hace falta poder crear
la ficha **ya en `Aprobado`**, que es lo que dispara la generación de CV y carta.

## Las dos bases de Notion, y cuál sirve para qué

| | **Ofertas de Trabajo** | **Candidaturas · Control de CVs** |
|---|---|---|
| Data source | `collection://33d11515-f4b2-8176-947b-000bbafd1ca7` | `collection://39f11515-f4b2-8129-9dce-000b5fc8f5eb` |
| Quién escribe | n8n y la tarea de Claude | Solo Verónica |
| Estados | 9 | 5 |
| Tiene `Descripción` | Sí | **No** |
| Tiene `Idioma` | Sí | **No** |
| Tiene `Vía / Recruiter` | No | Sí |

**Las ofertas van siempre a `Ofertas de Trabajo`.** No es una preferencia: `Candidaturas`
no tiene `Descripción` ni `Idioma`, y sin esos dos campos no se puede generar un CV
adaptado, porque la descripción de la oferta es justo lo que el cv-server lee.

`Candidaturas` es una tabla resumen, no un expediente.

Los dos vocabularios de estado no coinciden (`Oferta recibida` frente a `Oferta`), y eso
sigue sin resolverse.

## Los nueve estados, y quién los pone

Leídos del select real el 23 de julio de 2026:

| Estado | Lo pone |
|---|---|
| Pendiente | El bot, al detectar la oferta |
| Aprobado | El botón del correo, o Claude en una oferta de contacto directo |
| Enviado | El flujo, al generar carta y CV |
| Enviado a empresa | El flujo, al mandarlo a la empresa |
| En proceso | Verónica |
| Entrevista | Verónica |
| Oferta recibida | Verónica |
| Descartado | Verónica, cuando ella descarta |
| Rechazado | La empresa, cuando rechaza |

La columna mezcla dos ciclos de vida en una sola propiedad: el del automatismo y el de la
candidatura real. Por eso ninguno de los estados encaja bien en una oferta que entra a mano.

## Dónde vive hoy una candidatura

Repartida en cuatro sitios, sin ningún enlace entre ellos:

| Qué | Dónde |
|---|---|
| La oferta y su estado | Notion, Ofertas de Trabajo |
| El CV adaptado | Google Drive, carpeta `FOLDER_CV_GENERADOS` |
| La preparación de la entrevista | `buscartrabajo/entrevistas/`, dentro de git |
| El seguimiento | En la cabeza de Verónica |

`entrevistas/osapiens-prep/` contiene un challenge de backend completo, con código, notas
de estudio y preguntas y respuestas. Es una candidatura viva guardada en un repositorio de
git y desconectada de Notion.

**Sin decidir:** dónde vive el seguimiento de una candidatura una vez que hay entrevista.

## Los dos repositorios

| | `buscartrabajo` | `cv-server` |
|---|---|---|
| Remoto | `github.com/cookyourweb/buscartrabajo` | `github.com/cookyourweb/cv-server` |
| Qué contiene | Documentación, exports de n8n, scripts | La aplicación, 1.695 líneas Flask |
| Código que corre | Ninguno | Sí, en Render |

Son dos repositorios independientes. La carpeta `proyectosActivosCookyourweb` que los
contiene **no está versionada por ninguno de los dos**. No existe un sitio común.

Consecuencia: quien clona `cv-server` no ve nada de `buscartrabajo`, y al revés. La
descripción del sistema tiene que vivir en un solo repositorio y el otro apuntar por URL,
nunca copiarla. Duplicar la verdad es lo que produjo las once contradicciones del
documento 08.

## Dónde vive de verdad el programa

En n8n, en la nube, **fuera de git**. No hay un fichero que se pueda abrir para leer lo que
hace el sistema cada mañana.

Esto explica por qué la documentación de este proyecto caduca sin parar: el sistema se
puede cambiar entero sin que quede rastro en ningún commit. Un export guardado en
`workflows/` es una foto del día que se exportó, no el sistema.

**Antes de afirmar algo operativo, hay que verificarlo contra la fuente viva.** El repo no
puede contradecir a Verónica sobre lo que hay en n8n.

## Trampas verificadas el 23 de julio de 2026

- **`cv-server/real_jobs.py` está apagado.** Son 465 líneas para buscar ofertas, pero solo
  implementa Remotive y no lo llama nadie: el workflow PROD busca por su cuenta. Quien lo
  abra creyendo que es el buscador del sistema, está leyendo código muerto. Lo mismo con el
  endpoint `/buscar-ofertas-reales` (`cv_server_railway.py:1627`).
- **`/health` miente sobre el LLM.** Devuelve `llm_provider: groq` y `version: v2.3-groq`.
  Los CVs los escribe `claude-haiku-4-5` (`CV_MODEL`, línea 56) y las cartas
  `claude-sonnet-4-6` (`CARTA_MODEL`, línea 58). Es el mismo patrón del bug de
  `modelo_usado` arreglado el 22 de julio: reportar una constante en vez de lo que pasa.
  Es la contradicción 12, y no está en la auditoría del documento 08.
- **`api.py` no está desplegado.** Es la migración a FastAPI, con tests en verde, pero el
  `Procfile` sigue arrancando Flask con gunicorn.
- **`.claude/INSTRUCCIONES-INICIO.md` está caducado** desde el 21 de abril. Manda leer un
  `CLAUDE.md` que no existe, llamar a la instancia n8n `n8n-qwmu` que está deprecada, y
  hacer `cd` a una ruta que ya no existe. De sus pasos marcados como obligatorios antes de
  tocar nada, la mitad fallan al ejecutarlos.
- **`POST /crear-oferta` devuelve 404.** `cv_server_railway.py:74` usa el id del data source
  donde la línea 627 necesita el id de la database. Para el camino 3 no hace falta
  arreglarlo: la ficha la crea Claude directamente contra Notion.

## Lo que queda sin decidir

- Dónde vive el seguimiento de una candidatura con entrevista y preparación.
- Si el origen (te buscaron o buscaste tú) se registra, y en qué propiedad.
- Si se alinean los dos vocabularios de estado de las dos bases, o se separan del todo.
- Si `buscartrabajo/README.md` se reescribe como puerta de entrada única del repositorio.

---

**Generado:** 23 de julio de 2026.
