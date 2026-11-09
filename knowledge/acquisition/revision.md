# Revisión cruzada de la base de conocimiento – Metal Tech

> **Agente:** Revisor de conocimiento · **Fecha:** 2026-11-05 · **Versión revisada:** commit 33594a5 (48 reglas, 31 modos, 41 filas FMEA, D-001 a D-044).
> **Método:** apertura de las fuentes citadas (web y PDF), consulta de Crossref, Open Library y DataCite, y verificación automática de coherencia y de trayectorias de degradación con un script temporal.
> Decisiones: [decisiones.md](decisiones.md). Errores: [ERRORES.md](../../docs/agentes/ERRORES.md).

## Veredicto

**La base es apta para seguir con la Fase 3, con condiciones.** La Fase 2 ya existe y no hay que rehacerla, pero el repositorio queda desincronizado hasta completar la condición 1.

1. **Bloqueante, y solo de sincronización:** regenerar `knowledge/ontology/metaltech.owl` y ajustar tres clases de pruebas (ver [Acciones pendientes](#acciones-pendientes-para-otros-roles)).
2. **No bloqueante:** los umbrales que siguen como supuesto se declaran en *Limitaciones* y entran en un análisis de sensibilidad de M0.
3. **No bloqueante:** antes de citar D-003 en el documento final, revisar ISO 20816-3:2026 y conseguir ISO 10816-7 para la bomba.

La estructura lógica quedó sólida: todas las reglas se pueden disparar y el modo correcto es el principal en 41 de 41 firmas. El respaldo documental es desigual: motor y bomba tienen buena base; prensa, banda y CNC dependen de supuestos numéricos.

## Conteos

| Elemento | Antes | Después |
|---|---|---|
| Decisiones | 44 | 48 |
| Reglas | 48 | 55 |
| Síntomas | 63 | 67 |
| Modos de falla | 31 | 31 |
| Filas FMEA | 41 | 41 |
| Expresiones | 10 | 10 |
| Datasets de referencia | 6 | 7 |
| Modo correcto principal en firmas finales | 38 de 41 (más un empate resuelto por orden: 39 en D-043) | 41 de 41 |

`fmea.yaml` y `fmea.md` no cambiaron, así que siguen sincronizados.

## Hallazgos

Severidad: **alta** = valor o conclusión incorrectos; **media** = respaldo o lógica débiles; **baja** = forma.

### Decisiones críticas

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-01 | D-003 | ISO 20816-3 excluye los compresores de tornillo y no lista las bombas, pero la confianza era alta en ambos | alta | Valores iguales. Confianza: media en motor y banda; baja, como proxy, en bomba, compresor, prensa y CNC | Alcance en la ficha de INN; ERR-015 |
| H-02 | D-003 | La edición de 2022 fue reemplazada por ISO 20816-3:2026 | media | Registrado; no revisada | Catálogo de SFS |
| H-03 | D-004 | El 25 % venía de memoria | media | Confirmado en dos fuentes leídas. Valor igual, confianza media | Fabrico; Vibromera |
| H-04 | D-012 | Atribución imprecisa de HI; "2 a más de 4" no estaba en HI | media | Se leyó el texto. 1.3/1.1 se mantienen con nueva justificación | ANSI/HI 9.6.1-2017, tablas 9.6.1.5.x |
| H-05 | D-030 | Crítico de bus DC en 130 %, por encima del disparo real (≈ 127 %) | alta | 130 → 125 % | Flexa Systems; ERR-016 |
| H-06 | D-030 | THD de 8 % puesto de memoria; 12 % sin base | media | 8 % confirmado; 12 % = 1.5 × 8 %. Confianza de THD: media, no alta | PowerMonitors |

### Citas de la muestra (14 decisiones)

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-07 | D-016 | Las fuentes citadas no dan el rango "77–93 °C" ni un paro | alta | Fuentes reemplazadas; rango retirado; 100/110 °C se sostienen | Fabrico; Unitec-D; ERR-014 |
| H-08 | D-013 | Patente atribuida a Ebara: es de Yokogawa | media | Corregido y citado por inventores | Ogawa et al. (2022) |
| H-09 | D-013 | Inspenet no dice "1–20 kHz", solo "> 1 kHz" | media | Nueva fuente para la banda | Al-Hashmi et al. (2017) |
| H-10 | D-020, D-021 | La hoja Parker es de una válvula reductora VMY, no de D1FB/D3FB | media | Título y texto corregidos; 60/70 °C y 18/16/13 sí están | Hoja de datos |
| H-11 | D-022 | Machinery Lubrication no menciona calor | media | Calor atribuido solo a FridayParts | Las tres fuentes leídas |
| H-12 | D-041 | La regla del 50 % de 2X/3X no está en Fluke ni en Acoem | media | Declarada como sin fuente abierta | Fluke; Acoem |
| H-13 | D-009 | Nota de GIW con 93/115 °C en conflicto, sin registrar | baja | Conflicto registrado; 82/88 °C se mantienen | Extracto del buscador |
| H-14 | D-008 | ERR-002 afirmaba que el PDF era solo imagen | baja | Se leyó el PDF; valores confirmados | TECO-Westinghouse (2008) |

Decisiones de la muestra sin errores: D-005 y D-006 (ALL-TEST Pro, Evans), D-011 en lo cualitativo (Fluke), D-019 (Compressed Air Challenge, Anglian) y D-027 (ficha UCI). D-028 se sostiene con Lai et al. (2025).

### Supuestos de ERR-003

| Decisión | Valor | Resultado | Confianza |
|---|---|---|---|
| D-010 | Factores 2×/4× | **Segunda fuente hallada** (Filippenko et al., 2002; Vibromera, 2025) | baja → media |
| D-010 | Curtosis de 4 | Segunda fuente hallada (Zhou et al., 2023). El crítico de 6 no tiene fuente | media; 6 en baja |
| D-013 | Coeficiente de variación 5/10 % | Sin segunda fuente | baja |
| D-015 | Fuga 5/20 ml/h | **Valores corregidos a 3/9 ml/h** | baja → media; alerta en baja |
| D-018 | Diferencial 0.7/1.0 bar | **Alerta corregida a 0.55 bar**; el crítico tiene fuente | crítico baja → media; alerta en baja |
| D-022 | bar/min y nivel de tanque | Sin fuente: dependen del fabricante | baja |
| D-023 | "La prensa está dura" | Carroll (2013) sostiene el carrete pegado, no la expresión ni la presión alta | baja |
| D-024 | Desvío 25/50 mm | Sin fuente: los interruptores actúan por ángulo | baja |
| D-025 | Deslizamiento 2/5 % | Solo un interruptor al 20 %, lejos del valor | baja |
| D-028 | Impacto 5/10 g | Sin fuente: se ajusta por máquina | baja |
| D-029 | Husillo 50/60 °C y coeficiente de 10 % | Sin fuente | baja |
| D-030 | Bus DC | **Crítico corregido**; una fuente (dos páginas del mismo sitio) | baja |
| D-030 | Disipador y conteo de disparos | Disipador conservador frente a 85–95 °C; conteo sin fuente | baja |

### Cobertura hecha por el equipo (R41–R48, D-041, D-042)

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-15 | R41–R48 | Revisadas: premisas, FC ≤ 0.70 y disparo correctos. R45 empataba con R40 | media | R40 corregida (H-19) | Verificador |
| H-16 | `failure_modes.yaml` | Las 10 firmas de D-042 cruzan sus umbrales. Dos aumentos de corriente son grandes para su mecanismo | baja | Aceptadas como calibración; revisar en Fase 3 | D-042 |
| H-17 | D-041 | Decisión de agregar `holgura_mecanica` correcta; banda y CNC excluidos con motivo | – | Aceptada | Fluke; Acoem |

### Revisión lógica

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-18 | R02, R04 | **Contradicción:** en etapa 4, R02 pide relubricar y R04 dice no relubricar | alta | R02 exige curtosis en rango | D-045 |
| H-19 | R40, R45 | R40 incluida en R45 | media | R40 exige curtosis en rango | D-045 |
| H-20 | R03, R04 | R03 incluida en R04; evidencia sumada como independiente (0.975) | alta | R03 exige temperatura en rango; ahora 0.85 | D-045 |
| H-21 | R22, R23 | Válvula de admisión diagnosticada como fuga de red. D-043 lo daba por ambigüedad real | alta | R22 exige corriente en rango | D-045 |
| H-22 | R27, R28 | Válvula pegada diagnosticada como contaminación. D-043 lo daba por ambigüedad real | alta | R27 exige presión en rango | D-045 |
| H-23 | R01 | Ventilación se disparaba con contactor y aislamiento | media | R01 exige desbalance en rango | D-045 |
| H-24 | R07, R09 | R07 incluida en R09 | baja | Aceptado: diagnóstico diferencial | D-045 |
| H-25 | R10/R11, R13/R14 | Comparten evidencia; MYCIN sobrestima algo | baja | Aceptado; limitación | D-045 |
| H-26 | 11 reglas | FC por encima de la política de D-034 | media | Bajados, sin subir ninguno | D-046 |
| H-27 | Catálogo | 14 síntomas sin regla | media | 7 con reglas R49–R55; 7 con campo `uso` | D-047 |
| H-28 | `cavitacion` | Relación NPSH de 1.0 con caída de altura del 12 %, contra la definición de NPSH3 | media | Firma 1.0 → 0.9 | HI, sección 9.6.1.2 |
| H-29 | EXP08 | Declaraba bomba y banda, sin variables de variador | baja | Solo motor | D-002 |
| H-30 | `assets.yaml` | Revisados orden alerta/crítico y rango nominal: sin defectos | – | Ninguna | Verificador |
| H-31 | D-034 | Sin reglas percibidas por encima de 0.80 | – | Ninguna | Verificador |
| H-32 | Fase 3 | Rotura y colisión ocurren en segundos y el muestreo es de 10 min | media | Pendiente: el generador debe usar el máximo de la ventana | Lai et al. (2025) |

### D-043 y D-044

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-33 | D-043 | Fusificación, datos faltantes y traza correctos. Declaraba ambigüedad real donde había solución | media | Nota de revisión y cifras actualizadas | D-045 |
| H-34 | D-043 | El motor no aplica el corte de 0.2 de MYCIN | baja | Aceptado: es pragmático, no central | Buchanan y Shortliffe (1984, cap. 10) |
| H-35 | D-044 | Diseño coherente; referencias existentes | – | Aceptada; regenerar el `.owl` | Crossref |

### Dataset y referencias

| ID | Archivo | Problema | Severidad | Acción | Evidencia |
|---|---|---|---|---|---|
| H-36 | `datasets_referencia.md` | Dataset UCI hidráulico sin evaluar | media | Agregado con limitaciones; sirve en parte | Ficha UCI; D-048 |
| H-37 | Referencias | DOIs y autores pendientes (ERR-005) | media | Todos resueltos | Crossref, DataCite, Open Library |
| H-38 | Referencias | Siglas en lugar de nombre de autor; letras a, b… fuera de orden; lista sin ordenar según APA | baja | Corregido y reordenado; citas actualizadas | APA 7 |

Referencias confirmadas:

| Referencia | Resultado |
|---|---|
| Matzka (2020) | DOI 10.1109/AI4I49448.2020.00023 |
| Dyer y Stewart (1978) | DOI 10.1115/1.3453905 |
| PMC12251610 | Lai et al. (2025), *Sensors, 25*(13), 3880, DOI 10.3390/s25133880 |
| IEEE MRWG (1985) | DOI 10.1109/TIA.1985.349532 |
| Randall (2011) | DOI 10.1002/9780470977668 |
| Piotrowski, Karassik, Brennen, Bloch y Budris, Altintas, DOE (2003) | Existencia, año y editorial en Open Library o Crossref; contenido no leído |
| AIAG-VDA (2019) | 1.ª edición confirmada por fuentes secundarias |

## Confianzas modificadas

| Decisión | Antes | Después |
|---|---|---|
| D-003 | alta | media (motor, banda); baja (bomba, compresor, prensa, CNC) |
| D-010, factores 2×/4× | baja | media |
| D-015 | baja | media (orden de magnitud y crítico); baja (alerta) |
| D-018, crítico | baja | media |
| D-030, THD | alta en el texto | media |

Ninguna subió sin una fuente leída.

## Lo que no se pudo verificar

- **Sin abrir:** Acoem (s. f.-a), Edmac, Siemens, Malloy, KSB GIW, Pumps & Systems (2012), los manuales Sullair, Gardner Denver EDF-KB y Yaskawa, y la ficha FineTek. Lo que depende de ellos está marcado en cada D-NNN.
- **Texto oficial sin leer:** todas las normas salvo ANSI/HI 9.6.1. La muestra pública de ISO 20816-1 termina antes de la cláusula 6.3.3.
- **ISO 10816-7:** sin valores, de modo que la bomba sigue con proxy.
- **Libros:** se confirmó que existen, no lo que dicen.

## Acciones pendientes para otros roles

| Rol | Acción |
|---|---|
| Datos/ML | Regenerar `knowledge/ontology/metaltech.owl` con `kb/ontology.py` |
| QA | `tests/test_ontology.py`: actualizar 48 → 55 reglas y 63 → 67 síntomas, incluida la comprobación de `generar()` |
| QA | `tests/test_rules_engine.py::test_rodamiento_del_motor_combina_r03_y_r04`: R03 y R04 ya no se combinan; el valor esperado pasa de 0.975 a 0.85 y conviene renombrar la prueba |
| QA | Agregar a `tests/test_conocimiento.py` la comprobación de `en_rango` y la de trayectorias, que hoy no cubre |
| Datos/ML | Fase 3: usar el máximo de la ventana en eventos de segundos (H-32) y revisar las firmas de D-042 |
| Documentación | Declarar en *Limitaciones* los supuestos de la tabla de ERR-003; retirar las marcas entre corchetes de las referencias |
| Equipo | Conseguir por la biblioteca ISO 20816-3:2026, ISO 10816-7 e IEEE 519 |
