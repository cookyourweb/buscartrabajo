# TODO: Evolución Profesional BuscarTrabajo (Real Offers + Scale)

## 🚀 Fase 1: Backup Mocks (Groq Current)
- [ ] git add . (incluye TODO changes)
- [ ] git commit -m "Backup mocks Groq v2.3 + workflows actuales"
- [ ] git checkout -b feature/mocks-groq-backup
- [ ] git push -u origin feature/mocks-groq-backup

## 🔍 Fase 2: Ofertas Reales
- [ ] Leer/analizar workflows Groq (BuscarTrabajo-v2-Groq.json, workflows/)
- [ ] Implementar scraper/API: Adzuna/Jooble + InfoJobs (nuevo cv-server/real_jobs.py)
- [ ] Editar WF2: reemplazar Groq node → RealJobs node → filter por user prefs
- [ ] Update cv_server_railway.py: /generar-cv usa ofertas reales
- [ ] Test: manual trigger → real offers en Notion/Brevo

## 🎨 Fase 3: Figma + Lovable
- [ ] Crear Figma prototypes (form, dashboard)
- [ ] WF3: Lovable → React previews Vercel

## ⚡ Fase 4: Scale
- [ ] Redis queue, Sentry, CI/CD
- [ ] Deploy + monitor

**Criterios Éxito**: Ofertas reales (no inventadas), >50/día, match rate >70%, emails con links reales.
