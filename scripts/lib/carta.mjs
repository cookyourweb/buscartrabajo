// Comprueba una carta de presentacion contra docs/reference/16-COVER-LETTER-RULES.md.
//
// La regla de fondo: la carta no argumenta, abre la puerta. El CV es el que
// argumenta. Por eso aqui se rechaza cualquier merito, cualquier hueco
// confesado y la plantilla vieja, aunque lo que digan sea verdad.
//
// Devuelve una lista de errores en castellano. Lista vacia = la carta pasa.

const MAX_PALABRAS = 100;

const PLANTILLA_VIEJA = [
  /gracias por la oportunidad/i,
  /me encantar[ií]a participar/i,
  /llevo m[aá]s de diez a[nñ]os/i,
  /thank you for the opportunity/i,
  /happy to take part/i,
  /for more than ten years/i,
];

// Verbos y expresiones con los que una carta empieza a venderse.
const MERITOS = [
  /\b(lider[eé]|constru[ií]|dise[nñ][eé]|desarroll[eé]|implement[eé]|defin[ií]|migr[eé]|despleg(u[eé]|aba))\b/i,
  /\b(fui responsable|he trabajado|llevo \d+|a[nñ]os de experiencia|desde 20\d\d (trabajo|desarrollo))\b/i,
  /\b(led|built|designed|developed|implemented|defined|migrated|deployed|shipped|owned)\b/i,
  /\b(years of experience|most of my career|i('ve| have) (been )?work(ed|ing))\b/i,
];

// Lo que no se sabe hacer no se dice en la carta: se prepara para la llamada.
const HUECOS = [
  /no tengo experiencia|nunca he (trabajado|usado)|aunque no (he|tengo|s[eé])|ser[ií]a nuevo para m[ií]/i,
  /new ground|i (have not|haven'?t) (used|worked)|no experience (with|in)|although i (don'?t|haven'?t)/i,
];

const ASERTIVO = [
  /hecho para m[ií]|encaja perfectamente|perfil ideal|soy la persona/i,
  /made for me|perfect fit|ideal candidate|i am the right person/i,
];

const esEspanol = (texto) =>
  /^\s*(hola|buenas|estimad)/i.test(texto) || /\b(vuestra|oferta|puesto|detalle)\b/i.test(texto);

export const contarPalabras = (texto) => texto.trim().split(/\s+/).filter(Boolean).length;

// Un campo de formulario corto (nombre, email, salario) no es una carta.
export const pareceCarta = (texto) =>
  typeof texto === 'string' &&
  /^\s*(hola|hi|hello|dear|buenas|estimad)\b/i.test(texto) &&
  contarPalabras(texto) >= 25;

export function validarCarta(texto) {
  const errores = [];
  const es = esEspanol(texto);

  if (PLANTILLA_VIEJA.some((r) => r.test(texto))) {
    errores.push('Usa la plantilla vieja ("Gracias por la oportunidad…"). La válida es la de la regla 16.');
  }

  const palabras = contarPalabras(texto);
  if (palabras > MAX_PALABRAS) {
    errores.push(`Tiene ${palabras} palabras; el máximo son ${MAX_PALABRAS} (objetivo 50-70).`);
  }

  const merito = MERITOS.map((r) => texto.match(r)).find(Boolean);
  if (merito) {
    errores.push(`Argumenta un mérito ("${merito[0]}"). La carta no argumenta: los méritos están en el CV.`);
  }

  const hueco = HUECOS.map((r) => texto.match(r)).find(Boolean);
  if (hueco) {
    errores.push(`Confiesa un hueco ("${hueco[0]}"). Lo que no sabes hacer no va en la carta: se prepara para la llamada.`);
  }

  const asertivo = ASERTIVO.map((r) => texto.match(r)).find(Boolean);
  if (asertivo) {
    errores.push(`Tono asertivo ("${asertivo[0]}"). Tiene que ser una hipótesis: "creo que puede encajar".`);
  }

  if (/[—–→]|->/.test(texto)) {
    errores.push('Tiene una raya larga o una flecha. Cero rayas largas y cero flechas.');
  }

  if (es) {
    if (!/puede encajar/i.test(texto)) {
      errores.push('Falta "creo que puede encajar con lo que hago en mi trabajo".');
    }
    if (!/el detalle est[aá] en mi CV/i.test(texto)) {
      errores.push('Falta el cierre "El detalle está en mi CV."');
    }
    if (!/[áéíóúñÁÉÍÓÚÑ]/.test(texto)) {
      errores.push('Está en español y no lleva ni una tilde.');
    }
  } else {
    if (!/could fit/i.test(texto)) {
      errores.push('Missing "I think it could fit with what I do in my work".');
    }
    if (!/detail is in my CV/i.test(texto)) {
      errores.push('Missing the closing "The detail is in my CV."');
    }
  }

  return errores;
}
