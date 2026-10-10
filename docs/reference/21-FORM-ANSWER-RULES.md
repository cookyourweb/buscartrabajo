# Reglas para las preguntas abiertas de los formularios

**31 ago 2026** · Salieron de corregir once veces la respuesta al formulario de Lodgify.
No es teoría: cada regla viene de un borrador que no servía.

**Relacionado:** `16-REGLAS-CARTA-PRESENTACION.md` (la carta), `18-REGLAS-ADAPTACION-CV.md` (el CV).
Este documento cubre las **preguntas abiertas de los ATS**, que es lo que ninguno de los otros dos cubría.

---

## Qué están evaluando de verdad

No es si sabes escribir prompts. Están separando dos perfiles:

| Perfil A · integrador de IA | Perfil B · AI Engineer |
|---|---|
| *"Conecté GPT, hice un RAG, ajusté el prompt y funcionaba bastante bien."* | *"Tengo un sistema probabilístico en producción. Sé definir qué significa que falle, cómo detectarlo, medirlo y cambiar la arquitectura para reducir la clase de error."* |

Buscan el B. Las **cinco señales** que rastrean, en este orden:

1. ¿Ha puesto un sistema LLM **real en producción**?
2. ¿Entiende que puede fallar **aunque la respuesta parezca buena**?
3. ¿Tiene estrategia de evaluación **y sabe decir cómo sabe que AHORA funciona**?
4. ¿Ha descubierto un **failure mode real, con datos**?
5. ¿**Qué cambió** a raíz de eso?

La señal 3 es la que más se olvida. Contar la arquitectura nueva no es contar la garantía.

---

## Las ocho reglas de redacción

### 1. Empezar por el PROBLEMA, con sus cabeceras y en su orden

Si la pregunta pide `Problem, Evaluation Strategy, Critical Failure Mode, Impact`,
la respuesta lleva esas cuatro cabeceras, en mayúsculas, en ese orden, separadas por
líneas en blanco. **Escaneable.** Sin cabeceras el buen material llega tarde y se pierde.

### 2. No decir para qué usas la herramienta: decir cómo trabajas

Contar que `cv-server` es "una aplicación para buscar trabajo" te coloca como candidata
en paro antes de que te lean. El sistema es el mismo; lo que cambia es desde dónde se cuenta.

### 3. Enseñar el bucle, no una lista de logros

```
Build
  ↓ observar fallos
  ↓ crear casos de evaluación
  ↓ medir
  ↓ encontrar patrones de fallo
  ↓ mejorar contexto / retrieval / prompts
  ↓ repetir
```

NO: prompt, "looks good!", producción.

### 4. Vocabulario profesional, voz humana

La diferencia **no está en el léxico técnico**. Está en los conectores.

| Suena a informe | Suena a persona |
|---|---|
| *"which created a specific reliability problem"* | *"and that is where the real difficulty sits"* |
| *"The challenge was therefore not simply generating good text"* | *"So the hard part was never writing good text"* |
| *"The most important failure mode I discovered was that..."* | *"The one that mattered most: ..."* |
| *"The main architectural lesson was that context injection is not evidence of context use"* | *"Context injection is not evidence of context use."* |
| *"yet every output read naturally and plausibly"* | *"and every single one read naturally"* |

**Fuera:** `therefore`, `moreover`, `thus`, `which created`, `the main lesson was`,
`it is worth noting that`, y las nominalizaciones (*"the challenge was not simply generating"*
en vez de *"the hard part was never writing"*).

### 5. No despersonalizar la propiedad

*"That baseline was me"* es mejor que *"that baseline was human review"*.

"Human review" es pasivo: podría ser un becario o un equipo de anotadores.
*"Was me"* dice que la experta del dominio eras tú, y eso es lo que hace creíble
todo lo que viene después. Para un puesto donde vas a ser dueña de la evaluación,
asumir la propiedad **no es informal**.

