# Memoria del proyecto – Bitácora de agentes

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Errores: [ERRORES.md](ERRORES.md) · Plan: [PLAN.md](../PLAN.md)

## Estado actual
- **Fase en curso:** Fase 0 cerrada (salvo reparto de roles y publicación en GitHub); Fase 1 con los huecos de cobertura cerrados, a la espera de la revisión del Revisor.
- **Última tarea:** cierre de huecos de la Fase 1 (D-041, D-042, ERR-010). La base de conocimiento queda con 31 modos de falla, 41 filas FMEA, 48 reglas (R01–R48), 10 expresiones y 63 síntomas. `pytest`: 39 pruebas OK, `ruff` limpio.
- **Siguiente tarea:** Fase 2 – ontología (`kb/ontology.py`), motor de reglas (`kb/rules_engine.py`) y léxico (`kb/lexicon.py`) con sus tests. La revisión cruzada del agente **Revisor de conocimiento** sigue pendiente y puede hacerse en paralelo.
- **Bloqueos:** ninguno. Abiertos: normas de pago sin texto oficial (ERR-001), umbrales sin segunda fuente (ERR-003), Java no instalado para HermiT (ERR-008).
- **Pendiente por confirmar:**
  - definición exacta de RA/R1–R6 con el docente;
  - fecha de entrega;
  - acceso institucional a normas ISO/IEC para verificar D-003, D-004, D-012 y D-030;
  - reparto de roles del equipo y push del commit inicial al remoto `luisldra/proyecto_ing_conocimiento`;
  - instalar o no un JDK 17 (ERR-008).

---

## Bitácora (más reciente arriba)

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
