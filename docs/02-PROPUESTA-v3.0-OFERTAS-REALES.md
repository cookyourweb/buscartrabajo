# 🚀 BuscarTrabajo v3.0 — Ofertas REALES + CV adaptado

**Estado:** Diseño / propuesta técnica
**Objetivo:** Pasar de "ofertas inventadas por LLM" a "ofertas reales scrapeadas + CV adaptado al CV master del usuario"

---

## 🎯 Por qué esto es crítico

**Estado actual (v2.3):**
- Groq inventa empresas, puestos, contactos
- Bonito para demo pero no es un producto real
- El CV se "adapta" a una oferta inventada → no sirve para enviar a empresas

**Estado deseado (v3.0):**
- Ofertas REALES de LinkedIn / Remotive / Getonboard / InfoJobs
- LLM rankea cuáles encajan con el perfil del usuario
- CV del usuario (CV Master) se adapta a la oferta REAL
- El usuario puede enviar candidatura genuina

---

## 📊 Comparativa actual vs futura

| Aspecto | v2.3 actual | v3.0 propuesto |
|---------|-------------|----------------|
| Origen ofertas | Groq las inventa | APIs / scraping reales |
| Datos contacto | Inventados | Reales o ausentes |
| CV adaptado | Genérico, sin relación con CV Master | Basado en CV Master + oferta real |
| Útil para enviar | ❌ No | ✅ Sí |
| Coste LLM | ~$0/mes | ~$0/mes (mismo) |
| Esfuerzo dev | 0h (ya hecho) | 8-12h |

---

## 🏗️ Arquitectura propuesta v3.0

```
┌──────────────────────────────────────────────────────────────┐
│ FLASK CV SERVER v3.0                                         │
│                                                              │
│ NUEVO endpoint:                                              │
│  POST /buscar-ofertas-reales                                 │
│   ├→ Llama a APIs/scrapers en paralelo                       │
│   ├→ Filtra por preferencias del usuario                     │
│   ├→ Pide a Groq que rankee top 5                            │
│   └→ Devuelve ofertas con score                              │
│                                                              │
│ MEJORADO:                                                    │
│  POST /generar-cv                                            │
│   ├→ Lee CV Master del usuario (Drive)                       │
│   ├→ Pasa a Groq: CV Master + oferta REAL                    │
│   ├→ Groq REORDENA y ENFATIZA (no inventa)                   │
│   └→ Genera DOCX preservando experiencia real                │
└──────────────────────────────────────────────────────────────┘
                  ↑
                  │ POST /buscar-ofertas-reales
                  │
┌──────────────────────────────────────────────────────────────┐
│ N8N WORKFLOW v3                                              │
│                                                              │
│ Cambia el nodo "Groq - Generar Ofertas" por:                 │
│  → HTTP POST a /buscar-ofertas-reales                        │
│  (todo lo demás del flujo se mantiene igual)                 │
└──────────────────────────────────────────────────────────────┘
```

**Cambio mínimo en n8n**, mayor cambio en Flask.

---

## 🔍 Fuentes de ofertas REALES

### Opción A: APIs gratuitas oficiales

| Fuente | Tipo | Pros | Contras |
|--------|------|------|---------|
| **Remotive** | API REST gratis | 100% legal, JSON limpio, remoto | Solo ofertas remotas |
| **Getonboard** | API REST gratis | Ofertas LATAM/España IT, gratis | Catálogo limitado |
| **The Muse** | API REST gratis | Internacional, buena info | Mucha oferta US |
| **Jooble** | API key gratis | Agregador | Requiere registro |
| **Adzuna** | API REST con key | España + UK + 16 países | Plan gratis = 1k req/mes |

**Recomendación inicial:** **Remotive + Getonboard + Adzuna** = 3 fuentes complementarias.

### Opción B: Scraping (más complejo)

| Fuente | Tipo |
|--------|------|
| LinkedIn Jobs | Scraping (riesgo de bloqueo) |
| InfoJobs | Scraping HTML |
| Tecnoempleo | RSS feed disponible |

