# Rules for tailoring a CV to an offer

**30 Jul 2026.** They came out of external feedback on the Personio CV (Senior Frontend Engineer, Payroll Domain). Score received: 9.3/10 against 8.5 for the generic CV.

Sibling of `16-COVER-LETTER-RULES.md`. That one rules the cover letter, this one the CV.

---

## The rule that governs

> A tailored CV does not change who you are. It changes which part of your experience you put in the foreground.

It is the sentence from the feedback and it sums up everything else. Repositioning is legitimate. Inventing is not. And the line between the two is not what you write: it is whether you can defend it for forty minutes in front of an engineer.

---

## 1. The headline adapts to the offer, not to your whole identity

The generic headline was:

```
Frontend Tech Lead | Full-Stack Developer | AI Engineer
```

For a pure frontend offer, `AI Engineer` subtracts. It takes the most valuable spot in the CV with something that company is not looking for. For Personio:

```
Frontend Tech Lead | Senior Frontend Engineer | React · TypeScript · Design Systems
```

AI does not disappear: it stays inside the CV, in its own section. What changes is what is read first.

**Corollary.** For an offer where AI is a requirement (eDreams asks for it as `must have` and again under `preferred`), the headline does the opposite and moves it up.

---

## 2. Allude to a domain without saying you worked in it

The best finding of the Personio CV. Not saying "I have payroll experience", which would be a lie. Saying that you worked in domains where an error has real consequences: sensitive financial and personal data at scale, document generation, business workflow automation.

It is true, it is verifiable and it communicates exactly the same thing.

---

## 3. Be careful that the ATS does not show

The feedback flagged this sentence:

> Her work on **Payroll-adjacent** domains such as financial and sensitive personal data at scale...

`Payroll-adjacent` is not natural English. It is a word built so that an automatic filter finds "payroll". And it shows.

A version that says the same without giving itself away:

> Her experience includes building systems handling financial and sensitive personal data at scale, document generation and business workflow automation, domains where correctness, consistency and maintainability are as critical as they are in payroll products.

**This is the AI-trace rule applied to the CV.** You already had it for cover letters. It applies equally here: if a sentence looks written for a machine, a human sees it too.

---

## 4. Keywords ONLY if you can defend them

The offer literally asks for `React and Redux or similar stack` and mentions `SOLID`. The temptation is to add the two words and be done. No.

**Verified on 30 Jul 2026:**

- **Redux**: does NOT appear in `CV_Master_Veronica_v2.txt` nor in any of the eight CVs in `~/Desktop/cv/_fuentes/`. The only place where it exists is `~/Desktop/cv/tuyos/preparacion-entrevista-xe-iwantic.md`, which is the study base for interviews, not a record of experience.
- **SOLID**: does not appear in the CV Master either. But here the case is different: Clean/Hexagonal architecture and design patterns are declared ground for Vero, so it is defensible.

**The precedent that decides this.** At osapiens she was rejected in the final phase, and part of the feedback was that **she froze when asked for library names**. Putting a keyword in the CV to pass a filter and not being able to sustain it in the technical interview is reproducing that rejection on purpose.

**The rule:**

> A technology goes in the CV if you can tell a case where you used it and what you decided with it. If all you can say is that you know it, it stays out. The ATS does not hire you: the person who interviews you afterwards does.

If Vero can defend Redux with a real case, it goes in. If not, it stays out even if the offer asks for it.

---

## 5. Mirror the offer's vocabulary when the fact is already yours

Different from the previous point. Here nothing new is added: something that is already true is rewritten with the words the company uses.

Before:

> Established code review practices and development standards...

After, for an offer that repeats `engineering standards`, `guidelines` and `coaching`:

> Established frontend engineering standards, code review practices and development guidelines that improved maintainability and onboarding across teams.

Same fact, same language as the reader.

---

## 6. Literal tools from the offer

If the offer names `Webpack`, `Vite`, `npm/yarn` or `SQL` and you have used them, they have to appear written the same way. This is not cheating, it is that the filter looks for the exact string.

Point 4 still applies: only if it is true.

---

## Checklist before sending a tailored CV

- [ ] The headline puts first what that company is looking for
- [ ] What the company is not looking for has moved down a level, not disappeared
- [ ] No sentence sounds built for an automatic filter
- [ ] Every new technology in the CV has a real case behind it that you could tell
- [ ] The vocabulary of the bullets gets closer to the offer's, without changing the facts
- [ ] The tools the offer names literally appear written the same way

---

## Related

- `16-COVER-LETTER-RULES.md`: facts and not claims. It rules the cover letter.
- Engram memory `buscartrabajo/osapiens-feedback`: the rejection for freezing on library names, which is the origin of rule 4.
