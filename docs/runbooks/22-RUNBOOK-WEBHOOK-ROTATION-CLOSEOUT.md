# Runbook. Closing out the webhook rotation

**Date:** 1 Sep 2026 · **Issue:** #1 · **Related:** [ADR-001](../adr/ADR-001-webhook-protection.md)

This document closes what ADR-001 left half done. It decides nothing new: it applies
the decision that has already been made.

---

## What was happening, in one sentence

The routes of the four webhooks were rotated and removed from the repository, but
**the three files that build the links in the emails still had the old route written
by hand**, and `wf-join` puts them as they are into the workflow that is imported into
n8n. The next import would have put back into production links that point to dead
routes.

ADR-001 warned about half of the problem:

> Two production nodes still build the URL with the route written by hand.
> When rotating, it must be replaced with an expression, or the new route goes back to
> the repo on the next `wf-split`.

The other half, which was not noted down, is worse: **the old route goes back to
production**, and the approve, discard and send-to-company emails stop working. Nothing
warned about it, because `check-secretos` only looked for LIVE routes and a dead route
leaks nothing.

---

## What is already fixed in the repository

| What | Where |
|---|---|
| The three email links use `@@SECRET:<node>` instead of the route | `workflows/PROD/nodes/code-preparar-email-notificacion.js`, `code-preparar-email-carta-cv.js` |
| `wf-join` resolves the markers **inside** the node code, not only in `path` | `scripts/wf-join.mjs` |
| `wf-join` stops with an error if it finds a dead route or an orphan marker | `scripts/wf-join.mjs` |
| Check 3: **any** literal route is forbidden, live or dead | `scripts/check-secretos.mjs` |
| The two living documents use a route placeholder instead of a route | `docs/01-...` (now `docs/archive/01-...`), `docs/19-...` (now `docs/runbooks/19-...`) |
| `npm test` runs again on Node 23 | `package.json` |

The frozen files (`.archivo-historico-*`, `_archivo-exports-*`) are left out of check 3
on purpose: they are a record of what existed and nobody imports them into n8n. Their
live routes are still watched by checks 1 and 2.

Verified end to end: `wf-join` rebuilds the 50 nodes with **0 unresolved markers, 0 old
routes**, and the three email links pointing to the live route of their webhook.

---

## What you have to do, in this order

### 1. Confirm that n8n has the new routes

`workflows/PROD/secrets.local.json` has routes of 25, 32, 39 and 34 characters, and
none matches the published ones. Everything points to the rotation having been done on
30 and 31 August. **Confirm it before going on**: open the four webhook nodes in n8n
and compare their `path` field with the file.

- If they match: the rotation is done, go on to step 2.
- If they do not match: the routes in the file are the new ones and **have not been
  applied**. Apply them in n8n first, and come back here.

### 2. Re-import the workflow

```
npm run wf:join
```

It generates `workflows/PROD/_importar.json`, which is in `.gitignore`. Import it into
n8n. Without this step, the emails that go out still carry the old route.

If something is wrong, the command stops and says so: it exits with code 3 if it finds
a dead route written by hand, and with 4 if there is a marker whose name is not in the
secrets file.

### 3. Update the Notion buttons

The three webhooks invoked from a Notion button open a fixed URL. When rotating, that
URL changed. Review the buttons in the offers database and put in the route that is in
`secrets.local.json`.

### 4. Warn about the emails that already went out

**This is the effect to keep in mind.** The emails sent before the rotation carry
approve and discard links that no longer respond. There is no way to fix them: the link
lives in an email that is already in an inbox.

The offers waiting for approval from one of those emails **are approved or discarded
from Notion**, not from the email. The new emails, once step 2 is done, work.

### 5. Merge the branch

`seguridad/webhooks-sin-auth` has been out of `main` since 31 August.
When the previous steps are done, merge.

Mind the size: it is 121 files and about 67,500 lines, and almost all of it is backup
copies of summer workflows that came in the same bag as the security fix. If the
repository is going to be shown, it is worth separating the copies into their own
commit before merging.

---

## How to rotate next time

The order of ADR-001 is still the right one: **rotate, clean, publish.**

1. Generate new, long and unpredictable routes, and change them in the four n8n nodes.
2. Export the workflow and run it through `npm run wf:split`. The routes go out by
   themselves to `secrets.local.json` and the node code is left with markers.
3. `npm run check:secretos`. It has to come out green.
4. Update the Notion buttons.
5. `npm run wf:join` and re-import, so that new emails carry the live route.

Never write a route by hand in a repository file. Not even one you believe is dead:
check 3 rejects it, and it is right to.

---

## When all of this becomes unnecessary

When the Angular frontend exists, according to ADR-001. A browser application shows
the route in the network tab, and the unpredictable route stops protecting anything. At
that point real authentication is needed: a backend that holds the secret and talks to
n8n, or per-request tokens.

In other words: **the frontend and the security of these webhooks are the same task,
not two.** Starting the Angular work without resolving authentication makes this worse,
it does not fix it.
