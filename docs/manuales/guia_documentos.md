# Guía de documentos

Qué contiene cada documento y archivo importante, para quién es, quién lo mantiene, cuándo se actualiza y de qué depende. Responsables: Alejandro Pineda Gomez (conocimiento y QA), Luis David Rodríguez Arias (datos y modelos), Ivan Junior Echeverri Gomez (API y web) y David Ramirez Cruz (documento, póster y landing).

## Cadena de dependencias

Cambiar un archivo de la izquierda obliga a regenerar los de la derecha:

```text
configs/*.yaml + knowledge/**/*.yaml ──► metaltech.owl ──► API y web (base de conocimiento)
        │
        └──► data/synthetic/ ──► checkpoints/ ──► reports/tables/ ──► landing/data.js
                                                        │                documento APA y póster
                                                        └──► web (modelos, equidad, explicación)
```

El detalle de cada paso está en los [diagramas de flujo](diagramas_flujo.md#6-de-un-cambio-a-los-entregables).

## Entregables del curso

| Documento | Contenido | Para quién | Mantiene | Se regenera con |
|---|---|---|---|---|
| [documento_apa.pdf](../documento_APA/documento_apa.pdf) | Documento APA 7 con las 15 secciones del enunciado y anexos | Docente | David | `python scripts/generar_documento.py --pdf` |
| [documento.md](../documento_APA/documento.md), [referencias.md](../documento_APA/referencias.md) | Texto y referencias del documento (se edita aquí, no en el Word) | Equipo | David | — |
| [poster.pdf](../poster/poster.pdf) | Póster A1 | Docente y público | David | `python scripts/generar_poster.py` |
| [demo_guion.md](../demo_guion.md) | Guion de la demostración de 10 a 15 minutos | Equipo | Todos | A mano |
| Landing (`landing/`) | Página de presentación publicada en GitHub Pages | Público | David | `python scripts/generar_datos_landing.py` (cifras) |
| [README.md](../../README.md) | Presentación del repositorio, instalación y comandos | Cualquiera | Todos | A mano |

## Proceso y memoria del proyecto

| Documento | Contenido | Se actualiza |
|---|---|---|
| [AGENTS.md](../../AGENTS.md) | Manual de agentes: roles, protocolo, convenciones y comandos | Si cambia el protocolo |
| [PLAN.md](../PLAN.md) | Plan maestro por fases | Si cambia el alcance |
| [MEMORIA.md](../agentes/MEMORIA.md) | Bitácora: qué se hizo, qué falta, errores y decisiones; bloque *Estado actual* | Al terminar cada tarea |
| [ERRORES.md](../agentes/ERRORES.md) | Base de errores `ERR-NNN`: síntoma, causa, solución y prevención | Cada vez que aparece un error |
| [AVANCES_FASES_3_Y_4.md](../AVANCES_FASES_3_Y_4.md) | Explicación de archivos y avances de las Fases 3 y 4 | Histórico |

## Conocimiento (fuente única de verdad)

| Archivo | Contenido | Mantiene | Tras cambiarlo |
|---|---|---|---|
| [configs/assets.yaml](../../configs/assets.yaml) | Activos, unidades, variables, umbrales y catálogo de síntomas | Alejandro | Regenerar ontología; si cambian umbrales, datos y modelos |
| [configs/failure_modes.yaml](../../configs/failure_modes.yaml) | Modos de falla, firmas de degradación y confusores | Alejandro / Luis David | Regenerar ontología, datos y modelos |
| [knowledge/rules/rules.yaml](../../knowledge/rules/rules.yaml) | Las reglas SI-ENTONCES con FC, acción y fuente | Alejandro | Regenerar ontología y comparación M0–M3 |
| [knowledge/lexicon/expresiones.yaml](../../knowledge/lexicon/expresiones.yaml) | Expresiones de técnicos → síntomas → modos candidatos | Alejandro | Regenerar ontología |
| [knowledge/acquisition/fmea.yaml](../../knowledge/acquisition/fmea.yaml) | FMEA: severidad, ocurrencia, detección y NPR | Alejandro | Regenerar ontología |
| [decisiones.md](../../knowledge/acquisition/decisiones.md) | Decisiones D-NNN con alternativas, fuentes APA y confianza | Investigador / Alejandro | — |
| [matriz_adquisicion.md](../../knowledge/acquisition/matriz_adquisicion.md) | Matriz de adquisición: fuente, técnica, conocimiento, tipo y validación | Alejandro | — |
| [normas_fuentes_externas.md](../../knowledge/acquisition/normas_fuentes_externas.md) | Cómo se consultaron las normas de pago por fuentes públicas | Alejandro | — |
| [datasets_referencia.md](../../knowledge/acquisition/datasets_referencia.md) | Datasets públicos consultados y qué se tomó de cada uno | Investigador | — |
| [revision.md](../../knowledge/acquisition/revision.md) | Revisión cruzada del agente revisor: reglas sin sustento, choques y huecos | Revisor | — |
| [knowledge/ontology/metaltech.owl](../../knowledge/ontology/metaltech.owl) | Ontología OWL **generada** (abrible en Protégé). No se edita a mano | — | `python -m metaltech.kb.ontology` |

## Datos, modelos y resultados

| Archivo o carpeta | Contenido | Versionado |
|---|---|---|
| [configs/train.yaml](../../configs/train.yaml) | Semillas, ventana, horizonte, entrenamiento, fusión, evaluación e impacto | Sí |
| `data/synthetic/` | Datos sintéticos (Parquet) y su manifiesto; ficha en [data/README.md](../../data/README.md) | No (se regenera) |
| `checkpoints/` | Modelos entrenados por activo | No (se regenera) |
| `reports/tables/` | Todas las tablas de resultados (CSV y JSON) que leen la web, la landing y el documento | Sí |
| [sesgos_limitaciones.md](../../reports/sesgos_limitaciones.md) | Informe de sesgos, riesgos RA/R1–R6, limitaciones y marco legal | Sí |

## Ética y evaluación

| Documento | Contenido |
|---|---|
| [acta_etica.md](../etica/acta_etica.md) | Declaración de datos, origen del conocimiento, uso de IA, compromisos y firmas |
| [evaluacion_humana/README.md](../evaluacion_humana/README.md) | Procedimiento y consentimiento informado de la evaluación de explicaciones; resultados del panel de agentes |

## Código

| Carpeta | Contenido | Mantiene |
|---|---|---|
| `src/metaltech/data/` | Simulador, calibración y ventanas | Luis David |
| `src/metaltech/kb/` | Carga de la base, léxico, motor de reglas y ontología | Alejandro |
| `src/metaltech/models/` | MLP, CNN1D, LSTM, rama de conocimiento, entrenamiento y evaluación | Luis David |
| `src/metaltech/hybrid/` | Conocimiento por ventana, fusión M3 y comparación M0–M3 | Luis David |
| `src/metaltech/xai/` | Gradientes integrados y evaluación de explicaciones | Luis David |
| `src/metaltech/metrics/` | Intervalos, equidad, impacto y latencia | Luis David / Alejandro |
| `src/metaltech/api/` | API FastAPI | Ivan Junior |
| `src/metaltech/dashboard/` | Web Streamlit (8 páginas) | Ivan Junior |
| `scripts/` | JDK, contraste con datasets, revisión de la web, landing, documento y póster | Todos |
| `tests/` | Pruebas pytest | Alejandro |

El [manual técnico](manual_tecnico.md) describe cada módulo.
