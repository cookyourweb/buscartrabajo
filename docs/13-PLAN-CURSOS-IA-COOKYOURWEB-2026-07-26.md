# Plan de curso — Desarrollo asistido por IA

**CookYourWeb · Formación · v1 · 26 jul 2026**

Documento de trabajo. Vivo: se va desarrollando. No es material final.

---

## 1. La tesis (el mensaje que lo atraviesa todo)

> **La IA NO te hace mejor desarrollador. AMPLIFICA lo que ya eres.**

Es un multiplicador: multiplica orden o multiplica caos. Un equipo sin disciplina
de arquitectura y revisión, con IA, no va más rápido: **acelera el desastre.**

**Corolario (posicionamiento de CookYourWeb):** IA CON GOBERNANZA, no IA suelta.
Es la misma idea que sostiene todo el trabajo de este año — el generador de CVs con
guardrails y la gobernanza documental de TuVueltaAlSol. Una tesis, demostrada varias veces.

---

## 2. El gancho (el dolor con el que el alumno se identifica)

Caso real (una desarrolladora, jul 2026): en su equipo cada dev tiene Copilot, pero lo
usan solo para tareas del día y suben lo que genera sin control. Consecuencias:

- **Duplicación** (viola DRY): la IA no conoce todo el codebase y reimplementa lo que
  ya existía.
- **Deriva arquitectónica**: genera código que funciona pero ignora los patrones del
  proyecto (atomic design, capas, convenciones).
- **Entropía**: cada dev mete cosas innecesarias; deuda técnica acelerada.
- **Sin gate de revisión**: el code review debería atraparlo y no lo hace.

**Apertura de clase:** *"¿Os pasa esto?"*. Casi todos dirán que sí. Ahí engancha.

---

## 3. Los dos ejes (matriz de catálogo)

**Eje 1 — Público**
- **Desarrolladores (CookYourWeb):** el *"cómo"*. Hands-on, tocan teclado, salen
  sabiendo hacerlo.
- **General (CLE, septiembre):** el *"qué y por qué"*. Entienden el cambio y el
  potencial, no necesitan programar.
- *Mismo tema, distinta profundidad. Eso distingue a un buen formador.*

**Eje 2 — Formato**
- **Proyecto desde cero (green-field):** montar un repo bien desde el inicio.
- **Optimizar un proyecto existente (brown-field):** meter IA en algo que ya existe
  sin romperlo.
- *Son los dos únicos escenarios reales de un dev: empiezo algo, o mejoro lo que tengo.*

| | Proyecto desde cero | Optimizar lo existente |
|---|---|---|
| **Devs** (CookYourWeb) | Repo, reglas, TDD, workflow con IA | Meter IA en proyecto heredado sin romperlo |
| **General** (CLE sept) | Qué es y por qué importa, sin tanto código | Casos, herramientas, el panorama |

→ **Cuatro cursos a partir de dos ideas.**

---

## 4. Esqueleto del bloque técnico (para devs)

**Módulo 0 (opcional, corto) — Laboratorio reproducible**
Docker solo como *"todos partimos del mismo contenedor, sin perder 2h con el 'en mi
máquina funciona'"*. NO mezclar Docker con el bloque de IA: son niveles distintos y
"de cero + 2 temas grandes" pierde a la clase.

**Módulo 1 — Setup**
Conectar el asistente al repo (Claude Code / Copilot / Gemini). Diferencias entre
ellos y cuándo usar cada uno.

**Módulo 2 — La regla de oro**
La IA NO commitea sola. Rama dedicada, el humano revisa y decide. *(Es lo que separa
a un dev pro de uno que pega código a ciegas. Mensaje diferencial del curso.)*

**Módulo 3 — TDD asistido**
Escribo el test primero; la IA implementa; red-green-refactor. La IA trabaja CONTRA
un test, no a lo loco. El test es un gate que no puede saltarse.

**Módulo 4 — Enseñar la arquitectura a la IA**
Darle contexto/reglas del proyecto (patrones, atomic design) para que NO derive.
Revisar duplicación ANTES de subir. Resuelve el dolor del punto 2.

**Módulo 5 — Prompts efectivos + revisar la salida**
Cómo pedir; cómo detectar cuándo la IA se equivoca; no confiar a ciegas.

**Módulo 6 — Code review de código generado con IA**
Cómo revisar PRs hechos con IA: duplicación, deriva, cosas innecesarias.

**Módulo 7 — Documentar decisiones**
El patrón de dejar rastro de por qué se hizo algo.

> Nota: este esqueleto es **cómo ya trabaja Verónica**. No hay que inventar contenido,
> hay que ordenarlo.

---

## 5. Por qué Verónica tiene autoridad para esto

No es teoría de tutorial. Ya vivió y resolvió este problema en TuVueltaAlSol con la
gobernanza documental (hooks, gates, evidence-inject). Su doctrina: *"un control que
depende de que la IA elija bien no es un control, es una plegaria."* Eso es
credibilidad real.

---

## 6. Pendiente de decidir

- Público exacto de cada convocatoria (devs que ya programan sin IA vs más de cero).
- Nº de horas por curso (los de CLE ~10-12h) → repartir módulos en el tiempo real.
- Qué asistente usar como principal en las prácticas (Claude Code / Copilot / Gemini).
- Proyecto-ejemplo con el que trabajar en clase (¿uno preparado de antemano?).

---

## 7. Conexión con la carrera

Cuando Verónica **imparta** estos cursos, deja de ser "rol objetivo" en el Master y
pasa a ser **experiencia real de GenAI Adoption** — el hueco que hoy el perfil no tiene
documentado. Regla: primero se hace, luego entra al Master.
