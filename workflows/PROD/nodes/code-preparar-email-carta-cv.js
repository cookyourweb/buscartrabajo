const notionData = $('Notion - Obtener Datos Oferta').first().json;
const empresa = notionData.properties?.Empresa?.title?.[0]?.text?.content || notionData.properties?.Empresa?.title?.[0]?.plain_text || '';
const puesto = notionData.properties?.Puesto?.rich_text?.[0]?.text?.content || '';
const pageId = notionData.id || '';
const nombreContacto = notionData.properties?.['Nombre Contacto']?.rich_text?.[0]?.text?.content || '';
const emailContacto = notionData.properties?.['Email empresa']?.email || '';
const telefonoContacto = notionData.properties?.['Teléfono Contacto']?.phone_number || '';

const cartaText = $('Groq - Generar Carta').first().json.carta || '';

let linkCV = '';
try {
  linkCV = $('CV Server - Generar CV').first().json.link || null;
} catch(e) {}

let cvMaster = '';
try {
  cvMaster = $('CV Server - Generar CV').first().json.cv_master_url || '';
} catch(e) {}

// Email del usuario (para avisarle que está listo para revisar)
const emailDestino = notionData.properties?.['Email Enviado']?.email
  || notionData.properties?.['Email usuario']?.email
  || notionData.properties?.['Email usuario']?.rich_text?.[0]?.plain_text
  || 'hello.cookyourweb@gmail.com';

// Carta en chunks de 1900 chars para guardar en Notion (límite rich_text 2000)
const chunk = (s, n) => {
  const a = [];
  for (let i = 0; i < (s || '').length; i += n) a.push({ text: { content: s.slice(i, i + n) } });
  return a.length ? a : [{ text: { content: '' } }];
};
const cartaRichText = chunk(cartaText, 1900);

// Link a la página de Notion para editar la carta
const notionPageUrl = 'https://www.notion.so/' + pageId.replace(/-/g, '');

const htmlContent = '<div style="font-family:Arial;padding:20px;max-width:600px">'
  + '<h2 style="color:#1F5C8B">📝 Carta y CV listos para revisar</h2>'
  + '<h3>' + empresa + ' — ' + puesto + '</h3>'
  + '<p>Tu carta y CV ya están generados. <b>Revisalos y editalos si querés ANTES de enviar:</b></p>'
  + '<div style="padding:16px;line-height:1.6;white-space:pre-wrap;background:#f9f9f9;border-radius:6px">' + cartaText + '</div>'
  + '<p style="margin-top:16px">'
  + '<a href="' + notionPageUrl + '" style="color:#1F5C8B;font-weight:bold;text-decoration:underline" target="_blank">✏️ Editar la carta en Notion</a>'
  + (linkCV ? '&nbsp;&nbsp;|&nbsp;&nbsp;<a href="' + linkCV + '" style="color:#1F5C8B;font-weight:bold;text-decoration:underline" target="_blank">✏️ Editar el CV en Drive</a>' : '')
  + '</p>'
  + '<p style="color:#666;font-size:13px">Cuando la carta y el CV estén como querés, pulsá Enviar:</p>'
  + '<a href="https://n8n-asistente-correo.onrender.com/webhook/@@SECRET:Webhook Mandar Empresa?id=' + pageId + '" style="background:#22C55E;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;font-weight:bold">🚀 Enviar a empresa</a>'
  + '</div>';

const brevoBody = JSON.stringify({
  sender: { name: 'Verónica Serna', email: 'veronica@cookyourwebai.es' },
  to: [{ email: emailDestino }],
  subject: '📝 Revisar y enviar — ' + empresa + ' — ' + puesto,
  htmlContent: htmlContent,
  trackClicks: false,
  trackOpens: false
});

return [{
  json: {
    empresa, puesto, pageId, cartaText, linkCV, nombreContacto, emailContacto, telefonoContacto,
    notionPageId: pageId,
    notionLinkCV: linkCV || null,
    cvMaster: cvMaster || '',
    cartaEnviada: cartaText,
    cartaRichText,
    emailDestino,
    htmlContent,
    brevoBody
  }
}];
