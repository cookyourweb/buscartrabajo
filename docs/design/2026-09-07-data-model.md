# Panel data model

Date: 2026-09-07
Continues: `2026-09-05-panel-empleo-angular-design.md`, which foresaw three tables
Verified against three sources: the Notion schema through the API, a complete export of
the database, and the n8n workflow in production

## What changes with respect to the 5 September design

That document foresaw `offers`, `applications` and `documents`. Looking at the real
data, **two more entities** appear, and both were hidden in the same place: the body
of the Notion page, written in prose.

## The five entities

### `offers`, the offer

What describes the job and does not depend on who is looking at it. Thirteen fields:
company, job title, description, link, location, work mode, salary, contract type,
hiring mode, language, keywords, publication date and whether it is verified.

### `applications`, the application

The relationship between a person and an offer. Fourteen fields: user, status, phase,
submission channel, four dates, technical test format, the three contact fields, the
email sent and the notes.

### `documents`, what is generated

Five fields: CV used, Drive link, cover letter sent, preparation link and the
freelancer notice in the cover letter.

### `events`, the history

**It does not exist today as data.** It lives in prose, inside the body of the page:

```
15 July: replies interested and states her salary reference.
21 July: the recruiter is back from vacation and proposes a call.
22 July: call held. Good fit.
```

That is a log of dated events. In prose it cannot be sorted, queried or shown on a
screen. And it is exactly what is needed to know whom to follow up with: not the
status, but what happened and when.

### `encaje` (fit), what is strong and what is missing

It does not exist today as data either. Also in prose:

```
Strong:      React, Vue, TypeScript, Core Web Vitals, FastAPI
Gap:         PHP/Symfony. Not in her experience and not invented in the CV.
To negotiate: the offer's range is below the reference
```

It is the rule of not lying, applied offer by offer. And it is the data that feeds the
promise of helping to learn what is missing, instead of inflating the CV.

`Tags` does not migrate: zero values in the whole database.

## The missing dimension: who fills each field, and when

Fields are not distinguished only by which entity they belong to. Also by their
origin.

| | Who fills it | When |
|---|---|---|
| ① | The system | When the offer is gathered |
| ② | The system | When the CV or cover letter is generated |
| ③ | The person | When moving forward, after each contact |

And the measured fill rate confirms it:

| Origin | Fill rate |
|---|---|
| ① intake | above eighty percent of the rows |
| ③ by hand | below fifteen percent |

The worst ones are precisely those that say the most about a process: the phase it is
in, the format of the technical test, the interview date and the name of the person
being talked to.

**They are not empty because they do not matter. They are empty because filling them
means going back to Notion and editing a row by hand.** Those numbers are the measure
of the problem, not an oversight.

Consequences for the screen:

- The ① fields are shown, not edited. If they are wrong, what failed is the extraction.
- The ② fields are written by the system.
- The ③ fields are the ones that must cost one click. **That is where the panel wins
  or loses.**

### Why this forces shaping what is prose today

It is planned that later one will be able to dictate what has happened and have an
agent fill in the fields. That is not built now, but it conditions today's model: an
agent fills a closed-value field without mistakes, and does not fill a free-text box
well.

Today `Notas` (notes) is filled in almost every row and contains everything: technical
tests, guardrail warnings and pieces of history. That box is where information stops
being queryable.

## What was already decided and is respected here

From the July document on how an offer enters:

- **The origin is not a status.** The status changes constantly; the origin never
  changes. If the origin lives inside the status, it is lost as soon as the
  application moves forward.
- **`Aprobado` (approved) is not a status: it is an order.** Setting it triggers the
  generation of the CV and the cover letter, whether it comes from the email button
  or from the person's hand. That is why it has no rows: it is a queue, not a place
  where one is.
- **`Estado` (status) mixes two life cycles** in a single property, that of the
  automation and that of the real application. The split into `applications` and
  `events` is what unmixes them.

## What the data brings into view

**Duplicate offers.** Same company, same job title and the same link. It is the same
offer captured twice. A `UNIQUE` on the link would prevent it, and it is the same
failure that already happened with people: two records for the same one ended up
different and a CV came out with the wrong header.

**An offer without a user.** With a mandatory `user_id` it could not exist.

**Salary is free text.** A string that mixes the range the company offers with the
reference of the person searching carries three data points inside: minimum, maximum
and expectation. The system promises to search by salary, and that requires salary to
be a number.

**There is a second applications database, abandoned.** A few rows, all from three days
in July, with a status vocabulary that does not match. And part of what is there does
not exist in the main database. The question is not whether to align the two
vocabularies: it is to rescue what lives only there, freeze that database and not
write in two places again.

## What the panel really solves

Today an application is spread across four places with no link between them: the offer
and its status in Notion, the CV in Drive, the interview preparation in a folder
inside git, and the follow-up in the head of the person searching.

**There is no common place.** The panel is that place.
