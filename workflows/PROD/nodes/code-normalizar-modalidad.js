const response = $input.first().json;

if (response.error) {
  throw new Error('Groq API error: ' + JSON.stringify(response.error));
}

const text = response.choices?.[0]?.message?.content || '';
if (!text) {
  throw new Error('Respuesta vacía: ' + JSON.stringify(response).substring(0, 300));
}

const jsonMatch = text.match(/\[[\s\S]*\]/);
if (!jsonMatch) {
  throw new Error('No se encontró array JSON. Texto: ' + text.substring(0, 500));
}

let ofertas;
try { ofertas = JSON.parse(jsonMatch[0]); }
catch (e) { throw new Error('JSON inválido: ' + e.message); }

// Recuperar email_usuario Y user_id del nodo que alimentó el Wait
let emailUsuario = '';
let userId = '';
try {
  emailUsuario = $('Formatear ofertas').first().json.email_usuario || '';
  userId = $('Formatear ofertas').first().json.user_id || '';
} catch(e) {}
if (!emailUsuario || !userId) {
  const nodosOrigen = ['Code — Normalizar (interno)', 'Code — Normalizar users (schedule)'];
  for (const nodo of nodosOrigen) {
    if (emailUsuario && userId) break;
    try {
      const d = $(nodo).first().json;
      if (!emailUsuario) emailUsuario = d.email_usuario || d.email || '';
      if (!userId) userId = d.user_id || '';
    } catch(e) {}
  }
}

// Idioma detectado de la descripción REAL en "Formatear ofertas", indexado por link
let idiomaPorLink = {};
try { idiomaPorLink = $('Formatear ofertas').first().json.idioma_por_link || {}; } catch(e) {}
let ubicacionPorLink = {};
try { ubicacionPorLink = $('Formatear ofertas').first().json.ubicacion_por_link || {}; } catch(e) {}
let descripcionPorLink = {};
try { descripcionPorLink = $('Formatear ofertas').first().json.descripcion_por_link || {}; } catch(e) {}

return ofertas.map(oferta => {
  const linkKey = String(oferta.link || '').trim();
  const desc = String(descripcionPorLink[linkKey] || '');
  const ubic = String(ubicacionPorLink[linkKey] || '');

  // Señales de modalidad: lo que dijo Groq (suele venir vacío porque solo ve 60
  // chars) MÁS la descripción completa de 1800 chars que ya se guarda aquí al lado.
  // El RSS de Tecnoempleo mete la modalidad en el campo Provincia: "Provincia: hibrido",
  // "Provincia: 100% en remoto". Medido sobre el feed: 26 de 80 ofertas lo hacen así.
  const senales = ((oferta.modalidad || '') + ' ' + desc + ' ' + ubic).toLowerCase();

  // NUNCA se asume la modalidad. Si la oferta no lo dice, queda Sin confirmar y
  // entra igual, para que Vero abra el link y decida. Medido: 31 de 80 ofertas
  // del feed no dicen la modalidad en ninguna parte. Asumir Presencial las tiraba
  // todas, que era el motivo real de que no llegase nada a Notion.
  let modalidad = 'Sin confirmar';
  if (/100\s*%\s*(en\s+)?remoto|full\s*remote|fully\s*remote/.test(senales)) modalidad = 'Remoto';
  else if (/h[ií]brido|hybrid/.test(senales)) modalidad = 'Hibrido';
  else if (/\bremoto\b|teletrabajo|\bremote\b/.test(senales)) modalidad = 'Remoto';
  else if (/presencial|on-?site|in-?office/.test(senales)) modalidad = 'Presencial';

  const esMadrid = (ubic + ' ' + desc).toLowerCase().includes('madrid');

  // Se descarta SOLO con dato explícito. Lo desconocido pasa marcado.
  if (modalidad === 'Presencial') return null;
  if (modalidad === 'Hibrido' && !esMadrid) return null;

  const emailContacto = oferta.email_contacto && oferta.email_contacto.includes('@')
    ? oferta.email_contacto : '';

  const idioma = idiomaPorLink[linkKey] || '';

  // Aviso visible en Notas cuando la modalidad no se ha podido confirmar.
  const aviso = modalidad === 'Sin confirmar' ? '[VERIFICAR MODALIDAD] ' : '';

  return { json: {
    email_usuario:     emailUsuario,
    user_id:           userId,
    empresa:           oferta.empresa || 'Sin nombre',
    puesto:            oferta.puesto || '',
    salario:           oferta.salario || '',
    modalidad,
    ubicacion:         ubic || '',
    link:              oferta.link || '',
    descripcion_corta: aviso + (oferta.descripcion_corta || ''),
    descripcion_full:  descripcionPorLink[linkKey] || oferta.descripcion_corta || '',
    idioma,
    nombre_contacto:   oferta.nombre_contacto || '',
    email_contacto:    emailContacto,
    telefono_contacto: oferta.telefono_contacto || '',
    fecha_publicacion: oferta.fecha_publicacion || ''
  }};
}).filter(x => x !== null);
