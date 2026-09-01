// Convierte resultados de Notion a formato plano
const results = $input.first().json.results || [];
return results.map(u => {
  const p = u.properties || {};
  return { json: {
    user_id:    u.id,
    nombre:     p.Name?.title?.[0]?.plain_text || '',
    email:      p.Email?.email || '',
    email_usuario: p.Email?.email || '',
    perfil:     p.Perfil?.rich_text?.[0]?.plain_text || '',
    rol:        p['Rol objetivo']?.rich_text?.[0]?.plain_text || '',
    stack:      (p.Stack?.multi_select || []).map(s => s.name),
    salario:    p['Salario min']?.number || 0,
    modalidad:  (p.Modalidad?.multi_select || []).map(m => m.name),
    ciudad:     p.Ciudad?.rich_text?.[0]?.plain_text || '',
    linkedin:   p.LinkedIn?.url || '',
    cv_master_url: p['CV Master URL']?.url || '',
    source:     'schedule'
  }};
});