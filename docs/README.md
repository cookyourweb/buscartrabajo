# Documentation

This folder is split by **what you can do with each thing**, not by topic. The
distinction matters: documents that describe today's system live here alongside others
that are the record of why it came to be this way, and mixing them makes it impossible
to trust either.

| Folder | What it is | Current? |
|---|---|---|
| [`adr/`](adr/) | Architecture decisions: what was decided, what was discarded and why | Yes. An ADR is only superseded by another ADR |
| [`runbooks/`](runbooks/) | What to do when something happens. Read with the system broken | Yes |
| [`reference/`](reference/) | How the system works today and which rules apply | Yes |
| [`design/`](design/) | What is going to be built and does not exist yet: designs, tokens and open decisions | Yes, until it is built. Then it moves to `reference/` |
| [`archive/`](archive/) | Dated record: proposals, audits and fixes already applied. Kept in their original Spanish | **No.** Kept for the why, not for the what |

## How to read it

**If you are here to understand the system**, start with the [README](../README.md),
continue with [how an offer enters](reference/10-HOW-AN-OFFER-ENTERS-2026-07-23.md) and
finish at [ADR-001](adr/ADR-001-webhook-protection.md), which is the decision that
constrains the rest the most.

**If something is broken**, go straight to `runbooks/`.

**If you are wondering why something is the way it is**, `archive/`. It is dated on
purpose: a document from July describes July, and that is exactly what is asked of it.

## The rules are not here

The project rules live in [`CONTRIBUTING.md`](../CONTRIBUTING.md), at the root. What is
in `docs/` has to be looked up, and that is why it gets forgotten.
