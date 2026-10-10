# Jobs panel in Angular: design

Date: 2026-09-05
Status: proposal, pending approval
Decisions by: Verónica Serna

## 1. What this is

The face of a system that already works.

Today the system exists and is in production, but scattered: an n8n workflow gathers
offers, `cv-server` generates the tailored CV, nineteen Python scripts do the rest and
Notion serves as both storage and interface. It is operated from the command line.

This project builds the web interface for that system. It does not invent a new
product: it unifies the one that already exists.

## 2. Scope: multi-user by design, one user today

The system **is multi-user from day one**. What happens today is that there is only
one row in the users table.

This is not a wording nuance. It means there is no "when we open up multi-user": there
are no two modes, no pending migration and no conditionals scattered through the code.
There is a multi-user system with one user.

Entering the design from now:

| Included from day one | Why |
|---|---|
| `user_id` on every table | Adding it later forces a data migration and touching every query |
| Every query filters by user | Isolation cannot be retrofitted. Forget one query and someone else's data leaks |
| Real authentication, with identity coming from a token | It is the hole that already exists in `cv-server` and in `tu-vuelta-al-sol`. It is born right or born wrong |
| Per-user spending control | Model calls are the only variable cost. Without a per-user limit it cannot be opened to anyone |
| The data layer behind an interface | Enables the public demo and enables testing without a network |

Only what is product, and can be added without touching the architecture, stays out:
sign-up and invitation screens, fine-grained roles and permissions, an admin panel and
billing.

## 3. Goals

- Replace the command line and Notion as the daily working interface.
- Be defensible public code: a tech lead opens the repo and sees judgment.
- Turn Angular and Figma, today declared gaps, into real experience under the CV
  rule: a technology goes in only if it is genuinely held.

## 4. Two deployments

| | Data | Where | For whom |
|---|---|---|---|
| **Real** | Verónica's own | Local or private | Her, daily |
| **Demo** | Sample data, bundled in the front end itself | Public, static | Whoever opens the link |

The demo touches neither backend nor database. It is not a patch for any free plan: a
showcase must load instantly and cannot depend on a service being alive.

This is not solved with an `if`. The application depends on a data interface and one
implementation or another is injected.

## 5. Decisions made

| Decision | Choice | Reason |
|---|---|---|
| Framework | Angular latest version, standalone and signals | A gap to cover; decision of 22 Jul 2026 |
| Database | Postgres | The data is relational and constraints are needed |
| Who talks to the database | Only the backend | The browser never touches the database or sees a third-party token |
| Backend | `cv-server`, which already exists | It already works, with guardrails and tests. No services are added |
| Authentication | OIDC, with `cv-server` validating the token on every request | The transferable part is the protocol, not the provider |
| Intake | n8n, unchanged | It is in production |
| Notion | Only as an n8n input | It stops being storage and stops being an interface |
| Design | Figma with Variables, before the code | It is public evidence, just like Angular |

### Why Notion stops being the database

Notion is a tool for human work with an API on top. It has no constraints, no
referential integrity and no transactions, and its API runs at about three requests
per second.

It has already failed because of this, and it is documented in the repository itself.
From the header of `cv-server/tests/test_usuario_multicuenta.py`: since it was not
possible to declare that a user is unique, two records had to be created for the same
person, both drifted and the CV came out with the wrong header. A `UNIQUE` would have
prevented it.

## 6. Architecture

```
Angular (browser)
  |
  '-- cv-server (FastAPI)
        |
        |-- Postgres
        '-- Drive, language models, templates

n8n, outside the application: gathers offers.
  In slice 1 it keeps writing to Notion and a sync carries them
  to the database. Having it write straight to Postgres is separate work.
```

Rules that hold this up:

- The browser never sees a Notion, Drive or model token.
- The application does not talk to Notion. Ever.
- `cv-server` stops trusting the email that arrives in the request body.

## 7. Data model

Five tables. All with `user_id`, even though today there is only one value.

- `profiles`: one row per person.
- `profile_emails`: a person's mailboxes. It solves the case of the two emails without
  duplicating the person. `UNIQUE(email)`.
- `offers`: offers gathered. Company, job title, description, source, date.
- `applications`: the relationship between a person and an offer. Status, sent date,
  channel. Tracking lives here.
- `documents`: generated CVs and cover letters. They point to an `application` and
  store the Drive link and the guardrail warnings.

## 8. Document generation: in the background

Generating a CV calls a language model and can take quite a few seconds. A synchronous
request leaves the browser waiting and any proxy can cut it off.

