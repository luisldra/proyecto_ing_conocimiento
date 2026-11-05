# Plan: Mantenimiento predictivo explicable – Metal Tech (Proyecto 3, Ing. del Conocimiento 2026-2)

## Contexto
El enunciado ([PROYECTOS FINALES INGENIERIA DEL CONOCIMIENTO.pdf](PROYECTOS FINALES INGENIERIA DEL CONOCIMIENTO.pdf)) pide integrar un modelo de Deep Learning con una base de conocimiento experto para predecir fallas y generar diagnósticos explicables en la planta ficticia Metal Tech. Hoy los sensores (temperatura, vibración, corriente, presión, caudal) se consultan aislados y los técnicos diagnostican con heurísticas sensoriales ("el motor está cantando", "la bomba está golpeando") que dependen del turno/técnico → falsas alarmas, intervenciones tardías y cambios innecesarios de repuestos.

Resultado esperado: modelo DL entrenado con datos sintéticos, base de conocimiento (ontología + reglas), API + tablero, métricas (F1, precisión, recall, latencia, explicabilidad, reducción de falsas alarmas, equidad/impacto), informe de sesgos, **comparación modelo solo vs. modelo + conocimiento experto**, documento APA 7, anexos, póster y demo de 10–15 min.

La carpeta está vacía salvo el PDF; todo se construye desde cero.

## Decisiones tomadas
- **Stack:** Python 3.11, PyTorch, owlready2, SHAP/Captum, FastAPI, Streamlit, pytest.
- **Modelos:** MLP tabular (baseline) + 1D-CNN y LSTM sobre ventanas temporales.
- **Conocimiento:** ontología OWL (editable en Protégé) + motor de reglas propio en Python con factores de certeza y traza de reglas disparadas.
- **Prototipo:** FastAPI (predicción/diagnóstico) + Streamlit (tablero que consume la API).
- **Alcance:** parte técnica + documento APA + anexos + póster + guion de demo.
- **Manual de agentes** (`AGENTS.md`) con memoria paso a paso (`MEMORIA.md`) y base de conocimiento de errores (`ERRORES.md`).
- **Adquisición del conocimiento** a cargo de un agente investigador (revisión documental), sin entrevistas.
- **Web demostrativa** interactiva (Streamlit multipágina sobre la API) y **landing page** estática de presentación.
- **Orden de construcción al aprobar el plan:** (1) AGENTS.md, MEMORIA y ERRORES → (2) lanzar el agente investigador → (3) el resto de fases.

## Estructura del repositorio
```
Proyecto/
├── AGENTS.md                    # manual de agentes (protocolo, roles, convenciones)
├── CLAUDE.md                    # @AGENTS.md
├── README.md                    # instalación, ejecución, arquitectura
├── landing/                     # landing page estática (index.html, styles.css, app.js, data.json)
├── requirements.txt / pyproject.toml
├── configs/
│   ├── assets.yaml              # activos, sensores, rangos nominales, umbrales (ISO 20816 vibración)
│   ├── failure_modes.yaml       # modos de falla y firma en sensores (curvas de degradación)
│   └── train.yaml               # hiperparámetros, ventana, horizonte, semillas
├── knowledge/
│   ├── ontology/metaltech.owl   # ontología generada por script y editable en Protégé
│   ├── rules/rules.yaml         # ~30–40 reglas SI-ENTONCES con factor de certeza
│   ├── lexicon/expresiones.yaml # expresión coloquial → síntoma formal → variables
│   └── acquisition/             # matriz de adquisición, guiones de entrevista, actas (anexos)
├── data/
│   ├── synthetic/               # parquet generado (no versionar los grandes)
│   └── README.md                # ficha de datos (datasheet) y declaración de sintéticos
├── src/metaltech/
│   ├── data/generator.py        # simulador de sensores + inyección de fallas + observaciones técnicas
│   ├── data/features.py         # ventanas, features agregadas (RMS, curtosis, pendiente, etc.)
│   ├── kb/ontology.py           # construir/cargar ontología con owlready2, consultas
│   ├── kb/rules_engine.py       # encadenamiento hacia adelante, factores de certeza, traza
│   ├── kb/lexicon.py            # mapeo de expresiones de técnicos a síntomas
│   ├── models/mlp.py, cnn1d.py, lstm.py
│   ├── models/train.py, evaluate.py
│   ├── hybrid/fusion.py         # estrategias de integración modelo + conocimiento
│   ├── xai/explain.py           # SHAP / Integrated Gradients + explicación textual
│   ├── metrics/                 # clasificación, falsas alarmas, latencia, explicabilidad, equidad
│   ├── api/main.py              # FastAPI
│   └── dashboard/               # web demostrativa Streamlit (app.py + pages/01..08)
├── notebooks/                   # EDA, experimentos, figuras del documento
├── tests/                       # pytest: generador, reglas, ontología, API
├── reports/
│   ├── figures/, tables/        # salidas para el documento
│   ├── sesgos_limitaciones.md
│   └── resultados_comparacion.md
└── docs/
    ├── agentes/MEMORIA.md       # bitácora: hecho / pendiente / errores por tarea
    ├── agentes/ERRORES.md       # base de conocimiento de errores (ERR-NNN)
    ├── documento_APA/           # documento final (Word → PDF)
    ├── poster/
    └── demo_guion.md
```

