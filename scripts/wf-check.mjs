#!/usr/bin/env node
// Verificador previo a importar un export de n8n.

import { readFileSync } from 'node:fs';
import { analizarWorkflow } from './lib/wf-check.mjs';

const args = process.argv.slice(2);
const jsonMode = args.includes('--json');
const src = args.find((a) => !a.startsWith('--'));

if (!src) {
  console.error('uso: node scripts/wf-check.mjs <export.json> [--json]');
  process.exit(1);
}

let wf;
try {
  wf = JSON.parse(readFileSync(src, 'utf8'));
} catch (e) {
  if (jsonMode) console.log(JSON.stringify({ ok: false, nodes: 0, code_nodes: 0, warnings: [], errors: [String(e.message)], reviewed: true }, null, 2));
  else console.error(`JSON invalido o no parseable: ${e.message}`);
  process.exit(1);
}

const resultado = analizarWorkflow(wf);

if (jsonMode) {
  console.log(JSON.stringify(resultado, null, 2));
  process.exit(resultado.ok ? 0 : 1);
}

const ROJO = '\x1b[31m', VERDE = '\x1b[32m', AMBAR = '\x1b[33m', FIN = '\x1b[0m';
console.log(`${wf.nodes?.length ?? 0} nodos | ${resultado.code_nodes} de codigo`);
for (const a of resultado.warnings) console.log(`  AVISO  ${a}`);
for (const f of resultado.errors) console.log(`  FALLO  ${f}`);
console.log(resultado.ok ? `\n${VERDE}OK — se puede importar${FIN}` : `\n${resultado.errors.length} FALLO(S) — no importar`);
process.exit(resultado.ok ? 0 : 1);