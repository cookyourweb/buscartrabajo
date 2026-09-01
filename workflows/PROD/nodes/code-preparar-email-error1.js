const errorData = $input.first().json;

// Capturar TODA la información disponible del error
const workflowName = errorData.workflow?.name || 'Desconocido';
const nodeName = errorData.node?.name || errorData.nodeName || 'Unknown';
const errorMessage = errorData.error?.message || errorData.message || JSON.stringify(errorData);
const errorStack = errorData.error?.stack || errorData.stack || 'No stack';
const timestamp = new Date().toISOString();

// Serializar error completo para debugging
const errorCompleto = JSON.stringify(errorData, null, 2);

return [{
  json: {
    to: 'hello.cookyourweb@gmail.com',
    subject: `❌ ERROR en ${workflowName} - ${nodeName}`,
    htmlContent: `<div style="font-family:Arial;padding:20px;max-width:600px">
      <h2 style="color:#EF4444">❌ Error en Workflow</h2>
      <div style="background:#f9f9f9;padding:16px;border-radius:6px;margin:20px 0">
        <p><strong>Workflow:</strong> ${workflowName}</p>
        <p><strong>Nodo:</strong> ${nodeName}</p>
        <p><strong>Error:</strong> ${errorMessage}</p>
        <p><strong>Timestamp:</strong> ${timestamp}</p>
      </div>
      <div style="background:#fff0f0;padding:16px;border-radius:6px;margin:20px 0;font-family:monospace;font-size:12px;word-break:break-all">
        <strong>Raw error data:</strong><br>
        <pre>${errorCompleto}</pre>
      </div>
      <div style="background:#f0f0f0;padding:16px;border-radius:6px;margin:20px 0;font-family:monospace;font-size:11px;word-break:break-all;max-height:300px;overflow:auto">
        <strong>Stack trace:</strong><br>
        <pre>${errorStack}</pre>
      </div>
      <p style="color:#666;font-size:14px;margin-top:20px">Revisa n8n para más detalles.</p>
    </div>`
  }
}];