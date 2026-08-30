#!/usr/bin/env node
// Reconstruye el JSON de n8n desde las piezas de workflows/PROD/.
// Es la vuelta de wf-split: se edita el .js en el editor, y esto arma el
// fichero que se importa en n8n. Asi el cambio pasa por git ANTES que por la UI.
//
// Uso:  node scripts/wf-join.mjs [origen] [salida.json]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';

const [dir = 'workflows/PROD', out = 'workflows/PROD/_importar.json'] = process.argv.slice(2);
const wf = JSON.parse(readFileSync(join(dir, 'workflow.json'), 'utf8'));

// Los paths de webhook viven fuera de git (ver wf-split). Sin este fichero el
// workflow se reconstruye con los marcadores y n8n registraria rutas absurdas:
// mejor parar y decirlo.
let secretos = {};
try { secretos = JSON.parse(readFileSync(join(dir, 'secrets.local.json'), 'utf8')); }
catch { }

let n = 0, faltan = [];
for (const nodo of wf.nodes) {
  const p = nodo.parameters || {};
  if (typeof p.path === 'string' && p.path.startsWith('@@SECRET:')) {
    const real = secretos[nodo.name];
    if (real) { p.path = real; n++; } else faltan.push(nodo.name);
  }
  for (const campo of ['jsCode', 'jsonBody']) {
    const v = p[campo];
    if (typeof v === 'string' && v.startsWith('@@FILE:')) {
      p[campo] = readFileSync(join(dir, v.slice(7)), 'utf8');
      n++;
    }
  }
}
if (faltan.length) {
  console.error(`FALTAN los paths de estos webhook en ${join(dir, 'secrets.local.json')}:`);
  for (const f of faltan) console.error(`  - ${f}`);
  console.error('Ese fichero no esta en git a proposito. Recuperalos de n8n antes de importar.');
  process.exit(2);
}
writeFileSync(out, JSON.stringify(wf, null, 2) + '\n');
console.log(`${dir} -> ${out}  (${n} valores restaurados, ${wf.nodes.length} nodos)`);
