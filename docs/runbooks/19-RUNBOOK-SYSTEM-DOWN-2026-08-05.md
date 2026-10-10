# 19. Runbook: "the system is not sending me offers"

**Date:** 5 August 2026
**Status:** root cause found and fixed
**Applies to:** workflow `BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)`, id `CsvmtPcLVmGIZg6C`

This document exists because the same symptom has been diagnosed **five times** (24 Jun, 8 Jul, 13 Jul, 30 Jul, 5 Aug) and four of them started from scratch. The fifth found the real cause. It is written down here so that we do not pay that toll again.

---

## 1. The root cause of 5 August

The workflow has **four triggers**, not one:

| Trigger | Cron | What for |
|---|---|---|
| `Schedule Trigger (9am)` | `0 9 * * *` | the daily offer search |
| `Cron - Revisar Aprobadas` | `* * * * *` **(the culprit)** | review approved offers in Notion |
| `Manual Trigger` | manual | tests |
| `Error Trigger` | event | error notifications |

`Cron - Revisar Aprobadas` fired **every minute**: 1,440 executions a day of 400 to 650 ms, all with `success` status and producing nothing. Added to the rest of the active workflows, the instance accumulated **11,240 production executions**.

The full chain:

1. The every-minute cron saturates the n8n instance on Render all day.
2. The instance runs out of memory and restarts by itself.
3. When the 9:00 trigger arrives, there is no memory available: `WorkflowCrashedError: Workflow did not finish, possible out-of-memory issue`, dying right at the `Schedule Trigger (9am)`. It happened on 29, 30 and 31 July.
4. From 3 August onwards the instance did not even get to 9:00 alive, so there was no execution **and no error email**. Total silence, which is the most misleading symptom of all.

### The fix applied

`Cron - Revisar Aprobadas` goes from `* * * * *` to `*/15 * * * *`. From 1,440 executions a day to 96.

Verified by re-reading the workflow from the server and watching 6 minutes with no trigger firing. Previous backup in the history: `git show 1a868f3:workflows/BACKUP-CsvmtPcLVmGIZg6C-2026-08-05-0832-antes-fix-cron.json`.

---

## 1 bis. The other two failures, which were the ones that really emptied Notion

Fixing the cron stopped the instance from going down, but **offers still did not arrive**. There were two other chained failures, both measured on the real feed, not assumed.

### Failure A: the work-mode filter assumed On-site and threw away 39% of the offers

In `Code - Normalizar Modalidad`:

```js
let modalidad = 'Presencial';                  // default value
if (mod.includes('remoto'))  modalidad = 'Remoto';
else if (mod.includes('híbrido')) modalidad = 'Hibrido';
if (modalidad === 'Presencial') return null;   // discarded
```

If the offer did not declare a work mode, the value stayed at `Presencial` and the next line discarded it. The workflow ended as `success` with zero items and nobody found out.

**And it contradicted Groq's own prompt**, which literally says *"NUNCA asumas la modalidad: si la oferta no dice remoto/hibrido, deja el campo vacio"* (NEVER assume the work mode: if the offer does not say remote/hybrid, leave the field empty). Groq obeyed and returned `"modalidad": ""`. The code after it assumed. Two opposite rules in the same workflow.

**Measured on the real RSS (80 offers):**

| | offers |
|---|---|
| with a work mode somewhere in the text | 49 |
| **without a work mode anywhere** | **31 (39%)** |
| with the work mode visible in the first 60 chars | 31 |
| with the work mode visible in the first 500 chars | 31 |

Useful fact: **Tecnoempleo puts the work mode in the `Provincia` field**. In 23 offers it says `hibrido` and in 3 `100% en remoto` instead of a province. That is why they are already visible in the first 60 characters.

Hypothesis discarded along the way: it was thought that the problem was that only 60 characters of description are sent to Groq (`descFull.slice(0, 60)`). Raising it to 500 gains **2 offers out of 80**. That was not it, and measuring before touching it saved a useless change.

**Fix applied:** the work mode is no longer assumed. If it cannot be determined, it stays `Sin confirmar` (Unconfirmed; a new option added to the Notion select) and the offer **goes in anyway**, with `[VERIFICAR MODALIDAD]` (verify work mode) at the start of the Notes. It is discarded only with explicit data: On-site, or Hybrid outside Madrid. The work mode is also looked for in the 1800-character description that the node already had stored alongside, without touching the prompt or the formatting node.

### Failure B: only the first 30 offers of the RSS were read, out of 80

In `Formatear ofertas`:

```js
for (let k = 1; k < parts.length && k <= 30; k++) {   // the feed brings 80
```

**Measured on the 5 August feed:**

| | offers matching Vero's profile |
|---|---|
| in the first 30 | **0** |
| in all 80 | **5** |

The five that fit were below position 30. The cap threw them all away without looking at them. The Tecnoempleo feed is **not ordered by relevance**: the first 30 that day were Automation Technician, Electronics Operator, SAP MDG, ABAP and ERP Consultant.