Generation is queued and the front end polls the status until it finishes. It is built
this way from the start: it is what holds up once there is more than one user, and
changing it later forces the whole screen to be redone.

## 9. Design system

It is born from the CookYourWeb brand, which exists but is disconnected from the code.

Starting point verified in `cookyourwebai`: four brand colors in `tailwind.config.ts`
(`#32e2ec`, `#ec32c7`, `#8f32ec`, `#3fec71`), while the semantic tokens in `index.css`
still use the template's grays. The neons are repeated by hand up to eight times and
there is a `#BB60D1` that is not declared in any palette.

The path, in order:

1. The four colors enter Figma as Variables, with a full scale. A brand color is a
   ramp, not a value.
2. Contrasts are measured. The neons are designed for a dark background; the cyan and
   the green do not reach 4.5:1 on white. Each token declares which background it
   lives on.
3. The Variables are connected to the semantic tokens, keeping the names that already
   exist: `primary`, `muted`, `destructive`, `border`, `ring`. No names are invented.
4. The tokens come down to Angular as CSS custom properties. That is the bridge. No
   code is exported from Figma.
5. Each Figma component, with its variants, corresponds to a standalone Angular
   component where each variant is a typed `input`.

The design system is built for the panel. `cookyourweb.es` is migrated afterwards,
which is why the token names are kept.

## 10. What happens to Notion

Notion is used today as a visual CRM and contains three distinct domains: **job
offers**, **CookYourWeb leads** and **invoices**. Only the first one migrates.

The other two belong to another activity and stay where they are. Two businesses are
not mixed in one database just because they happen to share a tool.

And they stay because there Notion is the right tool: few records, human editing, no
concurrency and no critical integrity. The problem was never Notion; it was asking it
to act as the database of an automated system.

Notion does not disappear. It stops being the offers CRM.

### The rule that is not broken

**At any moment, writes go to a single place.** Never two. The day n8n writes to
Notion and the panel writes to Postgres, the data drifts.

This is not a theoretical precaution: it has already happened. Two records for the
same person ended up different and the CV came out with the wrong header.

### Transition in two phases

**Phase 1, while slice 1 is being built.**
Notion remains the source of truth. n8n writes there. A one-way sync dumps into
Postgres and the panel only reads. If the panel fails, nothing is lost and there is no
need to stop working.

**Phase 2, with the status screens of slice 2.**
It is reversed. n8n starts writing against the API, Postgres is the source of truth
and the Notion offers database is frozen as read-only. It becomes history, not a tool.

### Migrating the history

It is migrated in full: offers and applications, with dates, statuses and links to the
generated documents. It is the real record of the search and it is not thrown away.

The migration is also the moment to fix what is already known to be dirty, such as
discarded offers whose status was never updated.

### Where the design system lives

Neither in Notion nor in the CRM. Each piece in the place that suits it:

| Piece | Where | Why |
|---|---|---|
| The tokens | Figma, as Variables | They have types, scales and modes, and can be extracted by API |
| The why behind each decision | The repository | Project rules do not live in a vendor's tool, and a public repository does get opened |
| The values the application consumes | The code, as custom properties | |

If the tokens live in a document, someone copies them by hand and a color nobody knows
the origin of appears again. Which is the problem this work fixes.

## 11. Delivery by slices

Complete vertical slices, not layers.

**Slice 1.** See my offers, open one, generate CV and cover letter, download. It
touches the data layer, the design system and `cv-server`. It is the showcase.

**Slice 2.** Mark as applied, statuses and tracking. It replaces Notion as the
interface.

**Slice 3.** Interview preparation. It is the only one with nothing built behind it.

## 12. What is out of scope

- **Applying automatically.** Every portal is different, LinkedIn offers no API for it
  and automating it leads to fragile scraping that puts the account at risk. The panel
  opens the offer and the person records in one click that they applied.
- Sign-up and invitation screens, fine-grained roles, an admin panel and billing. It
  is product, and it is added without touching the architecture.
- Migrating `cookyourweb.es` to the new design system.
- Replacing n8n.
- Microservices, orchestrated containers and multi-region. A monolith that is well
  separated internally holds up much more than people think.

## 13. Risks

| Risk | Mitigation |
|---|---|
| The full scope is six subsystems | It is delivered by slices; slice 1 is worth it on its own |
| Migrating from Notion to Postgres can misalign n8n | n8n keeps writing to Notion in slice 1 |
| The neons fail contrast | It is measured before designing and documented |
| Learning Angular and Figma at the same time delays the job search | Slice 1 is small and publishable |
| "We will change it later" on the schema | That is why `user_id` and per-user filtering go in from day one |
