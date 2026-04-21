# 🚀 INSTRUCCIONES DE INICIO DE SESIÓN

> **Para cualquier agente IA que inicie una sesión en este proyecto:**

## 1. ANTES DE TOCAR NADA (obligatorio)

```bash
# Leer este archivo primero
cat .claude/INSTRUCCIONES-INICIO.md

# Leer memoria del proyecto
cat .claude/projects/-Users-vero-Desktop-buscartrabajo-cv-server/MEMORY.md

# Leer documentación completa
cat CLAUDE.md

# Verificar estado git
git status
git log --oneline -5
```

## 2. VERIFICAR SERVICIOS (antes de cualquier cambio)

```bash
# 1. CV Server está vivo
curl https://cv-server-ggd8.onrender.com/health

# 2. Diagnóstico completo
curl https://cv-server-ggd8.onrender.com/debug

# 3. n8n responde
curl -X POST https://n8n-qwmu.onrender.com/webhook/buscar-para-user \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","nombre":"Test","perfil":"test"}'
```

**Si algún servicio falla:**
- CV Server: revisar logs en Render Dashboard
- n8n: puede estar dormido (Render Free) — esperar 30-60s

## 3. REGLAS DE ORO (nunca violar)

| # | Regla | Por qué |
|---|-------|---------|
| 1 | `claude-sonnet-4-6` (sin fecha) | Ya inventamos fechas que no existen |
| 2 | `cv-server-ggd8.onrender.com` | Railway está muerto |
| 3 | `/generar-cv` requiere `email` | Multi-user, no hardcoded |
| 4 | `Teléfono Contacto` (con tilde) | Notion es case-sensitive |
| 5 | `Email empresa` (minúscula) | Notion es case-sensitive |
| 6 | 2 workflows separados | Patrón modular, debug independiente |
| 7 | Importar: primero Workflow 2, luego Workflow 1 | Webhook interno debe existir |

## 4. ANTES DE HACER COMMIT

```bash
# Verificar que no hay secrets
git ls-tree -r HEAD --name-only | grep -v ".archivo-historico" | xargs grep -l "ntn_G464872773099\|sk-ant-api03-[a-zA-Z0-9]\{20,\}" 2>/dev/null

# Si hay secrets: NO hacer commit, limpiar primero
```

## 5. ANTES DE HACER PUSH

```bash
# Repo principal
cd /Users/vero/Desktop/buscartrabajo
git push origin main

# CV Server (solo cambios críticos)
cd /Users/vero/Desktop/buscartrabajo/cv-server
git add <archivo>
git commit -m "fix: descripción"
git push origin main
```

**Si GitHub bloquea por secrets:**
1. Ir a la URL que te da GitHub
2. Click en "Allow"
3. Reintentar push

## 6. SKILLS A USAR (según tarea)

| Tarea | Skill |
|-------|-------|
| Planificar implementación | `superpowers:writing-plans` |
| Ejecutar plan | `superpowers:executing-plans` |
| Brainstorming | `superpowers:brainstorming` |
| Debugging | `superpowers:systematic-debugging` |
| Code review | `superpowers:requesting-code-review` |
| Frontend/CSS | `frontend-design:frontend-design` |
| n8n workflows | `n8n-workflow-patterns` |
| n8n Code node | `n8n-code-javascript` o `n8n-code-python` |

## 7. DOCUMENTACIÓN A LEER (según necesidad)

| Archivo | Cuándo leer |
|---------|-------------|
| `CLAUDE.md` | Siempre (memoria completa) |
| `MEMORY.md` | Inicio de sesión |
| `DOCUMENTACION_TECNICA_v2.md` | Arquitectura, deployment |
| `DOCUMENTACION_WORKFLOW.md` | Detalles de nodos n8n |
| `README.md` | Vista rápida |

## 8. ESTRUCTURA DEL PROYECTO

```
buscartrabajo/
├── .claude/
│   ├── INSTRUCCIONES-INICIO.md     ← ESTE ARCHIVO
│   └── projects/.../MEMORY.md      ← Memoria sesión
├── CLAUDE.md                        ← Memoria completa
├── README.md                        ← Vista general
├── DOCUMENTACION_TECNICA_v2.md      ← Arquitectura
├── DOCUMENTACION_WORKFLOW.md        ← Workflow n8n
├── cv-server/                       ← Repo separado (Render)
├── workflows/                       ← JSONs n8n exportados
├── add_notion_fields.py             ← Script local
├── sync_notion_schema.py            ← Script local
└── docs/
    └── .archivo-historico-2026-04-19/  ← NO USAR (histórico)
```

## 9. CHECKLIST RÁPIDA (pre-vuelo)

Antes de reportar "trabajo completo":

- [ ] Tests pasan (si hay)
- [ ] No hay secrets en archivos activos
- [ ] URLs correctas (Render, no Railway)
- [ ] Commits atómicos con mensajes claros
- [ ] Push realizado a GitHub
- [ ] Documentación actualizada (si cambia arquitectura)

---

## 10. CONTACTO DE EMERGENCIA

Si algo no está claro:

1. Revisar `CLAUDE.md` — sección "Bugs conocidos"
2. Revisar `docs/.archivo-historico-2026-04-19/` — qué se hizo antes
3. Preguntar a Verónica (usuario)

---

**Última actualización:** 21 Abril 2026  
**Versión:** 2.0 Multi-User
