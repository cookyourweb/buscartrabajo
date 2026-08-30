const body = $input.first().json.body || $input.first().json;
return [{ json: {
  nombre:        body.nombre     || '',
  email:         body.email      || '',
  email_usuario: body.email      || '',
  perfil:        body.perfil     || '',
  rol:           body.rol        || '',
  stack:         body.stack      || [],
  salario:       body.salario    || 0,
  modalidad:     body.modalidad  || [],
  ciudad:        body.ciudad     || '',
  linkedin:      body.linkedin   || '',
  cv_master_url: body.cv_master_url || '',
  user_id:    body.user_id || '',
    source:        body.source     || 'interno'
}}];