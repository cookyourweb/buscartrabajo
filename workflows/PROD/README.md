# The n8n workflow, in git and verifiable

## The problem this solves

The workflow lives on the n8n server, not here. It is edited through the UI, and the
export is one enormous JSON file where every code node sits inside a string full of
escaped `\n`.

The consequence: **a three-line change is invisible in `git diff`**. That is why the
neighbouring `BACKUP-*.json` files are "before X" snapshots instead of a history: they
were only good for restoring everything, not for reading what changed.

And without a readable diff there is no review. On 30 Aug 2026, while pasting by hand,
the code of `Formatear ofertas` ended up **also** inside `Code - Normalizar Modalidad`,
which lost its own 100 lines. It was caught by chance. This directory exists to prevent
that.

## What is here

```
workflow.json        structure and connections. Long bodies are "@@FILE:nodes/…"
                     and webhook paths are "@@SECRET:<node>"
nodes/*.js           one file per code node  -> readable git diff, node --check
nodes/*.body.txt     one file per request body (the Groq prompt, for example)
secrets.local.json   the webhook paths. NOT IN GIT (.gitignore)
```

## Why the webhook paths are not committed

Since 30 Aug 2026 the search webhook is protected by an **unpredictable path**: the old
name (`buscar-para-user`) was published in this repository and anyone could trigger it.
This was verified with `curl`, no credentials, HTTP 200.

This repository is **public**. If the new path ended up in `workflow.json`, the first
`git push` would publish it and the protection would last exactly one commit. That is why
`wf-split` moves it to `secrets.local.json`, which is in `.gitignore`, and `wf-check`
warns if it finds a path that was not redacted.

If `secrets.local.json` is lost, `wf-join` **stops** and tells you which webhooks are
missing: you have to recover those paths from n8n. It is the honest trade-off of keeping
the secret out of git.

## The cycle

**When the change comes from n8n** (someone edited the UI):

```bash
# 1. Export from n8n:  menu "..." -> Download
node scripts/wf-check.mjs ~/Downloads/<export>.json     # is it healthy?
node scripts/wf-split.mjs ~/Downloads/<export>.json workflows/PROD
git diff                                                # now it IS readable
git commit
```

**When the change comes from here** (the code is edited in the editor):

```bash
node scripts/wf-join.mjs workflows/PROD workflows/PROD/_importar.json
node scripts/wf-check.mjs workflows/PROD/_importar.json  # verify BEFORE importing
# import into n8n INSIDE the open workflow: menu "..." -> Import from File
```

The round trip is verified: `split` + `join` returns a JSON **identical** to the
original. If that ever stops being true, it is a bug in the script, not in the workflow.

## Importing without breaking anything

**Inside the open workflow**, menu `...` -> *Import from File*. From the workflow list it
creates a NEW workflow with no credentials.

## The rules of `wf-check.mjs`

Each one exists because something actually broke. None depends on anyone remembering.

| # | Rule | Where it comes from |
|---|------|---------------------|
| 1 | Two code nodes with different roles cannot have the same body | 30 Aug: `Formatear ofertas` overwrote `Code - Normalizar Modalidad` |
| 2 | Every code node compiles (`node --check`) | a syntax error only shows up at run time |
| 3 | Every `$('X')` points to a node that exists | renaming a node leaves dangling references |
| 4 | Groq: `max_tokens` <= 4096 and `reasoning_effort` if the model is `gpt-oss` | 30 Aug: the account has **8000 TPM** and `max_tokens` counts toward it; without `reasoning_effort` the model reasons and returns an empty `content` |
| 5 | Adzuna: no `where=`, no `app_key` in the URL, with `salary_min` | 30 Aug: `where=Madrid` discarded 85% of Spain; the key goes through an n8n credential |
| 6 | What is computed is returned, and what is returned is written | 30 Aug: `ubic` was computed and thrown away, and `Notion - Crear Oferta` did not even have the field |

Sibling nodes with the same body (`… Error` and `… Error1`, two branches that prepare the
same email) show up as a WARNING, not a failure: that is intentional.

When a new bug is fixed, **the rule that would have caught it is added here**. That is
what the project says in `POR_QUE_FALLA_LA_IA §3`: a control that depends on someone
remembering is not a control.

## What this system does NOT do

- It does not download the workflow by itself: the export is manual (it would need the
  n8n API key).
- It does not know what is in production **today**. Only what was exported last time.
- It does not execute the nodes. `node --check` says they compile, not that they do the
  right thing.
