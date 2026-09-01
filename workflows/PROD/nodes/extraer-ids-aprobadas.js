// De la respuesta de Notion, saca el id de cada oferta Aprobada.
const resp = $input.first().json;
const results = resp.results || [];
return results.map(p => ({ json: { id: p.id } }));