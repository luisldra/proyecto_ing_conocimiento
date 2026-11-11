# Base de conocimiento de errores

> Protocolo y formato: [AGENTS.md](../../AGENTS.md) · Bitácora: [MEMORIA.md](MEMORIA.md)

Antes de empezar una tarea, revise el índice y las lecciones aprendidas. Cada error recibe un ID consecutivo `ERR-NNN` que no se reutiliza, y se enlaza desde la entrada correspondiente de MEMORIA. Esta base alimenta las secciones *Análisis de errores* y *Limitaciones* del documento final.

## Índice por origen

| Origen | Errores |
|---|---|
| entorno (instalación, SO, dependencias) | ERR-002, ERR-006, ERR-007, ERR-008, ERR-012, ERR-013 |
| código (bugs, lógica) | ERR-009, ERR-011 |
| datos (generador, fugas, desbalance) | ERR-020, ERR-023 |
| conocimiento (reglas, ontología, fuentes) | ERR-001, ERR-003, ERR-005, ERR-010, ERR-014, ERR-015, ERR-016, ERR-017 |
| agente (supuestos falsos, malas decisiones del agente) | ERR-004, ERR-018, ERR-019, ERR-021, ERR-022, ERR-024 |

## Lecciones aprendidas
- Las normas ISO, IEC, NEMA, HI e IEEE son de pago: hay que citar la fuente secundaria que da el valor y marcar la confianza (ERR-001).
- Todo umbral sin segunda fuente se marca como **supuesto** con confianza baja en `decisiones.md`; no se presenta como dato (ERR-003).
- Hay que correr una verificación cruzada de IDs entre los YAML antes de cerrar cualquier cambio en la base de conocimiento (ERR-004).
- Nunca se inventa un DOI: si no se verifica, se cita la URL de la página oficial (ERR-005).
- Antes de asumir una versión de Python o una dependencia del plan, verificar la disponibilidad real en el equipo (ERR-007, ERR-008).
- Los verificadores automáticos deben ignorar plantillas y comentarios de los documentos que revisan (ERR-009).
- La validación estructural en Python no sustituye al razonador: HermiT encontró una inconsistencia que ningún chequeo propio veía (ERR-011).
- Las APIs y los servidores rechazan el User-Agent por defecto de `urllib` (ERR-012); en Windows, owlready2 no resuelve `file:///` con espacios (ERR-013).
- Una regla solo sirve si la firma del simulador puede activarla: la coherencia umbral ↔ firma ↔ regla se comprueba con un test, no a ojo (ERR-010).
- Una cita no está verificada hasta que se abre la fuente y se encuentra el dato: un título prometedor no basta (ERR-014).
- Antes de aplicar una norma, hay que leer su alcance: el valor puede ser correcto y la máquina estar excluida (ERR-015).
- Un umbral crítico debe compararse con el punto donde el equipo real se protege: si queda por encima, el síntoma nunca se ve (ERR-016).
- Comprobar solo el final de la degradación no basta; hay que mirar qué reglas se disparan juntas y si su evidencia es independiente (ERR-017).
- Antes de editar tras una tarea larga, hay que comprobar `git log` y releer: el repositorio pudo cambiar (ERR-018).
- "Sin conclusión" y "conclusión equivocada" son resultados distintos: una prueba debe afirmar exactamente lo que dice la decisión que protege (ERR-019).

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

### ERR-024 – Métrica de estabilidad sin capacidad de discriminar
- Fecha: 2026-11-11
- Fase/archivo: Fase 6, `src/metaltech/xai/explain.py`, `tests/test_xai.py`
- Origen: agente
- Síntoma: la estabilidad dio 1.000 en los 6 activos; además, una prueba nueva falló porque el modelo de juguete, lineal en una sola variable, da la misma explicación con cualquier ruido.
- Causa raíz: el nivel de ruido (0.05 desviaciones) se fijó sin comprobar que la métrica pudiera bajar, y la prueba usó un modelo en el que la estabilidad es 1 por construcción.
- Solución: se reporta la curva con 0.05, 0.25 y 0.5 desviaciones (sin elegir un nivel tras ver resultados) y la prueba usa un modelo no lineal.
- Prevención: antes de reportar una métrica, comprobar que puede tomar valores distintos en un caso controlado.
- Estado: resuelto

