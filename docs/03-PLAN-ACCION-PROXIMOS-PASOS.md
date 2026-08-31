# 🎯 Plan de acción — Próxima sesión BuscarTrabajo

**Para retomar el trabajo desde donde lo dejamos.**

---

## 📌 Estado al cierre (28 abril 2026)

✅ **Sistema completo funcionando end-to-end:**
- Registro web → Notion + email con oferta
- "Buscar ahora" desde web → email con oferta
- Aprobar oferta → genera CV + carta y se envía

❌ **Pendiente:**
- Las ofertas son **inventadas** por Groq (no reales)
- El CV adaptado no usa el CV Master del usuario (genera genérico)
- Hay deuda de seguridad (rotar keys, repo privado)

---

## 🚦 3 caminos posibles

Elige según tu prioridad:

### Camino A — VALIDAR primero (recomendado si quieres beta YA)
**Tiempo:** 2-3 horas
**Coste:** 0€

1. Limpiar usuarios y ofertas de prueba en Notion
2. Rotar API keys expuestas
3. Hacer repo cv-server privado
4. Invitar 2-3 personas de confianza a probar el formulario
5. Recoger feedback durante 1 semana
6. **Si validan que les sirve** → ir a Camino C

### Camino B — SEGURIZAR primero (recomendado si quieres dormir tranquila)
**Tiempo:** 1 hora
**Coste:** 0€

1. Rotar API keys (Groq, Notion, Brevo, Gemini)
2. Repo cv-server → privado
3. Suspender instancia n8n-qwmu (vacía)
4. Documentar credenciales nuevas en gestor seguro (1Password / Bitwarden)

### Camino C — OFERTAS REALES (lo gordo, recomendado para producto)
**Tiempo:** 8-12 horas
**Coste:** 0€ con APIs gratuitas

1. Implementar `/buscar-ofertas-reales` en Flask
2. Integrar Remotive + Getonboard + Adzuna
3. Mejorar `/generar-cv` para usar CV Master real
4. Cambiar nodo Groq por HTTP a Flask en n8n
5. Test end-to-end con ofertas reales

---

## 🎯 Mi recomendación

**Camino B + Camino C en paralelo.** Razones:

- Camino B son 30-60 min, deuda de seguridad real
- Camino C es lo que convierte tu MVP en producto real
- Sin Camino C, no tiene sentido ir a Camino A (las ofertas inventadas no sirven para validar nada serio)

**Orden óptimo:**

1. **Hoy/mañana** — Camino B (1h)
2. **Sesión siguiente** — Camino C, fase 1: Remotive (2h)
3. **Sesión +1** — Camino C, fases 2-3: endpoint + CV real (4h)
4. **Sesión +2** — Camino C, fases 4-5: integrar n8n + tests (3h)
5. **Sesión +3** — Camino A: invitar beta testers (1h)

Total: **~10-12h** repartidas en 4-5 sesiones.

---

## 📝 Primer mensaje para retomar

Cuando vuelvas, copia y pega esto:

```
Retomo BuscarTrabajo desde donde lo dejamos el 28 abril 2026.
Sistema v2.3 funcionando end-to-end. Documentación completa en:
  - 01-DOCUMENTACION-MAESTRA-v2.3.md
  - 02-PROPUESTA-v3.0-OFERTAS-REALES.md
  - 03-PLAN-ACCION-PROXIMOS-PASOS.md (este archivo)

Quiero hacer: [elige uno]
  - Camino B: rotar keys y proteger
  - Camino C: integrar Remotive (fase 1)
  - Otra cosa concreta

Sin asumir nada. UN paso cada vez. Espera a mi confirmación
antes de tocar código.
```

---

## ⚠️ Reglas no negociables que aprendimos

1. **NO API keys hardcoded** en código ni JSONs
2. **NO placeholders** tipo "TU_API_KEY_AQUÍ" en código
3. **Limpiar uploads de prueba** antes de cerrar sesión
4. **Probar UN paso cada vez**, sin bucles
5. **Esperar 3-5 min entre tests** (Render Free duerme)
6. **Una sola instancia n8n activa** (st1v actualmente)
7. **Reasignar credenciales nodo por nodo** tras cada import
8. **Email a remitentes verificados en Brevo** (o pasar a plan Lite)

---

## 🔧 Recordatorio técnico

### URLs producción
- CV Server: `https://cv-server-ggd8.onrender.com`
- n8n activo: `https://n8n-st1v.onrender.com`
- n8n viejo (no usar): `https://n8n-qwmu.onrender.com`

### Notion DBs
- Usuarios: `34811515f4b280f19a42f8da5e91a8fe`
- Ofertas: `33d11515f4b281efa776d0ea698b748f`

### Workflows n8n
- WF1 `BuscarTrabajo-Usuarios` (10 nodos) — recibe registros y dispara WF2
- WF2 `BuscarTrabajo-v2-Groq` (39 nodos) — genera ofertas, aprobar, CV+carta

### Comandos útiles
```bash
# Health check
curl https://cv-server-ggd8.onrender.com/health

# Test LLM
curl https://cv-server-ggd8.onrender.com/debug

# Disparar <RUTA_OCULTA> desde fuera
curl -X POST https://n8n-st1v.onrender.com/webhook/<RUTA_OCULTA> \
  -H "Content-Type: application/json" \
  -d '{"email":"hello.cookyourweb@gmail.com","nombre":"vero"}'
```