## Manual de agentes y memoria del proyecto (se crea primero)
Tres archivos que todo agente (humano o IA) lee **antes** de trabajar y actualiza **después**:

1. **`AGENTS.md`** (raíz), el manual de agentes. `CLAUDE.md` solo contiene `@AGENTS.md` para que Claude Code lo cargue. Incluye:
   - Propósito del proyecto, arquitectura resumida y mapa del repositorio.
   - Roles de agentes:
     - **Investigador**: Fase 1, base de conocimiento.
     - **Revisor de conocimiento**: valida reglas y fuentes.
     - **Datos/ML**: generador, modelos, fusión, XAI.
     - **Backend**: FastAPI.
     - **Frontend**: web demostrativa y landing.
     - **Documentación**: APA, póster, demo.
     - **QA**: tests y métricas.
   - **Protocolo obligatorio:**
     1. Leer `AGENTS.md`, `docs/agentes/MEMORIA.md` y `docs/agentes/ERRORES.md`.
     2. Buscar en ERRORES si el problema ya ocurrió.
     3. Ejecutar la tarea.
     4. Correr los tests.
     5. Registrar la entrada en MEMORIA.
     6. Si hubo un error, registrarlo en ERRORES y enlazarlo desde MEMORIA.
   - Convenciones: código en Python con nombres en español para el dominio, rutas, comandos para ejecutar y probar, definición de "terminado".
   - Enlaces a MEMORIA y ERRORES.
2. **`docs/agentes/MEMORIA.md`**, la bitácora paso a paso. Una entrada por tarea:
   ```
   ## [2026-11-02] Fase 2 – Motor de reglas (agente: Datos/ML)
   - Hecho: rules_engine.py con FC MYCIN y traza; 34 reglas cargadas; tests OK.
   - Pendiente: reglas de CNC (R30–R34) sin segunda fuente.
   - Errores: ERR-004 (ver ERRORES.md).
   - Decisiones: umbral de vibración tomado de ISO 20816 zona C.
   ```
   Al inicio lleva un bloque **Estado actual** que se reescribe en cada tarea: fase en curso, siguiente tarea y bloqueos.
3. **`docs/agentes/ERRORES.md`**, la base de conocimiento de errores. Cada entrada es reutilizable:
   ```
   ### ERR-004 – owlready2 no encuentra Java para HermiT
   - Fase/archivo: Fase 2, src/metaltech/kb/ontology.py
   - Síntoma: OwlReadyJavaError al llamar sync_reasoner()
   - Causa raíz: JDK no instalado / JAVA_EXE no configurado en Windows
   - Solución: instalar JDK 17 y fijar owlready2.JAVA_EXE
   - Prevención: verificación en tests/conftest.py + nota en README
   - Origen: entorno | código | datos | conocimiento | agente
   ```
   Al inicio lleva un índice por categoría y una sección de **lecciones aprendidas**. Esta base alimenta "Análisis de errores" y "Limitaciones" del documento.

