# Tarea programada LinkedIn+Indeed: diagnóstico y prompt corregido (23 jul 2026)

> Continuación directa de `06-INTEGRACION-LINKEDIN-Y-AUDITORIA-MULTIUSUARIO-2026-07-21.md`.
> El doc 06 explica **cómo se montó** la tarea. Este explica **qué falla** y deja el
> prompt corregido listo para pegar.

---

## 1. Estado verificado (datos reales, no supuestos)

Consultada la DB Notion "Ofertas de Trabajo"
(`collection://33d11515-f4b2-8176-947b-000bbafd1ca7`) el 22-jul con las 25 entradas
más recientes:

| Comprobación | Resultado |
|---|---|
| Ofertas creadas por la tarea | 25 en 2 días (21 y 22 jul) |
| Origen de los links | **25 de 25 son `to.indeed.com`** |
| Ofertas de LinkedIn | **0. Ninguna.** |
| Campo `Descripción` | ✅ Relleno y detallado (el n8n lo dejaba a `null`) |
| Campo `Ubicación` | ✅ Relleno (el n8n lo dejaba a `null`) |
| Filtro de modalidad | ✅ Respetado (solo Remoto + Híbrido Madrid) |
| Duplicados | ❌ Confirmados |

### Lo que la tarea aporta de verdad

Rellena `Descripción` y `Ubicación`, que el workflow n8n dejaba vacíos. **Ese era un
bug real**: `cv-server` saca de `Descripción` las keywords de la oferta para adaptar el
CV; sin ese campo, el CV se adaptaba a ciegas. La tarea lo arregla de rebote.

---

## 2. Los tres problemas

### 2.1 El anti-duplicados está roto POR DISEÑO

El paso 3 del prompt original deduplica leyendo la columna **`Link oferta`**. Pero
Indeed genera un link distinto para la misma oferta en cada ejecución
(`to.indeed.com/aaXXXX` cambia). Para el prompt son ofertas diferentes.

**Duplicados confirmados** (misma Empresa + mismo Puesto, links distintos):

- `Senior Frontend Engineer - 100% Remote - EMEA` @ **Hostaway**: 2 veces el 22-jul
  (06:08 y 07:27 UTC), links `aaxy4j2k2jm7` y `aa4rcyq6xcvk`
- `AI-Native TypeScript Engineer` @ **MarsBased**: 21 y 22 jul
- También repetidos entre días: **Trivelta**, **Luxoft**, **Trimble**

**Causa raíz:** el link NO identifica la oferta. La clave correcta es **Empresa +
Puesto**, que es justo por lo que dedupea el workflow n8n.

**Agravante:** una tarea programada es un agente con un prompt, no un workflow
determinista. Cada ejecución empieza sin memoria de lo que escribió ayer. Si no se le
ordena consultar antes de escribir, vuelve a crear lo mismo.

### 2.2 La rama de LinkedIn no produce nada

Cero ofertas de LinkedIn en dos días, pese a todo el bloque de búsqueda por Composio +
verificación por Chrome. Causas posibles (sin determinar todavía):

- La extensión Claude in Chrome no está conectada
- No hay sesión de LinkedIn iniciada en ese Chrome
- `COMPOSIO_SEARCH_WEB` no devuelve URLs usables de `site:linkedin.com/jobs`
- La verificación descarta todas las candidatas por cerradas

El paso 5 del prompt original ya obliga a informarlo, pero el resumen solo sale **en el
chat** de la tarea. Si no se abre, no se ve. Por eso se añade el email de resumen.

### 2.3 Las alertas de empleo de LinkedIn no llegan al buzón conectado

Verificado en Gmail: **0 correos de LinkedIn en 30 días** en
`hello.cookyourweb@gmail.com`.

**Motivo:** la cuenta de LinkedIn está registrada con `verserper@gmail.com`. LinkedIn
manda las alertas a la dirección **principal** de la cuenta; añadir una segunda
dirección no las duplica.

**Solución propuesta (sin tocar LinkedIn):** filtro de reenvío automático en
`verserper@gmail.com` hacia `hello.cookyourweb@gmail.com` para todo lo que venga de
LinkedIn. Así entra en el buzón que n8n y los agentes sí leen.

**Expectativa realista:** las alertas de LinkedIn son un resumen algorítmico, no un
volcado. Serán siempre un goteo frente a las ~12 diarias de Indeed. **LinkedIn es un
complemento, no la fuente principal.**