### ERR-023 – La métrica de falsa alarma mezcla avisos tempranos con alarmas reales
- Fecha: 2026-11-08
- Fase/archivo: Fase 4, `src/metaltech/models/evaluate.py`, etiquetas de D-049
- Origen: datos
- Síntoma: `falsa_alarma` da 5.74 % en test (modelos elegidos), pero el 99.1 % de esas 4379 alarmas ocurre con una degradación en curso y en el 98.8 % de ellas el modo es el correcto. En equipo sano la tasa es 0.11 % (39 de 35 494 ventanas).
- Causa raíz: las ventanas de degradación a más de H = 24 h de la falla se etiquetan `normal`. Un aviso correcto y temprano cuenta como falsa alarma y baja la precisión y el F1.
- Solución: ventanas grises fuera de entrenamiento y puntuación, falsa alarma solo con equipo sano y métricas aparte de aviso temprano (D-054). El F1 macro medio en test pasa de 0.599 a 0.919.
- Prevención: separar el estado real del equipo de la etiqueta al medir alarmas.
- Estado: resuelto

### ERR-022 – Script de cambios aplicado a medias por finales de línea
- Fecha: 2026-11-08
- Fase/archivo: Fase 3, script temporal sobre `configs/` y `decisiones.md`
- Origen: agente
- Síntoma: los YAML quedaron modificados y `decisiones.md` no; además, la descripción del síntoma `tiempo_ciclo_en_rango` se copió de otro.
- Causa raíz: un patrón con `$` no coincide antes de `\r\n` en archivos de Windows y el script escribía archivo por archivo sin validar antes. La descripción se copió de la plantilla sin adaptarla.
- Solución: se relanzó solo la parte pendiente, se corrigió el patrón y la descripción.
- Prevención: en scripts de edición, validar todo antes de escribir, y no usar `$` en multilínea con archivos CRLF.
- Estado: resuelto

### ERR-021 – Cifra de anticipación calculada con interpolación lineal
- Fecha: 2026-11-08
- Fase/archivo: Fase 3, cálculo temporal fuera del repositorio
- Origen: agente
- Síntoma: se informó que 7 de 41 firmas se detectaban tarde; con las formas y retardos reales son 16 de 30 casos evaluables con menos de 24 h de anticipación mínima.
- Causa raíz: el cálculo interpoló todo de forma lineal e ignoró `forma` y `retardo_frac`.
- Solución: se recalculó con las formas reales y se corrigió MEMORIA; `data/calibracion.py` mide ahora sobre las series generadas.
- Prevención: medir sobre el simulador real antes de dar cifras.
- Estado: resuelto

### ERR-020 – La calibración muestra un simulador demasiado fácil para las reglas
- Fecha: 2026-11-08
- Fase/archivo: Fase 3, `configs/failure_modes.yaml`, `src/metaltech/data/generator.py`
- Origen: datos
- Síntoma: M0 detecta el 100 % de las fallas de predicción y da 0 % de alarmas en operación sana sin confusores. Además, `valvula_hidraulica_pegada` cruza a otro modo en 14 de 14 episodios.
- Causa raíz: las firmas se ajustaron para alcanzar los umbrales de las reglas (D-042) y la señal sana se recorta al rango nominal. En la válvula, entre pulsos la presión vuelve al rango y solo queda la evidencia de contaminación.
- Solución: firmas incompletas, severidad variable, deriva, excursiones y señal sana sin recorte (D-052); válvula con ciclo sostenido y R27 con `tiempo_ciclo_en_rango`. M0 baja a 82 % (predicción) y 77 % (detección); los cruces de la válvula, de 14 a 3 de 14.
- Prevención: no presentar el recall de M0 sobre datos sintéticos como desempeño real; calibrar la dificultad con la física y datos públicos, nunca con el resultado de M3 (D-050).
- Estado: resuelto

