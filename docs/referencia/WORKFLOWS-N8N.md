# Workflows en n8n: qué está subido y su estado

Inventario de lo que está SUBIDO Y CORRIENDO en la instancia de n8n. Los ficheros `.json`
de `workflows/` NO son la fuente de verdad (son exports/backups); la fuente de verdad es la
instancia n8n. Este documento existe para saber, de un vistazo, qué corre en producción sin
tener que abrir n8n.

**Estado verificado vía n8n API el 28-ago-2026.** Si cambias algo en n8n, actualiza esta tabla.

> **Atención: NO te fíes de los IDs escritos aquí.** El ID cambia cada vez que se importa un export.
> Esta tabla apuntó al workflow equivocado del 5 al 28 de agosto: señalaba `5pTwriXcc6aYHO1Y`,
> que lleva APAGADO desde entonces, mientras producción corría en `CsvmtPcLVmGIZg6C`.
> Antes de tocar nada, lista los workflows y quédate con el que esté `active`.
> Ver `19-RUNBOOK-SISTEMA-PARADO-2026-08-05.md`, "Engaño 4".

> **¿Buscas los endpoints de webhook?** Están en [`../README.md`](../../README.md), sección
> **"Webhooks n8n"** (`/webhook/<RUTA_OCULTA>?id=`, `/-descartar`, `/-mandar-empresa`,
> `/<RUTA_OCULTA>`, `/<RUTA_OCULTA>`, `/buscar-para-user`), sobre el host
> `https://n8n-asistente-correo.onrender.com`.
>
> No se duplican aquí a propósito: dos copias de la misma tabla se desincronizan y acabas
> sin saber cuál es la buena. Este fichero cubre QUÉ workflows corren; el README, CÓMO se
> les llama.

---

## Workflows activos y su estado

Los 10 workflows de la instancia, leídos por API el 28-ago-2026. Seis activos.

| Workflow | ID n8n | Estado | Qué hace |
|----------|--------|--------|----------|
| **BuscarTrabajo - Ofertas Diarias (PROD, dedup ON)** | `CsvmtPcLVmGIZg6C` | ACTIVO | **EL DE PRODUCCIÓN.** 50 nodos. Cron `0 9 * * *` (09:00 Madrid = 07:00Z) busca ofertas, las escribe en Notion y manda el mail diario. Sender `veronica@cookyourwebai.es`. Además, `Cron - Revisar Aprobadas` cada 15 min. |
| **Asistente Correo Outlook - FIX 14-07** | `tVLM6O2a5doN2XZr` | ACTIVO | Fuera del flujo de ofertas. |
| **Búsqueda Empleo Diaria** (Telegram) | `LODaOAsNrmU7NnJ4` | ACTIVO | Manda ofertas por Telegram. NO escribe Notion. Que funcione NO dice nada del de producción. |
| **Captura Gmail - v4.1** | `yfmYPJc4FN2425Dt` | ACTIVO | Facturas de Gmail a Notion + PDF a Drive. Export canónico: `workflows/captura-gmail-facturas-BUENA-v4.1.json`. |
| **Digest Diario Correo** | `Nejqg3ETO8aIljp4` | ACTIVO | Fuera del flujo de ofertas. |
| **Keep-Warm CV Server** | `JAAqWbDvwAWqDvcN` | ACTIVO | Mantiene despierto el cv-server de Render. **Es el mayor consumidor de ejecuciones de la instancia.** |
| BuscarTrabajo - Ofertas Diarias (PROD, dedup ON) | `5pTwriXcc6aYHO1Y` | APAGADO | **Atención: MISMO NOMBRE EXACTO que el activo.** Buscar por nombre en n8n no los distingue: hay que mirar el ID. |
| Busqueda Empleo Diaria | `PCBULbYMrFCvzRPg` | APAGADO | Duplicado apagado. |
| WF2 Integrado v3 - Ofertas Reales | `3zFJWSkPPHDi4yMp` | APAGADO | Del plan original, nunca se usó. |
| WF2 Integrado v3 - Ofertas Reales | `OVoFiXTQwXmiyMfW` | APAGADO | Reimportación del anterior, con otro ID. |

### Webhooks: cuáles existen de verdad

Barridos los 10 workflows nodo a nodo el 28-ago-2026.

