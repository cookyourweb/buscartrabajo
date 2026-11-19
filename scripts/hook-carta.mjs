#!/usr/bin/env node
// Hook PreToolUse de Claude Code: bloquea una carta de presentacion que rompa
// docs/reference/16-COVER-LETTER-RULES.md antes de que llegue a un formulario.
//
// El 26-oct salieron cinco cartas que rompian la regla. La regla estaba
// escrita desde el 31-ago; lo que faltaba era algo que la comprobara.
//
// Recibe por stdin el JSON de la llamada a la herramienta. Mira:
//   - mcp__claude-in-chrome__form_input  -> tool_input.value
//   - mcp__claude-in-chrome__computer    -> tool_input.text (accion "type")
//   - Write                               -> tool_input.content, solo si el
//                                            fichero se llama carta*/cover*
// Si el texto parece una carta y no pasa, sale con 2 y el motivo: Claude Code
// bloquea la llamada y se lo enseña al modelo. Todo lo demas sale con 0.
import { validarCarta, pareceCarta } from './lib/carta.mjs';
import { validarRespuesta, pareceRespuesta } from './lib/respuesta.mjs';

let entrada = '';
for await (const trozo of process.stdin) entrada += trozo;

let llamada;
try {
  llamada = JSON.parse(entrada);
} catch {
  process.exit(0);
}

const { tool_name: herramienta = '', tool_input: datos = {} } = llamada;

let texto = null;
if (herramienta.endsWith('form_input')) texto = datos.value;
else if (herramienta.endsWith('__computer') && datos.action === 'type') texto = datos.text;
else if (herramienta === 'Write' && /(carta|cover)[^/]*$/i.test(datos.file_path ?? '')) texto = datos.content;

// Un fichero que no es una carta no se comprueba: solo los formularios.
const esFormulario = herramienta !== 'Write';

if (pareceCarta(texto)) {
  const errores = validarCarta(texto);
  if (errores.length === 0) process.exit(0);
  process.stderr.write(
    'CARTA BLOQUEADA: no cumple docs/reference/16-COVER-LETTER-RULES.md\n' +
      errores.map((e) => `  - ${e}`).join('\n') +
      '\nReescríbela con la plantilla de la regla 16 (no argumenta, abre la puerta) y vuelve a intentarlo.\n',
  );
  process.exit(2);
}

if (esFormulario && pareceRespuesta(texto)) {
  const errores = validarRespuesta(texto);
  if (errores.length === 0) process.exit(0);
  process.stderr.write(
    'RESPUESTA BLOQUEADA: no cumple docs/reference/21-FORM-ANSWER-RULES.md\n' +
      errores.map((e) => `  - ${e}`).join('\n') +
      '\nReescríbela con voz natural: sin conectores de informe, sin nombrar proyectos, sin huecos.\n',
  );
  process.exit(2);
}

process.exit(0);
