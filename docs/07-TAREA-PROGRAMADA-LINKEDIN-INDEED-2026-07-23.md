# Tarea programada LinkedIn+Indeed — diagnóstico y prompt corregido — 23 jul 2026

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

- `Senior Frontend Engineer - 100% Remote - EMEA` @ **Hostaway** — 2 veces el 22-jul
  (06:08 y 07:27 UTC), links `aaxy4j2k2jm7` y `aa4rcyq6xcvk`
- `AI-Native TypeScript Engineer` @ **MarsBased** — 21 y 22 jul
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
`verserper@gmail.com` → `hello.cookyourweb@gmail.com` para todo lo que venga de
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

- **Indeed → nube.** Conector oficial, corre 24/7 sin depender del portátil.
- **LinkedIn → local.** Atado a Chrome y a la sesión iniciada.

Decisión aplazada hasta tener el dato del punto 2.2: si la rama de LinkedIn sigue
devolviendo cero, no merece la pena mantener la parte local.

---

## 4. Prompt corregido (listo para copiar y pegar)

**Dónde:** Claude de escritorio → barra lateral `Programado` → tarjeta
**"Busqueda empleos mejor pagados"** → reemplazar las instrucciones enteras.

Cambios respecto al original:

1. **Línea IMPORTANTE**: antes decía "NO envíes ningún email". Si se añade el email de
   resumen sin tocarla, se crea una contradicción interna (el mismo tipo de fallo que
   hacía que el prompt de `cv-server` inventara métricas: la regla 1 lo prohibía y la
   regla 4 lo pedía). Ahora distingue **postularse** (prohibido) de **informar**
   (obligatorio).
2. **Paso 3**: dedup por **Empresa + Puesto** en vez de por link.
3. **Paso 5**: email de resumen con contadores y desglose por fuente.
4. Perfil de la primera línea actualizado al reposicionamiento de 22-jul
   (AI Engineer primero).

