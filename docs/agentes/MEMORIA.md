# Memoria del proyecto – Bitácora de agentes

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Errores: [ERRORES.md](ERRORES.md) · Plan: [PLAN.md](../PLAN.md)

## Estado actual
- **Fase en curso:** Fase 4 terminada y corregida (D-054, D-055). El equipo revisa antes de abrir la Fase 5.
- **Última tarea:** ventanas grises, confusores multivariable, 32 unidades con una reservada por tipo, ajustes con datos públicos, turnos rotativos y reentrenamiento. F1 macro medio: test 0.919, unidad no vista 0.930.
- **Siguiente tarea:** Fase 5 (fusión M0–M3), cuando el equipo lo indique.
- **Equipo:** Alejandro (conocimiento y QA), Luis David (datos y modelos), Junio (API y web demostrativa), David (documento APA, póster y landing).
- **Bloqueos:** ninguno. Abiertos: normas sin texto oficial, que se consultan por fuentes públicas porque no hay acceso institucional (ERR-001, ERR-015; ver [normas_fuentes_externas.md](../../knowledge/acquisition/normas_fuentes_externas.md)) y supuestos sin fuente (ERR-003).
- **Pendiente por confirmar:**
  - definición exacta de RA/R1–R6 con el docente;
  - fecha de entrega;

---

## Bitácora (más reciente arriba)

## [2026-11-08] Fases 3 y 4 – Documento de avances (agente: Documentación)
- Hecho: `docs/AVANCES_FASES_3_Y_4.md`, con el recorrido de las fases, resultados, límites y guía de todos los archivos. Conteos verificados contra el repositorio.
- Pendiente: nada de este documento; actualizarlo al cerrar la Fase 5.
- Errores: ninguno.
- Decisiones: ninguna.

## [2026-11-08] Fase 4 – Correcciones decididas por el equipo y reentrenamiento (agente: Datos/ML)
- Hecho:
  - Ventanas grises y métricas de aviso temprano (D-054).
  - 11 confusores multivariable, 32 unidades con `test_unidad`, omisión de firma 0.4 y severidad propia de herramienta (D-055).
  - Técnicos en turnos rotativos: separa persona y turno; los sensores no cambian (hash idéntico).
  - Reentrenamiento de 18 modelos. Elegidos: motor MLP, bomba CNN1D, compresor MLP, prensa CNN1D, banda CNN1D, CNC LSTM.
- Resultados (modelos elegidos, una semilla):
  - F1 macro: test 0.919, unidad no vista 0.930.
  - Falsa alarma en equipo sano: 0.08 % sin confusor y 2.12 % con confusor (test); 0.27 % y 2.28 % (unidad no vista).
  - M0 detecta 67.5 % (predicción) y 55.5 % (detección), con 16.72 % de alarmas en confusores.
  - `bomba_centrifuga/desalineacion_eje` sube de F1 0 a 0.71 (se confunde con desbalanceo; 2 episodios en test).
  - Acierto de técnicos: 84.2 % mañana, 85.7 % tarde, 75.0 % noche.
- Pendiente:
  - Una consulta al docente sobre RA/R1–R6.
  - La cavitación y otras clases siguen con poco soporte en test (Fase 7: 5 semillas).
  - El F1 alto refleja que el modelo se evalúa con el mismo generador con que se entrena; es optimista.
- Errores: ERR-023 (resuelto).
- Decisiones: D-054 y D-055.

## [2026-11-08] Fase 4 – Modelos de Deep Learning (agente: Datos/ML)
- Hecho:
  - `data/features.py`, `models/{mlp,cnn1d,lstm,train,evaluate}.py` y `tests/test_modelos.py`. 18 entrenamientos (3 arquitecturas por 6 activos).
  - Resultados en `reports/tables/modelos_*`; pesos en `checkpoints/` (no se versionan). Elegidos por validación: motor LSTM, bomba MLP, compresor MLP, prensa CNN1D, banda MLP, CNC CNN1D.
- Resultados en test (modelos elegidos, media por activo): F1 macro 0.599, precisión 0.537, recall 0.844. Las arquitecturas no se separan con claridad. `bomba_centrifuga/desalineacion_eje` queda con F1 0.
- Pendiente:
  - Decidir el tratamiento de los avisos tempranos (ERR-023).
  - 5 semillas e intervalos de confianza en la Fase 7.