---

## 3. Restricción de arquitectura: esta tarea NO se puede mover a la nube tal cual

Las rutinas de Claude Code (`/schedule`) corren en la nube de Anthropic: no dependen de
que el portátil esté encendido, a diferencia de las tareas programadas del Claude de
escritorio ("solo se ejecutan mientras tu ordenador está encendido y conectado").

**Pero** la verificación de ofertas de LinkedIn usa **Claude in Chrome con la sesión
logueada de Verónica**, y eso vive en la máquina local. En la nube no hay navegador ni
sesión.

Conectores MCP disponibles para rutinas en la nube (verificado): Notion, Indeed, Gmail,
Google Drive, Google Calendar, Composio. **No** hay claude-in-chrome.

**Consecuencia:** si se quiere pasar a la nube, hay que **partir la tarea en dos**:

- **Indeed, a la nube.** Conector oficial, corre 24/7 sin depender del portátil.
- **LinkedIn, en local.** Atado a Chrome y a la sesión iniciada.

Decisión aplazada hasta tener el dato del punto 2.2: si la rama de LinkedIn sigue
devolviendo cero, no merece la pena mantener la parte local.

---

## 4. Prompt corregido v2 (listo para copiar y pegar)

**Dónde:** Claude de escritorio o Cowork, barra lateral `Programado`, tarjeta
**"Busqueda empleos mejor pagados"**. Reemplazar las instrucciones enteras.

**Copia suelta:** `~/Downloads/prompt-tarea-empleos-linkedin-indeed-v2-2026-07-23.txt`

> ⚠️ **30-jul-2026: el fichero .txt ya NO es igual que el prompt de más abajo.** Es la
> versión buena y es la que hay que pegar. El de este documento se quedó en la v2.
>
> **Qué cambió y por qué.** El aviso `SIN VERIFICAR` se escribía solo dentro del campo
> `Notas`, que en la vista de tabla de Notion no se ve. Vero aprobó dos ofertas
> caducadas seguidas (Personio y Cactus) porque el sistema la avisó en un sitio donde
> no iba a mirar. Se añadió a la base de datos una casilla **`Verificada`**
> (checkbox, sin marcar por defecto) y el prompt ahora la rellena:
>
> - `Verificada = __YES__` solo si abrió el enlace y confirmó que la oferta sigue publicada
> - `Verificada = __NO__` en cualquier otro caso, incluido "no se pudo comprobar"
> - La casilla y el prefijo `SIN VERIFICAR:` de `Notas` tienen que decir siempre lo mismo
>
> Regla que se añadió al prompt: **nunca marcar la casilla por defecto ni porque la
> fuente parezca fiable.** Una casilla marcada sin comprobar es peor que una sin marcar,
> porque es justo la que Vero mira antes de aprobar.
>
> **Segundo cambio del 30-jul: filtro de antigüedad.** El prompt guardaba
> `Fecha Publicacion` pero no la usaba NUNCA para filtrar. Vero se encontró la búsqueda
> devolviendo una oferta **publicada hacía tres años** ("Fullstack Developer (mid &
> senior) - Hybrid Madrid", 0 solicitudes). Añadido al paso 2:
>
> - **Descartar** publicadas hace más de 30 días
> - **Descartar** zombis: más de 6 meses Y 0 solicitudes
> - **Marcar** `ANTIGUA: publicada hace N días` entre 15 y 30 días, que ahí sí hay duda
>
> **Tercer cambio: la regla de seniority era un buscar-palabra.** Decía "sin Senior,
> Staff, Lead, Principal o Architect no entra", así que un título como
> `Fullstack Developer (mid & senior)` la pasaba: contiene la palabra "senior". Ahora
> se lee el RANGO COMPLETO y solo entra si el SUELO del rango es senior o superior.
>
> **Cuarto cambio: el anti-duplicados no comparaba las candidatas entre sí.** La
> ejecución del 30-jul creó ~20 ofertas y seis venían por duplicado: Builder.io,
> Trivelta, CapsLock, Luxoft, Workato, Trimble e Iristrace.
>
> La regla del paso 3 comparaba cada candidata contra **lo que ya estaba en Notion**,
> nunca contra las otras candidatas de la misma tanda. Builder.io, Trivelta, CapsLock
> y Luxoft se crearon las dos copias en la misma ejecución: al consultar Notion no
> existía ninguna de las dos, así que pasaron las dos. La regla hizo exactamente lo
> que decía y aun así fallaron.
>
> Añadido al paso 3: agrupar las candidatas por Empresa + Puesto normalizados y crear
> una sola por grupo, y una verificación obligatoria de que la consulta a Notion se
> ejecutó de verdad antes de crear nada.
no >
> **SIN RESOLVER:** Workato, Trimble e Iristrace ya existían desde el 23-jul con
> Empresa y Puesto idénticos. Esas SÍ las tenía que haber cazado la regla vieja. O la
> consulta no llegó a ejecutarse, o volvió truncada. No se puede diagnosticar sin ver
> la ejecución.

