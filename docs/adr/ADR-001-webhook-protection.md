# ADR-001. How the webhooks are protected

**Date:** 31 Aug 2026 · **Status:** accepted, with a known expiry · **Issue:** #1 · **To be superseded by:** [ADR-003](ADR-003-authentication.md)

---

## Context

The n8n workflow exposes four webhooks. Three of them run actions with
**irreversible external effects**, and one sends email to third parties. All four
accept requests without any credential.

Three are invoked by **GET from a Notion button**. That constrains everything
else: a Notion button opens a URL and nothing more. **It sends no headers.**

On 31 August 2026 it was checked, by measuring against the n8n API, that all four
nodes have `authentication: ninguna` (none), and that the routes of three of them
had been published for months in this repository, which is public: in the README, in
six documents, in eleven backup copies of the workflow and inside the node code.
Nobody noticed because nothing was looking.

## Decision

**An unpredictable route, kept out of the repository, and an automatic check that it
never gets back in.**

The `path` values live in `workflows/PROD/secrets.local.json`, which is in
`.gitignore`. Everywhere in versioned files they appear as `@@SECRET:<node>`.
`check-secretos.mjs` runs in the pre-commit hook and in CI, and fails if it finds
any of them.

## Why not header authentication

It was tried on 30 August 2026 on the `buscar-para-user` webhook and **dropped after
two hours of diagnosis**. With Header Auth enabled, the endpoint returned 403 to
everything, including the correct token. Seven configuration variants of the
credential were ruled out one by one.

There was also a side effect nobody would have connected to it: **enabling Header
Auth overwrote the Groq credential of the same workflow**, which started returning
401. In n8n, shared things are overwritten silently.

For the three Notion-button webhooks the problem comes earlier and is simpler:
**even if Header Auth worked, a button cannot send the header.**

This holds for what n8n **receives**. For what n8n **sends** to `cv-server` it does
work (measured on 4 October 2026, [ADR-003](ADR-003-authentication.md)), with its own
credential and never the Groq one.

## Why redacting the repository is not the fix

A published route is burned. Removing it from the files does not unpublish it: it
stays in the commit history, which is already on GitHub.

Redaction helps with **what comes next**, not with what has already leaked. The only
thing that closes a published route is **rotating it**, and then every old occurrence
becomes a dead string: there is nothing to chase and no history to rewrite.

Hence the order: rotate first, then clean up, and publish last.

## Consequences

**Accepted:**

- The protection depends on the route not leaking. It is weaker than a credential,
  and that is known.
- Rotating a route forces the Notion buttons to be updated at the same moment, or
  they stop working.
- Two production nodes still build the URL with the route written by hand
  (`code-preparar-email-carta-cv.js`, `code-preparar-email-notificacion.js`). When
  rotating, it must be replaced with an expression, or the new route goes back into
  the repo on the next `wf-split`.

**Gained:**

- Closed without depending on Header Auth, which has been measured and does not work
  here.
- The check does not depend on anyone remembering. It is the same idea already
  applied to the `cv-server` prompts: a written prohibition is not a control; a
  control is code that fails.

## When this decision expires

**When the Angular frontend exists.**

It is decided that this system will have an Angular application covering the full
lifecycle of a job application. A browser application that calls these webhooks
**exposes the route in the network tab**. From that moment the unpredictable route
protects nothing.

In other words: this is a bridge, not a destination. The frontend forces real
authentication, with a backend that holds the secret and talks to n8n, or with
per-request tokens. When the Angular work starts, this ADR is superseded.

---

**Related:** issue #1 · `scripts/lib/secretos.mjs` · `tests/secretos.test.mjs`
· `scripts/check-secretos.mjs` · `workflows/PROD/README.md`