- Errores: ERR-023 (abierto).
- Decisiones: D-053.

## [2026-11-08] Fase 3 – Dificultad del simulador y umbrales de bombas (agente: Datos/ML)
- Hecho:
  - Bombas: vibración 2.8/4.5 → 5.1/8.5 mm/s (D-051); firmas compartidas con `tipo: frac_alerta`.
  - Simulador (D-052): firmas incompletas, severidad 0.8–1.15, deriva de sensor, excursiones operativas y señal sana sin recorte.
  - Válvula hidráulica: ciclo sostenido y R27 con `tiempo_ciclo_en_rango` (68 síntomas).
  - `scripts/contrastar_datasets.py` y `reports/tables/contraste_datasets.csv` con AI4I 2020 y SKAB.
  - Ontología regenerada; 515 pruebas OK.
- Resultados: M0 detecta 81.8 % (predicción) y 76.6 % (detección); cruces en 4.4 % de episodios; alarmas en sano 0 % sin confusor y 1.43 % con confusor.
- Pendiente:
  - NASA IMS y UCI hidráulico sin contraste numérico.
  - Diferencias aceptadas frente a datos públicos, listadas en `data/README.md`.
  - Revisar la cobertura de `sensores de CNC` si en la Fase 4 hay clases con muy pocas muestras (mínimo actual: 6 episodios por par modo-activo).
- Errores: ERR-020 (resuelto), ERR-022 (resuelto).
- Decisiones: D-051 y D-052.

## [2026-11-08] Fase 3 – Simulador y calibración inicial (agente: Datos/ML)
- Hecho:
  - `src/metaltech/data/generator.py`: señal por turno, 524 episodios sin solaparse, 7 confusores, faltantes, observaciones con sesgo por técnico y turno, partición temporal con purga. 36 meses, 16 unidades, 2.52 M filas, unos 25 s.
  - `src/metaltech/data/calibracion.py` y tablas `reports/tables/calibracion_*`; `tests/test_generator.py`; ficha en `data/README.md`.
  - Correcciones en `failure_modes.yaml` (D-049): 8 modos pasan a detección, `escalon_en` y lubricación 30 → 35 °C. `train.yaml`: 36 meses y parámetros del simulador (D-050).
  - `knowledge/acquisition/normas_fuentes_externas.md`: consulta de normas por fuentes públicas (sin acceso institucional).
- Resultados: 2.27 % de filas positivas; mínimo 5 episodios por par modo-activo; M0 detecta 100 % (predicción) y 98 % (detección); alarmas en sano 0 % sin confusor y 4.85 % con confusor; acierto de técnicos 87.6 % mañana, 85.5 % tarde y 78.9 % noche.
- Pendiente:
  - Dificultad del simulador, umbrales de bombas y contraste con datos públicos: resueltos en la entrada siguiente.
- Errores: ERR-020 (resuelto después), ERR-021 (resuelto).
- Decisiones: D-049 y D-050.

## [2026-11-08] Fase 2 – Resincronización tras la revisión cruzada (agente: QA)
- Hecho:
  - `.venv` con Python 3.12.10 y JDK 17 portable en este equipo.
  - `knowledge/ontology/metaltech.owl` regenerado desde los YAML (55 reglas, 67 síntomas).
  - `tests/test_ontology.py` actualizado a los nuevos conteos; prueba de R03/R04 reescrita (ya no se combinan, FC 0.85).
  - Pruebas nuevas en `tests/test_rules_engine.py`: modo principal en las 41 firmas, sin cruces de modo en t = 0.85–0.95 y bloqueo de las premisas `en_rango` fuera de rango.
  - Verificación: `pytest` 464 OK sin omitidas, incluidas `test_entorno.py` y HermiT; `ruff` limpio; `metaltech.proceso` OK.
