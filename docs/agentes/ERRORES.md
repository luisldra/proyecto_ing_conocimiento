# Base de conocimiento de errores

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Bitácora: [MEMORIA.md](MEMORIA.md)

Antes de empezar una tarea, revise el índice y las lecciones aprendidas. Cada error recibe un ID consecutivo `ERR-NNN` que no se reutiliza, y se enlaza desde la entrada correspondiente de MEMORIA. Esta base alimenta las secciones *Análisis de errores* y *Limitaciones* del documento final.

## Índice por origen

| Origen | Errores |
|---|---|
| entorno (instalación, SO, dependencias) | ERR-002, ERR-006, ERR-007, ERR-008 |
| código (bugs, lógica) | ERR-009 |
| datos (generador, fugas, desbalance) | – |
| conocimiento (reglas, ontología, fuentes) | ERR-001, ERR-003, ERR-005, ERR-010 |
| agente (supuestos falsos, malas decisiones del agente) | ERR-004 |

## Lecciones aprendidas
- Las normas ISO, IEC, NEMA, HI e IEEE son de pago: hay que citar la fuente secundaria que da el valor y marcar la confianza (ERR-001).
- Todo umbral sin segunda fuente se marca como **supuesto** con confianza baja en `decisiones.md`; no se presenta como dato (ERR-003).
- Hay que correr una verificación cruzada de IDs entre los YAML antes de cerrar cualquier cambio en la base de conocimiento (ERR-004).
- Nunca se inventa un DOI: si no se verifica, se cita la URL de la página oficial (ERR-005).
- Antes de asumir una versión de Python o una dependencia del plan, verificar la disponibilidad real en el equipo (ERR-007, ERR-008).
- Los verificadores automáticos deben ignorar plantillas y comentarios de los documentos que revisan (ERR-009).
- Una regla solo sirve si la firma del simulador puede activarla: la coherencia umbral ↔ firma ↔ regla se comprueba con un test, no a ojo (ERR-010).

---

## Registro de errores (más reciente arriba)

<!-- Plantilla:
### ERR-001 – Título corto
- Fecha: AAAA-MM-DD
- Fase/archivo:
- Origen: entorno | código | datos | conocimiento | agente
- Síntoma:
- Causa raíz:
- Solución:
- Prevención:
- Estado: resuelto | abierto
-->

### ERR-010 – Firmas de falla que no alcanzaban el umbral de sus propias reglas
- Fecha: 2026-11-05
- Fase/archivo: Fase 1, `configs/failure_modes.yaml` ↔ `configs/assets.yaml` ↔ `rules.yaml`
- Origen: conocimiento
- Síntoma: al cruzar los valores finales de cada firma con los umbrales de los síntomas, 10 combinaciones modo/variable no los activaban (p. ej. R04, R09, R12, R18, R28, R35: el motor con desgaste de rodamiento terminaba a 75 °C con alerta en 90 °C). Además, 5 modos de la FMEA no tenían regla, la FMEA de desalineación del compresor usaba variables que el compresor no define y 6 componentes no coincidían entre modo, FMEA y activo.
- Causa raíz: la Fase 1 validó solo IDs y NPR (ERR-004); no comparó los valores numéricos de las firmas con los umbrales. D-010 fijaba +8–15 °C, que es el comienzo de la etapa tardía y no el valor al momento de la falla.
- Solución: D-042 (firmas corregidas, variables y componentes agregados, reglas R41–R45) y D-041 (modo `holgura_mecanica`, reglas R46–R48). Se tocaron las firmas y no los umbrales, que se apoyan en normas.
- Prevención: `tests/test_conocimiento.py` verifica referencias, cobertura modo ↔ FMEA ↔ regla, componentes y que cada firma active los síntomas de su FMEA y de sus reglas. Debe pasar antes de cerrar cualquier cambio en `knowledge/` o `configs/`.
- Estado: resuelto

