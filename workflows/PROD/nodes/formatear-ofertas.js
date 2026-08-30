// Junta 3 fuentes + filtra por el stack del usuario actual (multi-usuario).
const U = $('Loop Over Users').item.json;
const LT = String.fromCharCode(60);
const GT = String.fromCharCode(62);
const tagRe = new RegExp(LT + '[^' + GT + ']*' + GT, 'g');
const limpiar = (s) => (s || '').replace(tagRe, ' ').split('&nbsp;').join(' ').replace(/\s+/g, ' ').trim();

// ── Detector de idioma (mismo criterio que el cv-server) ──
// Acentos/signos ¿¡ pesan doble (señal fuerte de español). Devuelve 'en', 'es' o '' (sin señal).
const _ACC = /[áéíóúñ¿¡]/gi;
const ES_W = ['de','la','el','en','con','para','los','las','una','por','experiencia','desarrollo',
  'trabajo','empresa','equipo','conocimientos','requisitos','buscamos','ofrecemos','nuestro','tus','responsable'];
const EN_W = ['the','and','with','for','you','our','are','experience','development','team','work',
  'company','skills','requirements','looking','join','role','about','your','we','will'];
const detIdioma = (txt) => {
  const t = (txt || '').toLowerCase();
  if (!t.trim()) return '';
  const words = new Set(t.match(/[a-záéíóúñü]+/g) || []);
  let es = (t.match(_ACC) || []).length * 2;
  for (const w of ES_W) if (words.has(w)) es++;
  let en = 0;
  for (const w of EN_W) if (words.has(w)) en++;
  if (en === 0 && es === 0) return '';
  return en > es ? 'en' : 'es';
};
// Mapa link -> idioma, detectado de la descripción REAL (antes de que Groq la resuma en español)
const idiomaPorLink = {};
const ubicacionPorLink = {};
const descripcionPorLink = {};

// ── Targeting del perfil de la usuaria: Frontend/React + AI/LLM + Tech Lead (frontend) ──
// Señales del perfil (debe haber AL MENOS UNA en el TÍTULO de la oferta)
// Grounded en el perfil real de Vero (Notion): Rol "Full-Stack Developer & AI Engineer";
// Stack React/TypeScript/Vue.js/Node.js/Python/AI-ML. Debe haber AL MENOS UNA en el TÍTULO.
const INCLUIR = [
  'full stack','fullstack','full-stack','software engineer','software developer','software dev',
  'frontend','front-end','front end','react','vue','vue.js','angular','typescript','javascript',
  'next.js','nextjs','svelte','node','node.js','web developer','web engineer',
  'ui engineer','ui developer','ux engineer','design system',
  'tech lead','frontend lead','front-end lead','head of frontend','head of engineering','engineering lead',
  'ai engineer','ml engineer','machine learning engineer','ai developer','llm','prompt engineer',
  'genai','generative ai'
];
// Backend / otros perfiles que NO son de ella: fuera salvo que el título tenga también señal del perfil
const EXCLUIR_PERFIL = ['java','spring','.net','c#','php','golang','rust','scala','kotlin',
  'abap','sap','salesforce','dba','sql server','oracle','sysadmin','devops','sre',
  'data engineer','data scientist','backend','android','ios','embedded','c++','wordpress developer'];
// Roles no técnicos / basura: fuera siempre
const EXCLUIR_DURO = ['administrador de sistemas','linux rhel','soporte','helpdesk','help desk',
  'comercial','ventas','sales','contable','contabilidad','recruiter','reclutador','qa manual',
  'qa engineer','tester manual','tester','becario','prácticas','beca','community manager'];

// Señal de IA en el título. Sirve para dos cosas: saltarse la puerta de seniority
// y para colarse primero cuando hay que recortar la lista.
const IA_SIGNAL = ['ai engineer','ai developer','ai software','ai full stack','ai fullstack',
  'ai full-stack','applied ai','agentic','ml engineer','machine learning engineer','llm',
  'genai','generative ai','gen ai','artificial intelligence','inteligencia artificial',
  'prompt engineer','ai-first','ai first','ai-native','ai native','conversational ai',
  'ai product','ai adoption','ai enablement','ai lead','ai tech lead','ia &','ai &','ia-first'];
const esIA = (t) => IA_SIGNAL.some(k => (t || '').toLowerCase().includes(k));

const JUNIOR = ['junior','jr.','jr ','trainee','becario','beca ','prácticas','practicas',
  'entry level','graduate','sin experiencia','recién titulado','recien titulado'];
