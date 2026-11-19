# Constitución — buscartrabajo

Principios innegociables. Toda spec, plan y tarea debe cumplirlos.

1. **El ecosistema manda**: cambios en `panel-empleo`, `cv-server` y `buscartrabajo` deben considerar impacto cruzado.
2. **La spec manda**: nada se implementa si no está en la spec activa. Si falta una decisión, se para.
3. **Trazabilidad**: los flujos de candidaturas deben poder auditarse por usuario, oferta y fecha.
4. **Secretos fuera del código**: env vars, nunca tokens en repo.
5. **Tests como puerta**: tests relevantes antes de avanzar.
6. **Cambios pequeños y verificables**: una tarea por vez y checkpoints claros.
7. **Idiomas**: código en inglés cuando haya stack compartido; UI, documentos y comunicación en español.
8. **Privacidad**: no exponer datos personales en logs o commits.