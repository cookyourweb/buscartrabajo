// El nodo "Formatear ofertas" de n8n no es un modulo: es el cuerpo de una funcion
// que n8n ejecuta con `$` en el ambito. Aqui se ejecuta igual, con un `$` falso
// que devuelve lo que devolverian los nodos anteriores.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const codigo = readFileSync(
  new URL('../workflows/PROD/nodes/formatear-ofertas.js', import.meta.url),
  'utf8',
);

const ejecutar = (nodos) => {
  const $ = (nombre) => {
    const salida = nodos[nombre] ?? [];
    return {
      item: { json: salida[0] ?? {} },
      first: () => ({ json: salida[0] ?? {} }),
      all: () => salida.map((json) => ({ json })),
    };
  };
  return new Function('$', codigo)($)[0].json;
};

const paginaNotion = (link, empresa = '', puesto = '') => ({
  properties: {
    'Link oferta': { url: link },
    Empresa: { title: [{ plain_text: empresa }] },
    Puesto: { rich_text: [{ plain_text: puesto }] },
  },
});

const ofertaAdzuna = (link, titulo, empresa) => ({
  redirect_url: link,
  title: titulo,
  description: 'We build LLM agents with TypeScript and Python.',
  company: { display_name: empresa },
  location: { display_name: 'Madrid' },
});

const USUARIO = [{ email: 'test@example.com', stack: [] }];
const LINK_REPETIDO = 'https://www.adzuna.es/details/5887440247?utm_medium=api&utm_source=524625d0';

test('una oferta de Adzuna que ya esta en Notion no se vuelve a crear', () => {
  const salida = ejecutar({
    'Loop Over Users': USUARIO,
    'Notion - Ofertas existentes': [
      { results: [paginaNotion('https://otra.example/1'), paginaNotion(LINK_REPETIDO)] },
    ],
    'Buscar en Adzuna': [
      { results: [ofertaAdzuna(LINK_REPETIDO, 'Senior Software Engineer AI Agentic Workflows', 'AgileEngine')] },
    ],
  });
  assert.equal(salida.total, 0, 'la oferta repetida se coló como nueva');
});

test('el dedup lee todas las paginas de Notion, no solo la primera', () => {
  const salida = ejecutar({
    'Loop Over Users': USUARIO,
    'Notion - Ofertas existentes': [
      { results: [paginaNotion('https://otra.example/1')] },
      { results: [paginaNotion(LINK_REPETIDO)] },
    ],
    'Buscar en Adzuna': [
      { results: [ofertaAdzuna(LINK_REPETIDO, 'Senior Software Engineer AI Agentic Workflows', 'AgileEngine')] },
    ],
  });
  assert.equal(salida.total, 0, 'la oferta de la segunda pagina se coló como nueva');
});

test('una oferta que no esta en Notion si entra', () => {
  const salida = ejecutar({
    'Loop Over Users': USUARIO,
    'Notion - Ofertas existentes': [{ results: [paginaNotion('https://otra.example/1')] }],
    'Buscar en Adzuna': [
      { results: [ofertaAdzuna('https://www.adzuna.es/details/1', 'Senior AI Engineer', 'Nueva SL')] },
    ],
  });
  assert.equal(salida.total, 1);
});