const SENIORITY = ['senior','sr.','sr ','staff','lead','principal','architect','arquitecto','head of'];
const matchea = (titulo, desc) => {
  const tit = (titulo || '').toLowerCase();
  if (EXCLUIR_DURO.some(k => tit.includes(k))) return false;   // basura/no-tech fuera
  // Si el título grita IA, entra y punto: ni INCLUIR ni seniority. Es la prioridad de Vero,
  // y titulos como 'AI Enablement Lead' o 'Artificial Intelligence Engineer' no casan con INCLUIR.
  if (esIA(tit)) return true;
  if (!INCLUIR.some(k => tit.includes(k))) return false;       // exige señal del perfil en el título
  // Las de IA NO pasan por la puerta de seniority: 'AI Engineer' a secas ya es un puesto
  // senior de mercado y casi nunca lleva 'Senior' en el título.
  // 28-ago-2026. Antes se EXIGIA seniority en el titulo. Las ofertas espanolas no
  // la escriben: "Desarrollador/a Frontend - Vue.js" es un puesto senior de
  // mercado y se estaba tirando. Medido sobre 93 ofertas reales, esta puerta
  // mataba 5 puestos que son exactamente su perfil. Se invierte: se descarta el
  // JUNIOR explicito, que ese SI se escribe siempre.
  if (JUNIOR.some(k => tit.includes(k))) return false;
  // EXCLUIR_PERFIL estaba declarada y NO se usaba nunca. Por eso colaba
  // "Senior Full Stack - PHP/Symfony/Vue", que es justo lo que existe para tirar.
  if (EXCLUIR_PERFIL.some(k => tit.includes(k))) return false;
  // El stack ajeno sin señal ya cayó arriba. Java+React vs .NET+React lo decide
  // el nodo de Groq leyendo la descripción, no el título.
  return true;
};

// ANTI-SPAM: links de ofertas que YA existen en Notion (no repetir)
const yaEnviadas = new Set();
const yaKeys = new Set();
try {
  const resp = $('Notion - Ofertas existentes').first().json;
  for (const page of (resp.results || [])) {
    const u = page?.properties?.['Link oferta']?.url;
    if (u) yaEnviadas.add(u.trim());
    const emp = (page?.properties?.['Empresa']?.title?.[0]?.plain_text || '').toLowerCase().trim();
    const pue = (page?.properties?.['Puesto']?.rich_text?.[0]?.plain_text || '').toLowerCase().trim();
    if (emp && pue) yaKeys.add(emp + '|' + pue);
  }
} catch (e) {}
const esNueva = (link) => link && !yaEnviadas.has(String(link).trim());
const keysBatch = new Set();
const esNuevaKey = (empresa, puesto) => {
  const e = (empresa || '').toLowerCase().trim();
  const p = (puesto || '').toLowerCase().trim();
  if (!e || !p) return true;
  const k = e + '|' + p;
  if (yaKeys.has(k) || keysBatch.has(k)) return false;
  keysBatch.add(k);
  return true;
};

// Un "Remoto" restringido a otra region NO sirve: Veronica trabaja desde Madrid.
// Remotive lo da en candidate_required_location ("Sao Paulo", "USA", "Europe"...).
// Si el campo viene vacio NO se asume nada y pasa.
const REGION_OK = /espa|spain|europe|europa|emea|worldwide|anywhere|global|uk|united kingdom|latam|remote/i;
const REGION_MAL = /\b(usa|u\.s\.|united states|canada|brazil|brasil|mexico|méxico|argentina|colombia|chile|peru|india|australia|nz|new zealand|philippines|singapore|japan|uae|nigeria|kenya|south africa)\b|sao paulo|são paulo|campinas|florianopolis|florianópolis|mexico city|buenos aires|bogota|bogotá|lima|santiago/i;
const remotoValido = (loc) => {
  const l = String(loc || '').trim();
  if (!l) return true;                       // sin dato: no se asume, pasa
  if (REGION_MAL.test(l) && !/espa|spain|europe|europa|emea/i.test(l)) return false;
  return REGION_OK.test(l) || /madrid/i.test(l);
};

const out = [];

// Remotive
try {
  const jobs = $('Buscar en Remotive').first().json.jobs || [];
  for (const j of jobs.slice(0, 50)) {
    const descReal = limpiar(j.description);
    if (!matchea(j.title, descReal)) continue;
    if (!esNueva(j.url)) continue;
    if (!esNuevaKey(j.company_name, j.title)) continue;
    if (!remotoValido(j.candidate_required_location)) continue;   // remoto de otra region
    idiomaPorLink[String(j.url).trim()] = detIdioma(j.title + ' ' + descReal);
    descripcionPorLink[String(j.url).trim()] = String(descReal || '').slice(0, 1800);
    ubicacionPorLink[String(j.url).trim()] = j.candidate_required_location || 'Remoto';
    out.push('[Remotive] ' + j.title + ' | ' + j.company_name + ' | ' + (j.candidate_required_location || 'Remoto') + ' | ' + (j.salary || 's/i') + ' | ' + j.url + ' | ' + descReal.slice(0, 600));
  }
} catch (e) {}

