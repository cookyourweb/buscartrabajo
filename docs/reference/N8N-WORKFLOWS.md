# n8n workflows: what is deployed and its status

Inventory of what is DEPLOYED AND RUNNING on the n8n instance. The `.json` files in
`workflows/` are NOT the source of truth (they are exports/backups); the source of
truth is the n8n instance. This document exists to know at a glance what runs in
production without having to open n8n.

**Status verified via the n8n API on 28 Aug 2026.** If you change something in n8n,
update this table.

> **Warning: DO NOT trust the IDs written here.** The ID changes every time an export
> is imported. This table pointed at the wrong workflow from 5 to 28 August: it
> pointed to `5pTwriXcc6aYHO1Y`, which has been OFF since then, while production was
> running on `CsvmtPcLVmGIZg6C`. Before touching anything, list the workflows and keep
> the one that is `active`.
> See `19-RUNBOOK-SYSTEM-DOWN-2026-08-05.md`, "Deception 4".

> **Looking for the webhook endpoints?** They are in [`../../README.md`](../../README.md),
> section **"n8n webhooks"** (`/webhook/<HIDDEN_PATH>?id=`, `/-descartar`,
> `/-mandar-empresa`, `/<HIDDEN_PATH>`, `/<HIDDEN_PATH>`, `/buscar-para-user`), on the
> host in the `N8N_HOST` variable.
>
> They are deliberately not duplicated here: two copies of the same table drift apart
> and you end up not knowing which one is right. This file covers WHICH workflows run;
> the README covers HOW they are called.

---

## Active workflows and their status

The 10 workflows on the instance, read via the API on 28 Aug 2026. Six active.

| Workflow | n8n ID | Status | What it does |
|----------|--------|--------|--------------|
| **`BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)`** | `CsvmtPcLVmGIZg6C` | ACTIVE | **THE PRODUCTION ONE.** 50 nodes. Cron `0 9 * * *` (09:00 Madrid = 07:00Z) searches for offers, writes them to Notion and sends the daily email. Sender `veronica@cookyourwebai.es`. Also `Cron - Revisar Aprobadas` every 15 min. |
| **Asistente Correo Outlook - FIX 14-07** | `tVLM6O2a5doN2XZr` | ACTIVE | Outside the offers flow. |
| **Búsqueda Empleo Diaria** (Telegram) | `LODaOAsNrmU7NnJ4` | ACTIVE | Sends offers over Telegram. Does NOT write to Notion. That it works says nothing about the production one. |
| **Captura Gmail - v4.1** | `yfmYPJc4FN2425Dt` | ACTIVE | Gmail invoices to Notion + PDF to Drive. Canonical export: `workflows/captura-gmail-facturas-BUENA-v4.1.json`. |
| **Digest Diario Correo** | `Nejqg3ETO8aIljp4` | ACTIVE | Outside the offers flow. |
| **Keep-Warm CV Server** | `JAAqWbDvwAWqDvcN` | ACTIVE | Keeps the Render cv-server awake. **It is the instance's biggest consumer of executions.** |
| `BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)` | `5pTwriXcc6aYHO1Y` | OFF | **Warning: EXACTLY THE SAME NAME as the active one.** Searching by name in n8n does not tell them apart: you have to look at the ID. |
| Busqueda Empleo Diaria | `PCBULbYMrFCvzRPg` | OFF | Duplicate, switched off. |
| WF2 Integrado v3 - Ofertas Reales | `3zFJWSkPPHDi4yMp` | OFF | From the original plan, never used. |
| WF2 Integrado v3 - Ofertas Reales | `OVoFiXTQwXmiyMfW` | OFF | Re-import of the previous one, with another ID. |

### Webhooks: which ones really exist

All 10 workflows were swept node by node on 28 Aug 2026.

