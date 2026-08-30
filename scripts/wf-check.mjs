#!/usr/bin/env node
// Verifica un workflow de n8n ANTES de importarlo. Sale con codigo 1 si algo falla.
//
// Cada regla existe porque algo se rompio de verdad. La fecha dice cuando.
//
// Uso:  node scripts/wf-check.mjs <export.json>
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const src = process.argv[2];
if (!src) { console.error('uso: node scripts/wf-check.mjs <export.json>'); process.exit(1); }
const wf = JSON.parse(readFileSync(src, 'utf8'));
const N = Object.fromEntries(wf.nodes.map(n => [n.name, n]));
const code = wf.nodes.filter(n => typeof n.parameters?.jsCode === 'string');

// Si le pasan el workflow.json PARTIDO (el de workflows/PROD/), los cuerpos son
// marcadores "@@FILE:" y el check daria una cascada de fallos absurdos. Se corta aqui
// con un mensaje que dice que hacer.
if (JSON.stringify(wf).includes('@@FILE:')) {
  console.error('Este workflow esta PARTIDO (contiene marcadores @@FILE:).');
  console.error('Reconstruyelo antes de verificarlo:');
  console.error('  node scripts/wf-join.mjs workflows/PROD workflows/PROD/_importar.json');
  process.exit(2);
}

const fallos = [], avisos = [];
const check = (ok, msg) => (ok ? null : fallos.push(msg));
const warn  = (ok, msg) => (ok ? null : avisos.push(msg));

// ── 1. Dos nodos de codigo NO pueden tener el mismo cuerpo ────────────────
// 30-ago-2026: al pegar a mano, el codigo de `Formatear ofertas` acabo TAMBIEN
// en `Code - Normalizar Modalidad`, que perdio sus 100 lineas propias. Se cazo
// por casualidad auditando el export. Esta regla lo caza siempre.
// Dos nodos HERMANOS con el mismo cuerpo son legitimos ("... Error" y "... Error1":
// dos ramas que preparan el mismo correo). El accidente es que dos nodos con roles
// DISTINTOS acaben iguales. Se distingue por el nombre: si uno es prefijo del otro,
// aviso; si no se parecen en nada, fallo.
const vistos = new Map();
for (const n of code) {
  const h = n.parameters.jsCode.trim();
  if (vistos.has(h)) {
    const otro = vistos.get(h);
    const hermanos = n.name.startsWith(otro) || otro.startsWith(n.name);
    const msg = `"${otro}" y "${n.name}" tienen codigo IDENTICO`;
    if (hermanos) avisos.push(`${msg} (hermanos: probablemente a proposito)`);
    else fallos.push(`${msg} — roles distintos: uno pisa al otro`);
  } else vistos.set(h, n.name);
}

// ── 2. Todo nodo de codigo tiene que compilar ─────────────────────────────
const dir = mkdtempSync(join(tmpdir(), 'wfcheck-'));
for (const n of code) {
  const f = join(dir, 'n.js');
  writeFileSync(f, n.parameters.jsCode);
  try { execFileSync(process.execPath, ['--check', f], { stdio: 'pipe' }); }
  catch (e) { fallos.push(`"${n.name}" no compila: ${String(e.stderr).split('\n').find(l => l.includes('Error')) || 'error de sintaxis'}`); }
}

// ── 3. Un nodo referenciado con $('X') tiene que existir ──────────────────
// Si se renombra un nodo, las referencias de los demas se quedan colgando y el
// fallo aparece en ejecucion, no al guardar.
for (const n of code) {
  for (const m of n.parameters.jsCode.matchAll(/\$\('([^']+)'\)/g)) {
    check(N[m[1]], `"${n.name}" referencia a $('${m[1]}'), que no existe en el workflow`);
  }
}

// ── 4. Groq: max_tokens dentro del limite real de la cuenta ───────────────
// 30-ago-2026: la cuenta tiene 8000 TPM y max_tokens cuenta DENTRO. Con 8192 la
// peticion se rechaza entera. Y sin reasoning_effort, gpt-oss gasta el
// presupuesto razonando y devuelve content VACIO.
const groq = N['Groq - Generar Ofertas'];
if (groq) {
  const b = String(groq.parameters.jsonBody || '');
  const mt = Number((b.match(/max_tokens:\s*(\d+)/) || [])[1] || 0);
  check(mt > 0 && mt <= 4096, `Groq max_tokens=${mt}: fuera del limite util (la cuenta tiene 8000 TPM y el prompt ya gasta ~2600)`);
  check(/gpt-oss/.test(b) ? /reasoning_effort/.test(b) : true,
        'Groq usa un modelo gpt-oss (de razonamiento) SIN reasoning_effort: devolvera content vacio');
}

