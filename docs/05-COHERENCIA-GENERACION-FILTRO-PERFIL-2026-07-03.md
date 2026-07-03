# 🧭 Coherencia Generación ↔ Filtro ↔ Perfil (3 jul 2026)

> **Por qué existe este doc:** antes de hacer un barrido de ofertas REALES y "empezar de cero",
> verificamos que los cambios de hoy en la generación del CV NO obligan a tocar el filtro de
> ingesta. Conclusión: el código del filtro **no se toca**; lo que hay que alinear es el
> **perfil del usuario en Notion**.

**Estado:** ✅ verificado · **Fuente de verdad operativa:** [`../README.md`](../README.md)

---

## 🎯 Las TRES fases (no confundirlas)

El sistema tiene tres momentos distintos. Un cambio en uno **no** implica cambio en los otros.

| Fase | Qué hace | Dónde vive | ¿Se tocó hoy? |
|------|----------|-----------|----------------|
| **1. Ingesta / Filtro** | De las ofertas reales, elige las 5 que mejor encajan | n8n `WF2-integrado-v3` → nodo **Groq - Generar Ofertas** | ❌ NO |
| **2. Aprobación** | Vero aprueba la oferta → dispara generación | n8n **Webhook Aprobar** → Notion "Marcar Aprobado" | ❌ NO |
| **3. Generación** | Arma el CV + carta adaptados a la oferta | **cv-server** `cv_server_railway.py` (prompt) | ✅ SÍ |

---

## 🔍 Fase 1 — Cómo filtra realmente (el hallazgo clave)

El nodo **Groq - Generar Ofertas** NO tiene "frontend/backend" hardcodeado. Filtra por el
**PERFIL del usuario leído de Notion**:

- `Rol objetivo`
- `Stack`
- `Salario mínimo`
- `Modalidad` (remoto / híbrido / ciudad)
- `Ciudad`

**Criterios (en orden):** 1) encaje perfil/stack · 2) salario · 3) modalidad ·
4) descarta lo fuera de perfil (ventas, soporte, oficios no técnicos).
Devuelve las **5 mejores** como array JSON. `temperature: 0.3`.

> Diseño correcto y multi-usuario: nada hardcodeado, todo por usuario en Notion.
> Por eso **el filtro no se cambia**.

---

## ⚠️ El punto de coherencia (lo que SÍ hay que alinear)

Los cambios de hoy consolidaron el posicionamiento de Vero en **tres frentes**:

**Frontend Tech Lead · Full-Stack Developer · UX Engineer** (+ IA aplicada).

Pero como el filtro elige por `Rol objetivo` + `Stack` del **perfil en Notion**:

> Si el perfil de Vero en Notion dice **solo "Frontend"**, el barrido de ofertas reales
> **descartará** las ofertas Full-Stack e IA — justo los frentes que el CV ya sabe generar.
> El CV los sabe hacer; el filtro no los dejaría entrar. Incoherencia.

### ✅ Acción (NO es código, es datos)

Actualizar el **perfil de Vero en Notion** para que refleje los tres frentes.

#### Perfil REAL en Notion (leído 3 jul 2026)

> DB `Users` (`collection://34811515-f4b2-80d6-875a-000b7b858306`) → página "Verónica Serna Pérez"

| Campo | Valor actual |
|-------|--------------|
| Rol objetivo | `Full-Stack Developer & AI Engineer` |
| Perfil | `Full-Stack Tech Lead & AI Engineer` |
| Stack | React, TypeScript, Vue.js, Node.js, Python, Java, AI/ML, DevOps |
| Salario min | 60000 · Modalidad: Remoto + Híbrido Madrid · Ciudad: Valdemorillo |
| CV Master EN | `1XzZm1MIZ2bj5...` ✅ (el bueno) |
| CV Master ES | `1hYSwJHWRMU47jkud2bWh...` ⚠️ SIN VERIFICAR (¿actualizado o viejo?) |

#### Gaps detectados vs. los 3 frentes

1. **`Rol objetivo` no menciona Frontend ni UX** → el filtro rankea abajo/descarta
   ofertas de Frontend puro y UX Engineer (2 de los 3 frentes).
2. **`Stack` con huecos:** faltan **Next.js, Firebase, MongoDB, Design Systems, UX,
   n8n, LLMs** → el filtro no engancha esos ángulos.
3. **`Java` en el stack** → contradice la regla "Java = tech vieja, no especialista";
   puede colar ofertas Java-heavy no deseadas. **Decisión pendiente de Vero.**

#### Cambio propuesto (pendiente de confirmar Rol objetivo con Vero)

- **Rol objetivo →** `Frontend Tech Lead · Full-Stack Developer · UX Engineer · AI`
  (opción "los 3 frentes"; hay 2 alternativas más estrechas sin decidir).
- **Stack →** sumar `Next.js, Firebase, MongoDB, Design Systems, UX, n8n, LLMs`.
  Revisar si se quita `Java`.

Así el filtro trae ofertas de los tres frentes, y la generación (ya alineada) las adapta.

---

## 🧬 Qué se cambió HOY en la Generación (contexto)

En `cv-server/cv_server_railway.py` (commits `9136979`, `d70a5c6` en `main`, deploy Render):

- **Sistema de titulares:** `IDENTIDAD REAL + ESPECIALIZACIÓN DE LA OFERTA`.
  Núcleo siempre uno de: Frontend Tech Lead / Full-Stack Developer / UX Engineer.
- **Casos por oferta:** Frontend · Full Stack · Tech Lead · IA (cada uno con su titular).
- **Títulos IA defendibles:** AI Product Builder / AI Solutions Engineer / AI Automation Engineer.
  Prohibido "AI Expert" / "AI Specialist".
- **Nivel del puesto:** el titular refleja seniority; el CUERPO se centra en lo técnico
  (no venderse como manager en ofertas IC).
- **Años de experiencia:** base **"10+"**, sube solo si la oferta valora seniority.
  NO clavar "15+".

---

## 🔄 Flujo completo (referencia)

```
Barrido ofertas REALES (Remotive + Adzuna + Tecnoempleo)
        ↓
Groq - Generar Ofertas  ← filtra por PERFIL Notion (Rol objetivo + Stack + ...)
        ↓
Notion - Crear Oferta   (entran las 5 mejores)
        ↓
Vero aprueba → Webhook Aprobar → Notion "Marcar Aprobado" → "Obtener Datos Oferta"
        ↓
cv-server → CV + carta adaptados (titulares/años/nivel de HOY)
        ↓
Google Drive (CV) + email al usuario
```

---

## ✔️ Checklist antes del barrido de "empezar de cero"

- [ ] **Perfil Notion de Vero** actualizado a los 3 frentes (Rol objetivo + Stack). ← bloqueante
- [ ] Ofertas de prueba viejas eliminadas de Notion (eran de desarrollo, no candidaturas reales).
- [ ] Confirmado que el barrido dispara `WF2-integrado-v3` (instancia `n8n-asistente-correo.onrender.com`).
- [ ] cv-server en Render con último deploy (`d70a5c6`). ✅ hecho.
