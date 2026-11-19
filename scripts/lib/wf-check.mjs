import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

export function analizarWorkflow(wf) {
  const errors = [];
  const warnings = [];

  if (!wf || !Array.isArray(wf.nodes)) {
    return {
      ok: false,
      nodes: 0,
      code_nodes: 0,
      warnings,
      errors: ['workflow inválido o sin nodos'],
      reviewed: true,
    };
  }

  if (JSON.stringify(wf).includes('@@FILE:')) {
    errors.push('workflow partido: reconstrúyelo con node scripts/wf-join.mjs workflows/PROD workflows/PROD/_importar.json');
    return {
      ok: false,
      nodes: wf.nodes.length,
      code_nodes: 0,
      warnings,
      errors,
      reviewed: true,
    };
  }

  const N = Object.fromEntries(wf.nodes.map((n) => [n.name, n]));
  const code = wf.nodes.filter(
    (n) => typeof n.type === 'string' && n.type.endsWith('code') &&
           typeof n.parameters?.jsCode === 'string',
  );

  // 1. Código duplicado con roles distintos
  const vistos = new Map();
  for (const n of code) {
    const h = n.parameters.jsCode.trim();
    if (vistos.has(h)) {
      const otro = vistos.get(h);
      const hermanos = n.name.startsWith(otro) || otro.startsWith(n.name);
      const msg = `"${otro}" y "${n.name}" tienen codigo IDENTICO`;
      if (hermanos) warnings.push(`${msg} (hermanos: probablemente a proposito)`);
      else errors.push(`${msg} — roles distintos: uno pisa al otro`);
    } else {
      vistos.set(h, n.name);
    }
  }

  // 2. Compilación de nodos de código
  const dir = mkdtempSync(join(tmpdir(), 'wfcheck-'));
  try {
    for (const n of code) {
      const f = join(dir, 'n.js');
      writeFileSync(f, n.parameters.jsCode);
      try {
        execFileSync(process.execPath, ['--check', f], { stdio: 'pipe' });
      } catch (e) {
        const stderr = String(e.stderr || '');
        errors.push(`"${n.name}" no compila: ${stderr.split('\n').find((l) => l.includes('Error')) || 'error de sintaxis'}`);
      }
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }

  // 3. Referencias colgantes
  for (const n of code) {
    for (const m of n.parameters.jsCode.matchAll(/\$\('([^']+)'\)/g)) {
      if (!N[m[1]]) {
        errors.push(`"${n.name}" referencia a $('${m[1]}'), que no existe en el workflow`);
      }
    }
  }

  // 4. Groq
  const groq = N['Groq - Generar Ofertas'];
  if (groq) {
    const b = String(groq.parameters.jsonBody || '');
    const mt = Number((b.match(/max_tokens:\s*(\d+)/) || [])[1] || 0);
    if (!(mt > 0 && mt <= 4096)) {
      errors.push(`Groq max_tokens=${mt}: fuera del limite util (la cuenta tiene 8000 TPM y el prompt ya gasta ~2600)`);
    }
    if (/gpt-oss/.test(b) && !/reasoning_effort/.test(b)) {
      errors.push('Groq usa un modelo gpt-oss (de razonamiento) SIN reasoning_effort: devolvera content vacio');
    }
  }

  // 5. Adzuna
  const adz = N['Buscar en Adzuna'];
  if (adz) {
    const u = String(adz.parameters.url || '');
    if (/[?&]where=/.test(u)) {
      errors.push('Adzuna vuelve a llevar `where=`: encierra la busqueda en una ciudad');
    }
    if (!/salary_min=/.test(u)) {
      warnings.push('Adzuna sin `salary_min`: no filtra por el suelo salarial del perfil');
    }
    if (/app_key=/.test(u)) {
      errors.push('Adzuna lleva `app_key` en la URL: va por credencial de n8n, se duplicaria');
    }
  }

  // 6. Lo calculado se devuelve
  const nm = N['Code - Normalizar Modalidad'];
  if (nm) {
    if (!/ubicacion:\s*ubic/.test(nm.parameters.jsCode)) {
      errors.push('`Code - Normalizar Modalidad` calcula `ubic` pero no lo devuelve');
    }
  }
  const crear = N['Notion - Crear Oferta'];
  if (crear) {
    const props = (crear.parameters.propertiesUi?.propertyValues || []).map((p) => p.key);
    if (!props.some((p) => p.startsWith('Ubicación'))) {
      errors.push('`Notion - Crear Oferta` no escribe la propiedad Ubicación');
    }
  }

  // 7. Credencial compartida
  const porCredencial = new Map();
  for (const n of wf.nodes) {
    for (const [tipo, v] of Object.entries(n.credentials || {})) {
      const k = `${tipo}:${v.name}`;
      if (!porCredencial.has(k)) porCredencial.set(k, []);
      porCredencial.get(k).push({ nombre: n.name, esWebhook: String(n.type || '').endsWith('webhook') });
    }
  }
  for (const [k, usos] of porCredencial) {
    const webhooks = usos.filter((u) => u.esWebhook);
    const otros = usos.filter((u) => !u.esWebhook);
    if (webhooks.length && otros.length) {
      errors.push(
        `la credencial "${k}" la comparten un webhook (${webhooks.map((u) => u.nombre).join(', ')}) y ` +
          `un nodo que llama fuera (${otros.map((u) => u.nombre).join(', ')}): al cambiar una, se rompe la otra`,
      );
    }
  }

  // 8. Secreto sin redactar en webhook
  for (const n of wf.nodes) {
    if (!String(n.type || '').endsWith('webhook')) continue;
    const path = n.parameters?.path;
    if (typeof path !== 'string') continue;
    const pareceSecreto = /[a-z]-?[0-9][a-z0-9]{4,}/i.test(path) || path.length > 28;
    if (pareceSecreto && !path.startsWith('@@SECRET:')) {
      warnings.push(
        `el webhook "${n.name}" lleva un path que parece secreto ("${path}") sin redactar: ` +
          `pasalo por wf-split antes de commitear`,
      );
    }
  }

  return {
    ok: errors.length === 0,
    nodes: wf.nodes.length,
    code_nodes: code.length,
    warnings,
    errors,
    reviewed: true,
  };
}