Cambios respecto al original:

1. **Línea IMPORTANTE**: antes decía "NO envíes ningún email". Si se añade el email de
   resumen sin tocarla, se crea una contradicción interna (el mismo tipo de fallo que
   hacía que el prompt de `cv-server` inventara métricas: la regla 1 lo prohibía y la
   regla 4 lo pedía). Ahora distingue **postularse** (prohibido) de **informar** y
   **marcar estado** (permitidos).
2. **Paso 3**: dedup por **Empresa + Puesto** en vez de por link.
3. **Paso 5**: email de resumen con contadores y desglose por fuente.
4. Perfil de la primera línea actualizado al reposicionamiento de 22-jul
   (AI Engineer primero).

Añadido en v2 (23-jul, tarde):

5. **Paso 5, ofertas numeradas.** El listado del chat y el del email van numerados 1..N
   con la URL de la página de Notion. La numeración es lo que hace posible el paso 6.
6. **Paso 6 nuevo: aprobar o descartar desde el propio chat.** Verónica responde
   "aprueba 1 y 4" o "descarta 2, 3" y el agente escribe `Estado` en Notion. Incluye
   revisión bajo demanda ("revisar pendientes") sin lanzar búsqueda nueva.
7. **Paso 3, ofertas descartadas.** El dedup mira **todos** los estados: una oferta que
   ella descartó no se vuelve a crear al día siguiente. Descartarla ya fue una decisión.

### Por qué el paso 6 es opcional por diseño

Una tarea programada corre sola a las 9:10h. Si Verónica no abre el chat, nadie
responde y las ofertas se quedan en `Pendiente`, que es un estado correcto: nada se
pierde ni se bloquea. La aprobación es una conversación disponible, no un requisito de
la ejecución. El agente NO debe quedarse esperando ni reintentar.

Esto **no sustituye** al botón "Aprobar" del email de n8n (doc 06, sección 3): ese
resuelve el caso síncrono desde el móvil sin abrir Claude. Son dos vías al mismo campo.

### Schema real de `Estado` (verificado en Notion, 23-jul-2026)

Leído del select de la data source `collection://33d11515-f4b2-8176-947b-000bbafd1ca7`.
Nueve opciones, ni cuatro ni seis:

`Pendiente` · `Enviado` · `En proceso` · `Entrevista` · `Oferta recibida` ·
`Descartado` · `Rechazado` · `Aprobado` · `Enviado a empresa`

Esto cierra la **contradicción 2 de `docs/08`**: ninguno de los tres documentos que
declaraban los estados los tenía bien. Distinción que hay que respetar al escribir:
**`Descartado`** = la descarta Verónica. **`Rechazado`** = la rechaza la empresa.

