"""Builds the Phase 1 per-user filter from the backup (design 2026-11-01-per-user-search-filter)."""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
wf = json.load(open(src))
nodes = {n["name"]: n for n in wf["nodes"]}

# 1. Normalisers: pass `evitar` through.
sched = nodes["Code — Normalizar users (schedule)"]["parameters"]
old = "    ciudad:     p.Ciudad?.rich_text?.[0]?.plain_text || '',\n"
assert old in sched["jsCode"]
sched["jsCode"] = sched["jsCode"].replace(
    old, old + "    evitar:     (p.Evitar?.rich_text || []).map(t => t.plain_text).join(''),\n")

interno = nodes["Code — Normalizar (interno)"]["parameters"]
old = "  ciudad:        body.ciudad     || '',\n"
assert old in interno["jsCode"]
interno["jsCode"] = interno["jsCode"].replace(old, old + "  evitar:        body.evitar     || '',\n")

# 2. Prefilter: the user's stack widens INCLUIR and is removed from EXCLUIR_PERFIL.
fmt = nodes["Formatear ofertas"]["parameters"]
code = fmt["jsCode"]
anchor = "const esIA = (t) =>"
assert anchor in code
per_user = (
    "// Per-user prefilter (design 2026-11-01). The user's own stack always counts as a\n"
    "// profile signal and is never excluded: a Java user must not lose Java offers.\n"
    "const STACK_U = (U.stack || []).map(s => String(s).toLowerCase().trim()).filter(Boolean);\n"
    "for (const s of STACK_U) if (!INCLUIR.includes(s)) INCLUIR.push(s);\n"
    "for (let i = EXCLUIR_PERFIL.length - 1; i >= 0; i--) {\n"
    "  if (STACK_U.some(s => s.includes(EXCLUIR_PERFIL[i]))) EXCLUIR_PERFIL.splice(i, 1);\n"
    "}\n\n"
)
code = code.replace(anchor, per_user + anchor, 1)
old = "  ciudad:         U.ciudad || '',\n"
assert old in code
code = code.replace(old, old + "  evitar:         U.evitar || '',\n")
fmt["jsCode"] = code

# 3. Groq prompt: every user value comes from $json.
PROMPT = r'''={{ JSON.stringify({
  model: "openai/gpt-oss-120b",
  messages: [{
    role: "user",
    content: (() => {
      const nombre = $json.nombre || 'el usuario';
      const ciudad = $json.ciudad || '';
      const mods = ($json.modalidad || []);
      const suelo = Number($json.salario || 0);
      const dia = suelo ? Math.round(suelo / 150) : 0;
      const hora = suelo ? Math.round(suelo / 1200) : 0;
      const sueloTxt = suelo
        ? suelo + ' EUR/ano con contrato, o ' + dia + ' EUR/dia o ' + hora + ' EUR/hora si es freelance (convierte otras monedas a EUR antes de comparar)'
        : 'sin suelo: no marques salario';
      return "Eres el career coach y reclutador senior de " + nombre + ". De una lista de ofertas REALES, elige las que MEJOR encajan con su perfil y descarta el resto sin piedad. NO inventes ofertas ni datos: usa SOLO las de la lista.\n\n"
      + "PERFIL DEL USUARIO:\n- Nombre: " + nombre
      + "\n- Rol objetivo (en orden de prioridad): " + ($json.rol || '')
      + "\n- Perfil: " + ($json.perfil || '')
      + "\n- Stack: " + (($json.stack || []).join(', '))
      + "\n- Ciudad base: " + ciudad
      + "\n- Modalidades que acepta: " + (mods.join(', ') || 'no indicadas')
      + "\n- Quiere evitar: " + ($json.evitar || 'nada indicado')
      + "\n\nFILTROS DUROS. Descarta si incumple cualquiera:"
      + "\n1) El trabajo principal no encaja con su Rol objetivo y su Stack. Lee la DESCRIPCION, no el titulo: si lo suyo es solo un anadido menor, descarta. Un puesto de solo frontend es tan valido como uno de IA o full-stack si encaja con su stack."
      + "\n2) Es explicitamente junior, practicas o pide menos de 3 anos de experiencia. Juzga la seniority por la DESCRIPCION, no por el titulo: las ofertas en espanol casi nunca escriben Senior. Si no lo aclara, DEJALA PASAR."
      + "\n3) Modalidad y ubicacion, segun SUS modalidades:"
      + "\n   - Presencial: solo vale si acepta Presencial y es en su ciudad base. Si no, descarta."
      + "\n   - Hibrido: vale en su ciudad base si acepta hibrido, y en cualquier ciudad que aparezca como 'Hibrido <ciudad>' en sus modalidades. Si la ciudad del hibrido NO es su ciudad base, dejala pasar y empieza notas con 'HIBRIDO <CIUDAD>: confirmar dias de oficina'. Hibrido en cualquier otra ciudad: descarta. Si el hibrido NO dice la ciudad, no asumas: dejala pasar y empieza notas con 'HIBRIDO: confirmar ciudad y dias de oficina'."
      + "\n   - Remoto: vale si acepta Remoto y la oferta permite trabajar desde el pais de su ciudad base o desde una region que lo incluya (por ejemplo Europa, EMEA o mundial). Si el remoto esta restringido a otra region ('US only', 'remote LATAM', 'must reside in Brazil'), descarta. Si no dice la region, no asumas y dejala pasar."
      + "\n4) Coincide con lo que quiere evitar: descarta."
      + "\n\nMARCA sin descartar (empieza notas con la marca): salario por debajo del suelo -> BAJO SUELO. SUELO: " + sueloTxt + ". Sin salario indicado no descartes ni marques. NUNCA asumas la modalidad: si la oferta no la dice, deja el campo vacio."
      + "\n\nORDEN entre las que sobreviven: 1) encaje con el PRIMER rol de su Rol objetivo, que es su prioridad; 2) encaje real con el resto del perfil; 3) salario mas alto; 4) remoto antes que hibrido."
      + "\n\nOFERTAS REALES:\n" + ($json.ofertas || '')
      + "\n\nDevuelve SOLO un array JSON (sin texto extra, sin markdown) con las que pasen los filtros (maximo 5, y puede ser NINGUNA: devuelve [] si ninguna encaja, no rellenes hasta cinco), cada una con estos campos EXACTOS:\n"
      + '[{"empresa":"","puesto":"","salario":"","modalidad":"Remoto|Hibrido|Presencial","link":"","descripcion_corta":"80-150 chars","notas":"","nombre_contacto":"","email_contacto":"","telefono_contacto":"","fecha_publicacion":""}]'
      + "\nUsa el link real de cada oferta. Si NINGUNA encaja, devuelve [].";
    })()
  }],
  max_tokens: 4000,
  temperature: 0.3,
  reasoning_effort: "low"
}) }}
'''
nodes["Groq - Generar Ofertas"]["parameters"]["jsonBody"] = PROMPT