// Adzuna
try {
  const results = ($('Buscar en Adzuna').first().json.results || []).slice(0, 50);
  for (const j of results) {
    const descFull = limpiar(j.description);
    if (!matchea(j.title, descFull)) continue;
    if (!esNueva(j.redirect_url)) continue;
    if (!esNuevaKey(((j.company||{}).display_name)||'', j.title)) continue;
    idiomaPorLink[String(j.redirect_url).trim()] = detIdioma(j.title + ' ' + descFull);
    descripcionPorLink[String(j.redirect_url).trim()] = String(descFull || '').slice(0, 1800);
    ubicacionPorLink[String(j.redirect_url).trim()] = ((j.location||{}).display_name||'');
    const sal = j.salary_min ? Math.round(j.salary_min) + '-' + Math.round(j.salary_max || j.salary_min) : 's/i';
    out.push('[Adzuna] ' + j.title + ' | ' + ((j.company||{}).display_name||'') + ' | ' + ((j.location||{}).display_name||'') + ' | ' + sal + ' | ' + j.redirect_url + ' | ' + descFull.slice(0, 600));
  }
} catch (e) {}

// Tecnoempleo (RSS XML)
try {
  const xml = $('Buscar en Tecnoempleo').first().json.data || $('Buscar en Tecnoempleo').first().json.body || '';
  const parts = xml.split('<item>');
  const slice = (s, a, b) => { const i = s.indexOf(a); if (i<0) return ''; const j = s.indexOf(b, i+a.length); return j<0 ? '' : s.substring(i+a.length, j); };
  const cdata = (s) => s.split('<![CDATA[').join('').split(']]>').join('').trim();
  for (let k = 1; k < parts.length && k <= 100; k++) {
    const it = parts[k];
    const title = cdata(slice(it, '<title>', '</title>'));
    const link = cdata(slice(it, '<link>', '</link>'));
    const descFull = limpiar(cdata(slice(it, '<description>', '</description>')));
    if (!matchea(title, descFull)) continue;
    if (!esNueva(link)) continue;
    idiomaPorLink[String(link).trim()] = detIdioma(title + ' ' + descFull);
    descripcionPorLink[String(link).trim()] = String(descFull || '').slice(0, 1800);
    ubicacionPorLink[String(link).trim()] = /madrid/i.test(title + ' ' + descFull) ? 'Madrid' : 'España';
    out.push('[Tecnoempleo] ' + title + ' | | España | s/i | ' + link + ' | ' + descFull.slice(0, 600));
  }
} catch (e) {}

// CAP modo prueba: máx 12 ofertas a Groq (ahorra tokens del cupo diario free)
const MAX_OFERTAS = 12;
// 30-ago-2026. Antes se ordenaba SOLO por "¿menciona IA?" y dentro de eso el orden
// era el de las fuentes. Con Adzuna trayendo 55 ofertas de golpe, CUALES son las 12
// que entran importa mas que cuantas. Ahora: las de IA primero (prioridad declarada
// de Vero) y, dentro de cada grupo, la mejor pagada primero.
//
// El salario es el campo que va JUSTO ANTES del link. Se ancla ahi y no en la posicion,
// porque los titulos llevan "|" dentro ("Lead / Staff AI Engineer | AI SaaS") y partir
// por indice daria el campo equivocado. Devuelve 0 si no hay cifra ("s/i"), sin colarse
// numeros de la descripcion. Probado con titulos con pipe, "s/i" y "$100,000 - $120,000".
const salarioDe = (l) => {
  const m = String(l).match(/\|\s*([^|]*?)\s*\|\s*https?:/);
  if (!m) return 0;
  const nums = (m[1].replace(/[.,]/g, '').match(/\d{4,}/g) || []).map(Number);
  return nums.length ? Math.max(...nums) : 0;
};
const ordenadas = [...out].sort((a, b) =>
  ((esIA(b) ? 1 : 0) - (esIA(a) ? 1 : 0)) || (salarioDe(b) - salarioDe(a)));
const recortadas = ordenadas.slice(0, MAX_OFERTAS);

const lista = recortadas.length
  ? recortadas.map((l, i) => '#' + (i+1) + ' ' + l).join('\n\n')
  : 'NO se encontraron ofertas NUEVAS que coincidan con el perfil del usuario hoy.';

// Arrastra el contexto del usuario para Groq y para crear la oferta
return [{ json: {
  ofertas:        lista,
  total:          out.length,
  idioma_por_link: idiomaPorLink,
  ubicacion_por_link: ubicacionPorLink,
  descripcion_por_link: descripcionPorLink,
  email_usuario:  U.email_usuario || U.email || '',
  nombre:         U.nombre || '',
  perfil:         U.perfil || '',
  rol:            U.rol || '',
  stack:          U.stack || [],
  salario:        U.salario || 0,
  modalidad:      U.modalidad || [],
  ciudad:         U.ciudad || '',
  cv_master_url:  U.cv_master_url || '',
  user_id:        U.user_id || ''
}}];
