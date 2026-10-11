# ADR-003. Who authenticates against what, and what the backend validates

**Date:** 2 Oct 2026 · **Status:** accepted · **Closes:** C4 of [architecture decisions](../design/2026-09-05-architecture-decisions.md) · **Will supersede:** [ADR-001](ADR-001-webhook-protection.md), once `cv-server` is the only caller of n8n

---

## Status as of 7 October 2026

| Item | Status |
|---|---|
| 1. In-memory token (Angular) | Implemented in `develop`, pending deployment |
| 2. Interceptor only towards `cv-server` | Implemented in `develop`, pending deployment |
| 3. Token validation in `cv-server` | Implemented in `develop`, pending deployment |
| 4. `(iss, sub)` to internal identifier | Pending |
| 5. Data layer with an owner and 404 for another user's resource | Pending |
| 6. Invitation | Implemented with an `INVITADAS` (invited users) list by email. The link to `(iss, sub)` stays pending until Neon exists |
| 7. CORS without a wildcard | Implemented in `develop`, pending deployment |

The Angular guard protects only the screens with real data. The public demo remains
open.

The public form routes were removed or closed in `cv-server` (`develop`) on 7 October
2026. Verification in production is pending until it is deployed.

---

## Context

`cv-server` does not yet identify the people who call it: until now only our own
processes used it. The system is opening up to other people, by invitation, and that
requires knowing who asks for what and that nobody sees another person's data.

As a preliminary step, on 2 October 2026 the two routes that could not stay open were
closed: `/debug` was removed and `/usuarios` requires a machine key.

The protocol was already decided: OIDC with OAuth2, a guard and an interceptor in
Angular. Storing passwords in `cv-server` is ruled out. What was missing was the
provider, and the criterion is that it be **free and add no services**
([ADR-002](ADR-002-where-postgres-lives.md)).

On 2 October 2026 the official pages were checked:

- **Google** issues a standard ID token, verifiable by JWKS, with a stable `sub`. But
  **it does not offer a browser application the code flow with PKCE and no secret**:
  the exchange happens in a backend, and the browser receives no refresh token.
- **Auth0** does offer that flow and 25,000 free users. But it **deletes the tenant
  after 150 days without activity**, with no way to recover it.
- **Supabase Auth** issues tokens verifiable by JWKS, but lives inside a project that
  is paused after 7 days.

## Decision

**Google as a direct OIDC provider. `cv-server` validates the token on every request.**

1. Angular obtains the token from Google and keeps it **in memory**, never in
   `localStorage`.
2. An interceptor adds it only to requests addressed to `cv-server`. The token never
   enters a prompt and never travels to a model provider.
3. `cv-server` checks the signature by JWKS, that `iss` is in the configured list
   (Google issues `accounts.google.com` and `https://accounts.google.com`), `aud`,
   `exp` and `email_verified`. The algorithm is a constant in the code (RS256) and is
   never read from the token. The JWKS keys are cached for 3600 s; an unknown `kid`
   triggers a new download, at most every 300 s.
4. `(iss, sub)` is translated to an internal identifier. **The user comes from the
   token and from nowhere else**: whatever the request body says is ignored.
5. Every query on owned data goes through a layer that requires that identifier.
   A resource belonging to someone else answers 404. There is one test per route in
   which one user asks for another user's resource and does not get it.
6. **Invitation.** People are invited by email. On first access, with
   `email_verified`, that email is linked to `(iss, sub)`, and from then on only `sub`
   counts. A valid token from someone who was not invited receives 403.
7. **CORS.** `cv-server` accepts only the origins of the panel and of development,
   with no wildcard.

The issuer, the JWKS address and the audience are configuration. **The code does not
name Google**: changing provider means changing the configuration and the input
adapter in Angular. The algorithm (RS256) is the exception: it is a constant.

`GET /yo` returns the identity of whoever signs in. It answers 401 if the token is
missing or invalid, 403 if it is valid but the person is not invited, and 503 if the
provider fails or configuration is missing.

## Why not Auth0

It is the textbook flow and the closest to what a large company uses. But it adds a
service, and its free plan deletes the tenant after 150 days of silence, which is
what happens to a personal project that goes months without use.

It is back on the table if signing in without a Google account becomes necessary.

## Why not Supabase Auth

It does not breach A6 to the letter: the browser would talk to an identity provider,
not to the database. But it ties identity to a project that gets paused.

