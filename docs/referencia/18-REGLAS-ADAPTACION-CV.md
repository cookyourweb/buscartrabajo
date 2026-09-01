# Reglas de adaptación de CV por oferta

**30-jul-2026.** Salieron del feedback externo sobre el CV de Personio (Senior Frontend Engineer, Payroll Domain). Valoración recibida: 9,3/10 frente al 8,5 del CV genérico.

Hermano de `16-REGLAS-CARTA-PRESENTACION.md`. Aquel manda en la carta, este en el CV.

---

## La regla que manda

> Un CV adaptado no cambia quién sos. Cambia qué parte de tu experiencia pone en primer plano.

Es la frase del feedback y resume todo lo demás. Reposicionar es legítimo. Inventar no. Y la línea entre las dos cosas no es lo que escribís: es si podés defenderlo cuarenta minutos delante de un técnico.

---

## 1. El titular se adapta a la oferta, no a tu identidad completa

El titular genérico era:

```
Frontend Tech Lead | Full-Stack Developer | AI Engineer
```

Para una oferta de frontend puro, `AI Engineer` resta. Ocupa el sitio más valioso del CV con algo que esa empresa no está buscando. Para Personio:

```
Frontend Tech Lead | Senior Frontend Engineer | React · TypeScript · Design Systems
```

La IA no desaparece: sigue dentro del CV, en su sección. Lo que cambia es qué se lee primero.

**Corolario.** Para una oferta donde la IA sí es requisito (eDreams la pide como `must have` y otra vez en `preferred`), el titular hace lo contrario y la sube.

---

## 2. Aludir a un dominio sin decir que trabajaste en él

El mejor hallazgo del CV de Personio. No decir "tengo experiencia en nóminas", que sería mentira. Decir que trabajaste en dominios donde un error tiene consecuencias reales: datos financieros y personales sensibles a escala, generación documental, automatización de flujos de negocio.

Es cierto, es comprobable y comunica exactamente lo mismo.

---

## 3. Cuidado con que se note el ATS

El feedback señaló esta frase:

> Her work on **Payroll-adjacent** domains such as financial and sensitive personal data at scale...

`Payroll-adjacent` no es inglés natural. Es una palabra construida para que un filtro automático encuentre "payroll". Y se nota.

Versión que dice lo mismo sin delatarse:

> Her experience includes building systems handling financial and sensitive personal data at scale, document generation and business workflow automation, domains where correctness, consistency and maintainability are as critical as they are in payroll products.

**Esto es la regla del rastro de IA aplicada al CV.** Ya la tenías para las cartas. Vale igual aquí: si una frase parece escrita para una máquina, un humano también lo ve.

---

## 4. Las keywords SOLO si las podés defender

La oferta pide literalmente `React and Redux or similar stack` y menciona `SOLID`. La tentación es añadir las dos palabras y listo. No.

**Verificado el 30-jul-2026:**

- **Redux**: NO aparece en `CV_Master_Veronica_v2.txt` ni en ninguno de los ocho CVs de `~/Desktop/cv/_fuentes/`. El único sitio donde existe es `~/Desktop/cv/tuyos/preparacion-entrevista-xe-iwantic.md`, que es la base de estudio para entrevistas, no un registro de experiencia.
- **SOLID**: tampoco aparece en el CV Master. Pero aquí el caso es distinto: la arquitectura Clean/Hexagonal y los patrones de diseño sí son terreno declarado de Vero, así que es defendible.

**El precedente que decide esto.** En osapiens la rechazaron en última fase, y parte del feedback fue que **se bloqueó cuando le preguntaron nombres de librerías**. Meter una keyword en el CV para pasar un filtro y no poder sostenerla en la entrevista técnica es reproducir ese rechazo a propósito.

**La regla:**

> Una tecnología entra en el CV si podés contar un caso donde la usaste y qué decidiste con ella. Si solo podés decir que la conocés, va fuera. El ATS no te contrata: te contrata el que te entrevista después.

Si Vero puede defender Redux con un caso real, entra. Si no, se queda fuera aunque la oferta la pida.

---

## 5. Espejar el vocabulario de la oferta cuando el hecho ya es tuyo

Distinto del punto anterior. Aquí no se añade nada nuevo: se reescribe algo que ya es verdad con las palabras que usa la empresa.

Antes:

> Established code review practices and development standards...

Después, para una oferta que repite `engineering standards`, `guidelines` y `coaching`:

> Established frontend engineering standards, code review practices and development guidelines that improved maintainability and onboarding across teams.

Mismo hecho, mismo idioma que el lector.

---

## 6. Herramientas literales de la oferta

Si la oferta nombra `Webpack`, `Vite`, `npm/yarn` o `SQL` y los has usado, tienen que aparecer escritos igual. Esto no es hacer trampa, es que el filtro busca la cadena exacta.

Sigue aplicando el punto 4: solo si es verdad.

---

## Checklist antes de enviar un CV adaptado

- [ ] El titular pone delante lo que esa empresa busca
- [ ] Lo que la empresa no busca ha bajado de nivel, no desaparecido
- [ ] Ninguna frase suena construida para un filtro automático
- [ ] Cada tecnología nueva del CV tiene un caso real detrás que podrías contar
- [ ] El vocabulario de los bullets se acerca al de la oferta, sin cambiar los hechos
- [ ] Las herramientas que la oferta nombra literalmente aparecen escritas igual

---

## Relacionado

- `16-REGLAS-CARTA-PRESENTACION.md`: hechos y no afirmaciones. Manda en la carta.
- `14-ESTRATEGIA-BUSQUEDA-PAN-VS-TECHO.md`: cuándo la IA es el plato y cuándo la guinda.
- Memoria engram `buscartrabajo/osapiens-feedback`: el rechazo por bloquearse con nombres de librerías, que es el origen de la regla 4.
