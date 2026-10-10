# BuscarTrabajo · how we work here

The rules of the project. They apply equally to a person who arrives at the repository
and to an agent: **they do not depend on which tool reads them.** The files that load
them (`AGENTS.md`, `CLAUDE.md`) only point here, and are disposable.

What is here is enforced; what is in `docs/` has to be looked up, and that is why it
gets forgotten.

**This repository is PUBLIC.** Before writing anything, assume it will be read by
someone who is not you.

---

## 1. What this is

A system that gathers job offers and takes them all the way to a sent CV. Three
pieces, and only the first one lives here:

```
n8n (this repo)          gathers the offer, filters it with an LLM, writes it to Notion
cv-server (other repo)   generates the CV and cover letter, uploads them to Drive
Notion                   is the state: what is pending, approved and sent
```

The heart is **an n8n workflow of 50 nodes**, not an application. There is no `src/`
here, and `package.json` has not a single dependency. This is deliberate: what is
versioned is the automation, plus the scripts around it.

- `workflows/PROD/` the workflow, split into pieces that git can diff
- `scripts/` Node tools (split, join, check) and Python tools (Notion, Drive)
- `tests/` `node --test`, no framework
- `docs/` dated runbooks and ADRs

---

## 2. No webhook route enters the repository

**This is the rule that hurts the most and the one that matters the most.**

The workflow exposes four webhooks. Three run actions with irreversible external
effects and **ask for no credential**. The only thing separating them from anyone who
can read the repository is that their route is unpredictable. The why, and why header
authentication is not used, is in
[ADR-001](docs/adr/ADR-001-webhook-protection.md).

Practical consequence, with no exceptions:

| Where | What is written |
|---|---|
| `path` field of a webhook node | `@@SECRET:<node name>` |
| Inside the code of a node (email links) | `@@SECRET:<node name>` |
| Documentation | a placeholder such as `<WEBHOOK_PATH>` |
| `workflows/PROD/secrets.local.json` | the live route, and that file is not in git |

**Never write a route by hand, not even one you believe is dead.** On 1 Sep 2026 three
already-rotated routes survived for months in the code of the nodes that build the
emails. They leaked nothing, and that is why nobody looked at them. The damage was the
opposite: `wf-join` put them back into production and the approve and discard buttons
in the emails led to a 404.

`scripts/check-secretos.mjs` checks this in the pre-commit hook and in CI. A written
prohibition is not a control; a control is code that fails.

---

## 3. The workflows: only `PROD/` is versioned

n8n exports a 46 KB JSON on a single line, unreadable in a diff. That is why
`wf-split` exists, which splits it: each code node goes out to its own file, and the
routes go to `secrets.local.json`.

The cycle, always in this order:

```
1. Export the workflow from n8n
2. npm run wf:split
3. Edit the node's .js
4. npm run wf:join
5. Import into n8n
```

The node file is edited in the editor, **never in the n8n interface**. That way the
change goes through git before it goes through production.

`wf-join` stops with an error if it finds a route written by hand (code 3) or a marker
whose name is not in the secrets file (code 4).

**Everything under `workflows/` that is not `PROD/` is ignored.** On 1 Sep 2026, 47
exports of the same workflow, taking up 38,000 lines, were removed. Git is already the
backup: a file called `antes-fix-adzuna.json` stores in its name exactly what belongs
in a commit message. To recover one, `git log --all -- 'workflows/BACKUP-*'`.

---

## 4. Before saying it is done

```
npm test              25 tests, node --test, no framework
npm run check:secretos no route in the repository
npm run wf:check      workflow warnings
npm run hooks         installs the pre-commit (once per clone)
```

The pre-commit runs the first two and does not let you commit if they fail.

Node 20 or higher. CI pins Node 20; development usually runs on Node 23, so the test
script uses `tests/*.test.mjs` and not `tests/`, which on Node 22 and later blows up
with `MODULE_NOT_FOUND`.

New tests are written test first. Red, green, refactor, and watch the red fail for the
right reason.

---

## 5. Known and declared debt

**The business rules of the filter live inside the prompt.** The 60,000 euro floor,
the restriction of remote to Spain, Europe or EMEA, and the priority of AI offers are
written in the text of `workflows/PROD/nodes/groq-generar-ofertas.body.txt`. No test
covers them: change a comma and nothing turns red.

It is noted here on purpose, because it is the first thing asked by whoever opens that
file. What decides a rule should not be decided by a model: hard filters are code. When
it is touched, they move out to a module with tests and the prompt keeps what only a
model can do.

---

**The tests cover only two pieces.** Of the 25 tests, 22 are for
`scripts/lib/secretos.mjs` and 3 for the offer formatting. The four `wf-*.mjs` have no
tests of their own, and the Python files (Notion and Drive) have none, nor does CI run
them, since it runs only on Node 20.

Covering secrets first was chosen because it is the only piece whose failure is
irreversible: a published route cannot be unpublished. The rest fails loudly and
recoverably. It is written here and in the README so that a green badge does not say
more than it covers.

## 6. What is not changed without an ADR

- How the webhooks are protected ([ADR-001](docs/adr/ADR-001-webhook-protection.md))
- Which framework the frontend uses when it exists
- That `secrets.local.json` does not enter git
- Where Postgres lives ([ADR-002](docs/adr/ADR-002-where-postgres-lives.md))
- Who authenticates against what and what the backend validates ([ADR-003](docs/adr/ADR-003-authentication.md))
- That each user brings their own AI key ([ADR-004](docs/adr/ADR-004-each-user-brings-their-own-ai-key.md))
- That Notion is frozen on migration ([ADR-005](docs/adr/ADR-005-notion-is-frozen.md))
- Where the product is published ([ADR-006](docs/adr/ADR-006-subdomains.md))

ADR-001 **expires when the frontend exists**: a browser application shows the route in
the network tab, and the unpredictable route stops protecting anything. The frontend
forces real authentication, with a backend that holds the secret. The frontend and the
security of these webhooks are the same task, not two.

## 7. Language: commits and comments in English

Since 8 October 2026. The repository is public and read by companies abroad, so what is
written from now on goes in English:

- **Commit messages and PR descriptions, in English.** They are the first thing read of
  the history. The conventional format (`fix:`, `feat:`...) and the rule of explaining
  the why are kept.
- **Comments in new code, or in code that is touched, in English.**
- **Domain names stay in Spanish** (`Oferta`, `Candidatura`, `autenticacion`,
  `ClavesPublicas`...). They are the language of the business, a job search in Spain,
  and the code uses the same words (ubiquitous language). They are not renamed.
- **Old comments are not translated all at once:** they move to English when that file
  is touched. Translating everything in one go fills the history with noise.
- **The documentation is in English** (ADRs, design, reference and runbooks), except
  `docs/archive/`, which is kept in its original Spanish. The README exists in both
  languages: `README.md` in English and `README.es.md` in Spanish, with the same facts.