```text
Eres el asistente de búsqueda de empleo de Verónica Serna Pérez (perfil Notion: "AI Engineer · Full-Stack Developer · Frontend Tech Lead", salario mínimo 60.000€, modalidad Remoto o Híbrido Madrid, ciudad Valdemorillo/Madrid). Su sistema real de búsqueda vive en n8n (Remotive+Adzuna+Tecnoempleo). Esta tarea es un complemento para LinkedIn e Indeed, integrado en la MISMA base de datos Notion.

IMPORTANTE: NO te postules a ninguna oferta ni escribas a ninguna empresa. Verónica gestiona los envíos ella misma. Tus únicas acciones permitidas son tres: crear páginas en Notion, actualizar el campo Estado de esas páginas cuando ella te lo pida explícitamente en el chat (paso 6), y enviarle a ella un email de resumen (paso 5).

Pasos:

1. BUSCAR (tres perfiles: "AI Engineer", "Frontend Tech Lead" / "Frontend Lead", y "Full Stack Developer" / "Full Stack Engineer"):
   a. Indeed (search_jobs / get_job_details si están disponibles): location="remote" y location="España", country_code="ES".
   b. LinkedIn vía Composio: llama a COMPOSIO_SEARCH_TOOLS con use_case "buscar ofertas LinkedIn AI Engineer / Frontend Lead / Full Stack España remoto o híbrido Madrid salario alto". Usa COMPOSIO_SEARCH_WEB con queries tipo "site:linkedin.com/jobs AI Engineer Spain remote OR hybrid Madrid salary", "site:linkedin.com/jobs Frontend Lead Spain remote OR hybrid Madrid salary" y "site:linkedin.com/jobs Full Stack Lead OR Senior Full Stack Spain remote OR hybrid Madrid salary" para descubrir URLs candidatas.

   VERIFICACIÓN DE ESTADO (obligatoria, LinkedIn únicamente): NO uses COMPOSIO_SEARCH_FETCH_URL_CONTENT para verificar si una oferta de LinkedIn sigue activa: choca con el muro de login y solo devuelve la pantalla "Aceptar y unirse a LinkedIn". En su lugar verifica cada candidata abriéndola con Claude en Chrome, usando la sesión de LinkedIn ya logueada de Verónica:
      - Carga las herramientas si están diferidas: ToolSearch "select:mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_context_mcp".
      - Para cada URL candidata: navega y lee el texto con get_page_text.
      - Descarta si dice "No longer accepting applications" / "Ya no se aceptan solicitudes" / "This job is no longer available", o si redirige a un aviso de oferta cerrada.
      - Si la extensión de Chrome no está conectada o no hay sesión de LinkedIn, NO descartes las ofertas: créalas igualmente y márcalas como SIN VERIFICAR. Empieza el campo `Notas` con "SIN VERIFICAR: no se pudo comprobar si la oferta sigue abierta." y dilo explícitamente en el paso 5. Una oferta caducada cuesta un clic; un día sin ofertas cuesta la búsqueda entera.

2. FILTRAR. Principio general: **descartar es una decisión que tomas por Verónica y no deja rastro; marcar se la deja a ella y le cuesta un vistazo.** Ante la duda, marca en vez de descartar.

   DESCARTA de verdad, sin marcar, solo esto:
   - Ofertas que hayas COMPROBADO que están cerradas.
   - Presencial, o híbrido de una ciudad que no sea Madrid, cuando el dato sea EXPLÍCITO.
   - Nivel junior o mid: sin Senior, Staff, Lead, Principal o Architect no entra.
   - Roles que no son los suyos: el frontend o la IA tienen que ser el TRABAJO, no un añadido. "Java y React" sobra; "React/TypeScript con algo de .NET" vale. Esto se decide leyendo la DESCRIPCIÓN, no el título.

   MARCA, y deja pasar:
   - No pudiste comprobar si sigue abierta: `SIN VERIFICAR:` al principio de Notas.
   - Salario por debajo del suelo: `BAJO SUELO: <la cifra>` al principio de Notas. Una oferta de 50k donde todo lo demás encaja puede valer más que una de 65k que no le gusta. Ella decide.

   SUELO SALARIAL, según el tipo de contrato:
   - Contrato: 60.000 € brutos anuales.
   - Freelance o por horas: 400 € al día, o 50 € la hora. Es la equivalencia aproximada de esos 60.000 por cuenta ajena, contando cuota de autónomos, vacaciones no pagadas y huecos entre proyectos. Verónica está de alta como autónoma: las ofertas freelance SÍ le interesan.
   - Si la tarifa viene en dólares, conviértela antes de comparar.
   - Sin salario indicado: no marques nada. Pasa por seniority.

   NUNCA ASUMAS LA MODALIDAD. Si la oferta no dice si es remota o híbrida, deja el campo `Modalidad` VACÍO y dilo en Notas. Rellenarlo a ojo es peor que dejarlo en blanco: la modalidad es un filtro duro, y una presencial colada como híbrida le cuesta un proceso entero, no un clic.

   REMOTO NO ES REMOTO DESDE CUALQUIER SITIO. Verónica trabaja desde Madrid. Si la oferta restringe el remoto a otra región, DESCÁRTALA aunque ponga "Remote": "remote role for candidates located in São Paulo", "US only", "remote LATAM", "must reside in Brazil", "remote (India)". Solo vale remoto desde España, Europa, EMEA o worldwide. Si no dice la región, no asumas: déjala pasar.

3. ANTI-DUPLICADOS: antes de crear nada, consulta la base de datos Notion "Ofertas de Trabajo" (data source collection://33d11515-f4b2-8176-947b-000bbafd1ca7) y trae las páginas de los últimos 30 días con sus campos Empresa, Puesto y Estado.

   Compara cada candidata por EMPRESA + PUESTO, normalizando mayúsculas y espacios sobrantes. Si ya existe, SÁLTALA y no la crees.

   La comparación incluye TODOS los estados, también las ofertas que Verónica ya descartó. Si una oferta está como "Descartado" o "Rechazado", NO la vuelvas a crear: descartarla ya fue una decisión suya.

   NO deduplices por "Link oferta": la misma oferta llega cada día con un link distinto (to.indeed.com/aaXXXX cambia), así que el link NO identifica la oferta.

4. CREAR EN NOTION (notion-create-pages) una página por cada oferta nueva en la data source collection://33d11515-f4b2-8176-947b-000bbafd1ca7 con estas propiedades exactas:
   - Empresa (title): nombre de la empresa
   - Puesto (text): el título EXACTO tal como aparece en LinkedIn/Indeed. NO lo reformules
   - Salario (text): si está disponible, si no dejar vacío
   - Modalidad (select): "Remoto" o "Hibrido" (sin tilde, únicas opciones válidas del schema). Si la oferta NO lo dice explícitamente, DÉJALO VACÍO. No lo deduzcas de que aparezca una ciudad
   - Tipo Contrato (text): "Indefinido", "Freelance", "Temporal"... lo que diga la oferta. Si no lo dice, vacío. Es lo que permite comparar un salario anual con una tarifa por hora
   - Link oferta (url): url original
   - Notas (text): 2-3 frases EN ESPAÑOL resumiendo qué busca la empresa en ESTA oferta (requisitos clave, stack, seniority). Lo usará cv-server para adaptar el CV: debe ser específico, no genérico
   - Descripción (text): descripción breve de la oferta (hasta 500 caracteres)
   - Ubicación (text): ciudad/país o "Remoto"
   - Estado (select): "Pendiente"
   - Idioma (select): "es" o "en" según el idioma de la oferta
   - Usuario (relation): ["https://app.notion.com/p/34b11515f4b2817980ecc0b6d2093abb"]
   - Fecha Publicacion (date): pasar expandida como "date:Fecha Publicacion:start": "YYYY-MM-DD"

   Guarda la URL de cada página creada: la necesitas en los pasos 5 y 6.

5. RESUMEN. En el chat: lista las ofertas nuevas NUMERADAS del 1 al N, agrupadas por perfil (AI Engineer / Frontend Lead / Full Stack). De cada una: número, empresa, puesto, salario, modalidad, link de la oferta y URL de la página de Notion.

   La numeración es lo que le permite aprobarlas o descartarlas en el paso 6. No la omitas nunca, aunque solo haya una oferta.

   Además, envía un email a hello.cookyourweb@gmail.com con asunto "Ofertas [FECHA]: N nuevas" y este contenido:
   - Ofertas encontradas / creadas / descartadas por duplicadas
   - Desglose por fuente: cuántas de Indeed y cuántas de LinkedIn
   - Si la rama de LinkedIn no devolvió nada, di POR QUÉ: sin acceso a Chrome, sin sesión iniciada, sin resultados de búsqueda, o todas descartadas por cerradas
   - Cuántas van marcadas como SIN VERIFICAR, y por qué no se pudieron comprobar
   - Cuántas van marcadas como BAJO SUELO
   - Listado numerado de las nuevas con los mismos números que usaste en el chat: empresa, puesto, salario, link
   - Una línea final: "Para aprobar o descartar, responde en el chat de la tarea con los números."

   Si no hubo ofertas nuevas, manda el email igualmente diciéndolo. El silencio no es información.

6. REVISIÓN: aprobar o descartar. Solo se ejecuta si Verónica responde en el chat. Si no responde, la tarea termina en el paso 5 y las ofertas se quedan en "Pendiente", que es un final correcto.

   Ella contestará refiriéndose a los números del paso 5. Ejemplos: "aprueba 1 y 4", "descarta 2, 3", "aprueba todas", "descarta el resto", "la 5 no".

   Reglas de escritura:
   - Aprobar el número N: actualiza esa página con notion-update-page, Estado = "Aprobado".
   - Descartar / denegar / rechazar el número N: Estado = "Descartado".
   - El campo Estado es un select y sus ÚNICAS opciones válidas son: "Pendiente", "Aprobado", "Descartado", "Rechazado", "En proceso", "Enviado", "Enviado a empresa", "Entrevista", "Oferta recibida". No inventes valores nuevos ni cambies mayúsculas o tildes.
   - En esta revisión usa SOLO "Aprobado" o "Descartado". "Descartado" es Verónica quien descarta la oferta; "Rechazado" es la empresa quien la rechaza a ella. No los confundas.
   - NO toques ningún otro campo de la página. Solo Estado.
   - Si un número no existe, la instrucción es ambigua o hay dos lecturas posibles, PREGUNTA antes de escribir. No adivines.
   - Después de cada tanda, confirma en una línea por oferta: número, empresa, puesto, estado nuevo. Si alguna actualización falló, dilo con el error. No des por buena una escritura que no confirmaste.

   Aprobar una oferta NO significa postularse. Aprobar solo marca el estado en Notion para que el resto del pipeline (generar CV y carta) la recoja. Sigue estando prohibido escribir a la empresa.

   REVISIÓN BAJO DEMANDA: si Verónica te escribe "revisar pendientes" sin pedir búsqueda nueva, no busques nada. Consulta la data source y trae las ofertas con Estado = "Pendiente" de los últimos 14 días, numeradas igual que en el paso 5 (empresa, puesto, salario, modalidad, link, URL de Notion), y aplica estas mismas reglas de aprobación.

Máximo 5 páginas nuevas creadas por perfil y por ejecución.
```