⚠️ **NO recomendado de inicio.** Riesgo legal + bloqueos + frágil. Mejor empezar con APIs.

### Opción C: Webhooks RSS

Muchos portales de empleo ofrecen RSS feeds. Se pueden parsear desde Flask.

---

## 🔧 Implementación Flask — endpoint `/buscar-ofertas-reales`

### Pseudocódigo

```python
@app.route("/buscar-ofertas-reales", methods=["POST"])
def buscar_ofertas_reales():
    datos = request.get_json()
    perfil = datos["perfil"]      # Tech Lead Frontend...
    rol = datos["rol"]            # Senior Frontend Developer
    stack = datos["stack"]        # ["React", "TypeScript"]
    salario_min = datos["salario"]
    modalidad = datos["modalidad"]
    ciudad = datos["ciudad"]
    
    # 1. Llamar a 3 APIs en paralelo
    ofertas_raw = []
    ofertas_raw += buscar_remotive(rol, stack)
    ofertas_raw += buscar_getonboard(rol, stack)
    ofertas_raw += buscar_adzuna(rol, ciudad)
    
    # 2. Filtrar duplicados (por URL o hash empresa+puesto)
    ofertas_unicas = deduplicar(ofertas_raw)
    
    # 3. Filtrar por modalidad y salario
    ofertas_filtradas = filtrar_preferencias(
        ofertas_unicas, modalidad, salario_min
    )
    
    # 4. LLM rankea top N
    if len(ofertas_filtradas) > 5:
        ofertas_top = rankear_con_groq(
            ofertas_filtradas, perfil, rol, stack
        )
    else:
        ofertas_top = ofertas_filtradas
    
    # 5. Devolver con score y motivo
    return jsonify({
        "ok": True,
        "ofertas": ofertas_top,
        "total_encontradas": len(ofertas_raw),
        "total_filtradas": len(ofertas_filtradas)
    })
```

### Helpers principales

```python
def buscar_remotive(rol, stack):
    """https://remotive.com/api/remote-jobs"""
    r = requests.get(
        "https://remotive.com/api/remote-jobs",
        params={"category": "software-dev", "search": rol},
        timeout=15
    )
    return [normalizar(j, source="remotive") for j in r.json()["jobs"][:20]]

def buscar_getonboard(rol, stack):
    """https://www.getonbrd.com/api/v0/categories/programming/jobs"""
    r = requests.get(
        "https://www.getonbrd.com/api/v0/search/jobs",
        params={"query": rol, "per_page": 20},
        timeout=15
    )
    return [normalizar(j, source="getonboard") for j in r.json()["data"]]

def buscar_adzuna(rol, ciudad):
    """https://developer.adzuna.com/"""
    r = requests.get(
        f"https://api.adzuna.com/v1/api/jobs/es/search/1",
        params={
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_API_KEY,
            "what": rol,
            "where": ciudad,
            "results_per_page": 20
        },
        timeout=15
    )
    return [normalizar(j, source="adzuna") for j in r.json()["results"]]

def normalizar(oferta_raw, source):
    """Convierte cada formato a un schema único."""
    return {
        "empresa": ...,
        "puesto": ...,
        "salario": ...,
        "modalidad": ...,
        "link": ...,
        "descripcion": ...,
        "fecha_publicacion": ...,
        "source": source
    }

def rankear_con_groq(ofertas, perfil, rol, stack):
    """Pide al LLM que devuelva las top 5 con score y motivo."""
    prompt = f"""Eres un recruiter senior. Tienes este candidato:
    
    Perfil: {perfil}
    Rol objetivo: {rol}
    Stack: {', '.join(stack)}
    
    Estas son {len(ofertas)} ofertas reales:
    {json.dumps([{
        "id": i,
        "empresa": o["empresa"],
        "puesto": o["puesto"],
        "descripcion": o["descripcion"][:300]
    } for i, o in enumerate(ofertas)], indent=2)}
    
    Devuelve SOLO un JSON array con las 5 mejores en orden de encaje:
    [
      {{"id": 3, "score": 92, "motivo": "Encaja por React + TypeScript + remoto"}},
      ...
    ]
    """
    raw = call_llm(prompt)
    rankings = parsear_json(raw)
    
    # Mezclar rankings con ofertas originales
    return [
        {**ofertas[r["id"]], "score": r["score"], "motivo": r["motivo"]}
        for r in rankings[:5]
    ]
```

