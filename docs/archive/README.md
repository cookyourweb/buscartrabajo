# Archive

These are historical notes: dated proposals, audits and fixes that were already
applied. They are kept for the *why*, not for the *what*, and they are **kept in their
original Spanish**. Each one describes the system as it was on its date, so do not rely
on them to learn how it works today. For that, see the [README](../../README.md) and
[`../reference/`](../reference/).

| Document | Date | What it records |
|---|---|---|
| [`01-DOCUMENTACION-MAESTRA-v2.3.md`](01-DOCUMENTACION-MAESTRA-v2.3.md) | 28 Apr 2026 (partly superseded in Jun 2026) | Master documentation of BuscarTrabajo v2.3: architecture, schema, lessons learned and cost model, with a banner listing what changed in v3. |
| [`02-PROPUESTA-v3.0-OFERTAS-REALES.md`](02-PROPUESTA-v3.0-OFERTAS-REALES.md) | Undated, before v3 | Design proposal to move from LLM-invented offers to real scraped offers with a CV tailored to the user's master CV. |
| [`03-PLAN-ACCION-PROXIMOS-PASOS.md`](03-PLAN-ACCION-PROXIMOS-PASOS.md) | 28 Apr 2026 | Action plan for the next session: what worked end to end, what was pending and three possible paths forward. |
| [`05-COHERENCIA-GENERACION-FILTRO-PERFIL-2026-07-03.md`](05-COHERENCIA-GENERACION-FILTRO-PERFIL-2026-07-03.md) | 3 Jul 2026 | Check that the CV generation changes did not require touching the intake filter; what had to be aligned was the user profile in Notion. |
| [`06-INTEGRACION-LINKEDIN-Y-AUDITORIA-MULTIUSUARIO-2026-07-21.md`](06-INTEGRACION-LINKEDIN-Y-AUDITORIA-MULTIUSUARIO-2026-07-21.md) | 21 Jul 2026 | How the LinkedIn search was set up as a scheduled Claude task outside n8n, plus a multi-user audit. |
| [`07-TAREA-PROGRAMADA-LINKEDIN-INDEED-2026-07-23.md`](07-TAREA-PROGRAMADA-LINKEDIN-INDEED-2026-07-23.md) | 23 Jul 2026 | Diagnosis of what failed in the scheduled LinkedIn and Indeed task, with a corrected prompt. |
| [`08-AUDITORIA-CONTRADICCIONES-DOCS-2026-07-23.md`](08-AUDITORIA-CONTRADICCIONES-DOCS-2026-07-23.md) | 23 Jul 2026 | Audit that cross-checked the documentation against the code, Notion, n8n and email, and found 11 real contradictions. |
| [`11-FILTRO-N8N-CORREGIDO-2026-07-23.md`](11-FILTRO-N8N-CORREGIDO-2026-07-23.md) | 23 Jul 2026 | Fix of the n8n offer filter, which let through offers outside the user's stack (Java, .NET, Ionic, Rails). |
| [`12-FIX-IDIOMA-CARTA-CV-2026-07-23.md`](12-FIX-IDIOMA-CARTA-CV-2026-07-23.md) | 23 Jul 2026 | Fix for a cover letter that came out in Spanish for an English-language offer, caused by a failed Notion lookup of the language. |
| [`15-ESTADO-SISTEMA-CV-2026-07-28.md`](15-ESTADO-SISTEMA-CV-2026-07-28.md) | 28 Jul 2026 | State of the CV system after the 27-28 Jul session: model change, duplicated user records fixed and new guardrails. |
| [`20-FIX-ADZUNA-SALARIO-2026-08-30.md`](20-FIX-ADZUNA-SALARIO-2026-08-30.md) | 30 Aug 2026 | Fix of the Adzuna search URL (location, salary filter and keyword query) that took it from 0 useful offers to 55. |
| [`AUDITORIA-2026-06-13.md`](AUDITORIA-2026-06-13.md) | 13 Jun 2026 | Status audit of the multi-user job search system to decide next steps, after four bugs were fixed. |
| [`superpowers/specs/2026-06-08-puente-ofertas-reales-wf2-design.md`](superpowers/specs/2026-06-08-puente-ofertas-reales-wf2-design.md) | 8 Jun 2026 | Design of the bridge that sends real offers from the daily search into the Notion and approval pipeline instead of only Telegram. |
| [`superpowers/plans/2026-06-08-puente-ofertas-reales-wf2.md`](superpowers/plans/2026-06-08-puente-ofertas-reales-wf2.md) | 8 Jun 2026 | Implementation plan for that bridge, as edits to the n8n workflow. |

## A note on file names inside these documents

The archived documents mention other files by the names they had on their date. Some
folders and files have since been renamed:

| Name mentioned in the archive | Current location |
|---|---|
| `docs/historico/` | `docs/archive/` |
| `docs/referencia/` | `docs/reference/` |
| `docs/diseno/` | `docs/design/` |
| `WORKFLOWS-N8N.md` | `docs/reference/N8N-WORKFLOWS.md` |
| `docs/runbooks/09-RUNBOOK-OFERTA-CONTACTO-DIRECTO` | `docs/runbooks/09-RUNBOOK-DIRECT-CONTACT-OFFER-2026-07-23.md` |
| `cv-server/docs/ADR-001-migracion-fastapi.md` | `cv-server/docs/ADR-001-fastapi-migration.md` |
| `cv-server/docs/ADR-002-modelo-del-cv.md` | `cv-server/docs/ADR-002-cv-model.md` |
| `cv-server/docs/ADR-003-usuario-multicuenta.md` | `cv-server/docs/ADR-003-multi-account-user.md` |
| `cv-server/docs/ADR-004-backend-llm.md` | `cv-server/docs/ADR-004-llm-backend.md` |
| `cv-server/docs/ADR-007-cifrado-del-cv.md` | `cv-server/docs/ADR-007-cv-encryption-at-rest.md` |
| `cv-server/docs/GUIA-DE-USO.md` | `cv-server/docs/USAGE-GUIDE.md` |
| `cv-server/docs/ONBOARDING-MULTIUSUARIO.md` | `cv-server/docs/MULTI-USER-ONBOARDING.md` |
| `cv-server/docs/PROMPT-ADAPTACION-CV.md` | `cv-server/docs/CV-ADAPTATION-PROMPT.md` |
