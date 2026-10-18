// wf-split, de punta a punta: parte un export y NADA de lo que deja para git
// puede llevar la ruta de un webhook.
//
// 18-oct-2026: wf-split tenia su propia redaccion, que solo limpiaba el campo
// `path`. `redactarPaths` (scripts/lib/secretos.mjs) ya limpiaba tambien el
// codigo de los nodos desde el 31-ago, pero wf-split no la usaba. Al partir el
// export de PROD, las rutas de aprobar, descartar y mandar-empresa quedaron en
// claro en nodes/*.js, a un commit de un repositorio PUBLICO.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), '..', 'scripts', 'wf-split.mjs');
const RUTA = 'aprobar-ruta-real-que-no-debe-publicarse';

const exportDePrueba = {
  name: 'PROD',
  nodes: [
    { name: 'Webhook Aprobar', type: 'n8n-nodes-base.webhook', parameters: { path: RUTA } },
    {
      name: 'Code - Preparar Email',
      type: 'n8n-nodes-base.code',
      parameters: { jsCode: `return '<a href="https://host/webhook/${RUTA}?id=' + id + '">';` },
    },
  ],
  connections: {},
};

function partir() {
  const dir = mkdtempSync(join(tmpdir(), 'wf-split-'));
  const src = join(dir, 'export.json');
  writeFileSync(src, JSON.stringify(exportDePrueba));
  const dest = join(dir, 'PROD');
  execFileSync('node', [SCRIPT, src, dest], { stdio: 'pipe' });
  return { dir, dest };
}

test('la ruta escrita dentro del codigo de un nodo no llega a nodes/*.js', () => {
  const { dir, dest } = partir();
  try {
    for (const f of readdirSync(join(dest, 'nodes'))) {
      const texto = readFileSync(join(dest, 'nodes', f), 'utf8');
      assert.ok(!texto.includes(RUTA), `${f} lleva la ruta en claro`);
      assert.ok(texto.includes('@@SECRET:Webhook Aprobar'), `${f} perdio el marcador`);
    }
    assert.ok(!readFileSync(join(dest, 'workflow.json'), 'utf8').includes(RUTA));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('la ruta queda guardada en secrets.local.json para que wf-join la restaure', () => {
  const { dir, dest } = partir();
  try {
    const secretos = JSON.parse(readFileSync(join(dest, 'secrets.local.json'), 'utf8'));
    assert.deepEqual(secretos, { 'Webhook Aprobar': RUTA });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
