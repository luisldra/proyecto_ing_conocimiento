# Memoria del proyecto – Bitácora de agentes

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Errores: [ERRORES.md](ERRORES.md) · Plan: [PLAN.md](../PLAN.md)

## Estado actual
- **Fase en curso:** Fase 1 – Adquisición del conocimiento (borrador terminado, en revisión).
- **Última tarea:** el agente Investigador construyó la base de conocimiento:
  - 40 decisiones;
  - 30 modos de falla;
  - 38 filas FMEA;
  - 40 reglas;
  - 10 expresiones;
  - 63 síntomas;
  - 6 datasets de referencia.
- **Siguiente tarea:** revisión cruzada del agente **Revisor de conocimiento** sobre `knowledge/` y `configs/`:
  - respaldo ≥ 2 fuentes o 1 norma;
  - contradicciones y huecos;
  - decisiones de confianza baja (ver ERR-003).
- **Bloqueos:** ninguno. Las normas de pago no se leyeron en su texto oficial (ERR-001).
- **Pendiente por confirmar:**
  - definición exacta de RA/R1–R6 con el docente;
  - fecha de entrega;
  - acceso institucional a normas ISO/IEC para verificar D-003, D-004, D-012 y D-030.

---

## Bitácora (más reciente arriba)

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
