# Filtro de ofertas de n8n, corregido

> Escrito el 23 de julio de 2026, después de comprobar que el workflow manda ofertas de
> Java, .NET, Ionic y Rails a una desarrolladora de React y Vue.
>
> Objetivo: que n8n use los mismos criterios que la tarea programada de Claude, que sí
> filtra bien. Un solo criterio, no dos.

## Los dos fallos

### 1. El `&&` deja pasar el stack ajeno

En el nodo **`Formatear ofertas`**, función `matchea`:

```js
if (esOtroPerfil && !tieneSenal) return false;
return tieneSenal;
```

Una oferta de backend que además mencione una palabra del perfil, pasa. Y en España casi
todas las ofertas mezclan las dos cosas.

Las cuatro del 20 de julio y las de hoy:

| Título | Por qué coló |
|---|---|
| Programador/a Senior .NET + Angular | `.net` excluye, `angular` incluye |
| Tech Lead ó Analista Fullstack Java | `java` excluye, `tech lead` incluye |
| Desarrollador/a Java Ionic Angular | `java` excluye, `angular` incluye |
| Senior Full Stack Engineer (Java/React) | `java` excluye, `react` incluye |
| Tech Lead Full-Stack Rails Engineer | `rails` no está ni en la lista de excluir |

### 2. El ranking no tiene suelo

En el nodo **`Groq - Generar Ofertas`**, el prompt pide:

> Devuelve SOLO un array JSON con las **5 MEJORES**

Siempre devuelve cinco, haya o no cinco buenas. Un ranking sin suelo siempre produce algo:
si el día no trae nada que valga, manda lo menos malo y el sistema parece sano.

## Por qué el título no basta, y quién decide qué

Primera versión de este documento proponía bloquear siempre por stack ajeno. **Estaba mal.**
Mirá estos dos títulos:

```
Senior Full Stack Engineer (Java/React)             sobra
Senior Fullstack Software Engineer (.NET + React)   vale
```

Misma forma. Stack ajeno delante, React detrás. Ninguna regla sobre el título los distingue,
y un bloqueo duro habría tirado la segunda, que es una oferta buena: la descripción dice
"React/TypeScript y C#/.NET Core, uso de IA y Cursor como herramienta principal".

Lo que los separa está en la **descripción**, y el nodo de código solo ve títulos.

De ahí el reparto:

| Capa | Ve | Decide |
|---|---|---|
| `Formatear ofertas` (código) | El título | La basura evidente, que es determinista |
| `Groq - Generar Ofertas` (modelo) | La descripción entera | Si el frontend es el trabajo o un añadido |

Determinista lo obvio, criterio lo que necesita criterio. No al revés.

## Corrección 1: nodo `Formatear ofertas`

Sustituir la función `matchea` entera por esta. Las listas `INCLUIR`, `EXCLUIR_PERFIL` y
`EXCLUIR_DURO` se quedan como están.

```js
// Seniority exigida en el titulo. Sin esto entran junior y mid.
const SENIORITY = ['senior', 'sr.', 'sr ', 'staff', 'lead', 'principal', 'architect',
  'arquitecto', 'head of'];

const matchea = (titulo, desc) => {
  const tit = (titulo || '').toLowerCase();

  // 1. Basura y roles no tecnicos: fuera siempre.
  if (EXCLUIR_DURO.some(k => tit.includes(k))) return false;

  // 2. Tiene que haber senal real de su perfil en el titulo.
  if (!INCLUIR.some(k => tit.includes(k))) return false;

  // 3. Seniority obligatoria.
  if (!SENIORITY.some(k => tit.includes(k))) return false;

  // 4. Stack ajeno SIN ninguna senal del perfil: fuera. Con senal, NO se decide aqui:
  //    el titulo no distingue "Java/React" de ".NET + React", y uno sobra y el otro no.
  //    Esa llamada la hace el nodo de Groq, que si lee la descripcion.
  return true;
};
```

**Efecto esperado:** caen "Desarrollador/a Node con Inglés" y "Tech Lead Full-Stack Rails"
por seniority o por falta de señal. Las de Java y .NET llegan al nodo de Groq, que decide
con la descripción delante.

**Riesgo asumido:** el filtro es más estrecho y habrá días de cero ofertas. Eso es correcto.
Un día sin ofertas buenas debe verse como un día sin ofertas, no como cinco mediocres.

