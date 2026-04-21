# Instrucciones para Sesiones N8N

## 🚀 Startup de Sesión

Cuando empieces una sesión de N8N:

1. **Escribe:** `/superpowers:using-superpowers`
2. **Pide cargar estos agents/skills:**

| Skill | Propósito |
|-------|-----------|
| `n8n-mcp-tools-expert` | 40+ herramientas para nodos, validación y gestión de workflows |
| `n8n-code-javascript` | Patrones para Code nodes en JavaScript |
| `n8n-code-python` | Patrones para Code nodes en Python |
| `n8n-validation-expert` | Interpreta y corrige errores de validación |
| `n8n-workflow-patterns` | 5 arquitecturas core de workflows |
| `n8n-expression-syntax` | Sintaxis correcta de expresiones n8n |

---

## 📧 Testing: Botón "Mandar a Empresa"

### Configuración Temporal (Testing)

**Email de destino:** `hello.cookyourweb@gmail.com`

Usar este email para pruebas del webhook `/mandar-empresa` hasta que se apruebe el flujo.

### Configuración Final (Producción)

Una vez aprobado el testing:

| Campo | Origen |
|-------|--------|
| Email empresa | Variable de Notion (`Contacto.email`) |
| Nombre contacto | Variable de Notion (`Contacto.nombre`) |
| Otros datos | Campos de la oferta en Notion |

---

## 📋 Checklist Implementación

- [ ] Añadir botón "✅ Mandar a empresa" en Email #2
- [ ] Crear webhook `/mandar-empresa` (testing → `hello.cookyourweb@gmail.com`)
- [ ] Añadir columnas en Notion: Fecha envío, Contacto, Link CV enviado, Seguimiento
- [ ] Añadir nodos de seguimiento en Notion
- [ ] Crear Email #4 de confirmación
- [ ] **Testing con email temporal**
- [ ] **Actualizar a variables de Notion para producción**

---

**Última actualización:** 17 Abril 2026