- Pendiente:
  - Hallazgo para la Fase 3, medido con las formas y retardos reales de `failure_modes.yaml` (sin ruido; sigmoide con k = 10 como supuesto, porque D-037 no fija k). Corrige la cifra inicial de 7 de 41, que interpolaba todo de forma lineal:
    - De 30 casos evaluables, 16 tienen una anticipación mínima de M0 menor que H = 24 h. No hay cruces a otro modo.
    - `motor_electrico/falla_lubricacion_rodamiento` solo se diagnostica en t = 1.0.
    - `centro_cnc/desgaste_herramienta` dura 3.3–4 h, menos que H y que la ventana de 6 h; `bomba_centrifuga/cavitacion` dura 1–48 h.
    - 11 casos con forma `escalon` o `intermitente` no se evaluaron: requieren definir su generador.
- Errores: ERR-019 (resuelto).
- Decisiones: ninguna de conocimiento. Se usa Python 3.12 en este equipo, dentro de `requires-python >= 3.11`.

## [2026-11-05] Fase 1 – Revisión cruzada de la base de conocimiento (agente: Revisor de conocimiento)
- Hecho:
  - Revisión sobre el commit 33594a5, con hallazgos en `knowledge/acquisition/revision.md` (H-01 a H-38).
  - Verificadas contra fuentes D-003, D-004, D-012 y D-030, y una muestra de 14 decisiones más. ANSI/HI 9.6.1-2017 se leyó en su texto completo.
  - Buscada una segunda fuente para todos los supuestos de ERR-003.
  - Revisadas R41–R48, las 10 firmas de D-042, D-041, D-043 y D-044.
  - Valores corregidos:
    - `dp_separador_bar`, alerta 0.7 → 0.55 bar (D-018);
    - `fuga_sello_ml_h`, nominal 0–2 → 0–1, alerta 5 → 3 y crítico 20 → 9 ml/h (D-015);
    - `tension_bus_dc_pct`, crítico 130 → 125 % (D-030);
    - firma de `cavitacion`, `npsh_margen_ratio` 1.0 → 0.9 (D-012).
  - Reglas: premisas `en_rango` en seis reglas (D-045), FC bajados en 11 (D-046) y R49–R55 nuevas (D-047). Síntomas de 63 a 67, con campo `uso` en siete.
  - EXP08 queda solo en motor. EXP06 y EXP07 corregidas.
  - Dataset UCI de sistemas hidráulicos evaluado y agregado (D-048).
  - Referencias en APA 7: DOIs verificados, nombres completos de autores corporativos y lista reordenada.
- Resultados de verificación:
  - Script temporal: IDs, síntomas por activo, modo ↔ FMEA ↔ regla, D-NNN, NPR y orden de umbrales sin errores; ninguna regla se dispara en operación normal y todas se pueden disparar.
  - El modo correcto es el principal en 41 de 41 firmas. En la trayectoria solo queda un cruce breve en `falla_valvula_admision`.
  - No hay `.venv` en este equipo: `pytest` se corrió con dependencias en el scratchpad y sin `test_entorno.py`. Antes de los cambios pasaban todas. Después falla `test_rodamiento_del_motor_combina_r03_y_r04`, y en `test_ontology.py` fallan las que dependen de los conteos y del `.owl`. Son fallas esperadas (ver Pendiente).
- Pendiente:
  - Regenerar `metaltech.owl` y ajustar `tests/test_ontology.py` y `tests/test_rules_engine.py` (tabla en `revision.md`).
  - Agregar a `tests/test_conocimiento.py` las pruebas de modo principal y de trayectoria.
  - Conseguir ISO 20816-3:2026 e ISO 10816-7.
  - Fase 3: máximo de ventana para eventos de segundos; revisar las firmas de D-042.
- Errores: ERR-014, ERR-015, ERR-016, ERR-017, ERR-018 (ver [ERRORES.md](ERRORES.md)). Actualizados: ERR-001 y ERR-003 (siguen abiertos), ERR-002 y ERR-005 (resueltos).
- Decisiones: D-045 (discriminadores `en_rango`), D-046 (FC ajustados a la política), D-047 (reglas para síntomas sin uso y campo `uso`) y D-048 (dataset UCI hidráulico). Confianza de D-003 bajada: ISO 20816-3 no cubre compresores de tornillo ni lista bombas.