---

## 📄 CV adaptado REAL — mejora a `/generar-cv`

### Concepto

El CV actual es **inventado** porque el prompt no usa el CV Master del usuario. Solo dice "genera un CV para este puesto".

El CV adaptado real:
1. **Lee CV Master** del usuario desde Drive (ya lo hacemos parcialmente)
2. **Pasa CV Master + oferta** al LLM
3. LLM **reordena, enfatiza y traduce keywords** (no inventa)
4. **DOCX final preserva** experiencia real

### Prompt mejorado

```
Eres un recruiter senior con 20 años de experiencia. Recibes:

CV MASTER del candidato (verdad):
---
{cv_master_texto}
---

OFERTA REAL:
- Empresa: {empresa}
- Puesto: {puesto}
- Descripción: {descripcion}
- Stack requerido: {stack_requerido}

TU TAREA — adaptar el CV (NO inventar):

1. PRESERVA todos los datos personales tal cual
2. PRESERVA toda la experiencia laboral REAL del CV Master
3. REORDENA bullets para destacar lo más relevante a esta oferta
4. RECONFIGURA el "Profile/Summary" para alinearlo con el puesto
5. ENFATIZA habilidades del CV Master que coincidan con la oferta
6. TRADUCE keywords (si CV dice "Vue.js" y oferta pide "frameworks JS",
   menciona ambos)
7. ❌ NO inventes empresas, fechas, certificaciones, idiomas
8. ❌ NO añadas experiencia que no esté en el CV Master
9. ✅ SÍ reformula bullets para usar palabras de la oferta
10. ✅ SÍ ajusta el orden de las skills

Devuelve solo el CV adaptado en formato:
## Profile
...
## Experience
...
## Skills
...
## Education
...
```

### Flujo completo

```python
@app.route("/generar-cv", methods=["POST"])
def generar_cv():
    datos = request.get_json()
    email = datos["email"]
    empresa = datos["empresa"]
    puesto = datos["puesto"]
    descripcion = datos["descripcion"]
    
    # 1. Leer CV Master del user
    usuario = buscar_usuario_por_email(email)
    cv_master_url = usuario["cv_master_url"]
    cv_master_texto = leer_cv_master_de_drive(cv_master_url)
    
    # 2. Pasar todo al LLM con prompt anti-invención
    prompt = construir_prompt_adaptacion(
        cv_master_texto, empresa, puesto, descripcion
    )
    cv_adaptado = call_llm(prompt)
    
    # 3. Generar DOCX
    docx_bytes = generar_docx(cv_adaptado, usuario["nombre"])
    
    # 4. Subir a Drive con nombre estructurado
    nombre = f"CV_{usuario['nombre']}_{empresa}_{datetime.now():%Y-%m-%d}.docx"
    link = subir_cv_a_drive(docx_bytes, nombre)
    
    return jsonify({"ok": True, "link": link, "archivo": nombre})
```

---

## 🗓️ Plan de implementación (8-12h dev)

### Fase 1 — APIs gratis (3-4h)
- [ ] Crear cuenta Adzuna y obtener `app_id` + `app_key` (10 min)
- [ ] Implementar `buscar_remotive()` (30 min)
- [ ] Implementar `buscar_getonboard()` (30 min)
- [ ] Implementar `buscar_adzuna()` (45 min)
- [ ] Función `normalizar()` y `deduplicar()` (45 min)
- [ ] Tests unitarios básicos (30 min)