// ── 5. Adzuna: la URL no puede volver a encerrarse en una ciudad ──────────
// 30-ago-2026: `where=Madrid` tiraba el 85% de Espana y todas las remotas de fuera.
const adz = N['Buscar en Adzuna'];
if (adz) {
  const u = String(adz.parameters.url || '');
  check(!/[?&]where=/.test(u), 'Adzuna vuelve a llevar `where=`: encierra la busqueda en una ciudad');
  warn(/salary_min=/.test(u), 'Adzuna sin `salary_min`: no filtra por el suelo salarial del perfil');
  check(!/app_key=/.test(u), 'Adzuna lleva `app_key` en la URL: va por credencial de n8n, se duplicaria');
}

// ── 6. Lo que se calcula se devuelve ──────────────────────────────────────
// 30-ago-2026: `ubic` se calculaba en Normalizar Modalidad y se tiraba, asi que
// Ubicacion llegaba vacia a Notion en TODAS las ofertas.
const nm = N['Code - Normalizar Modalidad'];
if (nm) check(/ubicacion:\s*ubic/.test(nm.parameters.jsCode), '`Code - Normalizar Modalidad` calcula `ubic` pero no lo devuelve');
const crear = N['Notion - Crear Oferta'];
if (crear) {
  const props = (crear.parameters.propertiesUi?.propertyValues || []).map(p => p.key);
  check(props.some(p => p.startsWith('Ubicación')), '`Notion - Crear Oferta` no escribe la propiedad Ubicación');
}

// ── 7. Un webhook y un nodo HTTP no pueden compartir credencial ───────────
// 30-ago-2026: al proteger `buscar-para-user` con Header Auth, n8n ofrecio la
// credencial que YA existia — la misma que `Groq - Generar Ofertas` usaba para su
// `Authorization: Bearer gsk_...`. Al ponerle encima `X-Webhook-Token`, Groq se
// quedo sin autorizacion y empezo a devolver 401. Una credencial, dos usos, y el
// segundo pisa al primero en silencio.
const porCredencial = new Map();
for (const n of wf.nodes) {
  for (const [tipo, v] of Object.entries(n.credentials || {})) {
    const k = `${tipo}:${v.name}`;
    if (!porCredencial.has(k)) porCredencial.set(k, []);
    porCredencial.get(k).push({ nombre: n.name, esWebhook: n.type.endsWith('webhook') });
  }
}
for (const [k, usos] of porCredencial) {
  const webhooks = usos.filter(u => u.esWebhook);
  const otros = usos.filter(u => !u.esWebhook);
  check(!(webhooks.length && otros.length),
    `la credencial "${k}" la comparten un webhook (${webhooks.map(u => u.nombre).join(', ')}) y ` +
    `un nodo que llama fuera (${otros.map(u => u.nombre).join(', ')}): al cambiar una, se rompe la otra`);
}

// ── 8. Ningun secreto en lo que se commitea ──────────────────────────────
// 30-ago-2026: el webhook de busqueda se protege por un `path` impredecible, y
// este repositorio es PUBLICO. Si ese path acaba en workflow.json, el primer
// commit lo publica y la proteccion dura lo que tarda un `git push`.
// wf-split lo saca a secrets.local.json; esta regla vigila que asi sea.
for (const n of wf.nodes) {
  if (!n.type.endsWith('webhook')) continue;
  const path = n.parameters?.path;
  if (typeof path !== 'string') continue;
  const pareceSecreto = /[a-z]-?[0-9][a-z0-9]{4,}/i.test(path) || path.length > 28;
  warn(!pareceSecreto || path.startsWith('@@SECRET:'),
    `el webhook "${n.name}" lleva un path que parece secreto ("${path}") sin redactar: ` +
    `pasalo por wf-split antes de commitear`);
}

// ── informe ──────────────────────────────────────────────────────────────
console.log(`${wf.nodes.length} nodos | ${code.length} de codigo`);
for (const a of avisos) console.log(`  AVISO  ${a}`);
for (const f of fallos) console.log(`  FALLO  ${f}`);
console.log(fallos.length ? `\n${fallos.length} FALLO(S) — no importar` : '\nOK — se puede importar');
process.exit(fallos.length ? 1 : 0);