### ERR-009 – El verificador de proceso contó la plantilla de ERRORES.md como un error duplicado
- Fecha: 2026-11-05
- Fase/archivo: Fase 0, `src/metaltech/proceso.py`
- Origen: código
- Síntoma: `test_memoria_y_errores_consistentes` falló con "ERR duplicados: ['ERR-001']".
- Causa raíz: la plantilla comentada (`<!-- ### ERR-001 – Título corto ... -->`) coincidía con la expresión regular de entradas.
- Solución: se eliminan los comentarios HTML antes de analizar ERRORES.md.
- Prevención: el test cubre este caso con el archivo real; los verificadores ignoran plantillas.
- Estado: resuelto

### ERR-008 – Java (JDK) no instalado: HermiT no disponible
- Fecha: 2026-11-05
- Fase/archivo: Fase 0 (entorno) / Fase 2, `kb/ontology.py`
- Origen: entorno
- Síntoma: `java: command not found`; `owlready2.sync_reasoner()` fallaría con `OwlReadyJavaError`.
- Causa raíz: el equipo no tiene JDK; HermiT (razonador de owlready2) lo necesita.
- Solución: pendiente. Las pruebas marcadas `@pytest.mark.java` se omiten sin Java (`tests/conftest.py`). Opciones: instalar JDK 17 (p. ej. `winget install EclipseAdoptium.Temurin.17.JDK`) o validar la consistencia con un chequeo propio en Python.
- Prevención: documentado en README; la Fase 2 no debe depender de Java para sus pruebas principales.
- Estado: abierto

### ERR-007 – El Python del equipo (3.14) no coincide con el del plan (3.11)
- Fecha: 2026-11-05
- Fase/archivo: Fase 0, entorno virtual
- Origen: entorno
- Síntoma: `AGENTS.md` y el plan indicaban Python 3.11; el único intérprete instalado es 3.14.7.
- Causa raíz: el plan se redactó sin verificar la versión instalada (ya anticipado en ERR-006).
- Solución: se verificó que torch 2.15 (CPU), pandas, scikit-learn, pyarrow, shap, captum, streamlit y owlready2 (desde código fuente) se instalan en 3.14; todas las pruebas de importación pasan. Se adopta `requires-python >= 3.11` y se actualizó `AGENTS.md`.
- Prevención: `requirements.txt` usa cotas mínimas; si algún compañero usa 3.11 debe correr `pytest` tras instalar. Si una dependencia falla en 3.14, crear el entorno con 3.12.
- Estado: resuelto

### ERR-006 – PyYAML no instalado en el entorno
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, verificación de los YAML de `knowledge/` y `configs/`
- Origen: entorno
- Síntoma: `ModuleNotFoundError: No module named 'yaml'` al validar los YAML.
- Causa raíz: el Python 3.12 del sistema no tiene dependencias del proyecto; todavía no existe `requirements.txt` (Fase 0 pendiente).
- Solución: se instaló PyYAML **solo en el scratchpad temporal del agente** (`pip --target`), sin tocar el entorno del sistema ni el repositorio.
- Prevención: incluir `pyyaml` en `requirements.txt`; el Python declarado en AGENTS.md es 3.11 y el instalado es 3.12, lo que debe revisarse al crear el entorno virtual.
- Estado: resuelto (`requirements.txt` creado y entorno `.venv` con pyyaml instalado en la Fase 0)

### ERR-005 – DOIs no verificables en algunas referencias
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, `knowledge/acquisition/decisiones.md` (referencias)
- Origen: conocimiento
- Síntoma: no se pudo confirmar el DOI de Matzka (2020) ni el de Dyer y Stewart (1978); del estudio PMC12251610 no se verificaron autores ni revista.
- Causa raíz: la búsqueda no devolvió los metadatos completos y el agente no debe inventar DOIs.
- Solución: Matzka (2020) se cita con la URL de IEEE Xplore; Dyer y Stewart (1978) sin DOI y con la marca "[consultada de memoria; DOI no verificado]"; el estudio de PMC se cita por título y URL con la marca "[autores y revista no verificados]".
- Prevención: antes del documento APA final, el agente de Documentación verifica estos registros en Crossref o en la base de la biblioteca.
- Estado: abierto

