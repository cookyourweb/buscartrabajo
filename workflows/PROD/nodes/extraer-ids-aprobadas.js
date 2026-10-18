// De la respuesta de Notion, saca el id de cada oferta Aprobada.
const resp = $input.first().json;
const results = resp.results || [];
// One offer per run: several at once ran n8n out of memory (8-oct-2026).
return results.slice(0, 1).map(p => ({ json: { id: p.id } }));