## Fase 0 – Preparación (semana 1)
- Crear `AGENTS.md`, `CLAUDE.md`, `docs/agentes/MEMORIA.md` y `docs/agentes/ERRORES.md`. La primera entrada de MEMORIA es la creación del repositorio.
- Crear repo GitHub, entorno virtual, `requirements.txt`, linters (ruff), pytest, `.gitignore`.
- Repartir roles: datos/modelo, conocimiento/ontología, prototipo, documento.
- Definir alcance de activos: **motor eléctrico, bomba centrífuga, compresor de tornillo, prensa hidráulica, banda transportadora, centro CNC** (6 tipos, varias unidades cada uno).

## Fase 1 – Adquisición del conocimiento por agente investigador (semanas 1–2)
**No hay entrevistas.** Se lanza un **agente investigador** (subagente con búsqueda web) que consulta las fuentes y **toma las decisiones** de la base de conocimiento, dejando cada una justificada y citada.
- **Encargo del agente:** para cada uno de los 6 activos, investigar modos de falla, síntomas medibles, umbrales, causas y acciones en:
  - Normas: ISO 17359, ISO 13374, ISO 20816/10816 (vibración), IEC 60034 y NEMA MG-1 (motores), API 610 / Hydraulic Institute (bombas, NPSH, cavitación).
  - Literatura de mantenimiento predictivo y XAI, empezando por Kusiak (2024).
  - Datasets públicos de referencia para calibrar las firmas del simulador: AI4I 2020 Predictive Maintenance (UCI), CWRU Bearing, NASA C-MAPSS/IMS Bearings, MIMII (bombas y válvulas), SKAB.
  - Manuales de fabricantes y guías técnicas de compresores de tornillo, prensas hidráulicas, bandas y CNC.
- **Reglas de decisión del agente:**
  - Cada regla y cada umbral debe estar respaldado por al menos 2 fuentes, o por 1 norma.
  - Si las fuentes se contradicen, se elige el valor más conservador y se registra el conflicto.
  - Cada expresión coloquial del enunciado se mapea a síntomas usando la física de la falla descrita en las fuentes.
- **Registro de decisiones:** `knowledge/acquisition/decisiones.md`, en formato tipo ADR (decisión, alternativas, fuentes APA, nivel de confianza).
- **Validación sin entrevistas:** triangulación de fuentes, coherencia FMEA ↔ reglas ↔ ontología (tests automáticos) y revisión cruzada por un segundo agente revisor que busca reglas sin sustento o contradictorias.
- **Productos:**
  - Matriz de adquisición: fuente, técnica (revisión documental asistida por agente), conocimiento obtenido, tipo (declarativo/procedimental/heurístico), validación.
  - Tabla FMEA: activo → componente → modo de falla → síntomas → causas → acciones → severidad.
  - Léxico de expresiones: p. ej.
    - "el motor está cantando" → ruido de alta frecuencia → vibración HF↑ → rodamiento / variador
    - "huele a quemado" → aislamiento degradado → temperatura devanado↑, corriente↑
    - "la bomba está golpeando" → cavitación → presión succión↓, vibración↑, caudal inestable
    - "el compresor está trabajando caliente" → temperatura de descarga↑, presión↓
    - "la prensa está dura" → presión hidráulica↑/fuga interna → presión, temperatura aceite
    - "la banda se está corriendo" → desalineación de banda → corriente asimétrica, vibración
    - "el variador está disparando por nada" → sobrecorriente intermitente / armónicos
  - Acta ética y declaración de que el conocimiento proviene de revisión documental y no de personas (en lugar de consentimientos).

## Fase 2 – Ontología y base de conocimiento (semanas 2–3)
- **Clases:** `Activo` (subclases por tipo), `Componente`, `Sensor`, `Variable`, `Sintoma` (`SintomaMedido`, `SintomaPercibido`), `ModoFalla`, `Causa`, `Accion`, `Regla`, `ExpresionColoquial`, `Tecnico`, `Turno`, `Alerta`.
- **Propiedades:** `tieneComponente`, `monitoreadoPor`, `mide`, `manifiesta(ModoFalla→Sintoma)`, `causadoPor`, `mitigadoPor`, `refiereA(ExpresionColoquial→Sintoma)`, `sustentadaPor(Alerta→Regla/Variable)`, `severidad`, `umbral`.
- `kb/ontology.py`: genera `metaltech.owl` desde los YAML (fuente única de verdad), con consultas como "síntomas de un modo de falla" y "acciones para una falla"; validación de consistencia con HermiT (incluido en owlready2).
- **Reglas (`rules.yaml`)**, formato:
  ```yaml
  - id: R07
    activo: bomba_centrifuga
    si: [presion_succion_baja, vibracion_alta, caudal_inestable]
    entonces: cavitacion
    fc: 0.85
    accion: revisar NPSH, válvula de succión, filtro
    fuente: entrevista_T2 + ISO 20816
  ```