## [2026-11-05] Fase 2 – Ontología, motor de reglas y léxico (agente: Datos/ML + Backend)
- Hecho:
  - `kb/base.py`: carga única de los YAML (`cargar_base()`), índices y utilidades `valor_nominal` / `valor_final`.
  - `kb/lexicon.py`: normaliza el texto (minúsculas, sin tildes) y reconoce las 10 expresiones y sus variantes; devuelve síntoma percibido y modos candidatos filtrados por activo (`fc_max` ≤ 0.6). Coincidencia difusa opcional (por defecto desactivada porque confunde "bomba" con "banda").
  - `kb/rules_engine.py`: fusificación por niveles (alerta, crítico, cola baja, en rango y tendencia vs. línea base), rampa opcional `margen_suave`, encadenamiento hacia adelante, FC de la premisa = mínimo, combinación MYCIN, **traza** con valor real y umbral por premisa, reglas parciales, datos faltantes, salida en texto y JSON, y CLI (`python -m metaltech.kb.rules_engine`).
  - `kb/ontology.py`: genera `metaltech.owl` con Owlready2 (22 clases: 14 superiores, 2 subclases de síntoma y 6 de activo; 18 propiedades de objeto y 24 de datos; clases disjuntas y propiedades funcionales). Individuos: 16 unidades, 37 componentes, 168 sensores, 60 variables, 63 síntomas, 31 modos, 127 causas, 108 acciones, 48 reglas, 10 expresiones, 41 filas FMEA, 10 técnicos y 3 turnos. Consultas (síntomas, causas, acciones, componentes y reglas por modo y activo; diagnóstico diferencial; sensores; `detalle_modo`; `grafo`), guardado y carga, `validar_estructura()` y `validar_con_hermit()`.
  - `knowledge/ontology/metaltech.owl` (499 KB) y `knowledge/ontology/README.md` (clases, propiedades y consultas, para Protégé y el documento).
  - `scripts/instalar_jdk.py`: JDK 17 Temurin portable en `.tools/jdk17`, con verificación SHA-256 (no modifica el sistema). Con él HermiT corre en unos 5 s.
  - `assets.yaml`: sección `planta` (3 turnos; 8 electromecánicos y 2 instrumentistas, anonimizados) para la ontología y la Fase 3.
  - Tests nuevos: `test_lexicon.py` (50), `test_rules_engine.py` (163) y `test_ontology.py` (24, tres con HermiT). Cubren las 48 reglas (caso positivo, falta de una premisa y operación normal en los 6 activos), el final de las 41 firmas del simulador, los escenarios del plan, MYCIN y el ida y vuelta del OWL. El `.owl` versionado se compara con lo que generan los YAML.
  - `README.md`, `AGENTS.md`, `.gitignore` y `conftest.py` actualizados.
- Resultados de verificación:
  - Sobre el valor final de las 41 firmas, el modo correcto está entre las conclusiones en 41/41 casos y es el principal en 39/41. Los dos fallos son ambigüedades reales (compresor: `fuga_aire_red` 0.75 contra `falla_valvula_admision` 0.70; prensa: `contaminacion_aceite_hidraulico` 0.90 contra `valvula_hidraulica_pegada` 0.65). Es la referencia inicial de **M0** (solo reglas).
  - Ninguna regla se dispara con la operación normal (punto medio y bordes nominales) en ningún activo.
- Pendiente:
  - Revisor: D-041 a D-044.
  - Revisar con el docente si `FilaFMEA` (clase agregada al plan) es aceptable para el documento.
  - Fase 3: el generador debe producir las observaciones de técnicos con `Lexico` y las 7 clases de eventos confusores.
- Errores: ERR-008 (resuelto), ERR-011, ERR-012, ERR-013 (ver [ERRORES.md](ERRORES.md)).
- Decisiones: D-043 (semántica del motor: nítido por defecto, una expresión sin síntomas medidos no diagnostica) y D-044 (ontología generada, `FilaFMEA`, validación en dos niveles). El JDK se instala en el proyecto y no en el sistema.

