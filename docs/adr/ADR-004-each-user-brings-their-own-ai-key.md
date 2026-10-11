# ADR-004. Each user brings their own AI key

**Date:** 2 Oct 2026 · **Status:** accepted on 3 Oct 2026, not implemented (see "What is missing for this to be true"), when deciding how offer search fits in

---

## Context

Generating CVs and cover letters, and chatting with the interview advisor, calls a
language model. It is the only real variable cost of the system (section D of the
[board](../design/2026-09-05-architecture-decisions.md)): it grows with every user
and every use.

The system is opening up to other people by invitation, and the criterion is that it
must **cost the owner nothing** ([ADR-002](ADR-002-where-postgres-lives.md)). Two
ways remained for the person using it to pay for it:

- **Charge them the cost.** This requires a payment gateway, issuing an invoice for
  each charge and handling VAT. For a few cents of model usage, the paperwork costs
  more than the service.
- **Each user uses their own key** from the provider. Nobody charges anybody.

### What it costs, measured on 2 October 2026

With the production prompt and model (`claude-sonnet-4-6`, USD 3 per million input
tokens and 15 per million output tokens), on three real offers:

| | Input tokens | Output tokens | Cost |
|---|---|---|---|
| CV | 9,600 to 10,100 | 1,400 to 1,600 | about USD 0.05 |
| Cover letter | 3,450 to 3,850 | 115 to 140 | about USD 0.013 |

An approved offer, with CV and cover letter, costs **about 6 US cents**.

### What does not exist: free and good

The same prompt was measured against Groq on its free plan (`gpt-oss-120b`). Its limit
is 8,000 tokens per minute and the CV prompt already takes about 7,600: **it did not
generate any of the three real offers**. It rejected them for size.

The Gemini API terms do not allow offering its free plan to users in the European
Economic Area, and Anthropic has no free API plan.

## Decision

**Each user connects their own AI key** (BYOK, *bring your own key*). What is
generated for them is charged to their account at the provider.

**Only models from a list of supported models are accepted.** A model enters the list
if it genuinely generates the cases in `cv-server/evaluacion.py` and passes them, with
the truthfulness guardrails (figures, technologies, skills, experience (in the cover
letter) and headline) green. Those guardrails compare the output against the Master CV
and do not depend on the model: they work the same for any of them. Today the list is
`claude-sonnet-4-6`.

**What the user sees:**

1. At sign-up, a step to connect their AI, with a short guide that recommends a key
   dedicated to this system with a spending cap.
2. When the key is pasted, the system checks that it exists and that it gives access
   to the supported model, **before** storing it. The balance cannot be known in
   advance: it is discovered on the first generation.
3. Afterwards they only see the last characters of the key. They can change or delete
   it.
4. Offers are visible and ordered without a key: the order is computed with rules,
   without an AI model.
5. Each document shows which model wrote it and how many tokens it used.

**How the key is handled:**

- It is stored **encrypted** (AES-256-GCM or Fernet), with the user identifier and the
  provider as associated data, so that a ciphertext cannot be moved to another user's
  row. The master key lives in the `cv-server` environment, never in the database or
  in the repository, and never in database backups.
- Each key stores the version of the master key it was encrypted with. Rotating means
  decrypting with the old one and encrypting with the new one. If the master key is
  lost, the keys cannot be recovered: each user pastes theirs again.
- It travels from the browser once, when it is saved, and **never comes back** to the
  panel.
- Only `cv-server` decrypts it, **on every call**: never through an environment
  variable and never in a client shared between users.
- **It does not appear in the logs.** It goes in a header, never in a URL, and
  provider errors are logged by type and code, never with their message. This is
  enforced by `cv-server/tests/test_claves_fuera_de_los_registros.py`.
- When a user leaves, the encrypted key is deleted. Database backups expire on their
  own, and the user is advised to revoke the key at their provider, because only they
  can do so.

**When the key fails:**

- **It never falls back to one of the owner's keys.** The owner would not pay, and the
  CV would not end up at a provider the user did not choose.
- Rate limit or provider down: retry with backoff, with the same key.
- Invalid, revoked or expired key, no balance, or spending cap reached: no retry. The
  key is marked "needs attention" and the panel explains it in plain language.

**Offer search (decided on 3 October 2026).** The bot searches once a day and stores a
**shared pool** of offers for all users. The order of that pool for each user is
computed **with rules, without an AI model**, from the fields of their profile (role,
technologies, work mode, location and salary). This way nobody pays for ordering
offers, no user's profile passes through another person's AI account, and the bot
scales the same with one user as with fifty. That is why sign-up has to collect the
profile in structured fields, not in free text.

The AI model is used only where it is truly needed: the CV, the cover letter and the
advisor, always with the user's key.

**Scheduled processes.** If in the future any scheduled process uses the model on
behalf of a user, it needs their explicit and separate consent, a daily cap of the
system's own, and an automatic pause after several failures in a row.

**Limits.** An **economic** quota is not needed: the money belongs to each user. What
is kept is not repeating a generation that has already been done, and a usage limit
per user, so that a system error does not spend from anyone's account.

## What is missing for this to be true

