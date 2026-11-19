// Comprueba una respuesta a una pregunta abierta de un formulario contra
// docs/reference/21-FORM-ANSWER-RULES.md y lo que Vero pidio el 26-oct.
//
// Solo mira lo que se puede comprobar sin juzgar el fondo: que no suene a
// informe, que no nombre sus proyectos, que no confiese huecos, que no se
// venda con palabras vacias y que no lleve rayas largas ni flechas. Si el
// contenido es bueno lo sigue decidiendo una persona.
//
// Devuelve una lista de errores en castellano. Lista vacia = pasa.

// Regla 21: "Out: therefore, moreover, thus, which created, the main lesson
// was, it is worth noting that". Y sus primos en castellano.
const INFORME = [
  /\b(therefore|moreover|thus|furthermore|hence|consequently)\b/i,
  /which created|the main (lesson|challenge) was|it is worth noting|in conclusion/i,
  /\b(por lo tanto|por consiguiente|asimismo|cabe destacar|cabe se[nñ]alar|en conclusi[oó]n|la principal lecci[oó]n fue)\b/i,
  // "y además" dentro de una frase es natural; "Además," abriendo frase, no.
  /(^|[.!?]\s+)ademá?a?s,/i,
];

// Sus proyectos se describen, no se nombran (26-oct).
const PROYECTOS = /\b(cv-server|tu vuelta al sol|tuvueltalsol|nova|panel-empleo|empleo\.cookyourwebai|reformas maestras|buscartrabajo)\b/i;

// Lo que no sabe hacer no se escribe: se prepara para la llamada.
const HUECOS = [
  /no tengo experiencia|nunca he (trabajado|usado)|aunque no (he|tengo|s[eé])|ser[ií]a nuevo para m[ií]/i,
  /new ground|i (have not|haven'?t) (used|worked)|no experience (with|in)|although i (don'?t|haven'?t)|not familiar with/i,
];

const VENTA = [
  /\b(passionate|thrilled|leverage|synergy|go-getter|rockstar|fast-paced environment)\b/i,
  /\b(apasionad[ao]|me entusiasma enormemente|sinergia|aportar un gran valor|altamente motivad[ao])\b/i,
];

const contarPalabras = (texto) => texto.trim().split(/\s+/).filter(Boolean).length;

// Una respuesta abierta es texto de varias frases. Un nombre, una ciudad, un
// salario o una URL no lo son.
export const pareceRespuesta = (texto) =>
  typeof texto === 'string' && !/^\s*https?:\/\//i.test(texto) && contarPalabras(texto) >= 25;

export function validarRespuesta(texto) {
  const errores = [];

  const informe = INFORME.map((r) => texto.match(r)).find(Boolean);
  if (informe) {
    errores.push(`Suena a informe ("${informe[0]}"). Regla 21: voz humana, sin esos conectores.`);
  }

  const proyecto = texto.match(PROYECTOS);
  if (proyecto) {
    errores.push(`Nombra un proyecto ("${proyecto[0]}"). Descríbelo: qué implementaste y cómo resolviste los problemas.`);
  }

  const hueco = HUECOS.map((r) => texto.match(r)).find(Boolean);
  if (hueco) {
    errores.push(`Confiesa un hueco ("${hueco[0]}"). Eso no se escribe: se prepara para la llamada.`);
  }

  const venta = VENTA.map((r) => texto.match(r)).find(Boolean);
  if (venta) {
    errores.push(`Palabra de venta vacía ("${venta[0]}"). Mejor un hecho concreto.`);
  }

  if (/[—–→]|->/.test(texto)) {
    errores.push('Tiene una raya larga o una flecha. Cero rayas largas y cero flechas.');
  }

  return errores;
}