### ERR-004 – Modo de falla asignado a activos sin fila FMEA
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, `configs/failure_modes.yaml` (`falla_lubricacion_rodamiento`)
- Origen: agente
- Síntoma: la verificación cruzada indicó que `falla_lubricacion_rodamiento` declaraba los activos `bomba_centrifuga` y `banda_transportadora`, que no tenían fila FMEA ni regla.
- Causa raíz: el agente amplió los activos del modo sin actualizar `fmea.yaml`.
- Solución: el modo queda restringido a `motor_electrico`; en los demás activos la lubricación deficiente se subsume en `desgaste_rodamiento` (hueco anotado para el Revisor).
- Prevención: correr la verificación de IDs (activo ↔ modo ↔ FMEA ↔ regla) tras cada cambio; en la Fase 2 se convierte en un test de pytest.
- Estado: resuelto

### ERR-003 – Umbrales y reglas sin segunda fuente (supuestos del agente)
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, `configs/assets.yaml`, `knowledge/acquisition/decisiones.md`
- Origen: conocimiento
- Síntoma: varios umbrales numéricos no tienen ≥ 2 fuentes ni norma:
  - fuga de sello en ml/h (D-015);
  - diferencial del separador de 0.7 bar (D-018);
  - interpretación de "la prensa está dura" (D-023);
  - deslizamiento de banda del 2/5 % y desvío de 25/50 mm (D-024, D-025);
  - temperatura de husillo y coeficiente de variación de la carga (D-029);
  - bus DC, temperatura del variador y conteo de disparos (D-030);
  - umbrales en g de impacto (D-028);
  - factores 2×/4× de alta frecuencia (D-010);
  - caída de presión en retención y nivel de tanque (D-022);
  - coeficiente de variación de caudal (D-013);
  - curtosis de la holgura mecánica (D-041) y magnitudes de las firmas corregidas (D-042), que se calibran contra los datos en la Fase 3.
- Causa raíz: no hay datos abiertos ni normas accesibles para esos valores en prensas, compresores, bandas y CNC.
- Solución: se registran como **supuestos con confianza baja** y se justifican por la física de la falla.
- Prevención: el Revisor debe intentar una segunda fuente para cada uno; si no la encuentra, el documento final los declara en *Limitaciones*. Además, conviene un análisis de sensibilidad de M0 a esos umbrales.
- Estado: abierto

### ERR-002 – PDF técnico no legible (TECO-Westinghouse)
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, D-008
- Origen: entorno
- Síntoma: WebFetch devolvió el PDF de ajustes RTD como binario, con la tabla en imágenes, sin texto extraíble.
- Causa raíz: PDF generado desde Excel con contenido en imágenes JPEG.
- Solución: se usaron los valores del extracto del buscador (alarma 90–110 °C y disparo 95–120 °C para rodamientos antifricción), contrastados con un manual Siemens. La referencia queda marcada.
- Prevención: si hace falta, leer el PDF con OCR (skill de PDF) o buscar otra fuente.
- Estado: resuelto (con reserva)

### ERR-001 – Normas de pago sin acceso al texto oficial
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, `knowledge/acquisition/decisiones.md`
- Origen: conocimiento
- Síntoma: no se pudo leer el texto de ISO 20816-1/-3, ISO 17359, ISO 13374, IEC 60034-1, IEC 60085, NEMA MG-1, ANSI/HI 9.6.1 (salvo la copia de law.resource.org, que no se abrió), IEEE 519, ISO 4406, IEC 60812 ni AIAG-VDA.
- Causa raíz: son normas de pago.
- Solución: los valores se tomaron de fuentes secundarias que las citan (Fabrico, Oxmaint, ALL-TEST Pro, Pumps & Systems, entre otras) o del conocimiento previo del agente. Cada caso queda declarado en la D-NNN. El criterio del 25 % de ISO 20816-1 (D-004) y el límite de THD de IEEE 519 vienen de memoria.
- Prevención: verificar contra el texto oficial si la universidad tiene acceso (biblioteca o ICONTEC); priorizar D-003, D-004, D-012 y D-030.
- Estado: abierto