Today `cv-server` talks to three providers, but with the owner's keys, read from the
environment and through a shared client, with a cascade that falls from one provider
to the next. BYOK forces this to change before the system is opened to anyone.

And the n8n bot today calls the model on its own, with the owner's key, to filter and
choose offers (the `Groq - Generar Ofertas` node); the CV and the cover letter are
already written by `cv-server`. With the shared pool it stops doing so: n8n searches
and stores the offer through `cv-server`, with the machine key, and `cv-server`
computes the order with rules. The base is in `real_jobs._ranking_fallback`, which
today only scores by technologies: role, work mode, location and salary must be added
to it.

## Consequences

**Accepted:**

- With rules, offer selection loses the filters that the model applies today by
  reading the description: that frontend or AI is the main job and the real seniority
  of the position. This is compensated with a richer profile at sign-up.
- With a shared pool, the state of an offer (approved, discarded) stops living on the
  offer and becomes per user: shared offers and per-user applications, as the data
  model foresees.

- Connecting a key is costly for non-technical people. The sign-up guide has to solve
  that.
- Looking after third-party keys is one more sensitive piece of data.
- Today there is no free option that meets the quality bar.

**Gained:**

- Zero cost for the owner, with no gateway, no invoices and no VAT.
- Each user controls their spending with their provider's cap, if the provider allows
  it.
- No model gets in by intuition: it gets in if it passes the quality tests.

## When to revisit

- If there are people willing to pay for the service: then a real paid plan is
  designed, not a pass-through of cost.
- If the CV prompt shrinks enough for a free model to fit and pass the evaluation.

## Amendment 2026-10: owner-paid CV extraction at sign-up

One exception to "each user brings their own key": reading the CV at sign-up and proposing
the profile fields is paid by the owner, once per user. Asking a newcomer to find, create
and paste an API key before she has seen anything of the service would lose most of the
people the invitation was meant for. Everything else stays BYOK.

- **One per user.** Each user gets a single extraction. A second request is refused and the
  panel shows the manual form. If the whole provider chain fails, the attempt is NOT used:
  the failed call is recorded, it still counts toward the cap, and she can try again later.
- **Model.** Claude Sonnet, the same model that writes her production CVs. Cheaper models gave
  visibly poorer results on 2 Oct 2026. The extraction has its own provider chain: Claude
  first, Groq on a provider failure only, and never any other provider or the general
  generation cascade. Both calls are capped at 1,200 output tokens (one constant shared with
  the cost estimate), time out after 30 seconds and are not retried. One extraction is bounded
  to 0.05 USD by capping the prompt size and the output tokens.
- **Dedicated key.** The Claude call uses a key reserved for sign-up extraction
  (`ANTHROPIC_CLAVE_ALTA`, in its own workspace with its own monthly limit), never the key
  used for generation. Without it the extraction is unavailable: nothing is reserved, no
  provider is called and the panel shows the manual form.
- **Cap with a pessimistic reservation.** The month's spend, in UTC, may not pass 5 EUR. Before
  any call a row is reserved with the worst case (input at 3 characters per token, the maximum
  output, primary and fallback both billed, plus a margin), under a database lock so
  concurrent requests cannot jointly pass the cap. A completed call replaces the estimate with
  its real cost; a failed or interrupted one keeps the estimate. Rows of deleted accounts are
  kept without a user, so the cap cannot be reset by deleting an account.
- **Kill switch.** `EXTRACCION_ACTIVA=false` in the environment is a hard off, and the
  `ajustes.extraccion_activa` row (flipped with `PUT /ajustes/extraccion`, machine key) turns
  it on or off without a redeploy. Both fail closed, and the switch is checked before
  anything else: while it is off, nobody is asked for consent or a CV.
- **Explicit consent.** The CV goes to an external AI provider only after a stored, versioned
  consent whose text names every provider the CV may reach (Anthropic and Groq). A new
  version of the text requires a new consent.
- **The interview advisor and any later use of a model remain BYOK.** Generating CVs and
  cover letters no longer is: see the amendment below.

Revisit if the monthly spend regularly approaches the cap, or if the number of sign-ups makes
the owner-paid step more than a small, bounded cost.

## Amendment 2026-10-11: owner-paid generation quota

Asking non-technical users to create a developer account and paste a key proved to be the
main obstacle, so generating CVs and cover letters for invited users is also paid by the
owner, within hard limits: 8 applications per user per month (a CV counts 0.7, a letter 0.3),
a global cap of 20 EUR per month for generation, a reservation made before any model call and
an email alarm at 70 % of the cap. When the quota runs out the panel says when it renews and
asks whether she would want paid packs or access through her academy. Paid packs, sold through
a merchant of record, only come if real demand shows up. The details, numbers and triggers are
in `cv-server/docs/ADR-010-owner-paid-generation-quota.md`.

---

**Sources, consulted on 2 Oct 2026:** platform.claude.com/docs/en/about-claude/pricing ·
ai.google.dev/gemini-api/terms · console.groq.com/docs/rate-limits ·
ai.google.dev/gemini-api/docs/api-key

**Related:** [ADR-003](ADR-003-authentication.md) · `cv-server/evaluacion.py` ·
`cv-server/guardrails.py` · [data model](../design/2026-09-07-data-model.md)
