#!/usr/bin/env node
// Impide que una ruta de webhook entre en el repositorio.

import { readFileSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { pathsSinRedactar, rutasLiterales } from './lib/secretos.mjs';

const FICHERO_SECRETOS = 'workflows/PROD/secrets.local.json';
const ROJO = '\x1b[31m', VERDE = '\x1b[32m', AMBAR = '\x1b[33m', FIN = '\x1b[0m';

const jsonMode = process.argv.includes('--json');
const versionados = execSync('git ls-files', { encoding: 'utf8' }).split('\n').filter(Boolean);
const violations = [];
const fallos = [];
let porValor = 0;

function anadirViolacion(archivo, tipo, detalle) {
  violations.push({ file: archivo, type: tipo, detail: detalle });
}

// ── 1. Por forma ────────────────────────────────────────────────────────
for (const ruta of versionados.filter((f) => f.endsWith('.json'))) {
  let wf;
  try {
    wf = JSON.parse(readFileSync(ruta, 'utf8'));
  } catch {
    anadirViolacion(ruta, 'invalid-json', 'JSON invalido o no parseable');
    continue;
  }
  const nodos = pathsSinRedactar(wf);
  if (nodos.length) {
    const detalle = `${nodos.length} webhook(s) con la ruta en claro (${nodos.join(', ')})`;
    fallos.push(`${ruta}: ${detalle}`);
    anadirViolacion(ruta, 'clear-webhook-path', detalle);
  }
}

// ── 2. Por valor ─────────────────────────────────────────────────────────
let secretosPresentes = existsSync(FICHERO_SECRETOS);
if (secretosPresentes) {
  const vivos = Object.entries(JSON.parse(readFileSync(FICHERO_SECRETOS, 'utf8')))
    .filter(([, path]) => typeof path === 'string' && path.length >= 8);

  for (const ruta of versionados) {
    let texto;
    try {
      texto = readFileSync(ruta, 'utf8');
    } catch {
      continue;
    }
    const encontrados = vivos.filter(([, path]) => texto.includes(path)).map(([nodo]) => nodo);
    if (encontrados.length) {
      const detalle = `contiene la ruta VIVA de ${encontrados.join(', ')}`;
      fallos.push(`${ruta}: ${detalle}`);
      anadirViolacion(ruta, 'live-webhook-path', detalle);
      porValor++;
    }
  }
} else {
  console.log(`${AMBAR}aviso: no hay ${FICHERO_SECRETOS}, solo se comprueba la forma${FIN}`);
}

// ── 3. Rutas literales ───────────────────────────────────────────────────
const CONGELADO = /(^|\/)(\.archivo-historico-|_archivo-exports-)/;
const alcance = (f) => !f.startsWith('tests/') && !CONGELADO.test(f);

for (const ruta of versionados.filter(alcance)) {
  let texto;
  try {
    texto = readFileSync(ruta, 'utf8');
  } catch {
    continue;
  }
  const literales = rutasLiterales(texto);
  if (literales.length) {
    const detalle = `ruta(s) de webhook escritas a mano (${literales.join(', ')})`;
    fallos.push(`${ruta}: ${detalle}`);
    anadirViolacion(ruta, 'literal-webhook-path', detalle);
  }
}

violations.sort((a, b) => {
  if (a.file !== b.file) return a.file < b.file ? -1 : 1;
  return a.type < b.type ? -1 : 1;
});

if (jsonMode) {
  console.log(JSON.stringify({
    ok: violations.length === 0,
    violations,
    reviewed_files: versionados.length,
    secrets_file_present: secretosPresentes,
  }, null, 2));
  if (violations.length) process.exitCode = 1;
  process.exit();
}

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