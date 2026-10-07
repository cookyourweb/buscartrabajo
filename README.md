[Español](README.es.md) · **English**

# BuscarTrabajo

[![tests](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml/badge.svg)](https://github.com/cookyourweb/buscartrabajo/actions/workflows/tests.yml)

A multi-user system that finds real job postings every morning, filters them against
each person's profile and sends them by email. When one is approved, it generates a CV
and cover letter tailored to the role and lets the person send them to the company.

In production since July 2026.

## The three repositories

| Repository | What it is | Where it runs |
|---|---|---|
| `buscartrabajo` (this one) | n8n workflows, scripts, ADRs and runbooks | n8n on Render |
| [`cv-server`](https://github.com/cookyourweb/cv-server) | Python (Flask) service that generates the CV and cover letter with truthfulness guardrails | Render, free plan |
| `panel-empleo` | Angular panel to view and manage postings. Access is by invitation, with a Google account; the public demo shows no real data | In development |

n8n searches and orchestrates, `cv-server` writes and validates, the panel is the visible
face.

## What makes it interesting

**The postings are real.** The previous version asked a language model for them, and it
returned plausible postings that did not exist. Now they come from three sources
(Remotive, Adzuna, Tecnoempleo), are filtered by the user's stack, and the ones already
saved are dropped.

**A model writes the text, not the facts.** CV and cover letter generation lives in
[`cv-server`](https://github.com/cookyourweb/cv-server), a separate service with
truthfulness guardrails and evaluation cases built from real production failures. A model
does not fail with an exception: it returns something plausible and worse.

**Secrets do not depend on anyone remembering.** n8n webhooks trigger actions with
external side effects, so their paths cannot go into a public repository.
`check-secretos` checks this in the pre-commit hook and in CI, and fails if it finds one.
It was written after discovering they had been public for months: a written rule is not
a control, a control is code that fails.
See [ADR-001](docs/adr/ADR-001-proteccion-de-los-webhooks.md) (in Spanish, like the rest
of `docs/`).

**The n8n workflow is diffable.** An n8n export is a huge JSON file with every code node
inside an escaped string: a three-line change is invisible in `git diff`. `wf-split`
breaks it into readable pieces, `wf-join` puts it back together, and `wf-check` has eight
rules that came out of real breakages. See [workflows/PROD](workflows/PROD/README.md).

## Quick start

```bash
npm install          # no dependencies: it only pins the node version
npm test             # 25 tests with node's built-in runner, no framework
npm run check:secretos
npm run hooks        # enables the pre-commit hook
```

Requires Node 20 or later. The Python scripts need `pip install -r requirements.txt`.

## What that green badge covers

The badge and `npm test` run 25 tests: 22 on `scripts/lib/secretos.mjs` and 3 on posting
formatting. `secretos.mjs` came first because it is the only piece whose failure cannot
be undone: if a webhook path leaks into the repository, it is already public.

What it does not cover, stated here so nobody infers it from a green badge:

| Piece | Coverage |
|---|---|
| `scripts/lib/secretos.mjs` | 22 tests |
| Posting formatting (workflow node) | 3 tests |
| `scripts/wf-*.mjs` | no tests of its own |
| `scripts/*.py` and `tools/*.py` | no tests, and CI does not run them |

CI runs on Node 20 and does not install Python. This is declared debt, not an oversight:
it is recorded in [CONTRIBUTING](CONTRIBUTING.md).

## Where it is heading

**The vision:** a job search companion that works with the person from start to finish.
It helps them build a solid master CV, finds the postings that fit, tailors each
application without inventing anything and prepares them for the interview. The person
always decides; the AI proposes, verifies and warns.

**The principles, already in place today:**

- **Invent nothing:** what the AI writes is checked against the master CV with deterministic detectors.
- **The person decides:** no application goes out without human approval.
- **Invitation-only and private:** each person signs in with their Google account, and only if invited.

### Action plan

| Phase | Goal | Status |
|---|---|---|
| 1. Secure access | Google sign-in by invitation in the panel; close the public routes that trusted an email from the request body | Done in `develop`, pending deployment |
| 2. Per-user identity and data | Postgres on Neon with the `(iss, sub)` identity, single-use invitations and every record owned by its user | Next |
| 3. Design system and landing page | Angular components built on the already-tested brand tokens, shared between a prerendered public landing page and the panel | Next |
| 4. Master CV | A checker that says what the master CV is missing before generating anything | Planned |
| 5. Master CV assistant | Helps complete the CV by interviewing the person, without inventing experience | Later |
| 6. Per-user AI keys | Each person brings their own key; no request falls back to the owner's keys ([ADR-004](docs/adr/ADR-004-cada-usuaria-trae-su-clave-de-ia.md)) | Later |
| 7. Interview preparation | Per posting: what they ask for and what evidence the person has; a simulator that does not hand out answers to read aloud and does not obey instructions hidden in a posting | Later |

No dates on purpose: the plan states the order and the reasoning, and the details of
each phase are opened as an issue.

## What is missing

Pending work is opened as an
[issue](https://github.com/cookyourweb/buscartrabajo/issues), not written here.
A hand-written list of next steps ages and ends up contradicting the code.
Issues labelled `seguridad` (security) go first.

What does get written down is what is not a task but a state of the system, and it is in
[CONTRIBUTING](CONTRIBUTING.md): the filter's business rules live inside a prompt with
no test covering them, and the tests cover only two pieces. That does not go stale,
because it describes how the system is built, not what is planned.

## Pieces

| Piece | What it does |
|---|---|
| `workflows/` | The n8n workflow, split into files git can diff |
| `scripts/wf-*.mjs` | Split, rebuild, verify and redact the workflow |
| `scripts/*.py` | Utilities for Notion and Drive |
| `docs/` | Decisions, runbooks and system rules |
| `tests/` | Tests for the secrets core and for posting formatting |

---

## Architecture

Three pieces. n8n orchestrates, `cv-server` generates and validates, the panel displays.

```
  PANEL (Angular)                 invitation-only access, Google account
      |
      | GET /yo, with Google ID token
      v
  CV-SERVER (Flask, Render free)  <------------------------+
      |                                                     |
      | calls n8n                                X-Clave-Maquina
      v                                                     |
  N8N (Render)  -------------------------------------------+
      |
      +-- Schedule 9:00, searches per user:
      |     Remotive + Adzuna + Tecnoempleo
      |     filter by stack and role + anti-spam against postings already in Notion
      |     cap of 12 postings, Groq formats, Notion creates the posting, Brevo notifies
      |
      +-- Approve:
      |     marks Aprobado, reads the posting, generates the cover letter and the CV
      |     (cv-server), Brevo sends "review and send", Notion stores the result
      |
      +-- Send to company:
            reads the already-edited letter; with a company email, sends letter and CV
            (replyTo = user's email); without one, tells the user to apply by hand
```

### cv-server routes

| Route | Access | Purpose |
|---|---|---|
| `GET /` | Public | Invitation page |
| `GET /health` | Public | Check that the service is up |
| `GET /yo` | Google ID token | Identifies the person signing in to the panel |
| `POST /registro` | `X-Clave-Maquina` | User sign-up |
| `POST /generar-cv` | `X-Clave-Maquina` | CV tailored to the role, uploaded to Drive |
| `POST /generar-carta` | `X-Clave-Maquina` | Cover letter tailored to the role |
| `GET /usuarios` | `X-Clave-Maquina` | List of active users |
| `POST /crear-oferta` | `X-Clave-Maquina` | Creates a posting in Notion |
| `POST /buscar-ofertas-reales` | `X-Clave-Maquina` | Posting search from cv-server |

The production n8n workflow only calls `/health`, `/generar-cv` and `/generar-carta`.
On 7 Oct 2026 `/check-email`, `/accion-existente` and the old sign-up form were removed.
Panel authentication is explained in [ADR-003](docs/adr/ADR-003-autenticacion.md).

Language models in `cv-server`: CV and cover letter with `claude-sonnet-4-6` in
production (set by the environment; `/health` shows it). If Claude fails: Groq
`openai/gpt-oss-120b`, then Gemini, then Claude Haiku 4.5.

---

## Services

| Service | Purpose |
|----------|-----------|
| cv-server (Render free) | Invitation page, user API and CV and cover letter generation |
| n8n (Render) | Orchestrator for the search and approval workflow |
| Notion | CRM for users and postings |
| Google Drive | Tailored CVs |
| Brevo | Email delivery |
| Groq | LLM for postings and fallback for CV and cover letter (`openai/gpt-oss-120b`) |

**Only one active n8n instance.** n8n does not allow two active workflows with the same
webhook path at the same time, so the old instances are deprecated and must not be
reactivated.

---

## n8n webhooks

The production workflow exposes webhooks to launch a search for a user and to resolve a
posting (approve, discard or send it to the company).

**The paths are not published here.** They trigger actions with external side effects
and currently require no credential, so the path is the only thing protecting them
(issue #1). They live in `workflows/PROD/secrets.local.json`, which is outside git, and
in the versioned workflow they appear as `@@SECRET:<nodo>`.

To recover them locally: export the workflow from n8n and run it through
`node scripts/wf-split.mjs <export.json>`, which extracts them into that file.

---

## Notion database

### Usuarios DB (users)

| Column | Type |
|---------|------|
| Name | Title |
| Email | Email (unique) |
| Perfil | Rich text |
| Rol objetivo | Rich text |
| Stack | Multi-select |
| Salario min | Number |
| Modalidad | Multi-select |
| Ciudad | Rich text |
| LinkedIn | URL |
| CV Master URL | URL |
| cv_master_file_id | Rich text |
| Activo | Checkbox |

### Ofertas DB (postings)

| Column | Type | What it stores |
|---------|------|------------|
| Empresa | Title | company name |
| Puesto | Rich text | |
| Salario | Rich text | |
| Modalidad | Select | Remoto / Hibrido / Presencial |
| Link oferta | URL | original URL (anti-spam key) |
| Notas | Rich text | short description |
| Estado | Select | Pendiente / Aprobado / Descartado / En proceso / Enviado a empresa |
| **Email Enviado** | Email | **email of the recipient user** |
| Usuario | Relation | relation to the Usuarios DB |
| Nombre Contacto | Rich text | HR contact for the posting |
| Email empresa | Email | company contact (for automatic sending) |
| Teléfono Contacto | Phone | |
| Fecha Publicacion | Date | |
| Fecha envio | Date | when the letter+CV were generated |
| Fecha Envio Empresa | Date | when it was sent to the company |
| **Link CV Drive** | URL | **tailored CV** for the posting |
| **CV usado** | Rich text | **master CV** (the reference it started from) |
| **Carta Enviada** | Rich text | generated/edited cover letter |
| Seguimiento | Date | manual follow-up |

**CV usado** is the master CV (the reference it started from). **Link CV Drive** is the tailored CV (the result). They are two different CVs.

---

## Quick debugging

```bash
# 1. Is CV Server up? Render Free sleeps after ~15 min and a cold start takes ~50 s
curl https://cv-server-ggd8.onrender.com/health

# 2. Does the search webhook respond?
#    The URL comes from workflows/PROD/secrets.local.json (outside git)
curl -X POST "$N8N_HOST/webhook/$RUTA_BUSCAR_AHORA" \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@correo.com","nombre":"tu-nombre"}'
```

If both return 200, the problem is in the internal flow: check Executions in n8n.

---

## Gotchas and known debt

- **Groq Free TPD = 200,000 tokens/day** (verified 2 Oct 2026) is the real bottleneck (not RPM). That is why there is a cap of **12 postings** in test mode. Exhausting it returns 429 until the daily reset.
- **cv-server Render variable** `WEBHOOK_BUSCAR_AHORA`: must point to the active n8n instance. If it points to a deprecated instance, the search fires into the void.
- **API keys**: after rotating them, you must update them in TWO places: n8n credentials (Notion, Brevo) **and** Render env vars (Groq, Gemini, Notion, Google OAuth).
- **n8n**: when importing a workflow from another instance, credential IDs are NOT mapped: reassign the credential node by node. Import with *Import from File* OVER the open workflow (otherwise it gets duplicated).
- **Notion**: property names are case-sensitive and include accents (`Teléfono Contacto`, `Email empresa`). Sending a property with the wrong type returns 400; leaving a property out of the payload does not fail, but writing to a name that does not exist breaks the PATCH.
- **CV/cover letter typography (cv-server)**: `cv-server` sanitizes the text before rendering (`sanear_tipografia`): long dashes and arrows are removed, because they are an AI tell and must NOT reach a company. Careful: the DOCX detects the company line using the long dash as a marker, so detection still reads the raw line and only the text being written is cleaned. Do not add a global sanitizing pass before parsing or you lose the bold text.

---

The state of this repository is told by `git log`, not by a hand-written line at the
end of the README. The workflow running in production is in [`workflows/PROD/`](workflows/PROD/README.md),
split into pieces git can diff.
