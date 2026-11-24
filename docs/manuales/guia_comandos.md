# Guía de comandos

Todos los comandos se ejecutan desde la raíz del repositorio con el entorno activado. Las rutas por defecto ya apuntan a `configs/`, `data/synthetic/` y `reports/tables/`, así que normalmente no hace falta ninguna opción. El orden para regenerar todo está en la [puesta en marcha](puesta_en_marcha.md#4-regenerar-datos-modelos-y-reportes).

## Calidad y proceso

| Comando | Qué hace |
|---|---|
| `pytest` | Corre todas las pruebas. Las que necesitan datos, modelos o Java se omiten si faltan |
| `pytest tests/test_rules_engine.py` | Corre solo un archivo de pruebas |
| `ruff check .` | Revisa el estilo del código |
| `python -m metaltech.proceso` | Comprueba que todo `ERR-NNN` citado en MEMORIA exista en ERRORES y al revés |

## Base de conocimiento (Fases 1 y 2)

| Comando | Qué hace | Produce |
|---|---|---|
| `python -m metaltech.kb.ontology` | Genera la ontología desde los YAML y la valida. **Obligatorio tras cambiar un YAML** | `knowledge/ontology/metaltech.owl` |
| `python -m metaltech.kb.ontology --hermit` | Además comprueba la consistencia lógica con HermiT (requiere Java) | — |
| `python -m metaltech.kb.ontology --modo cavitacion --activo bomba_centrifuga` | Muestra la ficha de un modo de falla: síntomas, causas, acciones, reglas y FMEA | Texto en pantalla |
| `python -m metaltech.kb.rules_engine --activo A --valores '{...}' --texto "..."` | Diagnóstico solo con reglas, con la traza de reglas disparadas, valores y FC | Texto en pantalla |
| `python scripts/instalar_jdk.py` | Descarga un JDK 17 portable (Windows x64) y verifica su SHA-256 | `.tools/jdk17` |

Opciones de `metaltech.kb.rules_engine`:
- `--activo` (obligatoria): tipo de activo, por ejemplo `bomba_centrifuga`.
- `--valores`: JSON con variable → valor, por ejemplo `'{"npsh_margen_ratio": 1.0, "vib_hf_rel": 4.2, "caudal_cv_pct": 8}'`.
- `--linea-base`: JSON con la línea base de las variables relativas.
- `--texto`: observación del técnico, por ejemplo `"la bomba está golpeando"`.
- `--json`: imprime el resultado como JSON.

## Datos sintéticos (Fase 3)

| Comando | Qué hace | Produce |
|---|---|---|
| `python -m metaltech.data.generator` | Simula 36 meses de sensores para las 32 unidades, con fallas, confusores y observaciones de técnicos | `data/synthetic/*.parquet`, `manifest.json` |
| `python -m metaltech.data.calibracion` | Mide la dificultad del simulador: detección de M0 por modo, falsas alarmas, acierto de los técnicos | `reports/tables/calibracion_*` |
| `python scripts/contrastar_datasets.py` | Compara el simulador con AI4I 2020 y SKAB (descarga los CSV públicos a `data/external/`) | `reports/tables/contraste_datasets.csv` |

Opciones de `metaltech.data.generator`: `--config` (por defecto `configs/train.yaml`), `--salida`, `--semilla` (42) y `--meses`, que reemplaza el valor del YAML (útil para pruebas rápidas, por ejemplo `--meses 3`).

## Modelos e integración (Fases 4 y 5)

| Comando | Qué hace | Produce |
|---|---|---|
| `python -m metaltech.models.train` | Entrena MLP, CNN1D y LSTM por activo y elige la mejor por F1 de validación (M1) | `checkpoints/`, `reports/tables/modelos_*` |
| `python -m metaltech.hybrid.comparar` | Compara M0, M1, M2 y M3 con una semilla; elige α y veto en validación | `reports/tables/comparacion_*`, `fusion_parametros.json` |
| `python -m metaltech.hybrid.comparar --todas` | Lo mismo con las 5 semillas de `configs/train.yaml` (Fase 7) | `comparacion_semillas.csv`, `fusion_parametros_semillas.json` |

Opciones comunes: `--config`, `--datos` y `--activos motor_electrico bomba_centrifuga` para limitar los activos. `models.train` acepta además `--arquitecturas mlp cnn1d lstm`, `--semilla` y `--epocas`; `hybrid.comparar` acepta `--semillas 42 43`.

## Explicabilidad (Fase 6)

| Comando | Qué hace | Produce |
|---|---|---|
| `python -m metaltech.xai.explain` | Gradientes integrados y métricas de fidelidad, concordancia y estabilidad sobre alertas de prueba | `reports/tables/xai_metricas.csv`, `xai_ejemplos.json` |
| `python -m metaltech.xai.evaluacion_humana preparar` | Prepara el formulario de evaluación de explicaciones para personas | `docs/evaluacion_humana/formulario.md`, `clave.csv` |
| `python -m metaltech.xai.evaluacion_humana analizar` | Analiza las respuestas transcritas en `respuestas.csv` | `reports/tables/evaluacion_humana*` |
| `python -m metaltech.xai.evaluacion_humana preparar --agentes` / `analizar --agentes` | Versión para el panel de agentes, con controles de longitud | `reports/tables/evaluacion_agentes*` |

`xai.explain` acepta `--muestras` (300 alertas por activo por defecto) y `--activos`.

## Evaluación final (Fase 7)

| Comando | Qué hace | Produce |
|---|---|---|
| `python -m metaltech.metrics.intervalos` | Intervalos t del 95 % entre semillas y diferencias pareadas (Wilcoxon) | `intervalos_*` |
| `python -m metaltech.metrics.equidad` | Acierto y falsa alarma por turno, observación, activo y máquina | `equidad_*` |
| `python -m metaltech.metrics.impacto` | Fallas detectadas, eventos de falsa alarma y costo relativo (r = 3, 5, 9) | `impacto_*` |
| `python -m metaltech.metrics.latencia` | Latencia por diagnóstico dentro del proceso | `latencia.csv`, `latencia_resumen.json` |
| `python -m metaltech.metrics.latencia --api http://127.0.0.1:8000` | Latencia extremo a extremo contra la API levantada | `latencia_api*` |

`metrics.latencia` acepta `--solicitudes` para cambiar el número de llamadas.

## Prototipo (Fases 8 y 8b)

| Comando | Qué hace |
|---|---|
| `uvicorn metaltech.api.main:app` | Levanta la API en http://127.0.0.1:8000 (`--reload` para desarrollo; `--port` para otro puerto) |
| `streamlit run src/metaltech/dashboard/app.py` | Levanta la web demostrativa en http://localhost:8501 |
| `python scripts/revisar_web.py --salida revision_web` | Levanta API y web en puertos propios y recorre cada página con Playwright; deja capturas e `informe.json`. `--ver` muestra el navegador |
| `python scripts/generar_datos_landing.py` | Regenera `landing/data.js` con las cifras de `reports/` |

## Documentación (Fase 10)

| Comando | Qué hace |
|---|---|
| `python scripts/generar_documento.py` | Genera `docs/documento_APA/documento_apa.docx` desde `documento.md` y `referencias.md` |
| `python scripts/generar_documento.py --figuras` | Además regenera las figuras (matplotlib y diagrama de la landing) |
| `python scripts/generar_documento.py --capturas revision_web` | Actualiza la captura del simulador desde la revisión de la web |
| `python scripts/generar_documento.py --pdf` | Además actualiza el índice y exporta a PDF con Microsoft Word |
| `python scripts/generar_poster.py` | Genera `docs/poster/poster.html` y `poster.pdf` (A1) |
