# ADR-002. Where Postgres lives

**Date:** 2 Oct 2026 · **Status:** accepted, pending confirmation of the region when the project is created · **Closes:** C2 of [architecture decisions](../design/2026-09-05-architecture-decisions.md)

---

## Context

A2 sets Postgres as the data model and A6 sets that only `cv-server` touches it.
That makes the provider replaceable, but the free plan is not a matter of
indifference: a personal project goes weeks without use, and the database cannot
disappear or fall asleep with nobody to wake it up.

**Change of criterion.** From 2 October 2026, zero cost becomes the first criterion,
ahead of "the destination rules" from the board: everything on a free plan as long as
there is no reason to pay. That the choice does not force a rewrite remains the
condition for choosing among free options.

On 2 October 2026 the official pages were checked for what each free plan does after
inactivity:

| | Render | Supabase | Neon |
|---|---|---|---|
| After inactivity | The database expires 30 days after creation, with 14 days of grace, and then **is deleted with all its data** | The project **is paused** after 7 days of low activity | Compute is suspended after 5 minutes without use |
| How it comes back | It does not | **By hand**, by logging in to the dashboard | **Automatically**, when a query arrives, in hundreds of milliseconds |
| Backups | None | Not verified | Point-in-time restore within the last 6 hours |
| Free plan | Expires | Does not expire, it pauses | Permanent, no card |

## Decision

**Neon, free plan, in the European Union, in the same region as `cv-server`.**

- `cv-server` connects through a standard connection string and migrations use
  Alembic. The code uses no Neon-specific feature.
- Database and server in the same region. Otherwise every query crosses an ocean.
- A separate Neon branch for development and tests. Nothing is tested against the
  real data.

## Why not Render

It is the only one that would not add a provider, because `cv-server` already lives
there. But a database that is deleted after 44 days is not suitable for real data,
and paying from day one goes against the cost criterion.

## Why not Supabase

It fails exactly at the risk the board pointed out. The database being paused is not
the problem. The problem is that **it does not come back by itself**: if nobody logs
in to the Supabase dashboard, the system does not start, and nobody finds out until
someone tries to use it.

Keeping it awake with a scheduled query is a workaround that adds one more piece that
can fail.

## Consequences

**Accepted:**

- A new provider. It is the only one this decision adds, and A2 already required it.
- 100 compute hours per month. If they run out, the database is suspended until the
  following month without losing data. So no process may poll the database in a
  loop, neither `cv-server` nor n8n through it.
- Restore only up to 6 hours back. A periodic copy of our own, outside the provider,
  is needed. It will be decided in a separate ADR.
- 1 GB of storage.

**Gained:**

- The database never needs anyone to wake it up by hand.
- Moving to a paid plan is not a migration: it is the same project, billed by usage
  with no monthly minimum.
- The provider remains a detail. Changing it means dumping, restoring and changing an
  environment variable.

## When to revisit

If Neon changes the terms of the free plan, if the compute hours are exceeded two
months in a row, or if `cv-server` moves to a paid plan and it becomes worthwhile to
have the database next to it.

**Pending when the project is created:** Neon offers regions in Frankfurt and London,
but its page does not clarify whether they are on the free plan. If they are not,
this decision is revisited before any personal data is stored.

---

**Sources, consulted on 2 Oct 2026:** neon.com/pricing ·
neon.com/docs/introduction/plans · neon.com/docs/introduction/scale-to-zero ·
neon.com/docs/introduction/regions · render.com/docs/free · supabase.com/pricing ·
supabase.com/docs/guides/platform/free-project-pausing

**Related:** [ADR-003](ADR-003-authentication.md) ·
[ADR-005](ADR-005-notion-is-frozen.md) · [data model](../design/2026-09-07-data-model.md)