## Corrección 2: nodo `Groq - Generar Ofertas`

En el prompt, sustituir el bloque de criterios y el de salida.

**Donde dice:**

```
CRITERIOS (en orden): 1) encaje real con su perfil/stack; 2) salario (prioriza mejor
pagadas; si no indica, no descartes pero ponla abajo); 3) modalidad (remoto/hibrido/su
ciudad); 4) descarta lo claramente fuera de perfil (ventas, soporte, oficios no tecnicos).
```

**Poner:**

```
Principio general: descartar es una decision que tomas por ella y no deja rastro; marcar
se la deja a ella y le cuesta un vistazo. Ante la duda, marca en vez de descartar.

DESCARTA de verdad, sin marcar, solo esto:
1. El frontend o la IA no son EL TRABAJO, sino un anadido. Lee la DESCRIPCION, no el
   titulo. "Java y React" sobra; "React/TypeScript con algo de .NET Core" vale. Si el
   puesto es backend y el frontend aparece de refuerzo, fuera.
2. No es Senior, Staff, Lead, Principal ni Architect.
3. Es presencial, o hibrida fuera de Madrid, cuando el dato sea EXPLICITO.

MARCA, y deja pasar, empezando el campo Notas con la marca:
- Salario por debajo del suelo: "BAJO SUELO: <la cifra>". Una oferta de 50k donde todo lo
  demas encaja puede valer mas que una de 65k que no le gusta. Ella decide.

SUELO SALARIAL, segun el tipo de contrato:
- Contrato: 60.000 EUR brutos anuales.
- Freelance o por horas: 400 EUR al dia, o 50 EUR la hora. Es la equivalencia aproximada
  de esos 60.000 por cuenta ajena, contando cuota de autonomos, vacaciones no pagadas y
  huecos entre proyectos. Veronica esta de alta como autonoma: el freelance SI le interesa.
- Si la tarifa viene en dolares, conviertela antes de comparar.
- Sin salario indicado: no marques nada, pasa por seniority.

NUNCA ASUMAS LA MODALIDAD. Si la oferta no dice si es remota o hibrida, deja Modalidad
VACIA y dilo en Notas. Rellenarla a ojo es peor que dejarla en blanco: es un filtro duro,
y una presencial colada como hibrida le cuesta un proceso entero, no un clic.

ORDEN entre las que sobreviven: 1) encaje real con su perfil y stack; 2) salario mas alto
primero; 3) remoto antes que hibrido.

IMPORTANTE: devuelve como maximo 5, pero puedes devolver MENOS, incluso NINGUNA.
Un array vacio [] es una respuesta valida y correcta cuando ninguna oferta pasa los
filtros. NO rellenes hasta cinco. Prefiero cero ofertas a una oferta mala.
```

**Donde dice** `con las 5 MEJORES`, **poner** `con las que hayan pasado los filtros, como
maximo 5`.

## Corrección 3: rellenar `Tipo Contrato`

El campo existe en el schema de Notion y hoy está vacío en todas las ofertas menos en la de
Tenth Revolution. Sin él no se puede comparar un salario anual con una tarifa por hora.

En el nodo que escribe en Notion, añadir `Tipo Contrato` (texto): "Indefinido", "Freelance",
"Temporal", lo que diga la oferta. Vacío si no lo dice.

## Antes de tocar nada

El workflow puede haber cambiado desde el 21 de julio, que es la fecha del export sobre el
que está escrito esto. Antes de pegar, comprobar en n8n que los nodos siguen llamándose
`Formatear ofertas` y `Groq - Generar Ofertas`, y que el código de `matchea` sigue teniendo
el `&&`. El repositorio no puede decir qué hay en n8n hoy.

## Efecto secundario que hay que vigilar

Si el nodo de Groq puede devolver un array vacío, el resto del workflow tiene que
aguantarlo sin romperse: el nodo de Notion no debe crear páginas y el de Brevo no debe
mandar un correo vacío. **Sin verificar.** Hay que mirarlo en n8n antes de dar el cambio
por bueno.

---

**Generado:** 23 de julio de 2026. Reescrito el mismo día tras comprobar que el bloqueo duro
por stack ajeno tiraba ofertas buenas.
