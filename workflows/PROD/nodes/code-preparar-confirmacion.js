// Rama "Enviar a empresa": lee la carta YA EDITADA de Notion y decide híbrido.
const d = $('Notion - Obtener Datos Mandar').first().json;
const p = d.properties || {};

const empresa = p.Empresa?.title?.[0]?.text?.content || p.Empresa?.title?.[0]?.plain_text || 'la empresa';
const puesto = p.Puesto?.rich_text?.[0]?.plain_text || p.Puesto?.rich_text?.[0]?.text?.content || '';
const pageId = d.id || '';
const linkOferta = p['Link oferta']?.url || '';
const linkCV = p['Link CV Drive']?.url || '';
const emailEmpresa = p['Email empresa']?.email || '';
const nombreContacto = p['Nombre Contacto']?.rich_text?.[0]?.plain_text || '';
const emailUsuario = p['Email Enviado']?.email || 'hello.cookyourweb@gmail.com';

// Carta editada (rich_text en chunks → unir)
const carta = (p['Carta Enviada']?.rich_text || []).map(t => t.plain_text || t.text?.content || '').join('') || '(carta no encontrada)';

const tieneEmail = emailEmpresa && emailEmpresa.includes('@');

let brevoBody;

if (tieneEmail) {
  // CASO AUTO: hay email de la empresa → mandar carta + CV directo a la empresa
  const html = '<div style="font-family:Arial;padding:20px;max-width:600px">'
    + (nombreContacto ? '<p>Estimado/a ' + nombreContacto + ',</p>' : '')
    + '<div style="line-height:1.6;white-space:pre-wrap">' + carta + '</div>'
    + (linkCV ? '<br><br><a href="' + linkCV + '" style="background:#1F5C8B;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block">📄 Ver mi CV</a>' : '')
    + '</div>';
  brevoBody = JSON.stringify({
    sender: { name: 'Verónica Serna', email: 'veronica@cookyourwebai.es' },
    to: [{ email: emailEmpresa }],
    replyTo: { email: emailUsuario, name: 'Verónica Serna' },
    subject: 'Candidatura: ' + puesto + (empresa ? ' — ' + empresa : ''),
    htmlContent: html,
    trackClicks: false,
    trackOpens: false
  });
} else {
  // CASO MANUAL: sin email → avisar a Verónica con el link para aplicar a mano
  const html = '<div style="font-family:Arial;padding:20px;max-width:600px">'
    + '<h2 style="color:#F59E0B">📋 Aplicar a mano</h2>'
    + '<p>La oferta de <b>' + empresa + ' — ' + puesto + '</b> no trae email de contacto, así que hay que aplicar por el portal.</p>'
    + '<p>Tu carta y CV ya están listos:</p>'
    + (linkOferta ? '<p><a href="' + linkOferta + '" style="background:#22C55E;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;font-weight:bold" target="_blank">🔗 Ir a la oferta para aplicar</a></p>' : '')
    + (linkCV ? '<p><a href="' + linkCV + '" style="color:#1F5C8B;font-weight:bold;text-decoration:underline" target="_blank">📄 Tu CV en Drive</a></p>' : '')
    + '<div style="margin-top:16px;padding:16px;background:#f9f9f9;border-radius:6px;line-height:1.6;white-space:pre-wrap"><b>Tu carta:</b><br>' + carta + '</div>'
    + '</div>';
  brevoBody = JSON.stringify({
    sender: { name: 'Verónica Serna', email: 'veronica@cookyourwebai.es' },
    to: [{ email: emailUsuario }],
    subject: '📋 Aplicar a mano — ' + empresa + ' — ' + puesto,
    htmlContent: html,
    trackClicks: false,
    trackOpens: false
  });
}

return [{
  json: {
    empresa, puesto, pageId, emailEmpresa, tieneEmail,
    modo: tieneEmail ? 'auto-email-empresa' : 'manual-link',
    brevoBody
  }
}];