## [2026-11-05] Fase 1 – Cierre de huecos de cobertura y coherencia (agente: Revisor de conocimiento / QA)
- Hecho:
  - Nuevo test `tests/test_conocimiento.py` (13 pruebas): referencias entre YAML, cobertura modo ↔ FMEA ↔ regla, componentes, trazabilidad regla → decisión y que cada firma active los síntomas medidos de su FMEA y de sus reglas. Reveló huecos que el chequeo anterior no veía (ERR-010).
  - Reglas **R41–R45** para los 5 modos de la FMEA sin regla (bomba/desbalanceo, compresor/desalineación, banda/rodamiento, banda/sobrecarga, CNC/rodamiento). Registradas en D-042.
  - Modo nuevo **`holgura_mecanica`** (motor, bomba, compresor) con reglas R46–R48, 3 filas FMEA, firma y candidato en EXP04. Registrado en D-041, con dos fuentes nuevas (Fluke, 2025; Acoem, s. f.-b).
  - `assets.yaml`: variables `vib_2x_1x_ratio` y `vib_axial_radial_ratio` en el compresor; componentes `carga_accionada` y `base_anclajes`.
  - `failure_modes.yaml`: `componentes_por_activo` para los componentes que cambian de nombre entre activos, y 10 firmas corregidas para que alcancen los umbrales (tabla en D-042). Los umbrales no se tocaron.
  - Corrección de D-010 (el aumento de 8–15 °C es el inicio de la etapa tardía, no el valor al fallar).
  - `fmea.yaml`/`fmea.md`, `rules.yaml`, `expresiones.yaml` y `matriz_adquisicion.md` actualizados.
- Pendiente:
  - Revisión cruzada del Revisor (V4) sobre todo lo anterior; D-041 y D-042 incluidas.
  - Las magnitudes de las firmas corregidas y la curtosis de la holgura son supuestos que se calibran en la Fase 3.
  - La lubricación deficiente fuera del motor sigue subsumida en `desgaste_rodamiento`.
  - Instalar JDK 17 (ERR-008), reparto de roles y push a GitHub.
- Errores: ERR-010 (resuelto). ERR-003 ampliado con los nuevos supuestos.
- Decisiones: D-041 (holgura mecánica, confianza media) y D-042 (cierre de huecos, confianza media; magnitudes de firma baja). Las firmas se ajustaron y los umbrales normativos no.

## [2026-11-05] Fase 0 – Infraestructura del repositorio (agente: QA/Documentación)
- Hecho:
  - Revisión de contexto: los YAML de Fase 1 son consistentes (referencias de síntomas, modos y activos; NPR = S·O·D). Se confirmaron 5 modos FMEA sin regla y variables de firma ausentes en algunos activos.
  - `.venv` con Python 3.14.7; instaladas torch 2.15 (CPU), pandas, scikit-learn, pyarrow, shap, captum, owlready2, FastAPI, Streamlit, pyvis, plotly, ruff y pytest.
  - Creados `requirements.txt`, `pyproject.toml` (ruff + pytest + paquete editable), `.gitignore`, `README.md`, `data/README.md` (declaración de datos sintéticos) y `configs/train.yaml` (ventana 36 pasos, H = 24 h, partición 60/20/20, 5 semillas, fusión M3).
  - Esqueleto `src/metaltech/{data,kb,models,hybrid,xai,metrics,api,dashboard}` y carpetas con `.gitkeep`.
  - `src/metaltech/proceso.py`: verifica que todo ERR citado en MEMORIA exista en ERRORES.
  - `tests/`: 26 pruebas (importaciones, subpaquetes, carga de YAML, coherencia de `train.yaml`, proceso). `ruff check .` sin observaciones.
  - `AGENTS.md`: versión de Python y comandos actualizados.
- Pendiente:
  - Reparto de roles del equipo y push al remoto de GitHub (requiere confirmación del usuario).
  - Decidir sobre JDK 17 (ERR-008).
  - Huecos de la Fase 1 (5 reglas faltantes, variables de firma ausentes, modo de holgura mecánica).
- Errores: ERR-007, ERR-008, ERR-009 (ver [ERRORES.md](ERRORES.md)); ERR-006 queda resuelto.
- Decisiones: se usa Python 3.14 (el único instalado) con `requires-python >= 3.11`; `requirements.txt` fija cotas mínimas y no versiones exactas.

