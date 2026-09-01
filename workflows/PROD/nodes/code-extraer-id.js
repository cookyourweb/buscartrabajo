const queryId = $input.first().json.query?.id;
const directId = $input.first().json.id;
const id = queryId || directId || '';
if (!id) throw new Error('No se encontró ID de oferta: ' + JSON.stringify($input.first().json));
console.log('✅ Oferta aprobada - ID:', id);
return [{ json: { id } }];