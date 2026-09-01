# Fix del idioma de la carta y el CV

> Escrito el 23 de julio de 2026, después de que la carta de una oferta en inglés
> (Revolut) saliera en español. El CV acertaba y la carta no, para la misma oferta.

## Qué pasaba

El idioma del CV y de la carta no llegaban desde n8n. El cv-server intentaba recuperarlo
buscando la oferta en Notion por **Empresa + Puesto exacto** (`buscar_oferta_en_notion`,
`cv_server_railway.py:643`, filtro `equals`). Cualquier diferencia mínima entre el puesto
que manda n8n y el guardado en Notion (un espacio, un `(78K-98K)`, una tilde) rompía el
match. Sin match, el idioma caía a la detección automática, y esa leía la **descripción**,
que la tarea programada reescribe **siempre en español**. Resultado: carta en español
aunque la oferta fuera inglesa.

## Los dos frentes del arreglo

### Frente 1: cv-server (hecho, commit en develop)

Nueva función `idioma_de_oferta(puesto, descripcion, empresa)`: **el título del puesto
manda**. Viene tal cual del anuncio, en su idioma. La descripción, reescrita en español,
ya no puede ahogar la señal del título. Solo si el título no da señal se mira la
descripción. Con tests, incluido el caso Revolut.

Esto es la RED DE SEGURIDAD. No arregla la causa: solo hace que, cuando el idioma se tenga
que adivinar, se adivine bien.

### Frente 2: n8n (pendiente, hay que pegarlo)

**La causa se arregla mandando el idioma explícito desde n8n**, que ya lo tiene en la
propiedad `Idioma` de la oferta. Así el cv-server no busca nada ni adivina nada: usa el
idioma que le llega. CV y carta quedan garantizados iguales.

En los dos nodos que llaman al cv-server, `CV Server - Generar CV` y `Groq - Generar
Carta`, añadir `idioma` al JSON del body. Hoy el body es:

```js
{
  email:       ...,
  empresa:     ...['Empresa']...,
  puesto:      ...['Puesto']...,
  descripcion: ...['Descripción']... || ...Notas...
}
```

Añadir esta línea dentro del objeto, en los DOS nodos:

```js
  idioma: $('Notion - Obtener Datos Oferta').first().json.properties['Idioma']?.select?.name || ''
```

`$('Notion - Obtener Datos Oferta')` es el nodo del que ya salen `empresa`, `puesto` y
`descripcion` en ese body, así que la referencia es la misma que ya usan. Si en tu workflow
el nodo tuviera otro nombre, usa el mismo que aparece en las otras líneas del body.

Un `idioma` vacío no rompe nada: el cv-server cae a su red de seguridad (Frente 1).

## Cómo comprobar que quedó bien

Genera el CV y la carta de una oferta claramente en inglés (por ejemplo Revolut, "Applied
AI Engineer"). Los dos deben salir en inglés. Antes, la carta salía en español.

## Antes de tocar n8n

El export sobre el que está escrito esto es del 21 de julio. Comprueba que los nodos
`CV Server - Generar CV` y `Groq - Generar Carta` siguen existiendo con ese nombre y que su
body sigue teniendo la forma de arriba.

---

**Generado:** 23 de julio de 2026.
