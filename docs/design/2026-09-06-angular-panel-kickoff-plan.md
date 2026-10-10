# Jobs panel in Angular: kickoff plan

Date: 2026-09-06
Status: prepared, not started
Continues: `2026-09-05-panel-empleo-angular-design.md`

## The map: what exists and how it coexists

There are four pieces that already exist and one that is added. None is rewritten.

| Piece | Repository | What it is | Role |
|---|---|---|---|
| Intake | `buscartrabajo` (`workflows/`) | n8n workflows | Gathers offers and writes them to Notion |
| System | `buscartrabajo` | Python and scripts | Filters, rules and documentation of decisions |
| Engine | `cv-server` | FastAPI on Render | Generates the tailored CV and cover letter |
| Brand | `cookyourwebai` | React, the agency's site | Source for the design system |
| **Face** | **`panel-empleo`** | **Angular 22** | **What is being added** |

The three roles that must not be confused:

- **`cv-server` is the engine.** The panel talks to it. It is not rewritten or
  duplicated.
- **`cookyourwebai` is the design quarry.** The ramps and the measured tokens come
  from there. The panel inherits them; the agency's website does not depend on the
  panel.
- **Angular is what is being practiced here.** It is the declared gap in the CV,
  and that is why the panel goes in its own repository: so that it can be seen.

In one sentence: the panel is the Angular face of an engine that already works,
dressed in the CookYourWeb brand.

### How they coexist

```
n8n ---- Notion
              \
               +---- cv-server (FastAPI) ---- panel-empleo (Angular)
                          |
                          +---- Postgres, Drive, models

cookyourwebai: does not take part at runtime.
               It provides the tokens, which are copied.
```

Coexistence rules:

- **The panel talks only to `cv-server`.** Never to Notion, nor Drive, nor a language
  model. The browser never sees a third-party token.
- **`buscartrabajo` does not depend on the panel.** It keeps working from the command
  line even if the panel does not exist. The panel replaces the interface, not the
  system.
- **`cookyourwebai` and the panel share tokens, not code.** They are copied, along with
  their tests. If one day maintaining them in two places hurts, they are extracted into
  a package.
- **At any moment, writes go to a single place.** The rule from the 5 September design
  still holds: in slice 1 Notion is the source of truth and the panel only reads.

## What changed since the 5 September design

The design said to take the colors to Figma, measure contrasts and then bring them down
into code. **The first two steps are already done, and in code.**

On 6 September the design system was implemented in `cookyourwebai`: the four complete
ramps, the semantic tokens pointing to them and twenty-four tests that calculate
contrast with the WCAG formula and fail if a pair drops below the minimum. It is in
production.

The tokens stopped being a proposal. Putting them into Figma now just to bring them
down again would create a second source of truth, which is exactly what that work
fixed.

**Figma comes in later, for the screens**: layout, components and variants. There it
does add value. For colors, no longer.

## Decisions made

| Decision | Choice | Reason |
|---|---|---|
| Where it lives | Its own repository, `panel-empleo` | See below |
| Framework | Angular 22, standalone and signals | Declared gap in the CV |
| Test runner | Vitest | Officially supported by Angular 22; Karma is on its way out |
| Tokens | Copied from `cookyourwebai` with their tests | They are already measured and protected |
| Figma | Later, and only for screens | The colors are already decided |

### Why a separate repository

Measured on 6 September: GitHub labels `buscartrabajo` as **Python** (79,130 bytes of
Python against 72,143 of JavaScript). Of the twenty repositories in the account,
**none is Angular**: the ones that show up as TypeScript are React.

An Angular panel buried in a subfolder of a repository that GitHub shows as Python
leaves the only Angular evidence where nobody looks. Whoever reviews a profile opens
and looks; they do not dive.

With its own repository there is its own README, TypeScript as the dominant language,
continuous integration with a single suite and independent deployment. And the nested
`package.json` disappears, which would force two different suites to run in the same
workflow.

It does not go inside `cookyourwebai`: that is the agency's site and the panel is a
different product.

### What happens with the shared design system

The tokens are copied into the panel. If one day maintaining them in two places hurts,
they are extracted into a package.

Copying twice is fine. Abstracting before the third time is premature, and creates a
dependency that has to be versioned and published for two consumers.

## Blocker before starting

**Angular 22 does not start with the installed Node.**

- It requires `^22.22.3 || ^24.15.0 || >=26.0.0`
- Installed today: `v20.19.3`, and it is the only version in `nvm`

It is solved with `nvm install 22`. It does not affect the global Node: `nvm` changes
the version per terminal, so the other projects stay the same.

## Steps, in order

1. **Node 22.** `nvm install 22`. Without this there is nothing.
2. **Create the repository** `panel-empleo`, public, and the scaffolding with `ng new`:
   standalone, signals, no server-side rendering, Vitest as the runner.
3. **Port the design system.** The four ramps and the semantic tokens as custom
   properties, and with them `contrast.ts`, `tokens.ts` and their twenty-four tests.
   The first suite is green on day one and the system is born protected.
4. **Continuous integration from the first commit.** The same workflow that already
   works in `buscartrabajo` and in `cookyourwebai`: install with `npm ci`, run the
   tests and build, on every push and every pull request.
5. **Slice 1, test first.** Starting with the data interface, which is what lets the
   public demo not depend on any live backend.

## How the work is done

- One failing test, the minimum piece that turns it green, and a commit. No
  exceptions.
- Small commits, each with one decision explained. No giant commit.
- One pull request per slice, not one at the end. With the suite green and the preview
  deployed before merging.
- Architecture, domain names and priorities are asked about. Implementation detail is
  resolved and reported.

## What is out of scope at kickoff

- Touching `cv-server`. Its lack of authentication is separate work and is documented.
- Migrating anything from Notion. In slice 1 Notion remains the source of truth.
- Figma.
- Applying automatically, which was already left out in the design.

## Still to decide at kickoff

Whether the work first goes through the spec-driven development flow (proposal,
specifications, design and tasks written before the code) or goes straight to the
slices with test first.

The first is slower at the start and leaves a trail of decisions in the repository.
The second is faster and already proved to work on 6 September.