# 4. Post-filter after Groq: hybrid and on-site cities come from the user, not "Madrid".
nm = nodes["Code - Normalizar Modalidad"]["parameters"]
code = nm["jsCode"]
old = """  const esMadrid = (ubic + ' ' + desc).toLowerCase().includes('madrid');

  // Se descarta SOLO con dato explícito. Lo desconocido pasa marcado.
  if (modalidad === 'Presencial') return null;
  if (modalidad === 'Hibrido' && !esMadrid) return null;
"""
assert old in code
new = """  // Per-user cities (design 2026-11-01). Base city tokens ("Valdemorillo, Madrid")
  // plus every "Híbrido <city>" in the user's modalidades. BCN is an alias of Barcelona.
  const UF = (() => { try { return $('Formatear ofertas').first().json; } catch (e) { return {}; } })();
  const ALIAS = { bcn: 'barcelona' };
  const norm = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').trim();
  const mods = (UF.modalidad || []).map(norm);
  const base = norm(UF.ciudad).split(',').map(s => s.trim()).filter(Boolean);
  const hibOcasional = mods.filter(m => m.startsWith('hibrido ')).map(m => m.slice(8).trim())
    .map(c => ALIAS[c] || c).filter(c => !base.includes(c));
  const aceptaHibrido = mods.some(m => m.startsWith('hibrido'));
  const aceptaPresencial = mods.some(m => m.startsWith('presencial'));
  const texto = norm(ubic + ' ' + desc);
  const enBase = base.some(c => texto.includes(c));
  const enOcasional = hibOcasional.some(c => texto.includes(c));

  // Se descarta SOLO con dato explícito. Lo desconocido pasa marcado.
  if (modalidad === 'Presencial' && !(aceptaPresencial && enBase)) return null;
  const sinCiudad = /confirmar ciudad/i.test(String(oferta.notas || ''));
  if (modalidad === 'Hibrido' && !(aceptaHibrido && (enBase || enOcasional || sinCiudad))) return null;
"""
code = code.replace(old, new)
old = "    descripcion_corta: aviso + (oferta.descripcion_corta || ''),"
assert old in code
code = code.replace(old, "    descripcion_corta: aviso + (oferta.notas ? oferta.notas + ' · ' : '') + (oferta.descripcion_corta || ''),")
old_parse = "catch (e) { throw new Error('JSON inválido: ' + e.message); }"
assert old_parse in code
code = code.replace(old_parse, old_parse + "\n// A model sometimes echoes the empty template instead of []: keep only real offers.\nofertas = (Array.isArray(ofertas) ? ofertas : []).filter(o => o && String(o.link || '').trim());", 1)
nm["jsCode"] = code

json.dump(wf, open(dst, "w"), ensure_ascii=False, indent=2)
print("ok:", dst)
