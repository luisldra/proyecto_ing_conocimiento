# Base de conocimiento de errores

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Bitácora: [MEMORIA.md](MEMORIA.md)

Antes de empezar una tarea, revise el índice y las lecciones aprendidas. Cada error recibe un ID consecutivo `ERR-NNN` que no se reutiliza, y se enlaza desde la entrada correspondiente de MEMORIA. Esta base alimenta las secciones *Análisis de errores* y *Limitaciones* del documento final.

## Índice por origen

| Origen | Errores |
|---|---|
| entorno (instalación, SO, dependencias) | ERR-002, ERR-006 |
| código (bugs, lógica) | – |
| datos (generador, fugas, desbalance) | – |
| conocimiento (reglas, ontología, fuentes) | ERR-001, ERR-003, ERR-005 |
| agente (supuestos falsos, malas decisiones del agente) | ERR-004 |

## Lecciones aprendidas
- Las normas ISO, IEC, NEMA, HI e IEEE son de pago: hay que citar la fuente secundaria que da el valor y marcar la confianza (ERR-001).
- Todo umbral sin segunda fuente se marca como **supuesto** con confianza baja en `decisiones.md`; no se presenta como dato (ERR-003).
- Hay que correr una verificación cruzada de IDs entre los YAML antes de cerrar cualquier cambio en la base de conocimiento (ERR-004).
- Nunca se inventa un DOI: si no se verifica, se cita la URL de la página oficial (ERR-005).

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

### ERR-006 – PyYAML no instalado en el entorno
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, verificación de los YAML de `knowledge/` y `configs/`
- Origen: entorno
- Síntoma: `ModuleNotFoundError: No module named 'yaml'` al validar los YAML.
- Causa raíz: el Python 3.12 del sistema no tiene dependencias del proyecto; todavía no existe `requirements.txt` (Fase 0 pendiente).
- Solución: se instaló PyYAML **solo en el scratchpad temporal del agente** (`pip --target`), sin tocar el entorno del sistema ni el repositorio.
- Prevención: incluir `pyyaml` en `requirements.txt`; el Python declarado en AGENTS.md es 3.11 y el instalado es 3.12, lo que debe revisarse al crear el entorno virtual.
- Estado: resuelto (temporal)

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
  - coeficiente de variación de caudal (D-013).
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