- `kb/rules_engine.py`: fusificación simple de variables a síntomas (umbrales desde `assets.yaml`), encadenamiento hacia adelante, combinación de factores de certeza tipo MYCIN, **traza** de reglas disparadas con sus premisas y valores reales.
- Tests: cada regla dispara con su caso positivo y no dispara con el normal; la ontología es consistente.

## Fase 3 – Datos sintéticos (semanas 2–3, en paralelo)
- `data/generator.py`: simula, por unidad de activo, series cada 10 min durante N meses:
  - Señales base con ciclo de carga por turno, ruido y deriva estacional.
  - **Inyección de fallas** con curvas de degradación (exponencial/lineal) según `failure_modes.yaml`: la firma de cada falla afecta variables específicas (coherente con la FMEA).
  - Etiquetas: `modo_falla` (incluye `normal`) en un **horizonte H** (p. ej. falla en las próximas 24 h) y `RUL` opcional.
  - **Observaciones de técnicos** simuladas (expresiones del léxico) con probabilidad de acierto/ruido dependiente del técnico y del turno → base para analizar sesgo y equidad.
  - Ruido realista: sensores faltantes, picos espurios y eventos de producción que imitan fallas (para generar falsas alarmas).
- Semillas fijas, partición **temporal y por unidad** (sin fuga de información): train / val / test.
- Ficha de datos (`data/README.md`): declaración explícita de que son sintéticos, supuestos, limitaciones.

## Fase 4 – Modelos de Deep Learning (semanas 3–5)
- **Tarea:** clasificación multiclase (modo de falla en horizonte H o normal) por ventana de T pasos × V variables.
- `features.py`: ventanas deslizantes; features agregadas para el MLP (media, RMS, curtosis, pendiente, máx).
- Modelos: `MLP` (baseline), `CNN1D`, `LSTM`. Manejo de desbalance con pesos de clase o focal loss, early stopping, calibración (temperature scaling).
- `train.py` / `evaluate.py` reproducibles desde `configs/train.yaml`, con guardado de checkpoints y métricas en `reports/`.

## Fase 5 – Integración modelo + conocimiento (semanas 5–6)
`hybrid/fusion.py` implementa y compara:
- **M0 – Solo reglas** (sistema experto).
- **M1 – Solo DL** (el mejor entre CNN1D y LSTM).
- **M2 – Conocimiento como features:** activaciones de síntomas/reglas como entradas adicionales al DL.
- **M3 – Fusión posterior (validación experta):** score final = combinación ponderada de la probabilidad DL y el FC de las reglas; las reglas confirman o vetan alertas → objetivo: **reducir falsas alarmas**. Pesos ajustados en validación.
- La salida de diagnóstico es: modo de falla, probabilidad, causa probable, acción recomendada (desde la ontología), variables más influyentes, reglas disparadas y expresión coloquial asociada.

## Fase 6 – Explicabilidad (semana 6)
- `xai/explain.py`: SHAP (KernelExplainer/DeepExplainer para el MLP) e Integrated Gradients (Captum) para CNN/LSTM → importancia por variable y por instante.
- Explicación textual que combina el top de variables con la traza de reglas: *"Alerta de cavitación (0.87): presión de succión −22 % en 3 h, vibración 7.1 mm/s; reglas R07, R09; acción: revisar NPSH."*
- **Métricas de explicabilidad:**
  - Fidelidad: caída de probabilidad al enmascarar las top-k variables (deletion test).
  - Concordancia: solapamiento entre las variables top del XAI y las variables de las reglas disparadas.
  - Estabilidad: similitud de las explicaciones ante pequeñas perturbaciones.
  - Evaluación humana: encuesta Likert (comprensibilidad, utilidad, confianza) con 3–5 evaluadores.

