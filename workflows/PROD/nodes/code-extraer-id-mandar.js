const queryId = $input.first().json.query?.id;
const directId = $input.first().json.id;
const id = queryId || directId || '';
const fechaEnvio = new Date().toISOString();
if (!id) throw new Error('No se encontró ID de oferta: ' + JSON.stringify($input.first().json));
return [{ json: { id, fechaEnvio } }];