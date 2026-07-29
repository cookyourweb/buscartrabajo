# Presencia pública: qué actualizar y dónde

**29 jul 2026** · Si te piden GitHub o portfolio, esto es lo que van a ver.

---

## La jerarquía (importante: hoy no está contada en ningún sitio)

```
CookYourWeb  ·  cookyourwebai.es        agencia de IA y automatización
   └── Wunjo Creations  ·  wunjocreations.com    marca de producto / IA educativa
        └── Tu Vuelta al Sol  ·  tuvueltalsol.es      SaaS de agenda astrológica con IA
```

**Tal y como está hoy, un recruiter ve tres dominios sueltos.** Ni las webs se enlazan
entre sí, ni los repos lo mencionan, ni el CV lo explica.

Contada, la estructura dice algo bueno: no son tres proyectos dispersos, es una
**agencia que lanza una marca de producto y esa marca lanza un producto**. Eso es
criterio de negocio, no solo código. Sin contar, parecen tres webs a medias.

**Dónde debería aparecer:**

- En `cookyourwebai.es` — sección de proyectos que baje por la cadena
- En la descripción de los repos de GitHub (`wunjocreations` → "marca de producto de
  CookYourWeb")
- En el `ÍNDICE DE EVIDENCIAS` del CV Master, hoy los lista como cuatro cosas planas

---

## Los cuatro enlaces (verificados hoy, todos 200)

| Proyecto | URL | Qué es |
|---|---|---|
| Tu Vuelta al Sol | `tuvueltalsol.es` | SaaS de agenda astrológica personalizada con IA generativa. Next.js, MongoDB, Vercel |
| Wunjo Creations | `wunjocreations.com` | IA que personaliza la experiencia de cada alumno en un curso. Next.js, Vercel |
| CookYourWeb | `cookyourwebai.es` | Estudio de IA y automatización. React, TypeScript, Vite, Firebase |
| cv-server | `github.com/cookyourweb/cv-server` | Generación de CVs con LLMs y guardrails. FastAPI, Pydantic, TDD, 132 tests |

> ⚠️ **Los dominios habían cambiado y el CV Master viejo tenía los tres mal**:
> `tuvueltaalsol.es` (dos aes), `wunjocreations.es`, `cookyourwebai.com`. Ninguno
> resuelve. Si aparecen en algún sitio antiguo, corregirlos.

**El cuarto es el más fuerte aunque no lo parezca**: es el único que un entrevistador
puede abrir y verificar línea por línea. Los otros tres son productos; ese es la
ingeniería en público. Y responde directamente al feedback de osapiens (*"le faltan
fundamentos para validar y arquitecturar"*) con código, tests y ADRs fechados.

---

## ✅ Hecho

- **CV Master EN y ES** — los cuatro proyectos añadidos al `ÍNDICE DE EVIDENCIAS`.
  Antes el índice era abstracto ("Diseño de un sistema RAG") y no mencionaba ni un
  nombre ni una URL: los productos en vivo eran invisibles en todos los CVs generados.
- **README de `cv-server`** — reescrito para liderar con la ingeniería (el problema de
  que el LLM no mienta, los cuatro guardrails con su caso real, los tres ADRs, los 132
  tests) en vez de con el manual de registro. Incluye una sección de lo que los
  guardrails **no** detectan.
- **Descripción del repo `cv-server`** en GitHub.

---

## ⏳ Pendiente (requiere tu mano)

### 1. Bio de GitHub
`https://github.com/settings/profile` — hoy dice `Tech Lead y UX Engineer`, desfasado.

```
Full-Stack Developer & AI Engineer · React · TypeScript · Python · +10 años en producto digital
```

Y rellenar el campo **Website**: `https://linkedin.com/in/veronica4web`

### 2. Fijar 6 repos en el perfil
Botón **Customize your pins**. Hay 52 repos propios y un recruiter mira tres.

| # | Repo | Qué dice |
|---|---|---|
| 1 | `cv-server` | Ingeniería: guardrails, ADRs, TDD, 132 tests |
| 2 | `wunjocreations` | IA en producción, con producto y usuarios |
| 3 | `cookyourwebai` | La marca, en producción |
| 4 | `bespoke-finance-pro` | TypeScript y React |
| 5 | `calendarioAdvientoIA` | Formación reciente **con el stack de hoy** (dic-2025) |
| 6 | `teenage-points-system` | Producto propio, React (jul-2025) |

Los seis son TypeScript, React o Python con IA: una línea coherente.

> **Descartado `practicaAvanzadaAndroidKeepcoding`**, que estaba en una versión previa
> de esta lista. Los repos de bootcamp **no se archivan** — prueban formación continua —
> pero ese es de **julio 2023 y en Kotlin/Android**: no aparece en el CV, ni en LinkedIn,
> ni tiene relación con lo que se busca. Fijado arriba, el perfil leería
> "React, IA, IA, Vite... y Android", que no dice *me formo* sino *no sé hacia dónde voy*.
> Quien sostiene el argumento de formación con fecha reciente es `calendarioAdvientoIA`.
>
> **Regla**: la formación se demuestra teniéndola en el historial, no fijándola arriba.

> `buscartrabajo` tampoco se fija: hace visible que estás en búsqueda activa y no aporta
> nada al perfil técnico.

### 3. Descripción de los repos sin ella
`wunjocreations`, `cookyourwebai`, `bespoke-finance-pro` y `calendarioAdvientoIA` no
tienen descripción. Un repo sin descripción no dice nada aunque el código sea bueno.

### 4. `cookyourwebai.es` no enlaza a nada tuyo ⚠️

**Verificado el 29-jul**: sus únicos enlaces salientes son `lovable.dev` y Google Tag
Manager. Cero menciones a `tuvueltalsol.es`, `wunjocreations.com`, LinkedIn o GitHub.

Importa porque es la web que va en **Website** de GitHub (y ya está en LinkedIn como
Company): es la puerta de entrada a tu marca. Hoy quien entra no puede ir a ningún
sitio.

Añadir una sección de proyectos con:

- Tu Vuelta al Sol → `tuvueltalsol.es`
- Wunjo Creations → `wunjocreations.com`
- GitHub → `github.com/cookyourweb`
- LinkedIn → `linkedin.com/in/veronica4web`

**Y quitar el badge de `lovable.dev`** si está visible en la página. Usar Lovable no es
el problema; un badge de herramienta no-code en la web de tu propia agencia de
desarrollo manda una señal que no conviene ante un recruiter técnico.

### 4b. Website de GitHub: `cookyourwebai.es`, no `tuvueltalsol.es`

En GitHub el campo `Website` se lee como *"quién eres profesionalmente"*. CookYourWeb es
la marca (empresa actual en el CV, experiencia en LinkedIn, firma del correo); Tu Vuelta
al Sol es **uno de sus productos**. Poner el producto obliga al lector a deducir la
relación; poner la marca lo hace entrar por la puerta correcta. Además ya es el enlace
que figura en LinkedIn: mismo enlace en los dos sitios.

### 5. Decidir sobre `buscartrabajo` (repo público)
Hoy no tiene nada comprometedor **en `origin/main`** (verificado). Pero la rama
`develop` local contiene:

- `entrevistas/edreams-prep/` — respuestas de entrevista, **rango salarial** y gaps
- `docs/14-ESTRATEGIA-PAN-VS-TECHO` — estrategia de posicionamiento
- `docs/15-ESTADO-SISTEMA-CV` — análisis de encaje de cada oferta
- `backups-master/` — copias del CV Master

Un push de `develop` a un repo público expondría el rango salarial y los gaps ante
empresas con las que estás en proceso. **Recomendación: ponerlo privado.** Nadie te va
a valorar por ese repo, y el coste de equivocarse es alto.

---

## LinkedIn (más adelante, no urge)

**El titular ya está bien y NO se toca.** Verificado el 29-jul contra el `Profile (8).pdf`
exportado el 23-jul: es idéntico al del CV Master, palabra por palabra.

```
Frontend Tech Lead | Full-Stack Developer | AI Engineer | React · TypeScript · Node.js | +10 años en producto digital
```

> ⚠️ La vista pública de LinkedIn **sin sesión** muestra "Verónica S." y solo
> `cookyourwebai`. Es un recorte de LinkedIn, no un problema del perfil. Para auditarlo,
> usar el PDF exportado, no `WebFetch`.

### Lo único a ajustar cuando toque

En el **Extracto**:

> *"Como Tech Lead **fui responsable de la migración frontend completa** de ALD Automotive a Ayvens"*

Es la misma inflación de alcance que se quitó de los CVs el 28-jul (`sole technical
authority`, `designed backend services`). Si alguien cruza LinkedIn con el CV, el sitio
público dice **más** de lo que el CV sostiene, que es la dirección equivocada.

Redacción propuesta:

> *"Como Tech Lead **lideré el frontend de** la migración de ALD Automotive a Ayvens: no
> solo el rebranding visual, sino la nueva arquitectura de componentes del design system,
> coordinando con diseño, backend y producto."*

El resto del Extracto está bien: el gancho de *"sé exactamente qué duele"* y el cierre
con llamada a la acción funcionan.

---

## Regla de fondo

**Sumar no es acumular.** 61 repos públicos no suman más que 6 bien elegidos: si hay
que bucear para encontrar lo bueno, el ruido resta. Los de formación se quedan —
prueban que sigues estudiando — pero no van primero.

---

**Relacionado:** `~/Desktop/cv/LEEME.md`, `docs/14-ESTRATEGIA-BUSQUEDA-PAN-VS-TECHO`,
`docs/16-REGLAS-CARTA-PRESENTACION`.
