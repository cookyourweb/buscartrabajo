# ADR-006. The product lives on subdomains of cookyourwebai.es

**Date:** 2 Oct 2026 · **Status:** accepted. Panel name decided on 7 Oct 2026

---

## Context

The system stops being a personal tool and becomes a product of the Cook Your Web
brand, open by invitation. It has two lines:

- **Jobs (`empleo`):** find offers, approve or discard them, and prepare for the
  interview.
- **Training (`formacion`):** the courses. Their relationship with the jobs panel will
  be decided separately.

The brand website exists and is built in React. The panel is in Angular.

## Decision

**One domain, cookyourwebai.es, with one subdomain per line and another for the API.**

- Jobs panel: `empleo.cookyourwebai.es` (decided on 7 Oct 2026 over `carrera`, which
  is ambiguous in Spanish: it also means a university degree or a sports race). It is
  published on Vercel, where the website already lives; the domain's DNS is at IONOS.
- API: `api.cookyourwebai.es`.
- Training: its own subdomain, for example `formacion.cookyourwebai.es`.

**The React website is not rewritten in Angular.** The website, the panel and the
training are tied together by three things, not by the framework:

1. **Links.** The website is the front door and leads to each line.
2. **One design system.** The same tokens, copied from `cookyourwebai` with their
   contrast tests, as the [panel plan](../design/2026-09-06-angular-panel-kickoff-plan.md)
   says. If maintaining them in two places hurts, they are extracted into a package.
3. **One account.** All lines use Google and the same internal identifier
   ([ADR-003](ADR-003-authentication.md)). Sharing the session across subdomains will
   come with the session cookie that ADR-003 leaves as an evolution.

## Why subdomains of the same domain

So that the panel and the API belong to the same site. Today the session goes through
an in-memory token (ADR-003), and the shared domain leaves open the evolution to a
cookie that no script can read, without changing domain. With different domains that
cookie would be third-party, and Safari and Firefox block it by default: it is not
reliable.

Subdomains also cost nothing: they come with the domain that is already paid for.

## On SEO

The subdomain name carries little weight in rankings: Google ranks by content. And the
panel lives behind sign-in, so Google does not see it.

What ranks are the **public pages** that explain each line. Those pages are generated
as HTML at publish time (`@angular/ssr` with `outputMode: "static"`), with no server
and no cost. This modifies B1 of the
[board](../design/2026-09-05-architecture-decisions.md) only for the public pages: the
panel remains a browser application.

**Pending:** whether those public pages live in the Angular panel or in the React
website.

## Consequences

**Accepted:**

- The domain's DNS has to be configured and each piece published on its subdomain.
- The website, the panel and the training have to respect the same design system to
  feel like a single product.

**Gained:**

- One product with a single brand and a single account.
- No rewrite: each piece stays in the technology it is in.

## When to revisit

When it is decided whether the website integrates the panel or only links to it. Today
it only links to it.

---

**Sources, consulted on 2 Oct 2026:** angular.dev/guide/ssr ·
developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies

**Related:** [ADR-003](ADR-003-authentication.md) ·
[panel plan](../design/2026-09-06-angular-panel-kickoff-plan.md)
