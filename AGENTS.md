# Manual de Agentes – Mantenimiento Predictivo Explicable (Metal Tech)

> Proyecto 3 – Ingeniería del Conocimiento 2026-2 (Universidad de Caldas, Facultad de IA e Ingenierías).
> Docente: Ing. Wilson Fernando López Cardona.
> Enunciado: [PROYECTOS FINALES INGENIERIA DEL CONOCIMIENTO.pdf](PROYECTOS%20FINALES%20INGENIERIA%20DEL%20CONOCIMIENTO.pdf)
> Plan maestro: [docs/PLAN.md](docs/PLAN.md)

Este manual es obligatorio para **todo agente**, sea humano o IA, que trabaje en el repositorio. Define el propósito, los roles, el protocolo de trabajo y dónde se registra la memoria del proyecto.

---

## 1. Archivos de memoria (leer SIEMPRE antes de empezar)

| Archivo | Para qué sirve | Cuándo se actualiza |
|---|---|---|
| [docs/agentes/MEMORIA.md](docs/agentes/MEMORIA.md) | Bitácora paso a paso: qué se hizo, qué queda pendiente, qué errores hubo y qué se decidió. Incluye el bloque **Estado actual**. | Al terminar **cada** tarea |
| [docs/agentes/ERRORES.md](docs/agentes/ERRORES.md) | Base de conocimiento de errores (`ERR-NNN`): síntoma, causa raíz, solución y prevención. | Cada vez que aparece un error, sea propio o del entorno |
| [docs/PLAN.md](docs/PLAN.md) | Plan maestro por fases. | Solo si cambia el alcance, y se registra en MEMORIA |

---

## 2. Propósito del proyecto

Integrar un **modelo de Deep Learning** con una **base de conocimiento experto** (ontología OWL + reglas con factores de certeza) para **predecir fallas** y generar **diagnósticos explicables** en la planta ficticia Metal Tech. El sistema muestra qué variables y qué reglas sustentan cada alerta.

Pregunta guía: *¿Cómo integrar un modelo de Deep Learning con una base de conocimiento experto para predecir fallas y generar diagnósticos explicables en una planta manufacturera?*

Comparación obligatoria: **M0 solo reglas · M1 solo DL · M2 conocimiento como features · M3 fusión DL + reglas**.

Métricas: F1, precisión, recall, latencia, explicabilidad, reducción de falsas alarmas, equidad e impacto.

## 3. Arquitectura resumida

```
Generador sintético ──► features / ventanas ──► MLP · CNN1D · LSTM ──► probabilidades + XAI (SHAP/IG)
                                                                         │
Agente investigador ──► decisiones.md ──► FMEA · léxico · reglas.yaml ──► motor de reglas (FC + traza)
                                          └─► ontología OWL ─────────────┤
                                                                         ▼
                                                     Fusión (M0–M3) ──► diagnóstico explicable
                                                                         │
                                         FastAPI ──► Web demostrativa (Streamlit) · Landing (estática)
```

## 4. Mapa del repositorio

```
AGENTS.md / CLAUDE.md / README.md
configs/            assets.yaml, failure_modes.yaml, train.yaml
knowledge/          ontology/, rules/, lexicon/, acquisition/ (decisiones.md, FMEA, matriz)
data/synthetic/     dataset generado (no versionar archivos grandes)
src/metaltech/      data/, kb/ (base, lexicon, rules_engine, ontology), models/, hybrid/, xai/, metrics/, api/, dashboard/
tests/              pytest
reports/            figures/, tables/, sesgos_limitaciones.md
landing/            landing page estática (GitHub Pages)
docs/               PLAN.md, agentes/ (MEMORIA, ERRORES), documento_APA/, poster/, demo_guion.md
```

## 5. Roles de agentes

| Rol | Responsabilidad | Salidas principales |
|---|---|---|
| **Investigador** | Fase 1: consulta normas, literatura y datasets; **toma las decisiones** de la base de conocimiento, sin entrevistas | `knowledge/acquisition/decisiones.md`, FMEA, léxico, borrador de reglas |
| **Revisor de conocimiento** | Revisa que cada regla tenga respaldo (≥2 fuentes o 1 norma), detecta contradicciones y huecos | Observaciones en MEMORIA y correcciones en reglas |
| **Datos/ML** | Generador sintético, features, modelos, fusión, XAI y métricas | `src/metaltech/{data,models,hybrid,xai,metrics}` |
| **Backend** | FastAPI, esquemas Pydantic, endpoints de KB y simulación | `src/metaltech/api/` |
| **Frontend** | Web demostrativa (8 páginas) y landing page | `src/metaltech/dashboard/`, `landing/` |
| **Documentación** | Documento APA 7, anexos, póster, guion de demo | `docs/` |
| **QA** | Tests, verificación de trazabilidad y de enlaces de MEMORIA y ERRORES | `tests/`, scripts de verificación |

