# Fix Adzuna: de 0 ofertas útiles a 55 — 30-ago-2026

Workflow `CsvmtPcLVmGIZg6C` (PROD), nodo **`Buscar en Adzuna`**, campo `URL`.

## Qué estaba mal

Tres decisiones que se anulaban entre sí:

1. **`where=Madrid`** — una oferta 100% remota desde Berlín o Ámsterdam no entraba jamás.
   Medido: `579` resultados con `where=Madrid` contra `3.946` sin él, misma España, mismos 14 días.
2. **Ningún filtro de salario**, aunque `salario` ya viaja en el perfil (`Salario min` = 60000
   en Notion, mapeado en `Code — Normalizar users (schedule)`).
3. **`what_or`** con los cinco roles más las ocho tecnologías del stack. Es un OR de palabras
   sueltas: engancha "Engineer", "Manager", "Senior", "Java"... y trae ruido masivo.

## Por qué no vale con añadir `sort_by=salary` y ya

Probado. Ordenar `what_or` por salario **ordena el ruido por dinero**:

```
900000 | Global Category Manager, External Manufacturing
834000 | Técnico en Matricería
827000 | Senior AVEVA E3D - Soportes (Presencial Cádiz)
```

La corrección real es `what` (frase exacta) en vez de `what_or`.

## El dato que decide

Mismo filtro, `salary_min=60000`, últimos 30 días, España:

| `what` | ofertas |
|---|---|
| AI engineer | **55** |
| machine learning engineer | **30** |
| AI software engineer | **21** |
| senior frontend engineer | 1 |
| full stack developer | 1 |
| frontend tech lead | 0 |

106 contra 2. En el tramo de más de 60.000 €, el perfil de IA está vivo y el de frontend no.

## OJO: `app_key` NO va en la URL

El backup del 28-ago llevaba `&app_key={{ $env.ADZUNA_APP_KEY }}`. **La URL viva de hoy NO lo
lleva**: el 28-ago la clave se movió de `$env` a una **credencial de n8n**, que la inyecta el
propio nodo. Añadirlo a mano duplicaría el parámetro.

## URL NUEVA (pegar en el nodo `Buscar en Adzuna`, campo URL, modo *Expression*)

```
https://api.adzuna.com/v1/api/jobs/es/search/1?app_id=524625d0&results_per_page=50&what={{ encodeURIComponent(($('Loop Over Users').item.json.rol || 'AI Engineer').split('·')[0].trim()) }}&salary_min={{ $('Loop Over Users').item.json.salario || 0 }}&sort_by=salary&max_days_old=30&content-type=application/json
```

Sin `=` delante: ese prefijo solo aparece en el JSON exportado, no en el campo de la UI.

`split('·')[0]` toma el primer rol de `Rol objetivo` ("AI Engineer · AI Software Engineer · ...")
sin romper el multi-usuario: cada usuario aporta el suyo.

## URL VIEJA (para revertir) — la que estaba viva el 30-ago

```
https://api.adzuna.com/v1/api/jobs/es/search/1?app_id=524625d0&results_per_page=30&what_or={{ encodeURIComponent(($('Loop Over Users').item.json.rol || '') + ' ' + (($('Loop Over Users').item.json.stack || []).join(' '))) }}&where={{ encodeURIComponent($('Loop Over Users').item.json.ciudad || 'Madrid') }}&max_days_old=14&content-type=application/json
```

## Verificado antes de proponerlo

URL nueva, con el rol y el salario reales de Notion:

```
count total: 55 | devueltas: 50 | con señal de remoto: 8
180000 | Senior Principal Engineer - Agentic AI
180000 | Lead / Staff AI Engineer | AI SaaS
150000 | Principal ML Engineer: Real-Time AI at Scale (Remote)
143000 | Senior AI & Agent Platform Engineer
150000 | Staff ML Engineer: Build Customer-Facing AI
```

Países de Adzuna que responden 200: `es gb de nl fr it at pl`. Irlanda (`ie`) da 404.
Ampliar a más países es el siguiente paso, no éste.

## SEGUNDO BUG, destapado por el primero — `max_tokens: 2048` en Groq

