// Las preguntas abiertas de un formulario tienen sus reglas en
// docs/reference/21-FORM-ANSWER-RULES.md: vocabulario profesional, voz humana.
// El 26-oct, ademas, Vero pidio no nombrar sus proyectos y no confesar huecos.
// Estos tests fijan lo que se puede comprobar sin leer la mente: los
// conectores de informe, los nombres de proyecto, los huecos y las rayas.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validarRespuesta, pareceRespuesta } from '../scripts/lib/respuesta.mjs';

const BUENA = `A multi-user dashboard that I built and run in production, on my own.

Front end: an Angular application with signals. I designed the component structure, forms and state, and wrote the component tests.

Back end: the Python service it talks to. I designed the REST API and the data model with each user's data isolated. The hard part was never writing good text; it was knowing when a fluent answer was wrong.`;

// Respuesta real de Siena (26-oct, primera version): nombra los proyectos.
const CON_PROYECTOS = `Nova, the AI chat inside Tu Vuelta al Sol (tuvueltalsol.es), a SaaS I built and run in production since August 2025. I owned it end to end: product, prompts, backend and UI. I applied the same lesson in cv-server (public on GitHub): a spending cap is checked before any model call.`;

// Respuesta real de OpenNebula (26-oct): confiesa un hueco.
const CON_HUECO = `Most of my career has been on the front end, and since 2025 I also build and run the back end myself. Infrastructure software and virtualization would be new ground for me, and it is a part of the role I would genuinely enjoy learning.`;

const DE_INFORME = `The challenge was therefore not simply generating good text. Moreover, the system had a specific reliability problem, which created a gap between what the model said and what was true. The main lesson was that context injection is not evidence of context use.`;

test('una respuesta con voz humana pasa', () => {
  assert.deepEqual(validarRespuesta(BUENA), []);
});

test('nombrar los proyectos falla', () => {
  const errores = validarRespuesta(CON_PROYECTOS);
  assert.ok(errores.some((e) => /proyecto/i.test(e)), errores.join('\n'));
});

test('confesar un hueco falla', () => {
  const errores = validarRespuesta(CON_HUECO);
  assert.ok(errores.some((e) => /hueco/i.test(e)), errores.join('\n'));
});

test('los conectores de informe fallan', () => {
  const errores = validarRespuesta(DE_INFORME);
  assert.ok(errores.some((e) => /informe/i.test(e)), errores.join('\n'));
});

test('los conectores de informe en español también fallan', () => {
  const es = 'El reto, por lo tanto, no era generar buen texto. Cabe destacar que el sistema fallaba sin avisar y además nadie lo veía hasta que un usuario se quejaba de una respuesta que parecía correcta.';
  assert.ok(validarRespuesta(es).some((e) => /informe/i.test(e)));
});

test('"y además" dentro de una frase pasa; "Además," abriendo frase falla', () => {
  const natural = 'Lo monté yo sola y además lo despliego yo, así que cuando algo falla lo veo antes que nadie y sé dónde mirar porque conozco cada parte del sistema de punta a punta.';
  const informe = 'Lo monté yo sola. Además, lo despliego yo, así que cuando algo falla lo veo antes que nadie y sé dónde mirar porque conozco cada parte del sistema de punta a punta.';
  assert.deepEqual(validarRespuesta(natural), []);
  assert.ok(validarRespuesta(informe).some((e) => /informe/i.test(e)));
});

test('las palabras de venta vacías fallan', () => {
  const venta = 'I am passionate about building products and I would love to leverage my experience to drive impact in a fast-paced environment where I can grow and learn every single day with a great team.';
  assert.ok(validarRespuesta(venta).some((e) => /venta/i.test(e)));
});

test('rayas largas y flechas fallan', () => {
  assert.ok(validarRespuesta(BUENA.replace('on my own.', 'on my own — alone.')).some((e) => /raya|flecha/i.test(e)));
  assert.ok(validarRespuesta(BUENA.replace('on my own.', 'build → measure.')).some((e) => /raya|flecha/i.test(e)));
});

test('pareceRespuesta ignora campos cortos', () => {
  assert.equal(pareceRespuesta(BUENA), true);
  assert.equal(pareceRespuesta('Madrid, Spain'), false);
  assert.equal(pareceRespuesta('60000'), false);
  assert.equal(pareceRespuesta('https://www.linkedin.com/in/veronica4web'), false);
});