### ERR-019 – Pruebas nuevas de trayectoria mal planteadas
- Fecha: 2026-11-08
- Fase/archivo: Fase 2, `tests/test_rules_engine.py`
- Origen: agente
- Síntoma: primero `KeyError: 'nivel'` al recolectar las pruebas; después, 9 fallos con `concluyó []` en t = 0.85–0.95.
- Causa raíz: se asumió que todo síntoma tiene `nivel` (los percibidos no) y que el modo correcto ya debía ser el principal en el tramo final, cuando D-045 solo descarta cruces hacia otro modo. Varias reglas se disparan recién al llegar a su umbral.
- Solución: uso de `.get("nivel")`; la prueba pasa a afirmar que, si hay conclusión, es el modo correcto.
- Prevención: leer la decisión que la prueba protege y distinguir "sin conclusión" de "conclusión equivocada".
- Estado: resuelto

### ERR-018 – El Revisor trabajó un tiempo sobre una copia desactualizada
- Fecha: 2026-11-05
- Fase/archivo: revisión cruzada, `knowledge/` y `configs/`
- Origen: agente
- Síntoma: el verificador contó 48 reglas, 31 modos y 44 decisiones, cuando la lectura inicial mostraba 40, 30 y 40.
- Causa raíz: los commits b60c27d y 33594a5 llegaron por pull después de la lectura inicial, y el Revisor no comprobó el estado del repositorio durante la tarea.
- Solución: no se había editado nada. Se releyó el diff completo, se revisaron R41–R48 en lugar de rehacerlas y la numeración siguió desde D-045 y ERR-014.
- Prevención: comprobar `git log -1` y `git status` justo antes de la primera edición. Las ediciones se aplicaron con reemplazos exactos que fallan si el texto cambió.
- Estado: resuelto

### ERR-017 – Reglas que chocaban sin que nada las distinguiera
- Fecha: 2026-11-05
- Fase/archivo: Fases 1 y 2, `knowledge/rules/rules.yaml`, D-043
- Origen: conocimiento
- Síntoma: R02 pedía relubricar mientras R04 lo desaconsejaba; R03 se sumaba a R04 como evidencia independiente (0.975); `falla_valvula_admision` y `valvula_hidraulica_pegada` salían diagnosticadas como otra falla, y R40 empataba con R45.
- Causa raíz: la validación solo pedía que el modo correcto apareciera entre las conclusiones. D-043 llamó "ambigüedades reales" a casos que los datos medidos sí separaban.
- Solución: D-045: cuatro síntomas `en_rango` y una premisa en R01, R02, R03, R22, R27 y R40. El modo correcto es el principal en 41 de 41 firmas.
- Prevención: agregar a `tests/test_conocimiento.py` el modo principal por firma y la trayectoria de degradación, no solo el valor final.
- Estado: resuelto en los YAML; la prueba sigue pendiente (rol QA)

### ERR-016 – Crítico del bus DC por encima del disparo real del variador
- Fecha: 2026-11-05
- Fase/archivo: Fase 1, `configs/assets.yaml` (`tension_bus_dc_pct`), D-030
- Origen: conocimiento
- Síntoma: el crítico era 130 %, pero un variador de clase 480 V dispara cerca de 820 VDC, ≈ 127 % de un bus de 648 V.
- Causa raíz: valor puesto sin fuente (ERR-003) y sin compararlo con el punto de disparo.
- Solución: crítico de 130 % a 125 %. Sigue con confianza baja: la fuente leída es un solo sitio.
- Prevención: contrastar cada umbral crítico con la protección real del equipo.
- Estado: resuelto (con reserva)

### ERR-015 – Norma aplicada a máquinas fuera de su alcance
- Fecha: 2026-11-05
- Fase/archivo: Fase 1, D-003 (ISO 20816-3)
- Origen: conocimiento
- Síntoma: D-003 tenía confianza alta para bomba y compresor, pero la norma excluye los compresores de tornillo y no lista las bombas.
- Causa raíz: la Fase 1 tomó las zonas de blogs sin leer el alcance de la norma, que sí está publicado en fichas de organismos nacionales.
- Solución: valores iguales, declarados como proxy en bomba, compresor, prensa y CNC; confianza media en motor y banda y baja en el resto. Además, ISO 20816-3:2026 reemplazó a la edición de 2022.
- Prevención: leer el alcance antes de usar una norma. Conseguir ISO 10816-7 e ISO 20816-3:2026.
- Estado: abierto (faltan esas dos normas)