This explains the trickle of "one offer in twelve days" better than anything else.

**Fix applied:** cap raised from 30 to 100.

### Failure C: the 30-second `Wait` lost the whole execution

`Wait - Rate Limit Groq` was set to 30 seconds. The 9:00 execution of 5 August (id 34056) died exactly there: it went through the three portals without a single failure, formatted the offers, reached the `Wait` and was left orphaned with `WorkflowCrashedError`.

In n8n **a short wait lives in process memory, not in the database**. If the process restarts during those 30 seconds, the execution is lost and the message that appears is the generic *"possible out-of-memory"* one, which sends the diagnosis in the wrong direction. It was not memory: it was a wait that nobody resumed.

With **a single user** only one call to Groq is made, so there is no rate limit to protect against. **Fix applied:** lowered to 2 seconds. The complete flow went from 38 to **6.7 seconds**, so the window in which a restart can kill the execution is fifteen times smaller.

### End-to-end verification

Triggering the real flow through `POST /webhook/<WEBHOOK_PATH>` with the Notion profile:

```
webhook: 200 (38.1s)
response: {"messageId": "<...>"}

NEW OFFERS IN NOTION: 2
  Online retailer | Senior AI Engineer         | Sin confirmar
  Reinsurer     | Senior Full Stack Engineer | Sin confirmar
```

The two are exactly the ones Groq had selected on 4 August and the filter discarded.

**How to relaunch the flow without waiting for 9:00:** `POST $N8N_HOST/webhook/<WEBHOOK_PATH>` with the body that `Code — Normalizar (interno)` expects: `nombre`, `email`, `perfil`, `rol`, `stack[]`, `salario`, `modalidad[]`, `ciudad`, `user_id`. The `user_id` is the id of Vero's page in the Users database. Script ready in the session scratchpad (`probar_flujo_real.py`).

---

## 2. The four deceptions that cost hours

Each of these wasted time in some earlier diagnosis. Read them before investigating.

### Deception 1: "the emails are not reaching me"

The emails **do** arrive. They are unread in the destination inbox, sender `veronica@cookyourwebai.es` (Brevo). On 5 August an offer of 2 Aug and the three error notices of 29, 30 and 31 July were unread.

The email is sent **once for each new offer created in Notion**. With no new offer there is no email. So "no emails arrive" almost always means "no offers are being created", which is a different problem and further upstream.

### Deception 2: "I get Telegram alerts, so the system works"

False. They are **different workflows**:

- Telegram: `Búsqueda Empleo Diaria`, id `LODaOAsNrmU7NnJ4`, 9 nodes.
- Notion and email: `BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)`, id `CsvmtPcLVmGIZg6C`, 50 nodes.

That one works says nothing about the other.

### Deception 3: "healthz answers 200, the instance is fine"

A single call is not enough. On 5 August `/healthz` answered 200 in 0.24 s, and ten minutes later it was **six probes in a row at 502** before coming back. An instance that restarts in a loop answers 200 half of the time.

**You have to probe several times, spaced out**, never just once.

### Deception 4: "the workflow ID is the one the documentation says"

The ID changes every time an export is imported. Known history: `3zFJWSkPPHDi4yMp`, `5pTwriXcc6aYHO1Y`, `OVoFiXTQwXmiyMfW` and now `CsvmtPcLVmGIZg6C`. All four still exist on the instance, three switched off.

**Never trust an ID written in a document.** List the workflows and keep the one that is `active`.

---

## 3. Diagnostic order (follow as written)

When Vero says "nothing is reaching me", do this **in this order**. The first three steps take a minute and are usually enough.

### Step 1: when did the last real offer come in?

Query Notion, data source `collection://<id>`:

```sql
SELECT createdTime, "Empresa", "Puesto", "Estado"
FROM "collection://<id>"
ORDER BY datetime(createdTime) DESC LIMIT 20
```

The column is `createdTime`, **not** `"Created time"`. Look at the **time**: the ones created around 07:00 UTC are from the cron; the mid-afternoon ones are manual loads and do not prove that the system works.

### Step 2: what do the error emails say?

Search the destination Gmail:

```
newer_than:14d subject:"❌ ERROR"
```

Open the **body** of the email, not just the subject. The subject always says `Nodo: Unknown` and is useless. The body carries the JSON with `error.message`, `lastNodeExecuted` and the execution id.

Count how many there are: two errors on two consecutive days is not an isolated incident, it is a daily failure. And **the absence of error emails is not a good sign**: it can mean that the instance does not even start.

### Step 3: how often is it running?

In the n8n UI, **Executions** tab, look at the `Started` column. If there is a row per minute, the problem is found.

By API, subtract two execution ids exactly 24 hours apart: on 30 July they gave 1,625 executions a day. The normal figure should be under 300.

### Step 4: does the instance stay alive?

Probe `$N8N_HOST/healthz` **ten times with 20 seconds in between**. If 502s appear, the instance is restarting and that is the real problem.

### Step 5: review the triggers of all active workflows

List by API and look cron by cron. On 5 August there were 6 active workflows, and between them they generated about 2,300 executions a day:

