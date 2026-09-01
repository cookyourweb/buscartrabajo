#!/usr/bin/env node
// Parte un workflow de n8n en piezas que git SI puede diffear.
//
// El problema: el export es un JSON de 91k en el que cada nodo de codigo vive
// dentro de un string con \n escapados. Un cambio de tres lineas es invisible
// en `git diff`, y por eso los backups solo servian para restaurar entero.
//
// Uso:  node scripts/wf-split.mjs <export.json> [destino]
// Deja: destino/workflow.json      estructura y conexiones, sin los cuerpos
//       destino/nodes/<nodo>.js    un fichero por nodo de codigo
//       destino/nodes/<nodo>.txt   un fichero por cuerpo de peticion (Groq, etc.)
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';

const [src, dest = 'workflows/PROD'] = process.argv.slice(2);
if (!src) { console.error('uso: node scripts/wf-split.mjs <export.json> [destino]'); process.exit(1); }

const slug = (s) => s.toLowerCase()
  .normalize('NFD').replace(/[̀-ͯ]/g, '')
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const wf = JSON.parse(readFileSync(src, 'utf8'));
const nodesDir = join(dest, 'nodes');
if (existsSync(nodesDir)) rmSync(nodesDir, { recursive: true });   // sin restos de nodos borrados
mkdirSync(nodesDir, { recursive: true });

// Los `path` de los webhook son SECRETOS: desde el 30-ago-2026 el webhook de
// busqueda se protege por path impredecible, y este repositorio es PUBLICO.
// Se sacan a secrets.local.json (ignorado por git) y en workflow.json queda un
// marcador. Sin esto, el primer commit publicaria el secreto.
const secretos = {};

let js = 0, bodies = 0;
for (const n of wf.nodes) {
  const p = n.parameters || {};
  if (n.type.endsWith('webhook') && typeof p.path === 'string') {
    secretos[n.name] = p.path;
    p.path = `@@SECRET:${n.name}`;
  }
  if (typeof p.jsCode === 'string') {
    const f = `${slug(n.name)}.js`;
    writeFileSync(join(nodesDir, f), p.jsCode);
    p.jsCode = `@@FILE:nodes/${f}`;
    js++;
  }
  if (typeof p.jsonBody === 'string' && p.jsonBody.length > 400) {
    const f = `${slug(n.name)}.body.txt`;
    writeFileSync(join(nodesDir, f), p.jsonBody);
    p.jsonBody = `@@FILE:nodes/${f}`;
    bodies++;
  }
}
writeFileSync(join(dest, 'workflow.json'), JSON.stringify(wf, null, 2) + '\n');
writeFileSync(join(dest, 'secrets.local.json'), JSON.stringify(secretos, null, 2) + '\n');
console.log(`${basename(src)} -> ${dest}`);
console.log(`  ${wf.nodes.length} nodos | ${js} de codigo | ${bodies} cuerpos extraidos`);
console.log(`  ${Object.keys(secretos).length} paths de webhook -> secrets.local.json (FUERA de git)`);
