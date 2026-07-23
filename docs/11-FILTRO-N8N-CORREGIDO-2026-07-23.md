# Filtro de ofertas de n8n, corregido

> Escrito el 23 de julio de 2026, después de comprobar que el workflow manda ofertas de
> Java, .NET e Ionic a una desarrolladora de React y Vue.
>
> Objetivo: que n8n use los mismos criterios duros que la tarea programada de Claude, que
> sí filtra bien.

## Los dos fallos

### 1. El `&&` deja pasar el stack ajeno

En el nodo **`Formatear ofertas`**, función `matchea`:

```js
if (esOtroPerfil && !tieneSenal) return false;
return tieneSenal;
```

Una oferta de backend que además mencione una palabra del perfil, pasa. Y en España casi
todas las ofertas mezclan las dos cosas.

Las cuatro ofertas del 20 de julio de 2026, que llegaron al correo de Verónica:

| Título | Por qué coló |
|---|---|
| Programador/a Senior .NET + Angular | `.net` excluye, `angular` incluye |
| Tech Lead ó Analista Fullstack Java | `java` excluye, `tech lead` incluye |
| Desarrollador/a Java Ionic Angular | `java` excluye, `angular` incluye |
| Desarrollador/a Node con Inglés | `node` está en `INCLUIR` |

### 2. El ranking no tiene suelo

En el nodo **`Groq - Generar Ofertas`**, el prompt pide:

> Devuelve SOLO un array JSON con las **5 MEJORES**

Siempre devuelve cinco, haya o no cinco buenas. Un ranking sin suelo siempre produce algo:
si el día no trae nada que valga, manda lo menos malo y el sistema parece sano.

La tarea programada de Claude, con los mismos catálogos, descartó la mayoría de 54
resultados y podría haber devuelto cero. Esa es la diferencia.

## Comparación de criterios

| Criterio | Tarea de Claude | n8n hoy |
|---|---|---|
| Stack ajeno | Descarta | Pasa si menciona también algo suyo |
| Seniority | Obligatoria (Senior, Staff, Lead, Principal) | No se mira |
| Modalidad | Remoto, o híbrido solo en Madrid | Solo ordena, no descarta |
| Salario | Descarta por debajo de 60.000 € | Solo ordena, no descarta |
| Puede devolver cero | Sí | No, siempre cinco |

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

  // 2. Stack ajeno: fuera SIEMPRE, aunque el titulo mencione algo de su perfil.
  //    Este es el cambio: antes era "esOtroPerfil && !tieneSenal", y ese && dejaba
  //    pasar "Java + Angular" y ".NET + React".
  if (EXCLUIR_PERFIL.some(k => tit.includes(k))) return false;

  // 3. Tiene que haber senal real de su perfil en el titulo.
  if (!INCLUIR.some(k => tit.includes(k))) return false;

  // 4. Seniority obligatoria.
  if (!SENIORITY.some(k => tit.includes(k))) return false;

  return true;
};
```

**Efecto esperado:** las cuatro ofertas del 20 de julio caen las cuatro. Las tres primeras
por la regla 2, la de Node por la regla 4, que no dice seniority.

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
FILTROS DUROS. Descarta la oferta si incumple CUALQUIERA de estos, sin excepcion:
1. El puesto principal no es del perfil de la usuaria. Una oferta de backend que
   mencione de pasada una tecnologia suya NO cuenta como encaje.
2. No es Senior, Staff, Lead, Principal ni Architect.
3. Es presencial fuera de Madrid, o hibrida fuera de Madrid. Remoto siempre vale.
4. Indica salario y el maximo esta por debajo de 60.000 EUR brutos anuales.
   Si NO indica salario, no la descartes por eso: pasa, pero va abajo del todo.

ORDEN entre las que sobreviven: 1) encaje real con su perfil y stack; 2) salario mas alto
primero; 3) remoto antes que hibrido.

IMPORTANTE: devuelve como maximo 5, pero puedes devolver MENOS, incluso NINGUNA.
Un array vacio [] es una respuesta valida y correcta cuando ninguna oferta pasa los
filtros duros. NO rellenes hasta cinco. Prefiero cero ofertas a una oferta mala.
```

**Donde dice** `con las 5 MEJORES`, **poner** `con las que hayan pasado los filtros duros,
como maximo 5`.

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

**Generado:** 23 de julio de 2026.