### 6. Nada de absolutos que no sostengas al 100%

*"Tracked every change to the domain logic"* se cambió por *"followed changes in the
domain logic"*. Un absoluto que no puedes defender es una trampa que te pones tú misma.

### 7. Adelántate a la pregunta incómoda

Si algo está a medias, dilo tú primero. Nadie puede pillarte en algo que has declarado.

> *"I did not start with a formal evaluation framework; I arrived at one by turning
> real production failures into explicit, testable criteria."*

### 8. Un solo dato duro

El segundo se guarda para la entrevista: dos cifras en el mismo texto compiten entre sí.

| Dato | Dónde |
|---|---|
| **77 de 78** items con atributo calculado erróneo, y todos se leían perfectamente | En el texto escrito |
| **166 ficheros de prosa** sin la respuesta frente a **14 commits** que la tenían | Guardado para la entrevista |

---

## La narrativa profesional

**NO** venderse como alguien con cinco años montando plataformas enterprise de evaluación de LLM.

**SÍ** como **ingeniera de software senior (20+ años) que ha evolucionado hacia AI Systems
Engineering y ha llegado por experiencia propia a conclusiones arquitectónicas correctas**:
separar la IA del core, diseñar el contexto explícitamente, contratos estructurados, validar
salidas, descubrir failure modes, convertir fallos observados en reglas verificables,
TDD en la capa determinista.

Coincide con lo que ya dice el PPS: *"I am not a Data Scientist. I am not an AI researcher."*

**La ventaja real de 20 años: sabe que un sistema no está terminado porque una demo funcione.**

Y hay una asimetría a favor: la mayoría llega desde el ML y está aprendiendo ingeniería de
sistemas. Ella llega desde la ingeniería y está aprendiendo IA. Para un puesto que pide
*evaluation, retrieval, production readiness y failure analysis*, ese camino es el que sirve.

---

## Qué material usar

**El bueno es `tu-vuelta-al-sol`, no `cv-server`.** Producto en producción con usuarios
reales desde agosto de 2025. cv-server es una herramienta propia; tuvueltalsol es un producto.
Para una candidatura eso pesa mucho más. cv-server sirve como enlace de código público auditable.

Repo real (largo y nada obvio, por eso se pierde):
`~/familiasEsteleares/react/agenda-tu-vuelta-al-sol/proyectoAgendaAstrologica/next-build-estable/tu-vuelta-al-sol`

Las copias en `Documents/`, `Downloads/`, `n8nClaude/` y `lovable/` están **muertas**.

---

## La distinción que evita quedar mal

> *"Ahora que sé que los prompts no pueden estar en el proyecto como los tenía, igual queda mal."*

**Premisa falsa.** Son dos cosas distintas:

1. **Prompts versionados dentro del proyecto: ESTÁ BIEN.** Es lo profesional, si están
   versionados, tienen tests, están separados de la lógica de negocio y se pueden evaluar
   los cambios.
2. **Una regla crítica de negocio que vive SOLO dentro del prompt: ESE es el fallo.**

El propio código demuestra las dos partes: en `cv-server` los prompts salieron de dentro de
las funciones a constantes de módulo con tests, y siguen en el proyecto. En `tu-vuelta-al-sol`,
`validarCandidataActivacion.ts` dice: *"una prohibición dentro del prompt no es un control"*.

**La evolución se cuenta así:**

```
ANTES:  datos de dominio · contexto grande · prompt con instrucciones y reglas · LLM · salida

AHORA:  cómputo determinista del dominio · evidencia estructurada · generación LLM
        · validación de la salida · tests y evaluadores
```

No se dice "tenía los prompts mal". Se dice **"moví la responsabilidad al nivel correcto
de la arquitectura"**.

---

## La evaluación empieza en el dominio

> *"Lo primero, aprender el producto perfectamente, saber qué cambios se están haciendo.
> Sin eso no es medible, y tiene que haber un human in the loop, que soy yo en mi primer proyecto."*