### ERR-014 – Citas que no dicen lo que se les atribuía
- Fecha: 2026-11-05
- Fase/archivo: Fase 1 y D-041, `knowledge/acquisition/decisiones.md`
- Origen: conocimiento
- Síntoma: al abrir las fuentes, varias no sostenían el dato citado:
  - Air Compressor Services y Atlas Copco no dan los valores de D-016, y el rango "77–93 °C" no se pudo confirmar;
  - la patente de D-013 es de Yokogawa, no de Ebara;
  - Inspenet solo dice "> 1 kHz", no "1–20 kHz";
  - la hoja Parker es de una válvula VMY, no D1FB/D3FB;
  - Machinery Lubrication no menciona calor (D-022);
  - la regla del 50 % de D-041 no está en Fluke ni en Acoem;
  - HI no da "1.3 para mayor energía" ni "2 a más de 4" (D-012).
- Causa raíz: se citó a partir de extractos del buscador o de la memoria, sin comprobar el texto.
- Solución: fuentes reemplazadas o texto corregido en cada D-NNN; la hoja de hallazgos está en `revision.md`. Ningún umbral cambió por esta causa.
- Prevención: una fuente se marca como leída solo si se abrió y se halló el dato. Las que no se pudieron abrir quedan declaradas.
- Estado: resuelto

### ERR-013 – owlready2 no carga ontologías por URI `file:///` con espacios (Windows)
- Fecha: 2026-11-05
- Fase/archivo: Fase 2, `src/metaltech/kb/ontology.py` (`Ontologia.cargar`)
- Origen: entorno
- Síntoma: `OSError: [Errno 22] Invalid argument: '/C:/Users/.../Ing Conocimiento/.../metaltech.owl'` al hacer `get_ontology(ruta.as_uri()).load()`.
- Causa raíz: owlready2 convierte el URI en una ruta con barra inicial inválida en Windows, y la ruta del proyecto tiene espacios.
- Solución: se abre el archivo y se pasa como `load(fileobj=f)` con el IRI fijo de la ontología.
- Prevención: el test `test_guardar_y_cargar_conserva_todo` cubre el ida y vuelta con una ruta temporal; no usar `as_uri()` con owlready2.
- Estado: resuelto

### ERR-012 – HTTP 403 al descargar el JDK con `urllib`
- Fecha: 2026-11-05
- Fase/archivo: Fase 2, `scripts/instalar_jdk.py`
- Origen: entorno
- Síntoma: `urllib.error.HTTPError: HTTP Error 403: Forbidden` al consultar la API de Adoptium; `curl` sí funcionaba.
- Causa raíz: el servidor rechaza el User-Agent por defecto de `urllib` (`Python-urllib/3.x`).
- Solución: el script envía `User-Agent: metaltech-setup/1.0`, reutiliza un zip ya descargado si su SHA-256 coincide y verifica el hash antes de extraer.
- Prevención: usar un User-Agent propio en toda descarga programática; no enviar datos del usuario en él.
- Estado: resuelto

