# Presencia pública: qué actualizar y dónde

**29 jul 2026** · Si te piden GitHub o portfolio, esto es lo que van a ver.

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
Botón **Customize your pins**. Tenés 61 repos públicos y un recruiter mira tres.

1. `cv-server`
2. `cookyourwebai`
3. `wunjocreations`
4. `calendarioAdvientoIA`
5. `bespoke-finance-pro`
6. `practicaAvanzadaAndroidKeepcoding`

El sexto va a propósito: **los repos de bootcamp son prueba de formación continua** y
no se archivan. Dejando uno arriba, el mensaje es "me sigo formando"; los otros cinco
dicen "y construyo cosas que funcionan".

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