| Workflow | Trigger | Frequency |
|---|---|---|
| `BuscarTrabajo - Ofertas Diarias` | Cron - Revisar Aprobadas | every minute (fixed to 15 min) |
| `Captura Gmail - v4.1` | 7 Gmail triggers | every 15 min **each** |
| `Asistente Correo Outlook` | Outlook Trigger | every 15 min |
| `Keep-Warm CV Server` | Every 10 minutes | every 10 min |
| `Digest Diario Correo` | Schedule | daily 8:00 |
| `Búsqueda Empleo Diaria` | Every day 9:00 | daily |

The 7 Gmail triggers of the capture workflow are the next candidate if the problem returns.

---

## 4. The n8n API

**Real host:** the one in the `N8N_HOST` variable (not the old host that appears in old documentation).

**Key:** in `buscartrabajo/.env`, variable `N8N_API_KEY`. Header `X-N8N-API-KEY`.

**Generated at:** `$N8N_HOST/settings/api`

### Gotcha that cost half a session

The key in the `.env` returned **401** and seemed revoked. It was not: it had **a `<` character stuck on the end**, which broke the JWT signature. The key is 267 characters and the file had 268.

Before declaring a key dead, check that it is a clean JWT:

```python
re.match(r"[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", valor)
```

If the match does not cover the whole string, there is junk at the end.

That same `<` is what breaks the shell. **Never do `source .env` or `. .env`**: zsh tries to interpret it, fails, and in the error message **prints the value of the previous line**. That is how the `NOTION_TOKEN` was burned on 5 August. To read a value from the `.env`, parse it with Python line by line and never print it.

### PUT gotcha

`PUT /api/v1/workflows/{id}` only accepts `name`, `nodes`, `connections` and `settings`. Any other field returns 400. And inside `settings` it only admits this list:

```
saveExecutionProgress, saveManualExecutions, saveDataErrorExecution,
saveDataSuccessExecution, executionTimeout, errorWorkflow, timezone, executionOrder
```

`binaryMode` has to be removed from the body. It is not lost: n8n keeps it on the server.

---

## 4 bis. Adzuna has been down for days, and fails silently

Found on 6 August, with the system already fixed and working. The `Buscar en Adzuna` node **does not make the HTTP call**. It returns:

```json
{"error": "access to env vars denied"}
```

The node URL uses `{{ $env.ADZUNA_APP_KEY }}` and the instance has reading environment variables from expressions blocked. The node returns the error as if it were a result, the workflow continues and ends as `success`.

**The same error verified in three executions on different days:** 4 August (id 32459), 5 August (id 34085) and 6 August (id 34340). It is not possible to look further back because n8n no longer keeps those executions.

**Of the three sources only two work.** And Adzuna is the only one that brings structured salary (`salary_min`, `salary_max`), so that signal is lost too.

### The clue that gives it away: the duration

```
Buscar en Remotive     698 ms
Buscar en Tecnoempleo  414 ms
Buscar en Adzuna         3 ms     (no call was made)
```

**Any network node that takes less than 10 ms has made no request.** The status says `success` and the duration tells the truth. Look at the duration column before the status one.

### Possible fixes

1. **The recommended one.** On Render, n8n service, add the environment variable `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` and restart. It unblocks `$env` in expressions without exposing the key in the workflow, and also fixes any other node that uses it.
2. Put the literal key in the node URL. It works immediately, but it ends up written in the workflow JSON and in every backup.
3. Create an n8n credential of type Query Auth and reference it. Cleaner than 2 and more work.

The `app_id` is already in the clear in the URL. The only thing missing is `ADZUNA_APP_KEY`.

---

## 5. What is still pending

1. **Purge the execution history.** There are 11,240 records taking up disk and memory. On Render, environment variables of the n8n service: `EXECUTIONS_DATA_PRUNE=true` and `EXECUTIONS_DATA_MAX_AGE=168` (7 days).

2. **Publish the OAuth consent screen to Production.** The Google project `n8n-asistente-correo` is in **Testing** mode, and Google kills refresh tokens **every 7 days**. It is the cause of the `invalid_grant` errors of 21 July and of the Drive token that expired on 31 July. As long as it stays in Testing, it will happen again every week.

3. **Rotate the `NOTION_TOKEN`**, exposed on 5 August by the `source .env`.

4. **Review the 7 Gmail triggers** of the capture workflow. Seven 15-minute pollings on seven mailboxes is a lot for a free instance.

5. **The LinkedIn branch has been dead since 23 July.** It needs Claude in Chrome with a signed-in session, and that does not exist in cloud routines. See document 07.

---

## 6. Summary in five lines

- The symptom "no emails arrive" is almost never about email. It is about offers not being created.
- Telegram and Notion are different workflows: one does not report on the other.
- A `healthz` that answers 200 once proves nothing. Probe ten times.
- Workflow IDs change with every import. List and filter by `active`.
- Before touching anything: look at how often it runs. A cron every minute takes down the whole instance.
