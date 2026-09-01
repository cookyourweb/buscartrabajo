# Auditoría de contradicciones en la documentación (23 jul 2026)

> **Por qué existe este doc:** se evaluó instalar [Graphify](https://github.com/Graphify-Labs/graphify)
> (grafo de conocimiento sobre código y docs) para detectar contradicciones que hoy no se ven.
> Antes de instalarlo se probó la hipótesis a mano: leer los 2.400 renglones de documentación
> del sistema y cruzarlos entre sí y contra la realidad (código, Notion, n8n, Gmail).
>
> **Resultado: 11 contradicciones reales.** La hipótesis era correcta. La herramienta no hizo falta.

**Verificado contra:** código de `cv-server`, DB Notion de Ofertas, API de n8n, PROD (`/health`),
y la bandeja de `hello.cookyourweb@gmail.com`.

---

## Veredicto sobre Graphify

**No instalar, por ahora.**

| Criterio | Dato |
|---|---|
| Tamaño real del código | 3.000 renglones (cv-server) + 840 (buscartrabajo) |
| Documentación del sistema | 25 ficheros markdown, ~2.400 renglones |
| Benchmarks publicados por el propio proyecto | `recall@10 = 0.497`, `QA accuracy = 45.3%` |

Graphify resuelve la navegación de bases de código grandes. Esta no lo es: cabe entera en
contexto y hoy se leyó completa. Y con un 45,3 % de acierto declarado, ni un "sí hay
contradicción" ni un "no hay ninguna" serían fiables: sería un generador de pistas, no una
autoridad.

**Lo decisivo:** las dos contradicciones más graves de esta auditoría (5 y 9) no están entre
documentos. Están entre un documento y el mundo exterior (un correo de Arsys, la API de n8n).
Un grafo construido sobre `docs/` no las alcanza, porque la información que las revela no vive
en `docs/`.

Queda archivado como candidato de I+D, no como decisión de arquitectura.

---

## Las 11 contradicciones

Ordenadas por gravedad. Cada una indica dónde está el error y qué corregir.

### 1. Qué LLM genera los CVs (tres versiones)

| Fuente | Dice |
|---|---|
| `buscartrabajo/README.md:28` | "Capa LLM (fallback): Groq, luego Gemini, luego Claude 3 haiku" |
| `docs/01-DOCUMENTACION-MAESTRA:59-61` | Lo mismo: Groq primario |
| `docs/06-INTEGRACION-LINKEDIN:62` | "cv-server (CV + carta) ya usa Claude de pago" |
| **Realidad (PROD, 22 jul)** | **`modelo_usado: claude-haiku-4-5`. Claude es PRIMARIO.** |

El `README.md` está declarado como "fuente de verdad operativa" y es el que se equivoca.

**Causa:** hay dos capas LLM distintas y la documentación solo describe una.
`call_llm()` es Groq, luego Gemini, luego Claude (para tareas baratas). `call_llm_calidad()`
es Claude primario con Groq de reserva, y es la que genera CV y carta.

**Impacto real:** esta contradicción sostuvo durante semanas la creencia de que los CVs los
escribía Groq. Se descubrió el 22-jul al arreglar el campo `modelo_usado`, que devolvía una
constante en vez del modelo usado.

**Corregir en:** `buscartrabajo/README.md:28` y `docs/01:58-61`. Documentar las DOS capas.

### 2. Los estados del CRM (cuatro versiones incompatibles) — RESUELTA 23-jul (tarde)

| Fuente | Estados declarados |
|---|---|
| `buscartrabajo/README.md:122` | Pendiente / Aprobado / Descartado / En proceso / Enviado a empresa |
| `docs/01:145` | Pendiente / Aprobado / Descartado / En proceso / **Enviado** |
| `cv-server/README.md:111-117` | Pendiente / Aprobado / En proceso / Enviado a empresa / Descartado / **Rechazado** (seis) |
| **Notion real (60 filas leídas, 22 jul)** | **Solo aparecen: Pendiente, En proceso, Descartado** |

Ningún documento coincide con otro. Y ninguno parece coincidir con el select real.

**Impacto real:** bloquea el trabajo en curso. El 23-jul se iba a configurar un juego de vistas
filtradas por `Estado` y hubo que parar: una vista sobre "Enviado" saldría siempre vacía si esa
opción no existe en el select.

**Schema real, leído del select el 23-jul (data source
`collection://33d11515-f4b2-8176-947b-000bbafd1ca7`). Nueve opciones:**

`Pendiente` · `Enviado` · `En proceso` · `Entrevista` · `Oferta recibida` ·
`Descartado` · `Rechazado` · `Aprobado` · `Enviado a empresa`

Lección: la tabla de arriba mezclaba dos cosas distintas. Las **60 filas leídas** solo decían qué
estados están **en uso**, no cuáles **existen**. `Enviado`, `Entrevista`, `Oferta recibida`,
`Rechazado`, `Aprobado` y `Enviado a empresa` sí existen en el select: nadie los ha usado todavía.
Un valor sin usar no es un valor inexistente, y una vista sobre él sale vacía pero es válida.

**Pendiente:** alinear con estas nueve opciones `buscartrabajo/README.md:122`, `docs/01:145` y
`cv-server/README.md:111-117`. Y respetar la distinción: **`Descartado`** = la descarta Verónica,
**`Rechazado`** = la rechaza la empresa.

### 3. `docs/01` se contradice consigo mismo

- Cabecera (renglones 5-7): "Instancia n8n viva: `n8n-asistente-correo`. NO `n8n-st1v`".
- Renglones 114-115: `WEBHOOK_NUEVO_USUARIO` y `WEBHOOK_BUSCAR_AHORA` apuntan a `n8n-st1v`.
- Renglones 246, 251, 256: los tres ejemplos de `curl` usan `n8n-st1v`.

El aviso de deprecación se añadió arriba sin tocar el cuerpo. Alguien que copie un comando de
la sección de debugging llama a una instancia muerta.

**Corregir en:** `docs/01:114-115` y los tres bloques `curl`. O marcar el documento como
histórico y quitarle los comandos ejecutables.

### 4. El README apunta como "canónico" a un fichero borrado

- `buscartrabajo/README.md:173`: "Archivo canónico workflow: `workflows/WF2-integrado-v3.json`".
- `git status`: ese fichero aparece como **borrado** (`D`).
- `docs/referencia/WORKFLOWS-N8N.md:70`: los exports de `workflows/` **NO son la fuente de verdad**.
- `docs/referencia/WORKFLOWS-N8N.md:26`: ese workflow está **OFF** en n8n y "NO se usa".

Cuatro afirmaciones sobre el mismo fichero, incompatibles entre sí.

**Corregir en:** `buscartrabajo/README.md:173`. Quitar la línea o sustituirla por un puntero a
`docs/referencia/WORKFLOWS-N8N.md`.

### 5. El dominio del remitente de correo

| Fuente | Remitente |
|---|---|
| `cv-server/README.md:100` | `veronica@`**`use`**`cookyourwebai.es` |
| `docs/referencia/WORKFLOWS-N8N.md:25` | `veronica@cookyourwebai.es` |

Son dominios distintos. Uno de los dos está mal, y ninguno de los dos documentos lo sabe.

**Y hay algo peor.** Correo de Arsys recibido el 1 de julio de 2026 en
`hello.cookyourweb@gmail.com`, asunto *"Tu producto Registro .es usecookyourwebai.es se
eliminará en unos días"*: "el día 08/07/2026 se eliminarán los siguientes productos para los
que tienes su renovación desactivada".

Si ese dominio caducó, el sistema estaría enviando desde una dirección cuyo dominio ya no
existe, con el riesgo de que Brevo rechace los envíos o de que lleguen a spam.

**Acción (prioritaria):** verificar en Arsys si `usecookyourwebai.es` sigue vivo, y comprobar
en Brevo qué sender está validado. Después unificar el dato en los dos documentos.

**Nota de método:** esta contradicción no está entre documentos. Está entre un documento y un
correo. Solo aparece si se cruza la documentación con el mundo exterior.

### 6. La guía de usuario dice que las ofertas son inventadas

`cv-server/README.md:134` (sección FAQ, documento **de cara al usuario**):

> "¿Las ofertas son reales? De momento están generadas por IA basándose en perfiles reales de
> empresas. En la próxima fase se conectará a buscadores de empleo reales (LinkedIn Jobs,
> Getonboard, Remotive...)."

Contradice a `buscartrabajo/README.md:9` ("v3 = ofertas **reales** scrapeadas de 3 fuentes") y
a la realidad desde junio.

Ese fichero lleva sin actualizarse desde el 21 de abril de 2026 y sigue rotulado como
"Versión 2.0 Multi-User".

**Corregir en:** `cv-server/README.md`, FAQ y encabezado de versión.

### 7. `CLAUDE_MODEL` documentado con un modelo antiguo

- `docs/01:107`: `CLAUDE_MODEL` = `claude-3-haiku-20240307`.
- Código real (`cv_server_railway.py:52`): ese sigue siendo el **valor por defecto**, cierto,
  pero es solo el fallback de `call_llm()`. Los modelos que de verdad escriben CV y carta son
  `CV_MODEL = claude-haiku-4-5` (renglón 56) y `CARTA_MODEL = claude-sonnet-4-6` (renglón 58),
  y **ninguno de los dos aparece en la tabla de variables de entorno de `docs/01`**.

**Corregir en:** `docs/01:100-115`. Añadir `CV_MODEL`, `CARTA_MODEL` y `FOLDER_CV_GENERADOS`
(esta última creada el 22-jul y ausente también de `.env.example`).

### 8. Falta la propiedad `CV Master URL ES` en el schema documentado

Ni `buscartrabajo/README.md:95-110` ni `docs/01:119-133` la mencionan al describir la DB
Usuarios. Solo aparece `CV Master URL`.

Pero el `cv-server` elige el master **según el idioma de la oferta**: `CV Master URL` para
inglés y `CV Master URL ES` para español (`cv_server_railway.py`, función `elegir_master`).
Sin esa propiedad, los CVs en español salen del master inglés.

**Corregir en:** las dos tablas de schema de la DB Usuarios.

### 9. `WORKFLOWS-N8N.md` señala un workflow de producción que ya no lo es

- `docs/referencia/WORKFLOWS-N8N.md:25`: PROD = `5pTwriXcc6aYHO1Y`, estado ACTIVE.
- Verificado el 21-jul contra la API de n8n: el PROD activo pasó a ser
  **`OVoFiXTQwXmiyMfW`** ("BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)", 50 nodos).
  `5pTwriXcc6aYHO1Y` (47 nodos) quedó apagado.

El propio documento avisa: "Estado verificado vía n8n API el 20-jul-2026". El cambio ocurrió
el 21. El documento no miente, **caducó**.

**Corregir en:** `docs/referencia/WORKFLOWS-N8N.md:21-26`, reverificando contra la API antes de escribir.

### 10. Cuántas ofertas llegan al día

| Fuente | Cantidad |
|---|---|
| `cv-server/README.md:3, 61, 140` | 5 cada mañana |
| `buscartrabajo/README.md:46` | cap de **12** ofertas |
| `docs/01:28` | "1-5 ofertas" |

**Corregir en:** los tres, tras confirmar el cap real en el workflow PROD.

### 11. El perfil de usuario y el checklist bloqueante de `docs/05`

`docs/05:129` deja un checklist con un ítem marcado como **bloqueante** y sin cumplir:
"Perfil Notion de Vero actualizado a los 3 frentes".

Ese perfil se actualizó el 22-jul, pero a otro valor distinto del propuesto en el documento:
ahora es `AI Engineer · AI Software Engineer · Full-Stack Developer · Senior Frontend Engineer ·
Frontend Tech Lead`, no el `Frontend Tech Lead · Full-Stack Developer · UX Engineer · AI` que
proponía `docs/05:84`.

Además `docs/05:71` da como CV Master ES el fichero `1hYSwJHWRMU47jkud2bWh...` marcado "SIN
VERIFICAR". El master ES vigente desde el 22-jul es `1vGDwx0cUqR7sp8Oq7tIObOZNaiRI-PwVaYXoMCsnkRw`.

**Corregir en:** `docs/05`. Cerrar el checklist y marcar el documento como histórico.

---

## Patrón de fondo

Las 11 caen en tres categorías, y solo una es un error de escritura:

1. **Documentación que caducó** (1, 6, 9, 10, 11). Era cierta cuando se escribió. El sistema
   cambió y el documento no. Es el caso más frecuente y el más peligroso, porque el documento
   parece sano.
2. **Documentación parcheada por arriba** (3). Se añade un aviso de "esto ya no es así" en la
   cabecera sin tocar el cuerpo, y el cuerpo sigue siendo ejecutable.
3. **Dato que nunca se escribió** (7, 8). El campo o la variable existen en el código desde el
   principio, pero no llegaron a ninguna tabla.

**Consecuencia práctica:** la documentación indica dónde mirar, no qué es verdad hoy. Antes de
afirmar algo operativo (qué modelo, qué instancia, qué estados, qué workflow), hay que
verificarlo contra la fuente viva: el código, la API de n8n, Notion o `/health`.

Ese fue exactamente el método que produjo esta lista.

---

## Orden de corrección propuesto

1. **Verificar el dominio del remitente** (contradicción 5). Es la única con riesgo de romper
   envíos en producción.
2. ~~**Leer el schema real del select `Estado`** en Notion (contradicción 2). Bloquea la
   configuración de vistas que está en curso.~~ **HECHO 23-jul (tarde)**: nueve opciones,
   listadas en la contradicción 2. Queda alinear los tres documentos con ellas.
3. Corregir `buscartrabajo/README.md`: capa LLM, archivo canónico, schema con `CV Master URL ES`
   (contradicciones 1, 4, 8).
4. Actualizar `docs/referencia/WORKFLOWS-N8N.md` reverificando contra la API de n8n (contradicción 9).
5. Actualizar `cv-server/README.md`: FAQ de ofertas reales y versión (contradicción 6).
6. Marcar `docs/01` y `docs/05` como históricos, o quitarles los comandos ejecutables
   (contradicciones 3, 11).

---

**Generado:** 23 julio 2026. Método: lectura completa de la documentación del sistema y cruce
contra código, Notion, API de n8n, PROD y correo. Sin herramientas externas.
