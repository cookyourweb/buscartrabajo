#!/usr/bin/env node
// Saca los paths de webhook de exports crudos de n8n que ya estan en el repo.
//
// `wf-split` redacta al partir un workflow nuevo. Esto es para los que YA
// existen: los nueve `BACKUP-*.json` que se exportaron a mano durante el verano,
// antes de que wf-split existiera, y que llevan los paths EN CLARO. Este
// repositorio es publico y tres de esos webhooks no piden credencial (issue #1),
// asi que el path es lo unico que los protege.
//
// Uso:  node scripts/wf-redact.mjs <fichero.json> [...]
//       node scripts/wf-redact.mjs workflows/PROD/BACKUP-*.json
//
// Reescribe cada fichero en su sitio y acumula los secretos encontrados en
// workflows/PROD/secrets.local.json (ignorado por git), fusionandolos con lo que
// ya hubiera. La redaccion es idempotente: pasarlo dos veces no hace nada.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { redactarPaths, fusionarSecretos } from './lib/secretos.mjs';

const FICHERO_SECRETOS = 'workflows/PROD/secrets.local.json';

const ficheros = process.argv.slice(2);
if (!ficheros.length) {
  console.error('uso: node scripts/wf-redact.mjs <fichero.json> [...]');
  process.exit(1);
}

let acumulados = existsSync(FICHERO_SECRETOS)
  ? JSON.parse(readFileSync(FICHERO_SECRETOS, 'utf8'))
  : {};

let tocados = 0;
let encontrados = 0;

for (const ruta of ficheros) {
  const original = JSON.parse(readFileSync(ruta, 'utf8'));
  const { workflow, secretos } = redactarPaths(original);
  const nombres = Object.keys(secretos);

  if (!nombres.length) {
    console.log(`  limpio ya   ${ruta}`);
    continue;
  }

  writeFileSync(ruta, JSON.stringify(workflow, null, 2) + '\n');
  acumulados = fusionarSecretos(acumulados, secretos);
  tocados++;
  encontrados += nombres.length;
  console.log(`  REDACTADO   ${ruta}  (${nombres.join(', ')})`);
}

if (tocados) {
  writeFileSync(FICHERO_SECRETOS, JSON.stringify(acumulados, null, 2) + '\n');
}

console.log(`\n${ficheros.length} ficheros | ${tocados} redactados | ${encontrados} paths fuera del repo`);
console.log(`secretos en ${FICHERO_SECRETOS} (fuera de git)`);
