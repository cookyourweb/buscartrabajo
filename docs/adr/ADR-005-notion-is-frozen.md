# ADR-005. Notion is frozen on migration day

**Date:** 2 Oct 2026 · **Status:** accepted

---

## Context

Today offers and applications live in a Notion database, written to by the n8n bot,
`cv-server` and the owner by hand. The destination is Postgres
([ADR-002](ADR-002-where-postgres-lives.md)), with the Angular panel as the place to
work.

Two places where the same thing is written is the surest way for data to get
disordered: something is updated in one and not in the other, and it stops being clear
which is the right one. It has already happened with two records of the same person: a
CV came out with the wrong header ([data model](../design/2026-09-07-data-model.md)).

There were three options: freeze Notion, keep it as a synchronized copy, or remove it.

## Decision

**On migration day, Notion becomes read-only.** Everything new is written to Postgres
and worked on from the panel. Notion remains as an archive of what came before.

- **Before migrating**, a complete copy of the database is made and it is checked that
  the number of cards copied matches the number in Notion.
- **"Read-only" is a control, not a promise.** The Notion integration is left with
  read permission only, and the write credential is removed from n8n and from
  `cv-server`.
- **From that day, n8n writes to Postgres through `cv-server`,** with the machine key
  ([ADR-003](ADR-003-authentication.md)). Never directly to the database.

## Until the migration

Notion is the source of truth. If the panel offers "Delete" before migrating, the card
goes to the Notion trash, and beforehand its fingerprint (link, and company with job
title) is stored outside Notion, so that the bot does not bring that offer back again.

## Consequences

**Accepted:**

- Whatever is in Notion after the migration is not visible in the panel.

**Gained:**

- A single place where the truth lives.
- The bot stops writing to Notion, and with it the free-plan block limit for
  workspaces with several members stops being a problem.

## When to revisit

Only if writing outside the panel became necessary again. The default answer is to
export from Postgres, not to go back to writing in two places.

---

**Sources, consulted on 2 Oct 2026:** developers.notion.com/reference/capabilities ·
notion.com/pricing

**Related:** [ADR-002](ADR-002-where-postgres-lives.md) ·
[ADR-003](ADR-003-authentication.md) · [data model](../design/2026-09-07-data-model.md)