## Fase 7 – Métricas y evaluación (semanas 6–7)
- **Clasificación:** F1 macro y por clase, precisión, recall, PR-AUC, matriz de confusión.
- **Falsas alarmas:** tasa por unidad y semana; % de reducción M3 vs. M1.
- **Latencia:** p50/p95 de `/predict` y `/diagnose` (con 1000 solicitudes vía script).
- **Equidad/impacto:** desempeño por turno, técnico (observaciones), tipo de activo y nivel de carga; brecha máxima entre grupos; impacto económico simulado (costo de paradas evitadas vs. intervenciones innecesarias).
- **Análisis de errores:** casos FP/FN con su explicación, fallas confundidas y por qué.
- Tabla comparativa M0–M3 con intervalos de confianza (bootstrap) y varias semillas.

## Fase 8 – Prototipo: API + web demostrativa (semanas 6–8)
La web demostrativa debe permitir **probar** el sistema y **ver todo** lo implementado: datos, ontología, reglas, modelos, explicaciones, métricas y errores.
- **FastAPI (`api/main.py`):**
  - `POST /predict` – ventana de sensores → probabilidades por modo de falla.
  - `POST /diagnose` – ventana + observación opcional del técnico → diagnóstico híbrido explicable.
  - `GET /assets`, `GET /kb/failure/{id}` – consultas a la ontología.
  - `GET /health`, `GET /metrics`.
  - Esquemas Pydantic, docs automáticas en `/docs`.
  - Endpoints extra para la web: `GET /kb/rules`, `GET /kb/ontology/graph` (nodos y aristas), `GET /kb/lexicon`, `POST /simulate` (inyectar una falla), `GET /reports/metrics`.
- **Web demostrativa en Streamlit multipágina (`dashboard/`):**
  1. **Planta:** estado por activo con semáforo y alertas activas.
  2. **Simulador en vivo:** elegir activo y modo de falla, ajustar severidad con sliders o escribir la expresión del técnico ("la bomba está golpeando"), y ver el diagnóstico híbrido paso a paso.
  3. **Explicación:** importancia de variables (SHAP/IG), mapa de calor temporal, **traza de reglas disparadas** con sus premisas, los valores reales y los FC combinados, la causa y la acción.
  4. **Base de conocimiento:** grafo interactivo de la ontología (pyvis), tabla de reglas filtrable con sus fuentes, léxico de expresiones y FMEA.
  5. **Modelos y comparación:** M0–M3 lado a lado (F1, precisión, recall, matriz de confusión, falsas alarmas, latencia).
  6. **Equidad e impacto:** brechas por turno, técnico y activo; costo simulado.
  7. **Datos:** explorador del dataset sintético y ficha de datos.
  8. **Bitácora y errores:** vista de MEMORIA.md y ERRORES.md para evidenciar el proceso.
- `docker-compose` para levantar API y web con un solo comando. Despliegue opcional en Streamlit Community Cloud o Render para la sustentación.

## Fase 8b – Landing page de presentación (semanas 8–9)
- Sitio estático `landing/` en HTML, CSS y JS sin framework, publicable en GitHub Pages.
- Secciones:
  1. Hero con el problema de Metal Tech.
  2. Reto y pregunta guía.
  3. Lo consultado: fuentes, normas y datasets del agente investigador, con contador de reglas y fuentes.
  4. Arquitectura en un diagrama SVG.
  5. Base de conocimiento: ontología y ejemplos de reglas y expresiones.
  6. Modelos y resultados: gráficos M1 vs. M3 y reducción de falsas alarmas.
  7. Ejemplo de explicación.
  8. Ética y limitaciones.
  9. Equipo.
  10. Enlaces a la web demostrativa, GitHub, documento PDF y póster.
- Los datos de la landing (métricas, conteos) se generan con un script desde `reports/` a `landing/data.json`, para que siempre coincidan con los resultados reales.
- Comparte identidad visual con el póster.