## 6. Protocolo obligatorio de trabajo

1. **Leer** este archivo, el bloque *Estado actual* de `MEMORIA.md` y el índice de `ERRORES.md`.
2. **Buscar** en `ERRORES.md` si el problema o la tarea ya tiene errores conocidos y aplicar su prevención.
3. **Ejecutar** la tarea dentro del alcance de su rol y de la fase del plan.
4. **Verificar** con los tests de la fase (`pytest`) o con la verificación indicada en el plan.
5. **Registrar** una entrada en `MEMORIA.md` (formato de la sección 8) y **reescribir** el bloque *Estado actual*.
6. **Si hubo error**, propio o del entorno, crear `ERR-NNN` en `ERRORES.md` y enlazarlo desde la entrada de MEMORIA.
7. Las decisiones de conocimiento van en `knowledge/acquisition/decisiones.md`; en MEMORIA solo se resumen.

Nunca dar por terminada una tarea sin el registro en MEMORIA. Nunca ocultar un error: también se documentan los errores del agente (supuestos falsos, código roto, fuentes mal citadas).

## 7. Convenciones

- **Lenguaje:** Python ≥ 3.11 (el entorno del equipo usa 3.14; ver ERR-007). El código usa nombres del dominio en español (`modo_falla`, `sintoma`, `regla`) y nombres técnicos en inglés cuando son estándar (`train`, `forward`).
- **Estilo:** ruff y type hints en funciones públicas. Docstrings breves.
- **Fuente única de verdad del conocimiento:** los YAML de `knowledge/` y `configs/`. La ontología `.owl` se **genera** desde ellos y no se edita a mano sin reflejar el cambio en los YAML.
- **Reproducibilidad:** semillas fijas en `configs/train.yaml`. Todo experimento debe poder regenerarse por comando.
- **Datos:** solo sintéticos o anonimizados. Ningún dato personal real.
- **Citas:** APA 7 en `decisiones.md` y en el documento.
- **Fechas** en MEMORIA y ERRORES: formato `AAAA-MM-DD`.

### Comandos (se completan a medida que existan)

```bash
python -m venv .venv && source .venv/Scripts/activate   # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install -e . --no-deps
pytest
ruff check .
python -m metaltech.proceso          # verifica enlaces MEMORIA <-> ERRORES
python -m metaltech.kb.ontology      # regenera knowledge/ontology/metaltech.owl (obligatorio si cambia un YAML)
python scripts/instalar_jdk.py       # JDK portable para HermiT (una vez, Windows x64)
python -m metaltech.kb.rules_engine --activo bomba_centrifuga --valores '{...}' --texto "..."
# --- se habilitan en fases posteriores ---
python -m metaltech.data.generator --config configs/assets.yaml
python -m metaltech.models.train --config configs/train.yaml
uvicorn metaltech.api.main:app --reload
streamlit run src/metaltech/dashboard/app.py
```

### Definición de "terminado"

- Código con tests pasando.
- Trazabilidad: regla → fuente, y alerta → reglas y variables.
- Entrada en MEMORIA y *Estado actual* actualizado.
- Errores documentados en ERRORES.
- Si afecta al usuario final, visible en la web demostrativa.

## 8. Formatos de registro

**Entrada de MEMORIA** (las más recientes arriba):

```markdown
## [AAAA-MM-DD] Fase N – Título de la tarea (agente: Rol)
- Hecho: ...
- Pendiente: ...
- Errores: ERR-NNN, ... | ninguno
- Decisiones: ...
```

**Entrada de ERRORES:**

```markdown
### ERR-NNN – Título corto
- Fecha: AAAA-MM-DD
- Fase/archivo: ...
- Origen: entorno | código | datos | conocimiento | agente
- Síntoma: ...
- Causa raíz: ...
- Solución: ...
- Prevención: ...
- Estado: resuelto | abierto
```