### ERR-011 – HermiT declaró inconsistente la primera versión de la ontología
- Fecha: 2026-11-05
- Fase/archivo: Fase 2, `src/metaltech/kb/ontology.py` (propiedad `umbral`)
- Origen: código
- Síntoma: `OwlReadyInconsistentOntologyError` al ejecutar `python -m metaltech.kb.ontology --hermit`, con `validar_estructura()` en verde.
- Causa raíz: `umbral` se declaró funcional y `umbralAlerta`, `umbralCritico` y `umbralAlertaBaja` como subpropiedades. Una variable con alerta 130 y crítico 155 tenía entonces dos valores de una propiedad funcional.
- Solución: `umbral` pasa a no funcional; las tres subpropiedades siguen siendo funcionales.
- Prevención: `tests/test_ontology.py` incluye `test_hermit_ontologia_consistente` y dos pruebas negativas (individuo en clases disjuntas y propiedad funcional con dos valores). No declarar funcional una superpropiedad con varias subpropiedades.
- Estado: resuelto

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
- Solución: `scripts/instalar_jdk.py` descarga Eclipse Temurin 17 en `.tools/jdk17` (ignorado por git, SHA-256 verificado, sin modificar el sistema) y `buscar_java()` lo usa si no hay Java en el PATH. Las pruebas marcadas `@pytest.mark.java` se omiten si no hay ninguno (`tests/conftest.py`). Solo Windows x64; en otro SO, instalar un JDK 17 y ponerlo en el PATH.
- Prevención: documentado en README; la validación estructural de la ontología no depende de Java.
- Estado: resuelto (2026-11-05)

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
- Actualización 2026-11-05 (Revisor): verificados en Crossref, DataCite y Open Library. Matzka (2020): 10.1109/AI4I49448.2020.00023. Dyer y Stewart (1978): 10.1115/1.3453905. PMC12251610: Lai et al. (2025), *Sensors, 25*(13), 3880. También se confirmaron IEEE MRWG (1985), Randall (2011) y los demás libros citados de memoria, cuyo contenido sigue sin leerse.
- Estado: resuelto

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
- Actualización 2026-11-05 (Revisor): se buscó segunda fuente para todos.
  - Con fuente leída: 2×/4× y curtosis de 4 (D-010), orden de magnitud y crítico de la fuga (D-015, ahora 3/9 ml/h) y crítico del separador (D-018).
  - Corregidos, con una sola fuente: alerta del separador, ahora 0.55 bar (D-018), y crítico del bus DC, ahora 125 % (D-030).
  - Sin fuente, siguen como supuesto: D-013 (coeficiente de variación), D-022, D-023, D-024, D-025, D-028, D-029, el disipador y el conteo de disparos (D-030), la curtosis de 6 y las magnitudes de D-041 y D-042.
- Estado: abierto (se reduce a los supuestos listados, que van a *Limitaciones*)

### ERR-002 – PDF técnico no legible (TECO-Westinghouse)
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, D-008
- Origen: entorno
- Síntoma: WebFetch devolvió el PDF de ajustes RTD como binario, con la tabla en imágenes, sin texto extraíble.
- Causa raíz: PDF generado desde Excel con contenido en imágenes JPEG.
- Solución: se usaron los valores del extracto del buscador (alarma 90–110 °C y disparo 95–120 °C para rodamientos antifricción), contrastados con un manual Siemens. La referencia queda marcada.
- Prevención: si hace falta, leer el PDF con OCR (skill de PDF) o buscar otra fuente.
- Actualización 2026-11-05 (Revisor): el diagnóstico era incorrecto: las imágenes son solo logos y la tabla es texto. `pdftotext` la extrae sin OCR. Confirma admisible 80–90 °C, alarma 90–110 °C y disparo 95–120 °C. Cuando WebFetch falle con un PDF, hay que descargarlo y extraer el texto antes de declararlo ilegible.
- Estado: resuelto

### ERR-001 – Normas de pago sin acceso al texto oficial
- Fecha: 2026-10-29
- Fase/archivo: Fase 1, `knowledge/acquisition/decisiones.md`
- Origen: conocimiento
- Síntoma: no se pudo leer el texto de ISO 20816-1/-3, ISO 17359, ISO 13374, IEC 60034-1, IEC 60085, NEMA MG-1, ANSI/HI 9.6.1 (salvo la copia de law.resource.org, que no se abrió), IEEE 519, ISO 4406, IEC 60812 ni AIAG-VDA.
- Causa raíz: son normas de pago.
- Solución: los valores se tomaron de fuentes secundarias que las citan (Fabrico, Oxmaint, ALL-TEST Pro, Pumps & Systems, entre otras) o del conocimiento previo del agente. Cada caso queda declarado en la D-NNN. El criterio del 25 % de ISO 20816-1 (D-004) y el límite de THD de IEEE 519 vienen de memoria.
- Prevención: verificar contra el texto oficial si la universidad tiene acceso (biblioteca o ICONTEC); priorizar D-003, D-004, D-012 y D-030.
- Actualización 2026-11-05 (Revisor):
  - D-012: ANSI/HI 9.6.1-2017 **leída** en law.resource.org.
  - D-003: alcance leído en la ficha de INN; las zonas siguen vistas por citas (ERR-015).
  - D-004: 25 % confirmado en dos fuentes secundarias; la muestra pública de ISO 20816-1 acaba antes de la cláusula 6.3.3.
  - D-030: tabla de IEEE 519 confirmada en una fuente secundaria leída.
- Estado: abierto (solo se leyó una norma; las demás siguen vistas por citas)
