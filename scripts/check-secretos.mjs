#!/usr/bin/env node
// Impide que una ruta de webhook entre en el repositorio.
//
// El 31-ago-2026 se descubrio que las rutas de tres webhooks GET sin
// autenticacion llevaban meses publicadas en un repositorio PUBLICO: en el
// README, en la documentacion y dentro de once backups del workflow. Nadie lo
// vio porque nada lo miraba.
//
// Escribirlo en una guia de estilo no habria servido. Esto si: corre en el hook
// de pre-commit y en CI, y devuelve 1.
//
// DOS COMPROBACIONES, y la primera es la que importa:
//
//   1. POR FORMA (siempre, tambien en CI). Un nodo webhook cuyo `path` no sea
//      `@@SECRET:<nodo>` es una ruta en claro. No hace falta conocer el valor,
//      asi que funciona en un entorno que no tiene los secretos.
//
//   2. POR VALOR (solo en local). Si existe secrets.local.json, busca esas
//      cadenas exactas en TODO fichero versionado: docs, codigo de nodos,
//      exports viejos. Ahi es donde estaban de verdad, y CI no puede verlo.
//
// Uso:  node scripts/check-secretos.mjs
import { readFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { pathsSinRedactar } from './lib/secretos.mjs';

const FICHERO_SECRETOS = 'workflows/PROD/secrets.local.json';
const ROJO = '\x1b[31m', VERDE = '\x1b[32m', AMBAR = '\x1b[33m', FIN = '\x1b[0m';

const versionados = execSync('git ls-files', { encoding: 'utf8' }).split('\n').filter(Boolean);
const fallos = [];

// ── 1. Por forma: un webhook con el path sin redactar ────────────────────────
for (const ruta of versionados.filter((f) => f.endsWith('.json'))) {
  let wf;
  try {
    wf = JSON.parse(readFileSync(ruta, 'utf8'));
  } catch {
    continue;                       // no es JSON valido: no es cosa de esta comprobacion
  }
  const nodos = pathsSinRedactar(wf);
  if (nodos.length) {
    fallos.push(`${ruta}: ${nodos.length} webhook(s) con la ruta en claro (${nodos.join(', ')})`);
  }
}

// ── 2. Por valor: las rutas vivas, en cualquier fichero versionado ───────────
let porValor = 0;
if (existsSync(FICHERO_SECRETOS)) {
  const vivos = Object.entries(JSON.parse(readFileSync(FICHERO_SECRETOS, 'utf8')))
    .filter(([, path]) => typeof path === 'string' && path.length >= 8);

  for (const ruta of versionados) {
    let texto;
    try {
      texto = readFileSync(ruta, 'utf8');
    } catch {
      continue;                     // binario o ilegible
    }
    const encontrados = vivos.filter(([, path]) => texto.includes(path)).map(([nodo]) => nodo);
    if (encontrados.length) {
      fallos.push(`${ruta}: contiene la ruta VIVA de ${encontrados.join(', ')}`);
      porValor++;
    }
  }
} else {
  console.log(`${AMBAR}aviso: no hay ${FICHERO_SECRETOS}, solo se comprueba la forma${FIN}`);
}

// ── Veredicto ────────────────────────────────────────────────────────────────
if (fallos.length) {
  console.error(`\n${ROJO}RUTAS DE WEBHOOK EN EL REPOSITORIO${FIN}\n`);
  for (const f of fallos) console.error(`  ${f}`);
  console.error(`\nEste repositorio es PUBLICO y esos endpoints no piden credencial (issue #1).`);
  console.error(`Saca las rutas con:  npm run wf:redact -- <fichero.json>`);
  if (porValor) {
    console.error(`\n${AMBAR}Si la ruta ya se publico, redactar no basta: hay que ROTARLA en n8n.${FIN}`);
  }
  process.exit(1);
}

console.log(`${VERDE}sin rutas de webhook${FIN} · ${versionados.length} ficheros versionados revisados`);