| Path | ¿Existe? | Dónde |
|------|----------|-------|
| `buscar-para-user` | Sí | `CsvmtPcLVmGIZg6C`. Es por donde el cv-server pide una búsqueda para un usuario. |
| `<RUTA_OCULTA>` | Sí | `CsvmtPcLVmGIZg6C` |
| `<RUTA_OCULTA>` | Sí | `CsvmtPcLVmGIZg6C` |
| `<RUTA_OCULTA>` | Sí | `CsvmtPcLVmGIZg6C` |
| `<RUTA_OCULTA>` | **NO EXISTE** | En ninguno. Lo que la documentación llamaba "WF1" nunca llegó a estar dado de alta. |
| `<RUTA_OCULTA>` | **NO EXISTE** | En ninguno. El cv-server le llamaba y se comía un 404 en silencio hasta el 28-ago-2026. |

Otros workflows menores comparten la credencial Groq viva `Groq account 2`
(`Ewz07GBHAM5voex1`): **Digest** y **Outlook FIX**. Estado no verificado en detalle aquí.

---

## Notas importantes (no perder)

- **El "workflow bueno" ya NO es WF2 v3.** El que corre en PROD es el de
  `workflows/PROD/`. Por reimportaciones sucesivas el mismo workflow ha tenido varios
  IDs en n8n; los anteriores siguen existiendo, apagados.

---

## Filtro de modalidad (20-jul-2026)

**Preferencia de Vero**: Remoto SIEMPRE, Híbrido SOLO Madrid, Presencial NUNCA, Híbrido de
otras ciudades fuera. Ver [[preferencia-modalidad-vero]].

**Fuentes de ofertas** (3 declaradas, **2 funcionando**), en el workflow PROD `CsvmtPcLVmGIZg6C`:
- **Remotive** (`Buscar en Remotive`): funciona. 100% remoto por diseño. Devuelve un aviso
  de que el dominio se movió a `remotive.com`.
- **Tecnoempleo** (`Buscar en Tecnoempleo`, RSS): funciona. Portal español, de aquí salen
  las presenciales y las que no cuadraban.
- **Adzuna** (`Buscar en Adzuna`): **MUERTA desde el 6-ago-2026.** Devuelve
  `{"error": "access to env vars denied"}`. La URL usa `{{ $env.ADZUNA_APP_KEY }}` y esta
  instancia de n8n tiene bloqueado el acceso a variables de entorno. **Falla en silencio
  dentro de una ejecución que acaba en `success`**, por eso nadie lo vio en tres semanas.
  Medido en la ejecución 40330. Para arreglarlo hay que meter la key como credencial de n8n,
  no como variable de entorno.

**El problema**: el nodo `Code - Normalizar Modalidad` clasificaba Remoto/Híbrido/Presencial
pero las pasaba TODAS a Notion. La preferencia de modalidad del usuario (`U.modalidad`) y la
ciudad viajaban por el workflow pero no se usaban para filtrar.

**El fix** (2 nodos, sin nodos nuevos ni tocar credenciales):
1. `Formatear ofertas`: además del idioma, ahora guarda `ubicacion_por_link` (ubicación de
   cada oferta por su link, de las 3 fuentes).
2. `Code - Normalizar Modalidad`: descarta `Presencial` y `Hibrido` no-Madrid justo antes de
   `Notion - Crear Oferta` (`return null` + `.filter(x => x !== null)`).

Nota: el filtro de PERFIL ya existía en `Formatear ofertas` (función `matchea`): exige señal
del perfil en el título (frontend/React/fullstack/AI/tech lead) y descarta backend puro.
Un ".NET + Angular" cuela porque tiene "Angular" (señal válida); endurecer eso queda como
mejora aparte.

**Edge case**: si un día TODAS las ofertas son presencial/híbrido-no-Madrid, no llega
ninguna (preferible a recibir presenciales). Raro, porque Remotive es 100% remoto.

---

## Ficheros de export en `workflows/` (NO son la fuente de verdad)

Son backups/exports, útiles para reimportar. **Trampa conocida**: el sufijo `(5)` en un
nombre de fichero descargado NO es la versión 5, es el contador de descargas del navegador.
No fiarse del número del nombre.

- `WF1-BuscarTrabajo-Usuarios.json`
- `WF2-BuscarTrabajo-v2-Groq.json`
- `WF2-integrado-v3.json` (workflow OFF en n8n)
- `captura-gmail-facturas-BUENA-v4.1.json` (canónico de Captura Gmail)
- `captura-gmail-facturas-BUENA-v4.json` (anterior)

---

**Última actualización:** 28 agosto 2026 (inventario releído por API, webhooks barridos nodo a nodo)
**Ver también:** `../README.md` (flujo completo del sistema).
