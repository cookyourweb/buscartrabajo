# Runbook: an offer that arrives by direct contact

> Written on 23 Jul 2026 after taking more than an hour to get the recruitment-agency CV
> out. The goal of this document is that next time it takes fifteen minutes.

## When it applies

A recruiter writes on LinkedIn, by email or calls. The offer does NOT come from the n8n
workflow or from the scheduled task, so it is not in Notion and the system does not
know it exists.

---

## The five steps

### 1. Put the offer into Notion

**How:** by telling Claude about it in the conversation and pasting the recruiter's
message. Claude creates the page. There is no form or endpoint to use.

The page goes in the data source `collection://<id>`
with these fields as a minimum: `Empresa`, `Puesto`, `Descripción`, `Salario`,
`Modalidad`, `Ubicación`, `Estado`, `Idioma`, `Usuario`.

- `Estado`: **`Aprobado`**. A direct-contact offer enters at the end of the route, not
  at the start: the decision that it is of interest has already been made when the
  recruiter writes, and `Aprobado` is what triggers the generation of CV and cover
  letter. No new status of the "They contacted me" type is needed. The reason is in
  `10-HOW-AN-OFFER-ENTERS-2026-07-23.md`.
- The nine valid options and who sets each one are in
  `10-HOW-AN-OFFER-ENTERS-2026-07-23.md`.
- **Always in `Ofertas de Trabajo`, never in `Candidaturas`**: the latter has neither
  `Descripción` nor `Idioma`, and without them a tailored CV cannot be generated.
- `Usuario`: `["https://app.notion.com/p/<id>"]`
- `Notas`: this is where the state of the conversation, what the recruiter asked for
  and **the known gaps** go. It is what avoids repeating the analysis two weeks later.
- The page body: paste the complete original message and the history of replies.

**Watch out:** the `Tags` multi_select has no options defined. Sending any value gives
`validation_error`. Either leave them empty or add the options to the schema first.

**Do not use `POST /crear-oferta`**: it returns 404 (it uses the data source id where
Notion expects the database id). See the bug in the project memory.

### 2. Generate the CV

> **The CV is written by the prompt. Never by Claude by hand in the chat.**
>
> On 23 July the recruitment-agency CV was produced by correcting by hand each flaw as it
> appeared. A good CV came out and the system stayed just as broken: the prompt learned
> nothing. When the generated CV fails, the fix goes in **the cv-server prompt**, not in
> the CV. Correcting the result hides the problem and guarantees it will repeat on the
> next offer.

```bash
# Since 4 Oct 2026 it requires the machine key. On the borrowed Mac it is in the keychain:
CLAVE_MAQUINA="$(security find-generic-password -s 'CLAVE_MAQUINA cv-server' -w)"
curl -s -X POST https://cv-server-ggd8.onrender.com/generar-cv \
  -H 'Content-Type: application/json' \
  -H "X-Clave-Maquina: $CLAVE_MAQUINA" \
  -d '{"email":"persona@example.com","empresa":"...","puesto":"...","idioma":"es","descripcion":"..."}'
```

Notion is NOT needed for this: the endpoint accepts company, job title and description
on their own. Notion is for the follow-up.

In `descripcion` goes the ad **plus whatever the recruiter asked for on the call**.
That last part is gold and it is in no ad.

### 3. READ the generated CV. Always.

The endpoint returns a Drive link. It has to be opened and read. It is not enough that
the response says `ok: true`.

Checklist, which are the real failures that have occurred. **Every box that comes out
ticked is a fix in the prompt, not a manual correction of the document:**

- [ ] Is there any **technology that the offer asks for and Vero does not have**? (PHP/Symfony
      slipped in with the ambiguous phrase "integration context with PHP/Symfony architectures")
- [ ] Does what the recruiter expressly asked for appear?
- [ ] Is the headline a **real identity** (`Frontend Tech Lead` / `Full-Stack Developer`
      / `UX Engineer`) and not the vacancy title?
- [ ] Are there **leadership verbs** in the body if the position does not ask for lead/manager?
      (`rg -i 'lider|responsable|coordinando|a cargo|dirig'`)
- [ ] Can any sentence be traced **almost verbatim to the ad**? That gets deleted.
- [ ] Any figure that is not in the Master? (the guardrail checks it and returns
      `cifras_no_respaldadas`, but it is worth looking)

Note on Drive: `read_file_content` may return empty on the first call on a `.docx`.
Retry before assuming it cannot be read.

### 4. Turn it into a PDF

The cv-server delivers `.docx`. PDFs are what get sent to companies.

```bash
python3 -m venv venv-pdf && ./venv-pdf/bin/pip install reportlab
./venv-pdf/bin/python buscartrabajo/tools/cv_md_a_pdf.py CV.md CV.pdf
```

On macOS the venv is needed: PEP 668 blocks `pip install` on the system Python.

File name with the job title inside, because in a recruiter's inbox a file that only
carries the name gets lost: `CV-Veronica-Serna-Perez-Frontend-Tech-Lead.pdf`.

### 5. Close the loop in Notion

Fill in `Link CV Drive` and `CV usado`, and set the `Estado` that applies.

---

## Why the previous time took more than an hour

It was not the CV. It was the corrections that could have been avoided:

1. `/crear-oferta` returned 404 and it had to be diagnosed on the fly.
2. The generated CV broke TWO rules that were already written in the prompt (position
   level and the evidence rule on technologies), and it had to be fixed by hand.
3. The profile echoed the ad and had to be cleaned up.
4. Several rounds of rewriting the AI paragraph because there was nothing written down
   about how this should be told.

All four are fixed at the source, not by repeating the manual work every time.

## Pending so that this runbook becomes unnecessary

- [x] ~~Technology guardrail in the cv-server prompt (evidence rule: a technology goes in
      only if the Master backs it)~~ **DONE 23 Jul**, commit `b3c98d2` in `cv-server`.
      `/generar-cv` returns `tecnologias_no_respaldadas`. Still to be deployed to PROD.
- [ ] Make the POSITION LEVEL rule actually hold (it exists in
      the `cv-server` prompt, module `server.py`, and was not applied)
- [ ] Anti-echo rule in the prompt (already documented in
      `cv-server/docs/CV-ADAPTATION-PROMPT.md`, still to be brought into the prompt)
- [ ] PDF export inside the cv-server itself, so it is not done by hand
- [ ] Fix the 404 of `/crear-oferta` (database id versus data source id)

---

**Generated:** 23 July 2026, after a recruitment-agency process.
