# Workflows en n8n — qué está subido y su estado

Inventario de lo que está SUBIDO Y CORRIENDO en la instancia de n8n. Los ficheros `.json`
de `workflows/` NO son la fuente de verdad (son exports/backups); la fuente de verdad es la
instancia n8n. Este documento existe para saber, de un vistazo, qué corre en producción sin
tener que abrir n8n.

**Estado verificado vía n8n API el 20-jul-2026.** Si cambias algo en n8n, actualiza esta tabla.

---

## Workflows activos y su estado

| Workflow | ID n8n | Estado | Qué hace |
|----------|--------|--------|----------|
| **BuscarTrabajo — Ofertas Diarias (PROD, dedup ON)** | `5pTwriXcc6aYHO1Y` | 🟢 ACTIVE | **EL DE PRODUCCIÓN.** Cada mañana (cron 07:00Z) busca ofertas reales, las escribe en Notion y manda el mail diario. Sender `veronica@cookyourwebai.es`. Dedup ON (no repite ofertas). |
| **WF2 Integrado v3** | `3zFJWSkPPHDi4yMp` | 🔴 OFF | Era "el bueno" del plan original, pero NO se usa. Se dejó inactivo. Export en disco: `workflows/WF2-integrado-v3.json`. |
| **Búsqueda Empleo Diaria** (Telegram) | `LODaOAsNrmU7NnJ4` | 🟢 ACTIVE | Manda ofertas por Telegram. NO escribe Notion, no afecta al flujo de ofertas por mail. |
| **Captura Gmail (Facturas + Trabajo)** | — | 🟢 ACTIVE | Captura facturas de Gmail y las registra en Notion + sube el PDF a Drive. Export canónico: `workflows/captura-gmail-facturas-BUENA-v4.1.json`. |

Otros workflows menores comparten la credencial Groq viva `Groq account 2`
(`Ewz07GBHAM5voex1`): **Digest** y **Outlook FIX**. Estado no verificado en detalle aquí.

---

## Notas importantes (no perder)

- **El "workflow bueno" ya NO es WF2 v3.** El que corre en PROD es el ex-TEST
  `5pTwriXcc6aYHO1Y`, promovido y renombrado. Si buscas por qué llegan las ofertas, es ese.
- **Búsqueda Empleo Diaria (Telegram)** fallaba TODOS los días (17-20 jul) porque su nodo
  "Groq Chat Model" apuntaba a una credencial BORRADA (`2b1f3WOTcvKNLpgy`). El 20-jul se
  repuntó a la credencial viva `Groq account 2` (`Ewz07GBHAM5voex1`) vía n8n public API.
  Pendiente verificar un run limpio.
- **Credencial Groq viva**: `Groq account 2` = `Ewz07GBHAM5voex1`. La muerta era
  `2b1f3WOTcvKNLpgy` (no existe en la instancia).

---

## Ficheros de export en `workflows/` (NO son la fuente de verdad)

Son backups/exports, útiles para reimportar. **Trampa conocida**: el sufijo `(5)` en un
nombre de fichero descargado NO es la versión 5, es el contador de descargas del navegador.
No fiarse del número del nombre.

- `WF1-BuscarTrabajo-Usuarios.json`
- `WF2-BuscarTrabajo-v2-Groq.json`
- `WF2-integrado-v3.json` (workflow OFF en n8n)
- `captura-gmail-facturas-BUENA-v4.1.json` (canónico de Captura Gmail)
- `captura-gmail-facturas-BUENA-v4.json` (anterior)

---

**Última actualización:** 20 julio 2026
**Ver también:** `../README.md` (flujo completo del sistema).