---

## 5. Principio que sale de aquí

Se repitió el mismo patrón en dos sistemas distintos el mismo día:

- En `cv-server`: el prompt prohibía inventar métricas Y pedía la fórmula XYZ ("medido
  por Y"). El modelo inventó "millions of users".
- En esta tarea: se pedía anti-spam, pero con una clave (`Link oferta`) que no
  identifica el objeto. Duplicó.

**Un prompt es una petición, no una garantía.** Y una regla contradictoria se resuelve
sola, a favor de la más concreta. Dos consecuencias prácticas:

1. Revisar los prompts buscando **reglas que se contradigan**, no solo reglas ausentes.
2. **Verificar la salida** contra la fuente en vez de confiar en la instrucción, y
   **emitir siempre un informe**, también cuando el resultado es cero. El silencio se
   interpreta como "poco", nunca como "nada", y así un canal muerto pasa semanas sin
   detectarse (justo lo que pasó con las alertas de LinkedIn).

---

## 6. Pendiente

- [ ] Pegar el prompt v2 en la tarea y ejecutarla a mano
- [ ] Probar el paso 6: responder "aprueba 1, descarta 2" y comprobar en Notion que el
      `Estado` queda en `Aprobado` / `Descartado` y que NINGÚN otro campo cambió
- [ ] Verificar en Notion que NO se recrean Hostaway / Trivelta / Luxoft / Trimble / MarsBased
- [ ] Alinear con el schema real de `Estado` (las nueve opciones de la sección 4) los tres
      documentos que lo declaran mal: `buscartrabajo/README.md:122`, `docs/01:145` y
      `cv-server/README.md:111-117`
- [ ] Leer el email de resumen para saber **por qué** LinkedIn devuelve cero
- [ ] Activar **"Mantener activo"** en la pantalla de tareas programadas (si no, el día
      que el portátil esté cerrado a las 9:00 no hay ofertas y no hay aviso)
- [ ] Filtro de reenvío `verserper@gmail.com` hacia `hello.cookyourweb@gmail.com` para
      correos de LinkedIn
- [ ] Decidir, con el dato del email en la mano, si se parte la tarea (Indeed a rutina
      en la nube, LinkedIn en local con Chrome) o si se abandona la rama de LinkedIn
- [ ] `docs/06-INTEGRACION-LINKEDIN-Y-AUDITORIA-MULTIUSUARIO-2026-07-21.md` sigue sin
      commitear en el repo

---

**Generado:** 23 julio 2026. Datos verificados contra Notion, Gmail y la API de rutinas.
**Actualizado:** 23 julio 2026 (tarde). Prompt v2 con aprobación desde el chat (paso 6) y
schema real del select `Estado` leído de Notion.
