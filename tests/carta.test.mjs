// Las reglas de la carta (docs/reference/16-COVER-LETTER-RULES.md) existian
// desde el 31-ago y aun asi el 26-oct salieron cinco cartas que las rompian:
// dos con la plantilla vieja y tres argumentando meritos, una de ellas
// diciendo lo que no sabia hacer. Nadie las comprobaba. Estos casos son esas
// cartas reales: tienen que fallar siempre.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validarCarta, pareceCarta } from '../scripts/lib/carta.mjs';

const PLANTILLA_ES = `Hola,

Soy Verónica Serna, ingeniera de IA. Me ha parecido muy interesante vuestra oferta de Applied AI Engineer, en particular la parte de herramientas internas con LLMs, y creo que puede encajar con lo que hago en mi trabajo.

El detalle está en mi CV. Quedo a vuestra disposición.

Un saludo,
Verónica Serna Pérez`;

const PLANTILLA_EN = `Hi,

I'm Verónica Serna, an AI engineer. I found your Senior Full-Stack Developer opening very interesting, in particular the work on the web interface, and I think it could fit with what I do in my work.

The detail is in my CV. I remain at your disposal.

Best regards,
Verónica Serna Pérez`;

const PLANTILLA_VIEJA = `Hola,

Gracias por la oportunidad. El puesto de Lead Frontend me parece muy interesante y me encantaría participar en el proceso.

Llevo más de diez años trabajando en frontend. Desde 2025 trabajo en proyectos de IA aplicada.

Os adjunto mi CV. Estaré encantada de hablar con vosotros y contaros más sobre los proyectos.

Verónica Serna Pérez`;

const CARTA_OPENNEBULA = `Hi,

I'm interested in this role because you are looking for someone who owns features across the stack and explains the decisions behind them, which is how I like to work.

Most of my career has been on the front end: I led the frontend of my project in a global car-rental platform, moved it from Vue.js to React + TypeScript and built a design system from scratch. Since 2025 I also build and run the back end myself, writing Python services with TDD and documenting trade-offs in ADRs, so the front-end/back-end boundary is now part of my day-to-day work.

Infrastructure software and virtualization would be new ground for me, and it is a part of the role I would genuinely enjoy learning.

Verónica Serna Pérez`;

const CARTA_PANEL = `Hola,

Me interesa este puesto porque buscáis a alguien que lidere técnicamente sin dejar el código, que es como he trabajado los últimos años.

En una plataforma global de renting de coches B2B y B2C fui responsable del frontend de mi proyecto: definí la migración de Vue.js a React + TypeScript (arquitectura, patrones de estado y estándares de código) y construí un design system propio desde cero. Coordinaba los contratos de datos con backend, consumiendo microservicios en Azure, y desplegaba con CI/CD.

Desde 2025 desarrollo full-stack con Node.js y Python e integro LLMs en producción con validaciones y guardrails, documentando las decisiones de arquitectura en ADRs.

Inglés C1 y disponibilidad inmediata.

Verónica Serna Pérez`;

test('la plantilla de la regla 16 en español pasa', () => {
  assert.deepEqual(validarCarta(PLANTILLA_ES), []);
});

test('la plantilla de la regla 16 en inglés pasa', () => {
  assert.deepEqual(validarCarta(PLANTILLA_EN), []);
});

test('la plantilla vieja ("Gracias por la oportunidad") falla', () => {
  const errores = validarCarta(PLANTILLA_VIEJA);
  assert.ok(errores.some((e) => /plantilla vieja/i.test(e)), errores.join('\n'));
});

test('la carta de OpenNebula falla: argumenta méritos y confiesa un hueco', () => {
  const errores = validarCarta(CARTA_OPENNEBULA);
  assert.ok(errores.some((e) => /mérito/i.test(e)), errores.join('\n'));
  assert.ok(errores.some((e) => /hueco/i.test(e)), errores.join('\n'));
  assert.ok(errores.some((e) => /palabras/i.test(e)), errores.join('\n'));
});

test('la carta de PANEL falla: méritos, más de 100 palabras y sin "puede encajar"', () => {
  const errores = validarCarta(CARTA_PANEL);
  assert.ok(errores.some((e) => /mérito/i.test(e)), errores.join('\n'));
  assert.ok(errores.some((e) => /palabras/i.test(e)), errores.join('\n'));
  assert.ok(errores.some((e) => /puede encajar/i.test(e)), errores.join('\n'));
});

test('una carta sin "El detalle está en mi CV" falla', () => {
  const sinCierre = PLANTILLA_ES.replace('El detalle está en mi CV. ', '');
  assert.ok(validarCarta(sinCierre).some((e) => /detalle está en mi CV/i.test(e)));
});

test('rayas largas y flechas fallan', () => {
  const conRaya = PLANTILLA_ES.replace('Hola,', 'Hola —');
  const conFlecha = PLANTILLA_ES.replace('Hola,', 'Hola →');
  assert.ok(validarCarta(conRaya).some((e) => /raya|flecha/i.test(e)));
  assert.ok(validarCarta(conFlecha).some((e) => /raya|flecha/i.test(e)));
});

test('una carta en español sin tildes falla', () => {
  const sinTildes = PLANTILLA_ES.normalize('NFD').replace(/[̀-ͯ]/g, '');
  assert.ok(validarCarta(sinTildes).some((e) => /tilde/i.test(e)));
});

test('el tono asertivo ("hecho para mí") falla', () => {
  const asertiva = PLANTILLA_ES.replace('creo que puede encajar con lo que hago en mi trabajo', 'este puesto está hecho para mí, y creo que puede encajar');
  assert.ok(validarCarta(asertiva).some((e) => /asertiv/i.test(e)));
});

test('pareceCarta reconoce una carta y deja pasar un nombre o un email', () => {
  assert.equal(pareceCarta(PLANTILLA_ES), true);
  assert.equal(pareceCarta(CARTA_OPENNEBULA), true);
  assert.equal(pareceCarta('Verónica'), false);
  assert.equal(pareceCarta('verserper@gmail.com'), false);
  assert.equal(pareceCarta('60000'), false);
});