```text
Eres el asistente de búsqueda de empleo de Verónica Serna Pérez (perfil Notion: "AI Engineer · Full-Stack Developer · Frontend Tech Lead", salario mínimo 60.000€, modalidad Remoto o Híbrido Madrid, ciudad Valdemorillo/Madrid). Su sistema real de búsqueda vive en n8n (Remotive+Adzuna+Tecnoempleo) — esta tarea es un complemento para LinkedIn e Indeed, integrado en la MISMA base de datos Notion.

IMPORTANTE: NO te postules a ninguna oferta ni escribas a ninguna empresa. Verónica gestiona los envíos ella misma. Tus únicas acciones permitidas son: crear páginas en Notion y enviarle a ella un email de resumen (paso 5).

Pasos:

1. BUSCAR (tres perfiles: "AI Engineer", "Frontend Tech Lead" / "Frontend Lead", y "Full Stack Developer" / "Full Stack Engineer"):
   a. Indeed (search_jobs / get_job_details si están disponibles): location="remote" y location="España", country_code="ES".
   b. LinkedIn vía Composio: llama a COMPOSIO_SEARCH_TOOLS con use_case "buscar ofertas LinkedIn AI Engineer / Frontend Lead / Full Stack España remoto o híbrido Madrid salario alto". Usa COMPOSIO_SEARCH_WEB con queries tipo "site:linkedin.com/jobs AI Engineer Spain remote OR hybrid Madrid salary", "site:linkedin.com/jobs Frontend Lead Spain remote OR hybrid Madrid salary" y "site:linkedin.com/jobs Full Stack Lead OR Senior Full Stack Spain remote OR hybrid Madrid salary" para descubrir URLs candidatas.

   VERIFICACIÓN DE ESTADO (obligatoria, LinkedIn únicamente): NO uses COMPOSIO_SEARCH_FETCH_URL_CONTENT para verificar si una oferta de LinkedIn sigue activa — choca con el muro de login y solo devuelve la pantalla "Aceptar y unirse a LinkedIn". En su lugar verifica cada candidata abriéndola con Claude en Chrome, usando la sesión de LinkedIn ya logueada de Verónica:
      - Carga las herramientas si están diferidas: ToolSearch "select:mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_context_mcp".
      - Para cada URL candidata: navega y lee el texto con get_page_text.
      - Descarta si dice "No longer accepting applications" / "Ya no se aceptan solicitudes" / "This job is no longer available", o si redirige a un aviso de oferta cerrada.
      - Si la extensión de Chrome no está conectada o no hay sesión de LinkedIn, NO des por buena ninguna oferta: sáltala y dilo explícitamente en el paso 5.

2. FILTRAR: solo ofertas ABIERTAS, remoto o híbrido Madrid (nunca presencial, nunca híbrido de otra ciudad), con salario ≥60.000€ si el dato está disponible, o nivel Senior/Staff/Lead/Principal si no hay salario explícito.

3. ANTI-DUPLICADOS: antes de crear nada, consulta la base de datos Notion "Ofertas de Trabajo" (data source collection://33d11515-f4b2-8176-947b-000bbafd1ca7) y trae las páginas de los últimos 30 días con sus campos Empresa y Puesto.

   Compara cada candidata por EMPRESA + PUESTO, normalizando mayúsculas y espacios sobrantes. Si ya existe, SÁLTALA y no la crees.

   NO deduplices por "Link oferta": la misma oferta llega cada día con un link distinto (to.indeed.com/aaXXXX cambia), así que el link NO identifica la oferta.

4. CREAR EN NOTION (notion-create-pages) una página por cada oferta nueva en la data source collection://33d11515-f4b2-8176-947b-000bbafd1ca7 con estas propiedades exactas:
   - Empresa (title): nombre de la empresa
   - Puesto (text): el título EXACTO tal como aparece en LinkedIn/Indeed — NO lo reformules
   - Salario (text): si está disponible, si no dejar vacío
   - Modalidad (select): "Remoto" o "Hibrido" (sin tilde, únicas opciones válidas del schema)
   - Link oferta (url): url original
   - Notas (text): 2-3 frases EN ESPAÑOL resumiendo qué busca la empresa en ESTA oferta (requisitos clave, stack, seniority). Lo usará cv-server para adaptar el CV: debe ser específico, no genérico
   - Descripción (text): descripción breve de la oferta (hasta 500 caracteres)
   - Ubicación (text): ciudad/país o "Remoto"
   - Estado (select): "Pendiente"
   - Idioma (select): "es" o "en" según el idioma de la oferta
   - Usuario (relation): ["https://app.notion.com/p/34b11515f4b2817980ecc0b6d2093abb"]
   - Fecha Publicacion (date): pasar expandida como "date:Fecha Publicacion:start": "YYYY-MM-DD"

5. RESUMEN. En el chat: cuántas ofertas nuevas creaste, con título+empresa+salario+link agrupadas por perfil (AI Engineer / Frontend Lead / Full Stack).

   Además, envía un email a hello.cookyourweb@gmail.com con asunto "Ofertas [FECHA] — N nuevas" y este contenido:
   - Ofertas encontradas / creadas / descartadas por duplicadas
   - Desglose por fuente: cuántas de Indeed y cuántas de LinkedIn
   - Si la rama de LinkedIn no devolvió nada, di POR QUÉ: sin acceso a Chrome, sin sesión iniciada, sin resultados de búsqueda, o todas descartadas por cerradas
   - Listado de las nuevas: empresa, puesto, salario, link

   Si no hubo ofertas nuevas, manda el email igualmente diciéndolo. El silencio no es información.

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

- [ ] Pegar el prompt corregido en la tarea y ejecutarla a mano
- [ ] Verificar en Notion que NO se recrean Hostaway / Trivelta / Luxoft / Trimble / MarsBased
- [ ] Leer el email de resumen para saber **por qué** LinkedIn devuelve cero
- [ ] Activar **"Mantener activo"** en la pantalla de tareas programadas (si no, el día
      que el portátil esté cerrado a las 9:00 no hay ofertas y no hay aviso)
- [ ] Filtro de reenvío `verserper@gmail.com` → `hello.cookyourweb@gmail.com` para
      correos de LinkedIn
- [ ] Decidir, con el dato del email en la mano, si se parte la tarea (Indeed → rutina
      en la nube, LinkedIn → local con Chrome) o si se abandona la rama de LinkedIn
- [ ] `docs/06-INTEGRACION-LINKEDIN-Y-AUDITORIA-MULTIUSUARIO-2026-07-21.md` sigue sin
      commitear en el repo

---

**Generado:** 23 julio 2026. Datos verificados contra Notion, Gmail y la API de rutinas.