### Fase 2 — Endpoint Flask (2h)
- [ ] Crear `/buscar-ofertas-reales` que orqueste todo (1h)
- [ ] Función `rankear_con_groq()` (45 min)
- [ ] Probar con curl (15 min)

### Fase 3 — Adaptación CV real (2h)
- [ ] Mejorar prompt en `generar_cv_adaptado()` (45 min)
- [ ] Asegurar lectura CV Master desde Drive (30 min)
- [ ] Testear con CV real de Verónica (45 min)

### Fase 4 — Cambios en n8n (1h)
- [ ] Reemplazar nodo `Groq - Generar Ofertas` por `HTTP - Flask /buscar-ofertas-reales` (30 min)
- [ ] Adaptar el `Code - Normalizar Modalidad` al nuevo schema (15 min)
- [ ] Test end-to-end (15 min)

### Fase 5 — Tests con beta users (1-2h)
- [ ] Test con 1 oferta real → email → aprobar → CV+carta
- [ ] Test con 5 ofertas → ver ranking
- [ ] Validar que el CV preserva la experiencia real

---

## 💡 Otros aspectos a considerar

### 1. Filtrado por seniority

Los APIs no siempre devuelven seniority. Hay que detectarlo:

```python
def detectar_seniority(puesto, descripcion):
    texto = (puesto + " " + descripcion).lower()
    if any(k in texto for k in ["senior", "lead", "principal", "staff"]):
        return "senior"
    if any(k in texto for k in ["junior", "entry", "graduate"]):
        return "junior"
    return "mid"
```

### 2. Anti-spam (mismas ofertas cada día)

Si lanzamos cada mañana, hay que evitar mostrar las mismas:

```python
# En Notion, antes de crear nueva oferta:
def ya_enviada_a_user(email, link_oferta):
    # Query: ¿existe oferta con este link Y este email_usuario?
    return notion_query(
        db_ofertas,
        filter={
            "and": [
                {"property": "Link oferta", "url": {"equals": link_oferta}},
                {"property": "Email usuario", "email": {"equals": email}}
            ]
        }
    ).get("results", [])
```

### 3. Manejo de fallos por API caída

```python
def buscar_con_fallback(perfil, rol, stack, ciudad):
    ofertas = []
    for fuente in [buscar_remotive, buscar_getonboard, buscar_adzuna]:
        try:
            ofertas += fuente(rol, stack, ciudad)
        except Exception as e:
            logger.warning(f"{fuente.__name__} falló: {e}")
    return ofertas  # devuelve lo que tenga, aunque algunas fallen
```

### 4. CV Master debe ser texto plano

Para que LLM lo entienda bien, mejor que el CV Master en Drive sea:
- ✅ Doc Google Drive convertible a texto
- ✅ PDF con texto seleccionable (no escaneado)
- ❌ NO PDF imagen (OCR sería otro paso)

Idealmente: pedir al usuario que pegue su CV en plano cuando se registra.

---

## 🎯 Decisiones a tomar antes de empezar

1. **¿Qué fuentes de ofertas?** (Remotive + Getonboard + Adzuna recomendado)
2. **¿Cuántas ofertas/usuario/día?** (1 para validar, luego 3-5)
3. **¿CV Master cómo se guarda?** (Drive como ahora, o subida directa al registro?)
4. **¿Adzuna API key gratis o pagar?** (gratis = 1k req/mes, suficiente al principio)
5. **¿Implementamos hoy mismo o mañana?**

---

## 🚀 Primer paso recomendado

Empezar HOY con **Remotive** (la API más fácil, sin key, JSON limpio).

```bash
# Test rápido — sin código, ver qué devuelve Remotive
curl "https://remotive.com/api/remote-jobs?category=software-dev&search=frontend" | python3 -m json.tool | head -50
```

Si la respuesta es buena → implementar el endpoint en Flask en 1 hora.
Si no → probar otras fuentes.
