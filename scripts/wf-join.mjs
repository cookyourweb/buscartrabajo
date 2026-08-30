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

let n = 0;
for (const nodo of wf.nodes) {
  const p = nodo.parameters || {};
  for (const campo of ['jsCode', 'jsonBody']) {
    const v = p[campo];
    if (typeof v === 'string' && v.startsWith('@@FILE:')) {
      p[campo] = readFileSync(join(dir, v.slice(7)), 'utf8');
      n++;
    }
  }
}
writeFileSync(out, JSON.stringify(wf, null, 2) + '\n');
console.log(`${dir} -> ${out}  (${n} ficheros incrustados, ${wf.nodes.length} nodos)`);