Antes de evaluar un sistema LLM hay que saber **qué significa "correcto" para ese producto**.
Nadie construye un pipeline de evaluación el día uno.

```
comprensión humana del dominio
  ↓ evaluación manual
  ↓ fallos observados
  ↓ casos de fallo definidos
  ↓ validators
  ↓ tests de regresión automáticos
```

**Cuidado con "human-in-the-loop":** hoy mucha gente lo entiende como *"un humano aprueba
cada respuesta antes de enviarla"*. No es lo que pasó. Lo suyo fue ser el **oráculo inicial**
que permitió construir la evaluación.

---

## Las frases que hacen el trabajo

- *"A fluent claim that is not grounded looks exactly like one that is."*
- *"Telling the model a rule is not the same as enforcing it."*
- *"Providing context to an LLM is not sufficient evidence that the context has actually been used."*
- *"I treated it as a reliability failure of the system, not as a prompting problem."*
- *"That manual review was never meant to be the solution. It was how I found the failure modes
  and established the ground truth that later became automated checks."*
- *"I did not start with a formal evaluation framework; I arrived at one by turning real
  production failures into explicit, testable criteria."*
- **El cierre:** *"Prompts guide behaviour, but critical invariants belong in the deterministic,
  observable and testable parts of the architecture."*

---

## Preparación de entrevista

**P: "So, did you have an evaluation framework from the beginning?"**

No aparentar que sí.

> *"No. I started with human evaluation because I first needed to understand what correctness
> meant for the product. The important part was turning what I learned from those reviews into
> explicit failure cases and then automating them."*

**P: "Why were you the human in the loop?"**

> *"Because I was also responsible for the product and the domain logic. I couldn't meaningfully
> evaluate the model without understanding what the underlying data meant and what the expected
> behaviour was. Once those criteria were stable, the goal was to remove myself from the critical
> path by turning them into automated checks."*

Esta segunda es la buena. No dice *"yo revisaba porque no me fiaba de la IA"*: dice que usó
conocimiento humano para construir el mecanismo que permite que el sistema se evalúe solo.
Y termina en **"remove myself from the critical path"**, que es mentalidad de ingeniería.

---

## Errores de método que no repetir

**Sesgo de recencia.** Al empezar el día nos centramos en `cv-server` y se ignoró
`tu-vuelta-al-sol`, que era el material bueno, solo porque las últimas sesiones habían ido de
cv-server. Es el hallazgo de `POR_QUE_FALLA_LA_IA_Y_QUE_CONTROL_SIRVE.md` aplicado a nosotros
mismos: el marco se fija en los primeros treinta segundos y no se revisa.

**Un resultado negativo sobre la fuente equivocada parece un hecho.** Se afirmó "no existe la
capa de evaluación" tras buscar en copias muertas del repo. Antes de decir que algo no existe,
confirmar cuál es el repo con historia de commits.

**Traer contraste de fuera funciona, pero no se acepta sin verificar.** Cuando un consejo externo
dijo "no te vendas como Data Scientist", se comprobó contra el PPS: ya estaba escrito ahí.
Cuando dijo "despersonaliza el baseline", se rechazó con argumento.

---

## Checklist antes de enviar

- [ ] ¿Empieza por el problema?
- [ ] ¿Usa sus cabeceras, en su orden?
- [ ] ¿Cuenta cómo se sabe que AHORA funciona?
- [ ] ¿Hay un dato duro, y solo uno?
- [ ] ¿Algún absoluto que no se pueda sostener?
- [ ] ¿Suena a persona o a informe? (buscar `therefore`, `the main lesson was`)
- [ ] ¿Se puede defender cada frase en entrevista?
- [ ] ¿Cero guiones largos y cero flechas en lo que sale a la empresa?

---

*Origen: sesión del 31 de agosto de 2026, candidatura a Lodgify (Senior AI Engineer, vía Lever).*