## Consequences

**Accepted:**

- Only people with a Google account can sign in.
- No refresh token in the browser: the session is renewed by requesting another token
  from Google, in principle without the user noticing. This has to be measured.
- The ID token is used as a credential against our own API. That is not canonical,
  and that is known. It is defensible because `aud` is the client identifier of the
  brand's applications, and the backend is ours.
- With the token in memory, each application (jobs, training) requests its own token
  from Google. Signing in once and having it work everywhere comes with the evolution
  described below.

**Gained:**

- No new service, no plan that expires, no password to look after.
- What is learned carries over: guard, interceptor, in-memory token and JWKS
  validation are the same against any provider.

## Email links and n8n calls

Today the approve and discard links are GET requests with side effects, to n8n
webhooks protected only by an unpredictable route (ADR-001). Email filters open links
on their own.

- They will carry a **token signed by `cv-server`**, single-purpose and with an
  expiry. The link opens a panel page that shows the offer and a button; the button
  does a POST to `cv-server`, which validates the token. **Repeating the POST does
  not repeat the action.**
- Whether that page asks for sign-in, or whether the token is enough as
  authorization, is **still to be decided**.
- `cv-server` becomes **the only caller of n8n**. On that day ADR-001 is superseded
  entirely.
- Calls from n8n to `cv-server` carry a **machine key** in the `X-Clave-Maquina`
  header, distinct from the identity of people. ADR-001 measured that header
  authentication failed on the webhooks n8n **receives**. Here n8n **sends** the
  header, which is a different case, but it has to be measured and then checked that
  the workflow's Groq credential is still alive.
- **Measured on 4 October 2026.** n8n sends `X-Clave-Maquina` with its own Header Auth
  credential ("cv-server clave de maquina") in the `/generar-cv` and `/generar-carta`
  nodes; the Groq credential stays in its node, untouched. `cv-server` requires the
  key on `/registro`, `/usuarios`, `/generar-cv`, `/generar-carta`, `/crear-oferta`
  and `/buscar-ofertas-reales`: without it, it answers 401 and does not call the
  model. Importing a workflow over an existing one did not preserve the credential:
  it was set by hand.

## When to revisit

When the panel is published on its subdomain ([ADR-006](ADR-006-subdomains.md)). Panel
and API share a domain, and that allows `cv-server` to do the exchange and the session
to travel in a cookie that no script can read. If that step is taken, item 3 changes
(the JWKS is validated only on sign-in) and CSRF protection appears: it will be a new
ADR that supersedes this one.

## Amendment 2026-10: invitations move to the database

Invitations move from the `INVITADAS` environment variable to the `invitaciones` table.
`email_verified` stays required (and is tested). `INVITADAS` is kept only as a bootstrap
fallback while no `DATABASE_URL` is configured.

- **Identity.** A user is the verified Google `(iss, sub)` pair, mapped to an internal
  `usuarios.id`. The email is only the key of an invitation and a label in
  `usuario_emails`. One user can own several mailboxes; a mailbox belongs to one user.
- **Linking.** On first sign-in, an unused, unexpired invitation for the verified email
  creates the user and is consumed in the same transaction. A mailbox held by another
  `(iss, sub)` is never merged, and no invitation means denial with no writes.
- **Two modes, for a safe rollout.** Without `DATABASE_URL` (production when this was
  written) the `INVITADAS` list decides, `/yo` works as before and no database is
  touched. With `DATABASE_URL`, the table decides; `INVITADAS` only counts when
  `INVITADAS_COMO_RESPALDO=1`, a temporary fallback to be removed once the table is the
  only source. `/health` never touches the database.
- **Layering.** `autenticacion.py` stays free of database code: the server injects an
  `autorizar` callback.
- **Tooling.** `scripts/invitar.py` creates invitations with a mandatory expiry.

---

**Sources, consulted on 2 Oct 2026:**
developers.google.com/identity/openid-connect/openid-connect ·
developers.google.com/identity/oauth2/web/guides/use-code-model ·
developers.google.com/identity/gsi/web/guides/verify-google-id-token ·
auth0.com/pricing · supabase.com/docs/guides/auth/jwts

**Related:** [ADR-001](ADR-001-webhook-protection.md) ·
[ADR-004](ADR-004-each-user-brings-their-own-ai-key.md) ·
`cv-server/tests/test_rutas_cerradas.py`
