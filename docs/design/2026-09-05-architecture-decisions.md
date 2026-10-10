# Architecture decisions: initial board

Date: 2026-09-05
Status: listed for decision. C2 and C4 closed on 2026-10-02 in
[ADR-002](../adr/ADR-002-where-postgres-lives.md) and [ADR-003](../adr/ADR-003-authentication.md).

The criteria that rule, in this order:

1. **The destination rules, not today's free plan.** The system is designed for where
   we want to end up, and today we pick what does not force a rewrite to get there.
   Anything that is disposable is marked as such.
2. **Cost close to zero while there is a single user.**
3. **Fast load.** Whoever opens the link judges it within three seconds.
4. **What is learned must be transferable** to a company with a large team.

Order revised on 2026-10-02: zero cost becomes the first criterion. See
[ADR-002](../adr/ADR-002-where-postgres-lives.md).

Scope: **the system is designed as multi-user from day one**, even though a single
person uses it today. There is no "when we open up multi-user": there is a multi-user
system with one user.

The three groups below separate what is already closed, what is decided by default
without discussion, and what really has to be talked through.

---

## A. Already closed

| # | Decision | Choice |
|---|---|---|
| A1 | Front-end framework | Angular latest version, standalone |
| A2 | Data model | Relational, Postgres |
| A3 | CV and cover letter generation | `cv-server`, which already exists |
| A4 | Offer intake | n8n, unchanged |
| A5 | Prior design | Figma with Variables, and our own design system |
| A6 | The browser does not talk to the database | Angular calls `cv-server`; only the backend touches Postgres |

A6 is today's change. It removes the Backend-as-a-Service pattern, which is not used
in large teams, and turns the database provider into a replaceable detail.

---

## B. Decided by default

No debate unless someone objects. All of them go in the same direction: less
JavaScript, fewer servers, a smaller bill.

| # | Decision | Choice | Reason |
|---|---|---|---|
| B1 | Rendering | Client SPA, no SSR | The panel lives behind login. SSR adds nothing and forces paying for a Node server |
| B2 | Front-end hosting | Static on a CDN | Zero cost and first load from the edge. A static front end has no server to maintain |
| B3 | State | Native signals | NgRx is overkill at this size and adds weight and ceremony |
| B4 | Change detection | No zone.js | Less startup JavaScript and less work per interaction |
| B5 | Code loading | Lazy loading per route and deferred blocks | Only what is visible is downloaded |
| B6 | Component library | None. Own components on top of the tokens | A library has weight and also imposes its aesthetic, which is exactly what we want to show we can build |
| B7 | Styles | CSS with custom properties | The tokens are the contract. No build dependency |
| B8 | API contract | REST | GraphQL adds a server, cache and complexity that do not pay for themselves here |
| B9 | Forms | Typed reactive forms | |
| B10 | Database migrations | Alembic | The backend is already Python |
| B11 | Fonts | Hosted with the app | Avoids an extra connection to a third party and the text jump on load |
| B12 | Tests | Unit tests in the front end, Playwright on the main flow | |

---

## C. To be talked through

These four change the outcome. The rest are details.

### C1. Backend availability (decided)

In the target architecture the backend is always available. That is a requirement and
it is not negotiated with the hosting plan.

**Decided, on its own merits**: the public demo does not depend on the backend. A
showcase must load instantly and cannot go down because a service does not respond.

That `cv-server` runs today on a free plan that goes to sleep is an operational matter
of the moment, not a design constraint. It is solved by changing plan the day it is
needed.

### C2. Where Postgres lives

With A6, the provider is replaceable. But the free plan matters: some pause projects
that go days without activity, and a showcase goes weeks without visits.

What each plan does after inactivity, and how long it takes to come back, has to be
checked plan by plan and not from memory. Candidates: Supabase, Neon, Render.

If the public demo does not touch the database (see C1), this risk drops a lot.

### C3. CV generation is slow, because it calls a model (decided)

An LLM call can take quite a few seconds. If the request is synchronous, the browser
sits waiting and any proxy can cut it off.

**Decided**: background work that the front end polls until it finishes. It is what
holds up once there is more than one user, and changing it later forces the whole
screen to be redone.

### C4. Authentication: which provider and which protocol

The protocol is the transferable part: OIDC with OAuth2, a guard and an interceptor in
Angular. That works the same against any identity provider, including a large
company's.

What remains to be decided is who to authenticate against and, above all, that
`cv-server` validates the token on every request and stops trusting the email that
arrives in the body.

---

## D. Cost, which is criterion one

| Item | How it ends up at zero |
|---|---|
| Front end | Static on a CDN |
| Backend | A single service, the one that already exists. No more are added |
| Database | Free plan, pending C2 |
| Model calls | The only real variable cost. The number a user can trigger has to be limited, and a generation already done must not be repeated. Since 2026-10-02 each user pays with their own key: [ADR-004](../adr/ADR-004-each-user-brings-their-own-ai-key.md) |
| Public demo | No backend and no database, if C1 is resolved that way |

The rule: **every new service added has to be justified.** One service more is one
bill more and one more thing that can go down during an interview.