Aplicada la URL nueva y lanzado el webhook `buscar-para-user`: **HTTP 500 en 10,6 s**,
ejecución `#41034`.

```
Problem in node 'Code - Normalizar Modalidad'
//www.adzuna.es/details/58507897011?utm_medium=api&utm_source=
[line 14]
```

**Adzuna funcionó.** Esa URL es un `redirect_url` de Adzuna que llegó hasta un nodo del final
de la cadena: pasó el filtro y pasó por Groq. Antes, con `where=Madrid`, no llegaba ninguna
oferta de Adzuna y este nodo nunca veía una.

`Code - Normalizar Modalidad:12-14`:

```js
const jsonMatch = text.match(/\[[\s\S]*\]/);
if (!jsonMatch) {
  throw new Error('No se encontró array JSON. Texto: ' + text.substring(0, 500));
}
```

Groq devolvió la respuesta **truncada a mitad de una URL** (`utm_source=`), sin el `]` de
cierre, así que la regex no casa y lanza.

Causa: nodo `Groq - Generar Ofertas`, `max_tokens: 2048`. El modelo es `openai/gpt-oss-120b`,
**de razonamiento**: los tokens de pensar salen del mismo presupuesto. Con más ofertas
entrando y links de Adzuna larguísimos, 2048 no llega.

Groq da a ese modelo **131K de contexto y hasta 33K de salida**, así que 2048 era muy
conservador.

**PRIMER INTENTO, EQUIVOCADO**: subir a `max_tokens: 8192`. La API lo tumbó:

```
Request too large for model `openai/gpt-oss-120b` ... service tier `on_demand`
on tokens per minute (TPM): Limit 8000, Requested 8418
```

**La cuenta de Groq tiene 8.000 TPM y `max_tokens` cuenta DENTRO de ese límite.** Pedir 8192
es imposible por definición: la petición se rechaza antes de empezar. En n8n eso volvió a
reventar `Code - Normalizar Modalidad`, ahora en la **línea 9** (`Respuesta vacía`) en vez de
la 14, con el texto del razonamiento asomando (`wants AI Engineer, AI Sof`).

**FIX REAL, medido con el prompt de verdad y 12 ofertas**:

```
max_tokens: 4000,
temperature: 0.3,
reasoning_effort: "low"
```

```
prompt_tokens: 2643 | max_tokens: 4000
TPM reservado = 6643 / límite 8000        entra
finish_reason: stop                        no trunca
la regex del nodo encuentra array?  True
ofertas devueltas: 5, JSON válido
```

`reasoning_effort: "low"` importa tanto como el número: `gpt-oss-120b` es un modelo de
razonamiento y sin esa brida gasta el presupuesto pensando y devuelve `content` **vacío**.

Body completo listo para pegar: `~/Desktop/groq-body-nuevo.txt`.

Modelos vivos hoy en esa cuenta de Groq (comprobado contra `/v1/models`): `openai/gpt-oss-120b`,
`openai/gpt-oss-20b`, `openai/gpt-oss-safeguard-20b`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b`,
`groq/compound`, `groq/compound-mini`. **Ya no queda ningún `llama` de chat.**

Lección: **el sistema estaba en verde porque no traía nada**. Arreglar la captación puso en
rojo el siguiente eslabón, que ya estaba roto y nadie podía verlo.

## Pendiente después de este cambio

- **El link vacío y el dedup son el mismo bug.** `Formatear ofertas` llena `yaEnviadas` con
  `properties['Link oferta'].url` (línea 94). Mindera y knowmad mood tienen `Link oferta`
  VACÍO en Notion, así que el dedup queda ciego. Guardar siempre el link arregla los dos.
- La ordenación de `Formatear ofertas` (línea 183) sigue siendo por señal de IA, no por salario.
- `MAX_OFERTAS = 12` sigue recortando a 12 antes de Groq.
- Adzuna no filtra remoto: `remotoValido()` solo se aplica al bucle de Remotive.
- Las otras dos fuentes siguen siendo españolas: Tecnoempleo (RSS) y este mismo Adzuna (`/es/`).
