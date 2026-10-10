# Rules for the open questions in application forms

**31 Aug 2026** · They came out of correcting the answer to a vacation-rental software form eleven times.
It is not theory: every rule comes from a draft that did not work.

**Related:** `16-COVER-LETTER-RULES.md` (the cover letter), `18-CV-ADAPTATION-RULES.md` (the CV).
This document covers the **open questions in ATS forms**, which neither of the other two covered.

---

## What they are really evaluating

It is not whether you can write prompts. They are separating two profiles:

| Profile A · AI integrator | Profile B · AI Engineer |
|---|---|
| *"I connected GPT, built a RAG, tuned the prompt and it worked pretty well."* | *"I have a probabilistic system in production. I know how to define what failing means, how to detect it, measure it and change the architecture to reduce that class of error."* |

They are looking for B. The **five signals** they track, in this order:

1. Has this person put a **real** LLM system **into production**?
2. Do they understand that it can fail **even when the answer looks good**?
3. Do they have an evaluation strategy **and can they say how they know it works NOW**?
4. Have they discovered a **real failure mode, with data**?
5. **What changed** as a result?

Signal 3 is the one most often forgotten. Describing the new architecture is not describing the guarantee.

---

## The eight writing rules

### 1. Start with the PROBLEM, with its headings and in their order

If the question asks for `Problem, Evaluation Strategy, Critical Failure Mode, Impact`,
the answer carries those four headings, in capitals, in that order, separated by
blank lines. **Scannable.** Without headings the good material arrives late and gets lost.

### 2. Do not say what you use the tool for: say how you work

Saying that `cv-server` is "an application for finding a job" places you as an
unemployed candidate before they read you. The system is the same; what changes is where
it is told from.

### 3. Show the loop, not a list of achievements

```
Build
  then observe failures
  then create evaluation cases
  then measure
  then find failure patterns
  then improve context / retrieval / prompts
  then repeat
```

NOT: prompt, "looks good!", production.

### 4. Professional vocabulary, human voice

The difference **is not in the technical vocabulary**. It is in the connectors.

| Sounds like a report | Sounds like a person |
|---|---|
| *"which created a specific reliability problem"* | *"and that is where the real difficulty sits"* |
| *"The challenge was therefore not simply generating good text"* | *"So the hard part was never writing good text"* |
| *"The most important failure mode I discovered was that..."* | *"The one that mattered most: ..."* |
| *"The main architectural lesson was that context injection is not evidence of context use"* | *"Context injection is not evidence of context use."* |
| *"yet every output read naturally and plausibly"* | *"and every single one read naturally"* |

**Out:** `therefore`, `moreover`, `thus`, `which created`, `the main lesson was`,
`it is worth noting that`, and nominalizations (*"the challenge was not simply generating"*
instead of *"the hard part was never writing"*).

### 5. Do not depersonalize ownership

*"That baseline was me"* is better than *"that baseline was human review"*.

"Human review" is passive: it could be an intern or a team of annotators.
*"Was me"* says that the domain expert was you, and that is what makes
everything that follows credible. For a role where you will own the evaluation,
taking ownership **is not informal**.

### 6. No absolutes you cannot back 100%

*"Tracked every change to the domain logic"* was changed to *"followed changes in the
domain logic"*. An absolute you cannot defend is a trap you set for yourself.

### 7. Get ahead of the uncomfortable question

If something is half-done, say so first. Nobody can catch you on something you declared.

> *"I did not start with a formal evaluation framework; I arrived at one by turning
> real production failures into explicit, testable criteria."*

### 8. A single hard number

The second is kept for the interview: two figures in the same text compete with each other.

| Figure | Where |
|---|---|
| **77 of 78** items with a wrongly calculated attribute, and all of them read perfectly | In the written text |
| **166 prose files** without the answer versus **14 commits** that had it | Kept for the interview |

---

## The professional narrative

Do **NOT** sell yourself as someone with five years building enterprise LLM evaluation platforms.

**DO** present as a **senior software engineer (20+ years) who has evolved towards AI Systems
Engineering and has reached the right architectural conclusions through her own experience**:
separating AI from the core, designing context explicitly, structured contracts, validating
outputs, discovering failure modes, turning observed failures into verifiable rules,
TDD in the deterministic layer.

It matches what the PPS already says: *"I am not a Data Scientist. I am not an AI researcher."*

**The real advantage of 20 years: she knows a system is not finished because a demo works.**

And there is an asymmetry in her favor: most people arrive from ML and are learning systems
engineering. She arrives from engineering and is learning AI. For a role that asks for
*evaluation, retrieval, production readiness and failure analysis*, that is the path that works.

---

## Which material to use

**The good one is `tu-vuelta-al-sol`, not `cv-server`.** A product in production with real
users since August 2025. cv-server is a tool of her own; tuvueltalsol is a product.
For an application that weighs far more. cv-server serves as an auditable public code link.