## [2026-10-29] Fase 1 – Adquisición del conocimiento por revisión documental (agente: Investigador)
- Hecho:
  - Revisión documental asistida por agente (búsqueda web). Se consultaron:
    - normas ISO 17359, 13374, 20816-1/-3, IEC 60034-1/60085, NEMA MG-1, ANSI/HI 9.6.1, ISO 4406 e IEEE 519, vía fuentes secundarias;
    - literatura: Kusiak (2024), Shortliffe y Buchanan (1975), Randall y Antoni (2011), Teti et al. (2010), Lei et al. (2018) y otras;
    - guías de fabricantes: Atlas Copco, Parker, KSB, TECO, Martin Engineering, entre otros;
    - 6 datasets: AI4I 2020, CWRU, NASA IMS, C-MAPSS, MIMII y SKAB.
  - Archivos creados:
    - `knowledge/acquisition/decisiones.md`: D-001 a D-040, con conflictos y referencias APA 7;
    - `knowledge/acquisition/fmea.md` y `fmea.yaml`: 38 filas en 6 activos;
    - `knowledge/lexicon/expresiones.yaml`: 10 expresiones;
    - `configs/assets.yaml`: 6 activos con variables, umbrales y un catálogo de 63 síntomas;
    - `configs/failure_modes.yaml`: 30 modos, con firmas, formas de degradación y eventos confusores;
    - `knowledge/rules/rules.yaml`: R01–R40;
    - `knowledge/acquisition/matriz_adquisicion.md`;
    - `knowledge/acquisition/datasets_referencia.md`.
  - Verificación cruzada automática de IDs entre todos los YAML y de NPR = S·O·D, con un script temporal fuera del repositorio. Resultado: OK.
- Pendiente:
  - Revisión cruzada por el agente Revisor.
  - Huecos de cobertura de reglas, con modo en la FMEA pero sin regla:
    - `banda_transportadora/desgaste_rodamiento`;
    - `banda_transportadora/sobrecarga_mecanica`;
    - `bomba_centrifuga/desbalanceo_rotor`;
    - `centro_cnc/desgaste_rodamiento`;
    - `compresor_tornillo/desalineacion_eje`.
  - Falta un modo de falla de holgura mecánica, que "cascabeleo" también podría indicar.
  - Verificar las normas en su texto oficial y los DOIs pendientes.
  - Evaluar el dataset UCI de sistemas hidráulicos para la prensa.
  - Agregar `pyyaml` a `requirements.txt`.
- Errores: ERR-001, ERR-002, ERR-003, ERR-004, ERR-005, ERR-006 (ver [ERRORES.md](ERRORES.md)).
- Decisiones:
  - Vibración según ISO 20816-3, Grupo 2, soporte rígido: alerta 2.8 y crítico 4.5 mm/s (D-003).
  - Aislamiento clase F: alerta 130 °C y crítico 155 °C (D-005).
  - NPSHA/NPSH3: alerta 1.3 y crítico 1.1 (D-012).
  - Factores de certeza MYCIN, con un tope de 0.8 para reglas con síntomas percibidos (D-034).
  - El léxico se formaliza por física de la falla, con varios candidatos y fc_max ≤ 0.6 (D-038).
  - Variables relativas a la línea base de cada unidad (D-040).
  - Hay 6 decisiones de confianza baja (D-015, D-018, D-023, D-025, D-029, D-030), además de valores numéricos marcados como baja dentro de otras decisiones.

## [2026-10-29] Fase 0 – Manual de agentes y memoria (agente: Documentación)
- Hecho: lectura y análisis del enunciado (Proyecto 3, Metal Tech); plan maestro aprobado y copiado a `docs/PLAN.md`; creados `AGENTS.md`, `CLAUDE.md`, `docs/agentes/MEMORIA.md` y `docs/agentes/ERRORES.md`.
- Pendiente:
  - Estructura del repositorio (`configs/`, `knowledge/`, `src/metaltech/`, `tests/`, `landing/`).
  - `requirements.txt` y `README.md`.
  - Inicializar git y GitHub.
  - Lanzar el agente investigador (Fase 1).
- Errores: ninguno.
- Decisiones:
  - Stack Python + PyTorch + owlready2 + FastAPI + Streamlit.
  - Modelos MLP (baseline) + CNN1D/LSTM.
  - Ontología OWL + reglas Python con factores de certeza.
  - Adquisición del conocimiento por un agente investigador, sin entrevistas.
  - Web demostrativa multipágina y landing page estática.
