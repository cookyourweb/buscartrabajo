return $input.all().map((item, idx) => {
  const d = item.json;

  const titleProp = Object.values(d.properties || {}).find(p => p.type === 'title');
  const empresa = titleProp?.title?.[0]?.plain_text || titleProp?.title?.[0]?.text?.content || 'Sin nombre';

  // Email del usuario: 1º del nodo que lo grabó (valor probado), 2º la página, 3º fallback
  let email = '';
  try {
    const src = $('Code - Normalizar Modalidad').all();
    const j = (src[idx] || src[0] || {}).json || {};
    if (j.email_usuario && j.email_usuario.includes('@')) email = j.email_usuario;
  } catch (_) {}
  if (!email) {
    const emailPropNotion = d.properties?.['Email Enviado'] || d.properties?.['Email usuario'];
    email = emailPropNotion?.email
      || emailPropNotion?.rich_text?.[0]?.plain_text
      || d.email_usuario
      || 'hello.cookyourweb@gmail.com';
  }

  const puesto     = d.properties?.Puesto?.rich_text?.[0]?.plain_text || '';
  const salario    = d.properties?.Salario?.rich_text?.[0]?.plain_text || '';
  const modalidad  = d.properties?.Modalidad?.select?.name || '';
  const notas      = d.properties?.Notas?.rich_text?.[0]?.plain_text || '';
  const linkOferta = d.properties?.['Link oferta']?.url || '';
  const pageId     = d.id || '';
  const nombreContacto = d.properties?.['Nombre Contacto']?.rich_text?.[0]?.plain_text || '';
  const emailContacto  = d.properties?.['Email empresa']?.email || '';

  const htmlContent = '<div style="font-family:Arial;padding:20px;max-width:600px">'
    + '<h2 style="color:#1F5C8B">' + empresa + '</h2>'
    + '<p><b>Puesto:</b> ' + puesto + '</p>'
    + '<p><b>Salario:</b> ' + salario + '</p>'
    + '<p><b>Modalidad:</b> ' + modalidad + '</p>'
    + '<p>' + notas + '</p>'
    + (nombreContacto ? '<p><b>Contacto:</b> ' + nombreContacto + '</p>' : '')
    + (emailContacto  ? '<p><b>Email empresa:</b> ' + emailContacto + '</p>' : '')
    + (linkOferta ? '<p><a href="' + linkOferta + '" style="color:#1F5C8B;font-weight:bold;text-decoration:underline" target="_blank">🔗 Ver oferta completa</a></p>' : '')
    + '<br><a href="https://n8n-asistente-correo.onrender.com/webhook/oferta-aprobar?id=' + pageId
    + '" style="background:#22C55E;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block">Aprobar</a> '
    + '<a href="https://n8n-asistente-correo.onrender.com/webhook/oferta-descartar?id=' + pageId
    + '" style="background:#EF4444;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold;display:inline-block;margin-left:12px">Descartar</a>'
    + '</div>';

  const brevoBody = JSON.stringify({
    sender: {name: 'Verónica Serna', email: 'veronica@cookyourwebai.es'},
    to: [{email: email}],
    subject: 'Nueva oferta: ' + empresa + ' - ' + puesto,
    htmlContent: htmlContent,
    trackClicks: false,
    trackOpens: false
  });

  return { json: { empresa, puesto, salario, modalidad, pageId, email, linkOferta, brevoBody } };
});
