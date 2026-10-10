# Rules for cover letters

**31 Aug 2026** · Fully rewritten. The previous version (29 Jul) mandated the opposite
of what is decided here, and stayed in force for two days after the rule changed.

---

## The rule that overrides the others

**The letter does not argue. It opens the door.**

Her words, correcting three drafts in a row:

> *"I'm justifying myself before speaking."*

Nobody has yet asked why you fit. A letter that answers that question competes with the
CV and loses: the recruiter reads two texts that say the same thing, and neither with
attention. **The CV is what argues. The letter only gets it opened.**

---

## The six rules

### 1. Zero justification

No reason, no achievement, no skill is named. **Not one.**

This includes those that sound good and are true. Any of these is surplus:

| Surplus | Why |
|---|---|
| *"I make LLM behaviour testable"* | It is a merit. It is already in the CV. |
| *"I measure a tool before adopting it"* | It is a merit. It is already in the CV. |
| *"llevo tiempo poniendo modelos en producción"* (I have been putting models into production for a while) | It is a merit. It is already in the CV. |
| *"con código público que podéis revisar"* (with public code you can review) | It is self-promotion. |

### 2. Non-assertive language

> Yes: *"creo que **puede encajar** con lo que hago en mi trabajo"* (I think it **could fit** what I do in my work)
> No: *"este puesto **está hecho para mí**"* (this position **was made for me**)

It is a hypothesis, not a verdict. Let them confirm it.

### 3. Three moves, and no more

1. I introduce myself.
2. I found the offer interesting and I think it could fit what I do.
3. I refer to the CV: *"El detalle está en mi CV."* (The detail is in my CV.)

### 4. A single nod, and it points to THE OFFER

A single sentence from their offer shows that you read it. Two or more sound like an
echo, and the echo is what makes a letter look generated.

**The nod points to what THEY ask for, never to your merits.** That is the difference
between showing you read the ad and justifying yourself again:

> Yes: *"en particular la parte de Google Cloud y Gemini"* (in particular the Google Cloud and Gemini part)
> No: *"vengo de años diseñando arquitecturas y hoy diseño arquitecturas con LLMs"* (I come from years of designing architectures and today I design architectures with LLMs)

If the offer title is generic (a bare *"Senior AI Engineer"*) and you do not have their
text in front of you, **the letter goes without a nod**. What they ask for is not
invented.

### 5. Quote the job title correctly

The one on the vacancy, in full and exactly as they write it. If it is called
*"Arquitecto de Soluciones IA y GenAI"*, it is not shortened to
*"Arquitecto de Soluciones IA"*.

### 6. Short, and in Spanish with accents

~50-70 words. Maximum 100. Zero long dashes and zero arrows.

The accents are not a detail: on 29 Aug two letters went out to the Spanish market
**without a single accent in the body**, with the letterhead above it correctly
accented. The contrast within the same page is what gives it away.

---

## The template

```
Hola,

Soy Verónica Serna, ingeniera de IA. Me ha parecido muy interesante vuestra
oferta de {PUESTO EXACTO}{, en particular {GUIÑO A LA OFERTA}} y creo que
puede encajar con lo que hago en mi trabajo.

El detalle está en mi CV. Quedo a vuestra disposición.

Un saludo,
Verónica Serna Pérez
```

The template is the Spanish-language letter; `{PUESTO EXACTO}` is the exact job title
and `{GUIÑO A LA OFERTA}` is the nod to the offer.

In English, same skeleton: *"I found your {PUESTO} opening very interesting and I
think it could fit with what I do in my work."*

**Without a nod, two letters to different companies come out almost identical. That is
fine:** nobody compares your letters across companies, and the CV does the heavy
lifting.

---

## Before sending it

- [ ] Does it name any merit, achievement or skill? If so, **out**.
- [ ] Does it say "could fit" and not "was made for me"?
- [ ] Does it quote the full vacancy name?
- [ ] Does the nod point to the offer, and not to her?
- [ ] Fewer than 100 words?
- [ ] If it is in Spanish, does it carry all the accents?
- [ ] Zero long dashes and zero arrows?

The last two are checked automatically by `scripts/render_carta.py`: it **aborts the
render** if it finds a long dash or an arrow.

---

## What was left behind

The 29 Jul version mandated *"three or four short paragraphs"*, *"the stack overlap as
a list of facts"* and *"where your depth is, with 2 concrete facts"*. All of that **is
justifying yourself**, and it has been removed.

Only one of its rules survives, rule 4: *a single sentence from their offer*.

Its master rule, **facts, not claims**, is still true and now lives in the CV, which is
where it belongs. In the letter it is not needed: without merits there is nothing to
defend.

---

**Related:** the CV Master's LEEME (red lines and canonical data),
`PROMPT_CARTA` in `cv-server/server.py` (**pending alignment**: it still asks for
"ONE SINGLE concrete anchor", which this version removes).
