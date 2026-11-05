# Mantenimiento predictivo explicable – Metal Tech

Proyecto 3 de Ingeniería del Conocimiento 2026-2 (Universidad de Caldas, Facultad de IA e Ingenierías).
Integra un modelo de **Deep Learning** con una **base de conocimiento experto** (ontología OWL + reglas con factores de certeza) para predecir fallas y generar **diagnósticos explicables** en la planta ficticia Metal Tech.

> Todos los datos son **sintéticos**. No se usa ningún dato personal real.

Documentación del proceso: [AGENTS.md](AGENTS.md) (manual de agentes) · [docs/PLAN.md](docs/PLAN.md) (plan maestro) · [docs/agentes/MEMORIA.md](docs/agentes/MEMORIA.md) (bitácora) · [docs/agentes/ERRORES.md](docs/agentes/ERRORES.md) (errores conocidos).

## Comparación central

| Modelo | Descripción |
|---|---|
| M0 | Solo reglas (sistema experto) |
| M1 | Solo Deep Learning (MLP / CNN1D / LSTM) |
| M2 | Conocimiento como features del DL |
| M3 | Fusión DL + reglas (validación experta) |

Métricas: F1, precisión, recall, latencia, explicabilidad, reducción de falsas alarmas, equidad e impacto.

## Requisitos

- Python 3.11 o superior (probado con 3.14).
- Git.
- **Opcional:** JDK 17 para validar la ontología con el razonador HermiT. En Windows x64 basta `python scripts/instalar_jdk.py`, que lo deja en `.tools/` sin tocar el sistema; en otro SO, ponga un JDK 17 en el `PATH`. Sin Java las pruebas marcadas `java` se omiten (ver ERR-008).

## Instalación

```bash
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Windows (Git Bash):    source .venv/Scripts/activate
# Linux / macOS:         source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
```

## Comandos

```bash
pytest                                              # pruebas
ruff check .                                        # linter
python -m metaltech.proceso                         # verifica MEMORIA <-> ERRORES

# Base de conocimiento (Fase 2)
python -m metaltech.kb.ontology                     # genera knowledge/ontology/metaltech.owl y valida
python -m metaltech.kb.ontology --hermit            # + consistencia lógica con HermiT (Java)
# diagnóstico por reglas con traza (síntomas, reglas disparadas, FC y valores reales)
python -m metaltech.kb.rules_engine --activo bomba_centrifuga \
  --valores '{"npsh_margen_ratio": 1.0, "vib_hf_rel": 4.2, "caudal_cv_pct": 8, "presion_descarga_pct": 88}' \
  --texto "la bomba está golpeando"

# Se habilitan en fases posteriores
python -m metaltech.data.generator --config configs/assets.yaml
python -m metaltech.models.train --config configs/train.yaml
uvicorn metaltech.api.main:app --reload
streamlit run src/metaltech/dashboard/app.py
```

## Estructura

```
configs/      assets.yaml, failure_modes.yaml, train.yaml
knowledge/    ontology/ (metaltech.owl generado), rules/, lexicon/, acquisition/ (decisiones, FMEA, matriz)
data/         synthetic/ (generado, no se versiona) y ficha de datos
src/metaltech/  data, kb (base, lexicon, rules_engine, ontology), models, hybrid, xai, metrics, api, dashboard
tests/        pytest
reports/      figures/, tables/, informes
landing/      landing page estática
docs/         PLAN.md, agentes/, documento_APA/, poster/
```

## Arquitectura

```
Generador sintético -> features/ventanas -> MLP · CNN1D · LSTM -> probabilidades + XAI
Investigador -> decisiones.md -> FMEA · léxico · reglas.yaml -> motor de reglas (FC + traza)
                                 └-> ontología OWL ------------┤
                                                               v
                                       Fusión (M0–M3) -> diagnóstico explicable
                                                               v
                                 FastAPI -> Web demostrativa (Streamlit) · Landing
```

## Estado

Ver el bloque *Estado actual* de [MEMORIA.md](docs/agentes/MEMORIA.md).
