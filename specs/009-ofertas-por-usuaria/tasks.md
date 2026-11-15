# Tasks 009 — Ofertas por usuaria

- [x] T1. Añadir campos al perfil en Postgres (`regiones_remoto`, `ciudades_hibrido`, `tarifa_dia_min`, `evitar`) con migración.
- [x] T2. Extender modelo `perfil` en cv-server y lectura por usuaria.
- [x] T3. Implementar `POST /buscar-para-usuaria` (mínimo: lee perfil y ejecuta búsqueda; Notion/creación en T6).
- [x] T4. Portar filtrado Groq + Normalizar Modalidad a Python.
- [ ] T5. Integrar fuentes (Remotive, Tecnoempleo, Google Jobs, Adzuna) por usuaria.
- [x] T6. Crear oferta en Notion por usuaria (vinculada por email/notion_id) — puntuación sigue en T8 (n8n).
- [ ] T7. Respetar cuota Neon (8/mes, spend cap).
- [ ] T8. Actualizar n8n: bucle por usuaria → webhook, scoring una vez.
- [ ] T9. Tests unitarios de filtrado y aislamiento.
- [ ] T10. Prueba end-to-end con usuaria de prueba.
- [ ] T11. Retirar/marcar deprecated Phase 1.
- [ ] T12. Verificar en Chrome DevTools (móvil).