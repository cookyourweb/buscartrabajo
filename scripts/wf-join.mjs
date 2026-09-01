#!/usr/bin/env node
// Reconstruye el JSON de n8n desde las piezas de workflows/PROD/.
// Es la vuelta de wf-split: se edita el .js en el editor, y esto arma el
// fichero que se importa en n8n. Asi el cambio pasa por git ANTES que por la UI.
//
// Uso:  node scripts/wf-join.mjs [origen] [salida.json]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { restaurarSecretosEnTexto, rutasLiterales, PREFIJO_SECRETO } from './lib/secretos.mjs';

const [dir = 'workflows/PROD', out = 'workflows/PROD/_importar.json'] = process.argv.slice(2);
const wf = JSON.parse(readFileSync(join(dir, 'workflow.json'), 'utf8'));

// Los paths de webhook viven fuera de git (ver wf-split). Sin este fichero el
// workflow se reconstruye con los marcadores y n8n registraria rutas absurdas:
// mejor parar y decirlo.
let secretos = {};
try { secretos = JSON.parse(readFileSync(join(dir, 'secrets.local.json'), 'utf8')); }
catch { }

let n = 0, faltan = [], rutasMuertas = [], marcadoresHuerfanos = [];
for (const nodo of wf.nodes) {
  const p = nodo.parameters || {};
  if (typeof p.path === 'string' && p.path.startsWith('@@SECRET:')) {
    const real = secretos[nodo.name];
    if (real) { p.path = real; n++; } else faltan.push(nodo.name);
  }
  // El fichero del nodo entra tal cual, y dentro puede llevar marcadores: los
  // enlaces de los correos de aprobar, descartar y mandar-empresa se arman ahi.
  // Restaurar solo `path` dejaba esos enlaces con lo que hubiera escrito, que
  // el 1-sep-2026 eran las rutas VIEJAS. Los correos salian a rutas muertas.
  for (const campo of ['jsCode', 'jsonBody']) {
    const v = p[campo];
    if (typeof v === 'string' && v.startsWith('@@FILE:')) {
      const contenido = readFileSync(join(dir, v.slice(7)), 'utf8');
      p[campo] = restaurarSecretosEnTexto(contenido, secretos);
      n++;

      const literales = rutasLiterales(p[campo]).filter((r) => !Object.values(secretos).includes(r));
      if (literales.length) rutasMuertas.push(`${nodo.name}: ${literales.join(', ')}`);
      if (p[campo].includes(PREFIJO_SECRETO)) marcadoresHuerfanos.push(nodo.name);
    }
  }
}

// Una ruta escrita a mano que no es ninguna de las vivas es una ruta ROTADA: se
// va a importar a n8n y el enlace del correo llevara a un 404. Parar es mejor
// que descubrirlo cuando alguien pulse "Aprobar" en un correo.
if (rutasMuertas.length) {
  console.error('RUTAS MUERTAS escritas a mano en el codigo de estos nodos:');
  for (const r of rutasMuertas) console.error(`  - ${r}`);
  console.error(`Sustituilas por ${PREFIJO_SECRETO}<nombre del nodo webhook> y volve a intentarlo.`);
  process.exit(3);
}

if (marcadoresHuerfanos.length) {
  console.error('MARCADORES sin ruta viva en el codigo de estos nodos:');
  for (const nombre of marcadoresHuerfanos) console.error(`  - ${nombre}`);
  console.error(`El nombre del marcador tiene que coincidir con una clave de secrets.local.json.`);
  process.exit(4);
}
if (faltan.length) {
  console.error(`FALTAN los paths de estos webhook en ${join(dir, 'secrets.local.json')}:`);
  for (const f of faltan) console.error(`  - ${f}`);
  console.error('Ese fichero no esta en git a proposito. Recuperalos de n8n antes de importar.');
  process.exit(2);
}
writeFileSync(out, JSON.stringify(wf, null, 2) + '\n');
console.log(`${dir} -> ${out}  (${n} valores restaurados, ${wf.nodes.length} nodos)`);
