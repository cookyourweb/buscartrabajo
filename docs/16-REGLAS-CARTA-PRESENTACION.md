# Reglas para las cartas de presentación

**31 ago 2026** · Reescrito entero. La versión anterior (29 jul) mandaba lo contrario
de lo que se decide aquí, y siguió vigente dos días después de que la regla cambiara.

---

## La regla que manda sobre las demás

**La carta no argumenta. Abre la puerta.**

Sus palabras, corrigiendo tres borradores seguidos:

> *"Estoy justificando antes de hablar."*

Nadie ha preguntado todavía por qué encajas. Una carta que responde a esa pregunta
compite con el CV y pierde: el reclutador lee dos textos que dicen lo mismo, y ninguno
con atención. **El que argumenta es el CV. La carta solo consigue que lo abran.**

---

## Las seis reglas

### 1. Cero justificación

No se nombra ninguna razón, ningún logro, ninguna competencia. **Ni una.**

Esto incluye las que suenan bien y son verdad. Cualquiera de estas sobra:

| Sobra | Por qué |
|---|---|
| *"I make LLM behaviour testable"* | Es un mérito. Ya está en el CV. |
| *"I measure a tool before adopting it"* | Es un mérito. Ya está en el CV. |
| *"llevo tiempo poniendo modelos en producción"* | Es un mérito. Ya está en el CV. |
| *"con código público que podéis revisar"* | Es darse bombo. |

### 2. Lenguaje no afirmativo

> ✅ *"creo que **puede encajar** con lo que hago en mi trabajo"*
> ❌ *"este puesto **está hecho para mí**"*

Es una hipótesis, no una sentencia. Que lo confirmen ellos.

### 3. Tres movimientos, y ninguno más

1. Me presento.
2. La oferta me ha parecido interesante y creo que puede encajar con lo que hago.
3. Remito al CV: *"El detalle está en mi CV."*

### 4. Un solo guiño, y apunta a LA OFERTA

Una sola frase de su oferta demuestra que la leíste. Dos o más suenan a eco, y el eco
es lo que hace que una carta parezca generada.

**El guiño apunta a lo que ELLOS piden, nunca a tus méritos.** Esa es la diferencia
entre demostrar que leíste el anuncio y volver a justificarte:

> ✅ *"en particular la parte de Google Cloud y Gemini"*
> ❌ *"vengo de años diseñando arquitecturas y hoy diseño arquitecturas con LLMs"*

Si el título de la oferta es genérico (*"Senior AI Engineer"* a secas) y no tienes su
texto delante, **la carta va sin guiño**. No se inventa qué piden.

### 5. Cita bien el nombre del puesto

El de la vacante, entero y tal cual lo escriben ellos. Si se llama
*"Arquitecto de Soluciones IA y GenAI"*, no se recorta a *"Arquitecto de Soluciones IA"*.

### 6. Corta, y en español con tildes

~50-70 palabras. Máximo 100. Cero guiones largos (—) y cero flechas (→).

Las tildes no son un detalle: el 29-ago salieron dos cartas al mercado español
**sin una sola tilde en el cuerpo**, con el membrete de encima bien acentuado. El
contraste dentro del mismo folio es lo que canta.

---

## La plantilla

```
Hola,

Soy Verónica Serna, ingeniera de IA. Me ha parecido muy interesante vuestra
oferta de {PUESTO EXACTO}{, en particular {GUIÑO A LA OFERTA}} y creo que
puede encajar con lo que hago en mi trabajo.

El detalle está en mi CV. Quedo a vuestra disposición.

Un saludo,
Verónica Serna Pérez
```

En inglés, mismo esqueleto: *"I found your {PUESTO} opening very interesting and I
think it could fit with what I do in my work."*

**Sin guiño, dos cartas a empresas distintas salen casi idénticas. Está bien:**
nadie compara tus cartas entre empresas, y el trabajo pesado lo hace el CV.

---

## Antes de enviarla

- [ ] ¿Nombra algún mérito, logro o competencia? Si sí, **fuera**.
- [ ] ¿Dice "puede encajar" y no "está hecho para mí"?
- [ ] ¿Cita el nombre de la vacante entero?
- [ ] ¿El guiño apunta a la oferta, y no a ella?
- [ ] ¿Menos de 100 palabras?
- [ ] Si va en español, ¿lleva todas las tildes?
- [ ] ¿Cero guiones largos y cero flechas?

Las dos últimas las verifica sola `scripts/render_carta.py`: **aborta el render** si
encuentra un guion largo o una flecha.

---

## Qué se ha quedado por el camino

La versión del 29-jul mandaba *"tres o cuatro párrafos breves"*, *"el solape de stack
como lista de hechos"* y *"dónde está tu profundidad, con 2 hechos concretos"*. Todo eso
**es justificarse**, y se ha eliminado.

Sobrevive una sola de sus reglas, la 4: *una sola frase de su oferta*.

Su regla maestra —**hechos, no afirmaciones**— sigue siendo cierta y ahora vive en el CV,
que es donde toca. En la carta no hace falta: sin méritos no hay nada que defender.

---

**Relacionado:** `~/Desktop/cv/LEEME.md` (líneas rojas y datos canónicos),
`cv-server/server.py` → `PROMPT_CARTA` (**pendiente de alinear**: aún pide
"UNA SOLA ancla concreta", que esta versión elimina).