Real repo (long and not at all obvious, which is why it gets lost):
`<local-repo-path>`

The copies in `Documents/`, `Downloads/`, `n8nClaude/` and `lovable/` are **dead**.

---

## The distinction that avoids looking bad

> *"Now that I know the prompts cannot be in the project the way I had them, it probably looks bad."*

**False premise.** They are two different things:

1. **Versioned prompts inside the project: THAT IS FINE.** It is the professional thing, if they are
   versioned, have tests, are separated from the business logic and changes to them can
   be evaluated.
2. **A critical business rule that lives ONLY inside the prompt: THAT is the failure.**

The code itself shows both parts: in `cv-server` the prompts moved out of the
functions into module constants with tests, and they are still in the project. In `tu-vuelta-al-sol`,
`validarCandidataActivacion.ts` says: *"a prohibition inside the prompt is not a control"*
(in Spanish in the source: *"una prohibición dentro del prompt no es un control"*).

**The evolution is told like this:**

```
BEFORE: domain data, big context, prompt with instructions and rules, LLM, output

NOW:    deterministic domain computation, structured evidence, LLM generation,
        output validation, tests and evaluators
```

You do not say "I had the prompts wrong". You say **"I moved the responsibility to the right level
of the architecture"**.

---

## Evaluation starts in the domain

> *"First, learn the product perfectly, know what changes are being made.
> Without that it is not measurable, and there has to be a human in the loop, which is me in my first project."*

Before evaluating an LLM system you have to know **what "correct" means for that product**.
Nobody builds an evaluation pipeline on day one.

```
human understanding of the domain
  then manual evaluation
  then observed failures
  then defined failure cases
  then validators
  then automatic regression tests
```

**Careful with "human-in-the-loop":** today many people understand it as *"a human approves
every answer before it is sent"*. That is not what happened. Her role was to be the **initial oracle**
that made it possible to build the evaluation.

---

## The sentences that do the work

- *"A fluent claim that is not grounded looks exactly like one that is."*
- *"Telling the model a rule is not the same as enforcing it."*
- *"Providing context to an LLM is not sufficient evidence that the context has actually been used."*
- *"I treated it as a reliability failure of the system, not as a prompting problem."*
- *"That manual review was never meant to be the solution. It was how I found the failure modes
  and established the ground truth that later became automated checks."*
- *"I did not start with a formal evaluation framework; I arrived at one by turning real
  production failures into explicit, testable criteria."*
- **The closing:** *"Prompts guide behaviour, but critical invariants belong in the deterministic,
  observable and testable parts of the architecture."*

---

## Interview preparation

**Q: "So, did you have an evaluation framework from the beginning?"**

Do not pretend that you did.

> *"No. I started with human evaluation because I first needed to understand what correctness
> meant for the product. The important part was turning what I learned from those reviews into
> explicit failure cases and then automating them."*

**Q: "Why were you the human in the loop?"**

> *"Because I was also responsible for the product and the domain logic. I couldn't meaningfully
> evaluate the model without understanding what the underlying data meant and what the expected
> behaviour was. Once those criteria were stable, the goal was to remove myself from the critical
> path by turning them into automated checks."*

This second one is the good one. It does not say *"I reviewed because I did not trust the AI"*: it says she used
human knowledge to build the mechanism that lets the system evaluate itself.
And it ends on **"remove myself from the critical path"**, which is an engineering mindset.

---

## Method mistakes not to repeat

**Recency bias.** At the start of the day we focused on `cv-server` and ignored
`tu-vuelta-al-sol`, which was the good material, only because the latest sessions had been about
cv-server. It is the finding of `POR_QUE_FALLA_LA_IA_Y_QUE_CONTROL_SIRVE.md` applied to ourselves:
the frame is set in the first thirty seconds and is not revisited.

**A negative result on the wrong source looks like a fact.** "The evaluation layer does not exist" was
stated after searching dead copies of the repo. Before saying something does not exist,
confirm which repo has the commit history.

**Bringing in outside contrast works, but it is not accepted without checking.** When outside advice
said "don't sell yourself as a Data Scientist", it was checked against the PPS: it was already written there.
When it said "depersonalize the baseline", it was not adopted, and the reason was written down.

---

## Checklist before sending

- [ ] Does it start with the problem?
- [ ] Does it use their headings, in their order?
- [ ] Does it say how we know it works NOW?
- [ ] Is there one hard figure, and only one?
- [ ] Any absolute that cannot be sustained?
- [ ] Does it sound like a person or a report? (look for `therefore`, `the main lesson was`)
- [ ] Can every sentence be defended in an interview?
- [ ] Zero long dashes and zero arrows in what goes to the company?

---

*Origin: session of 31 August 2026, application to a vacation-rental software company (via Lever).*