| Path | Exists? | Where |
|------|---------|-------|
| `buscar-para-user` | Yes | `CsvmtPcLVmGIZg6C`. It is how the cv-server requests a search for a user. |
| `<HIDDEN_PATH>` | Yes | `CsvmtPcLVmGIZg6C` |
| `<HIDDEN_PATH>` | Yes | `CsvmtPcLVmGIZg6C` |
| `<HIDDEN_PATH>` | Yes | `CsvmtPcLVmGIZg6C` |
| `<HIDDEN_PATH>` | **DOES NOT EXIST** | In none. What the documentation called "WF1" was never registered. |
| `<HIDDEN_PATH>` | **DOES NOT EXIST** | In none. The cv-server called it and silently swallowed a 404 until 28 Aug 2026. |

Other minor workflows share the live Groq credential `Groq account 2`
(`Ewz07GBHAM5voex1`): **Digest** and **Outlook FIX**. Status not verified in detail
here.

---

## Important notes (do not lose)

- **The "good workflow" is NO LONGER WF2 v3.** The one running in PROD is the one in
  `workflows/PROD/`. Through successive re-imports the same workflow has had several
  IDs in n8n; the previous ones still exist, switched off.

---

## Work-mode filter (20 Jul 2026)

**Vero's preference**: Remote ALWAYS, Hybrid ONLY Madrid, On-site NEVER, Hybrid in
other cities out. See [[preferencia-modalidad-vero]].

**Offer sources** (3 declared, **2 working**), in the PROD workflow `CsvmtPcLVmGIZg6C`:
- **Remotive** (`Buscar en Remotive`): works. 100% remote by design. Returns a notice
  that the domain moved to `remotive.com`.
- **Tecnoempleo** (`Buscar en Tecnoempleo`, RSS): works. Spanish portal, the on-site
  ones and the ones that did not fit come from here.
- **Adzuna** (`Buscar en Adzuna`): **DEAD since 6 Aug 2026.** Returns
  `{"error": "access to env vars denied"}`. The URL uses `{{ $env.ADZUNA_APP_KEY }}` and
  this n8n instance has access to environment variables blocked. **It fails silently
  inside an execution that ends as `success`**, which is why nobody saw it for three
  weeks. Measured in execution 40330. To fix it, the key has to go in as an n8n
  credential, not as an environment variable.

**The problem**: the `Code - Normalizar Modalidad` node classified
Remote/Hybrid/On-site but passed ALL of them to Notion. The user's work-mode
preference (`U.modalidad`) and the city travelled through the workflow but were not
used to filter.

**The fix** (2 nodes, no new nodes and no credentials touched):
1. `Formatear ofertas`: besides the language, it now stores `ubicacion_por_link` (the
   location of each offer by its link, from the 3 sources).
2. `Code - Normalizar Modalidad`: drops `Presencial` and non-Madrid `Hibrido` right
   before `Notion - Crear Oferta` (`return null` + `.filter(x => x !== null)`).

Note: the PROFILE filter already existed in `Formatear ofertas` (the `matchea`
function): it requires a profile signal in the title (frontend/React/fullstack/AI/tech
lead) and drops pure backend. A ".NET + Angular" slips through because it has "Angular"
(a valid signal); tightening that is left as a separate improvement.

**Edge case**: if one day ALL offers are on-site/non-Madrid hybrid, none arrive
(preferable to receiving on-site ones). Rare, because Remotive is 100% remote.

---

## Export files in `workflows/` (NOT the source of truth)

They are backups/exports, useful for re-importing. **Known trap**: the `(5)` suffix in a
downloaded file name is NOT version 5, it is the browser's download counter. Do not
trust the number in the name.

- `WF1-BuscarTrabajo-Usuarios.json`
- `WF2-BuscarTrabajo-v2-Groq.json`
- `WF2-integrado-v3.json` (workflow OFF in n8n)
- `captura-gmail-facturas-BUENA-v4.1.json` (canonical for Captura Gmail)
- `captura-gmail-facturas-BUENA-v4.json` (previous)

---

**Last updated:** 28 August 2026 (inventory re-read via the API, webhooks swept node by node)
**See also:** `../../README.md` (full flow of the system).