## Fase 9 – Ética, sesgos y marco legal (transversal, cierre en semana 8)
- `reports/sesgos_limitaciones.md`: sesgos de datos sintéticos (supuestos del simulador), sesgo de técnico/turno, sobreconfianza en la automatización, deriva de datos, límites de generalización a una planta real.
- Marco legal y normativo a revisar y citar: Ley 1581 de 2012 y Decreto 1377 de 2013 (datos personales de técnicos), CONPES 3975 (2019) y la política nacional de IA vigente en Colombia, Reglamento Europeo de IA (2024) como referencia, ISO/IEC 42001 e ISO/IEC 23894, normas de seguridad industrial y SST (Decreto 1072 de 2015): el sistema **recomienda**, el humano decide.
- Acta ética, consentimiento informado y declaración de uso de datos sintéticos/anonimizados.

## Fase 10 – Documento APA 7, póster y demo (semanas 7–9)
- Documento con las 15 secciones del enunciado. Mapeo de contenido:
  - Marco teórico: IA, representación del conocimiento, ontologías, sistemas expertos y factores de certeza, inferencia, DL (CNN/LSTM), XAI, mantenimiento predictivo, ética. Citar las 5 referencias base (Alimam et al., 2023; Ciriello et al., 2024; Ferrara, 2024; Friston et al., 2024; Kusiak, 2024) más unas 10–15 adicionales.
  - Metodología: ABP/ABPr + CommonKADS (modelos de organización, tarea, conocimiento) + CRISP-DM para la parte de ML.
  - Desarrollo: diagrama de arquitectura, ontología (figura de Protégé), reglas, modelos, prototipo.
  - Resultados: tablas M0–M3, métricas, validación con evaluadores, análisis de errores.
  - Discusión: relación con RA/R1–R6 (pedir al docente la definición exacta), ética, sesgos, limitaciones.
  - Anexos: matriz de adquisición, FMEA, reglas, ontología, enlace al código, consentimientos, ficha de datos sintéticos, acta ética.
- Formato: Times New Roman 12, márgenes de 2.54 cm, sangría de 1.27 cm, tablas y figuras numeradas.
- Póster: problema → arquitectura → resultados M1 vs. M3 → ejemplo de explicación → conclusiones.
- Guion de demo (10–15 min): contexto (2) → conocimiento y ontología (3) → simulación de falla en vivo en el tablero (4) → comparación de métricas (3) → ética y limitaciones (2).

## Cronograma resumido (ajustar a la fecha de entrega)
| Semana | Entregable |
|---|---|
| 1 | AGENTS.md, MEMORIA, ERRORES, repo; agente investigador lanzado |
| 1–2 | Decisiones de conocimiento, FMEA, léxico, revisión cruzada |
| 2–3 | Ontología, reglas y tests; generador de datos sintéticos |
| 3–5 | MLP / CNN1D / LSTM entrenados y evaluados |
| 5–6 | Fusión M0–M3, XAI |
| 6–7 | Métricas completas, equidad, análisis de errores |
| 6–8 | API + web demostrativa (8 páginas) |
| 8–9 | Landing page publicada en GitHub Pages |
| 7–9 | Documento APA, anexos, póster, demo ensayada |

## Verificación
- `pytest` sobre generador (firmas de falla presentes, sin fuga entre particiones), motor de reglas (casos positivos y negativos por regla), ontología (consistencia con HermiT) y API (tests con `TestClient`).
- `python -m metaltech.data.generator --config configs/assets.yaml` produce el dataset con semilla fija y es reproducible (mismo hash).
- `python -m metaltech.models.train` y `evaluate` generan `reports/tables/comparacion.csv` con M0–M3; criterio de éxito: M3 con F1 ≥ M1 y menos falsas alarmas.
- `uvicorn metaltech.api.main:app` y luego `streamlit run src/metaltech/dashboard/app.py`: recorrer el flujo de la demo (inyectar cavitación en una bomba → alerta explicada con reglas y variables).
- Script de carga para latencia p50/p95 < 200 ms por solicitud.
- Web demostrativa: cada una de las 8 páginas carga sin errores; el simulador muestra las reglas disparadas y la explicación para al menos un caso por activo.
- Landing: abrir `landing/index.html` en local y en GitHub Pages; las cifras coinciden con `reports/`; se ve bien en el móvil.
- Trazabilidad: cada regla de `rules.yaml` tiene una fuente en `decisiones.md` (test automático).
- Proceso: MEMORIA.md tiene una entrada por tarea, y todo ERR-NNN citado existe en ERRORES.md (script de verificación de enlaces).
- Revisión final del documento contra la lista de 15 secciones y el formato APA.
