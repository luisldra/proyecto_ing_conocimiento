# Registro de decisiones de conocimiento (ADR) – Metal Tech

> **Autor:** agente Investigador, Fase 1 · **Fecha:** 2026-10-29 (D-041 y D-042: 2026-11-05) · **Estado:** revisado por el agente Revisor de conocimiento (2026-11-05); hallazgos en [revision.md](revision.md).
> **Técnica:** revisión documental asistida por agente (búsqueda web y lectura de fuentes). No hubo entrevistas ni participación de personas.
> **Archivos que dependen de este registro:** [`configs/assets.yaml`](../../configs/assets.yaml), [`configs/failure_modes.yaml`](../../configs/failure_modes.yaml), [`knowledge/rules/rules.yaml`](../rules/rules.yaml), [`knowledge/lexicon/expresiones.yaml`](../lexicon/expresiones.yaml), [`fmea.yaml`](fmea.yaml) / [`fmea.md`](fmea.md), [`matriz_adquisicion.md`](matriz_adquisicion.md), [`datasets_referencia.md`](datasets_referencia.md).

## Reglas de decisión aplicadas

1. Cada umbral y cada regla tiene respaldo de **≥ 2 fuentes o 1 norma**. Cuando no se alcanza, la decisión se marca con confianza **baja** y queda como supuesto explícito.
2. Si las fuentes no coinciden, se elige el valor **más conservador**, es decir, el que alerta antes, y el conflicto se registra en la decisión.
3. Las normas ISO, IEC, NEMA, HI e IEEE son de pago. Sus valores se tomaron de **fuentes secundarias que las citan**, y así se indica en cada caso. Se recomienda verificar contra el texto oficial si la universidad tiene acceso. La excepción es ANSI/HI 9.6.1-2017, que el Revisor leyó en la copia pública de law.resource.org.
4. **Confianza:**
   - **alta:** norma, o ≥ 2 fuentes independientes concordantes, más física clara.
   - **media:** fuentes secundarias concordantes, o una norma solo vista por citas.
   - **baja:** valor heurístico o supuesto del agente con una sola fuente o ninguna verificable.

## Índice

| ID | Tema | Confianza |
|---|---|---|
| D-001 | Marco de monitoreo de condición (ISO 17359 / ISO 13374) | alta |
| D-002 | Alcance de activos | media |
| D-003 | Zonas de severidad de vibración (ISO 20816-3) | media (motor, banda) / baja (proxy en bomba, compresor, prensa y CNC) |
| D-004 | Criterio de cambio de vibración (tendencia) | media |
| D-005 | Clases térmicas y temperatura de devanado | alta |
| D-006 | Desbalance de tensión/corriente | media |
| D-007 | Umbrales de corriente y factor de servicio | media |
| D-008 | Temperatura de rodamientos de motor | media |
| D-009 | Temperatura de rodamientos de bomba y tambor | media |
| D-010 | Indicadores de defecto de rodamiento (curtosis, alta frecuencia, etapas) | media |
| D-011 | Firmas espectrales de desbalanceo y desalineación | media |
| D-012 | Margen de NPSH | alta |
| D-013 | Firma de cavitación | alta |
| D-014 | Firma de obstrucción de bomba | media |
| D-015 | Desgaste de sello mecánico | media (orden de magnitud y crítico) / baja (alerta) |
| D-016 | Temperatura de descarga del compresor de tornillo | media |
| D-017 | Pérdida de presión en compresor de tornillo | media |
| D-018 | Diferencial del separador de aceite | baja |
| D-019 | Fugas de la red de aire y tiempo en carga | media |
| D-020 | Temperatura del aceite hidráulico | media |
| D-021 | Limpieza del aceite hidráulico (ISO 4406) | media |
| D-022 | Fugas externas e internas en la prensa | media |
| D-023 | Interpretación de "la prensa está dura" | baja |
| D-024 | Corrimiento de banda | media |
| D-025 | Deslizamiento y rotura de banda | baja |
| D-026 | Falla de rodillos | media |
| D-027 | Desgaste de herramienta CNC | media |
| D-028 | Rotura de herramienta y colisión | media |
| D-029 | Chatter y sobrecalentamiento de husillo | baja |
| D-030 | Fallas de variador | media (THD) / baja (resto) |
| D-031 | Fallas de contactor | media |
| D-032 | Degradación de aislamiento ("huele a quemado") | media |
| D-033 | Ventilación obstruida vs. lubricación deficiente | media |
| D-034 | Factores de certeza (MYCIN) | alta (método) / media (valores) |
| D-035 | Escalas FMEA | media |
| D-036 | Datasets públicos para calibrar el simulador | media |
| D-037 | Formas de degradación y eventos confusores | media |
| D-038 | Método de formalización del léxico | media |
| D-039 | Rol de la base de conocimiento en la explicabilidad | media |
| D-040 | Variables relativas (`_pct`, `_rel`) en lugar de absolutas | media |
| D-041 | Holgura mecánica (modo nuevo) | media |
| D-042 | Cierre de huecos: cobertura de reglas, variables y firmas coherentes | media |
| D-043 | Semántica del motor de reglas (fusificación, FC y traza) | alta (método) / media (umbrales de rampa) |
| D-044 | Diseño de la ontología OWL y validación con HermiT | alta |
| D-045 | Discriminadores `en_rango` en reglas que chocaban | media |
| D-046 | Ajuste de los FC a la política de D-034 | media |
| D-047 | Reglas para síntomas sin uso y campo `uso` del catálogo | media |
| D-048 | Dataset UCI de sistemas hidráulicos para la prensa | media |
| D-049 | Tarea de predicción o detección por modo de falla | media |
| D-050 | Supuestos y límites del simulador | baja en valores, media en estructura |
| D-051 | Umbrales de vibración para bombas (ISO 10816-7 vía Europump) | media |
| D-052 | Dificultad del simulador calibrada con datos públicos | media |
| D-053 | Ventanas y entrenamiento de los modelos | media |
| D-054 | Ventanas grises y métricas de aviso temprano | media |
| D-055 | Confusores multivariable, más unidades y ajustes con datos públicos | media en estructura, baja en parámetros |
| D-056 | Integración del conocimiento: M0, M2 y M3 | media |

---

## D-001 – Marco de monitoreo de condición (ISO 17359 / ISO 13374)
- **Contexto:** se necesita un marco reconocido que ordene el sistema: qué se mide, cómo se detecta, cómo se diagnostica y qué se recomienda.
- **Decisión:**
  - **ISO 17359:2018** da el procedimiento general del programa de monitoreo: selección de equipos y modos de falla, selección de mediciones, alarmas, diagnóstico y realimentación.
  - **ISO 13374** (arquitectura OSA-CBM de MIMOSA) da los bloques funcionales, que se mapean así:
    - Adquisición y manipulación de datos → `generator.py`, `features.py`.
    - Detección de estado → umbrales de `assets.yaml`, que generan síntomas.
    - Evaluación de salud → reglas con FC y modelo DL.
    - Pronóstico → horizonte H y RUL opcional.
    - Generación de recomendaciones → acciones de la ontología.
  - La FMEA es el puente que ISO 17359 pide entre modos de falla y mediciones.
- **Alternativas:** usar solo CRISP-DM, que no cubre la parte de conocimiento experto; usar un marco propio sin norma.
- **Conflicto registrado:** las fuentes secundarias no coinciden en el número de bloques de OSA-CBM: seis, siete (con presentación) u ocho. Se adoptan los **seis bloques funcionales** más una capa de presentación, que es la web.
- **Fuentes:** ISO (2018); ISO (2003); Ran et al. (2019); Jardine et al. (2006).
- **Confianza:** alta.

## D-002 – Alcance de activos
- **Contexto:** el enunciado describe una planta metalmecánica con varios tipos de equipos.
- **Decisión:**
  - Se modelan 6 tipos de activo: motor eléctrico de inducción (con su contactor y variador como componentes), bomba centrífuga, compresor de tornillo lubricado, prensa hidráulica, banda transportadora y centro CNC. Cada tipo tiene varias unidades.
  - El variador y el contactor se tratan como **componentes del motor** porque sus fallas se manifiestan en las variables del motor.
  - El **puente grúa** queda fuera y solo como nota de extensión futura: frenos, cables, ruedas y carriles. No tiene sensores comparables a los del enunciado, y su riesgo es sobre todo de seguridad, lo que exige otro marco.
- **Alternativas:** incluir el puente grúa; modelar el variador como activo independiente.
- **Fuentes:** enunciado del proyecto (PDF del curso); ISO (2018), que pide seleccionar equipos por criticidad; IEEE Motor Reliability Working Group (1985), donde rodamientos y estator dominan las fallas de motores y eso justifica centrar el motor en esos componentes.
- **Confianza:** media.

## D-003 – Zonas de severidad de vibración (ISO 20816-3)
- **Actualización:** para bombas rige D-051; ISO 20816-3 las excluye. Además, la edición 2026 reemplazó a la de 2022 y sus valores no están disponibles públicamente. Las prensas y máquinas herramienta no aparecen cubiertas ni excluidas en el alcance.
- **Contexto:** se necesitan umbrales de velocidad de vibración (mm/s RMS) para máquinas industriales de 15–300 kW.
- **Decisión:**
  - Se usa **ISO 20816-3, Grupo 2** (15–300 kW o motores con altura de eje de 160–315 mm), **soporte rígido**.
  - Los límites de zona son A/B = 1.4 mm/s, B/C = 2.8 mm/s y C/D = 4.5 mm/s:
    - nominal 0.5–1.4 (zona A);
    - **alerta = 2.8** (entrada a zona C: no apta para operación prolongada);
    - **crítico = 4.5** (zona D: riesgo de daño).
  - Se aplican los mismos valores a motor, bomba, compresor, unidad hidráulica de la prensa, motorreductor de banda y cabezal CNC.
- **Valores de las otras filas de la norma, según fuentes secundarias:**

  | Grupo y soporte | A/B (mm/s) | B/C (mm/s) | C/D (mm/s) |
  |---|---|---|---|
  | Grupo 2, flexible | 2.3 | 4.5 | 7.1 |
  | Grupo 1, rígido | 2.3 | 4.5 | 7.1 |
  | Grupo 1, flexible | 3.5 | 7.1 | 11.0 |

- **Alternativas:** soporte flexible, con umbrales más altos; ISO 10816-7 para bombas, con límites por categoría que son, según recuerda el agente, más permisivos que el Grupo 2 rígido (no verificado).
- **Conflictos:**
  1. Rígido frente a flexible: se elige rígido, que es lo más conservador.
  2. ISO 10816-7 para bombas: no se pudo verificar y se elige 20816-3 rígido por ser más conservador.
  3. El cabezal de un centro CNC no está en el alcance típico de 20816-3, que excluye máquinas herramienta. Allí el valor es un **proxy** y su confianza baja (ver D-029).
- **Fuentes:** ISO (2022), con valores vía Fabrico (s. f.-d) y Oxmaint (s. f.); ISO (2016).
- **Revisión (Revisor, 2026-11-05):** ningún umbral cambia; cambia su respaldo.
  - **Valores:** las zonas coinciden en Fabrico (s. f.-d) y Vibromera (s. f.), ambas leídas. El texto oficial sigue sin leerse.
  - **Alcance:** el resumen de la norma que publica INN (s. f.) incluye motores, compresores rotativos y transportadores, y excluye de forma expresa los "rotary positive displacement compressors (e. g. screw compressors)". Las bombas rotodinámicas no están en la lista de máquinas cubiertas, y la norma remite a ISO 10816-7 las que tienen el impulsor en el eje del motor. Por eso, en el compresor de tornillo, la bomba y la unidad hidráulica de la prensa el valor es un **proxy**, igual que en el CNC. La decisión original no lo advertía.
  - **ISO 10816-7:** sus límites para bombas tampoco se pudieron leer (Ludeca confirma el alcance y los grupos de criticidad, sin valores). El conflicto 2 sigue abierto.
  - **CNC:** MTD Media (s. f.) da umbrales de husillo de 0.1 y 0.2 in/s (≈ 2.5 y 5.1 mm/s), del mismo orden que 2.8/4.5, sin aclarar si son RMS o pico.
  - **Edición:** el catálogo de SFS (s. f.) registra ISO 20816-3:2026, publicada el 2026-10-28, que reemplaza a la de 2022. No se revisó si cambian las zonas.
- **Confianza:** media para motor y banda (norma vista por citas; antes alta); baja para bomba, compresor, prensa y CNC, por ser proxy fuera del alcance (antes alta en bomba y compresor).

## D-004 – Criterio de cambio de vibración (tendencia)
- **Contexto:** el enunciado habla de "vibración creciente". Un valor absoluto en zona B puede ocultar un deterioro rápido.
- **Decisión:**
  - Se define `vibracion_creciente` como un aumento respecto a la línea base sana de la unidad **≥ 25 % del límite B/C** (0.25 × 2.8 = 0.7 mm/s).
  - Corresponde al "criterio II" (cambio de magnitud) de la serie ISO 10816/20816, que considera significativo un cambio del 25 % del valor del límite B/C aunque no se cambie de zona.
- **Alternativas:** pendiente lineal mínima por semana; doble de la línea base, que es la práctica común de software de monitoreo.
- **Fuentes:** ISO (2016), parte 1, cláusula 6.3.3, cuyo título confirma la muestra pública de la norma; el texto de la cláusula no está en la muestra. Revisión 2026-11-05: el 25 % ya no depende de la memoria del agente, porque Fabrico (s. f.-d) y Vibromera (s. f.), leídas, dan el mismo criterio y Fabrico el mismo ejemplo de 0.7 mm/s. El criterio vale para cambios hacia arriba y hacia abajo; el síntoma solo modela el aumento. Randall (2011) respalda el uso de tendencias respecto a la línea base.
- **Confianza:** media.

## D-005 – Clases térmicas y temperatura de devanado
- **Contexto:** sobrecalentamiento de motores y la expresión "huele a quemado".
- **Decisión:**
  - Motor con **aislamiento clase F (155 °C)** y calentamiento de clase B, que es la práctica habitual de diseño.
  - Temperatura de devanado: nominal 60–110 °C, **alerta 130 °C** (límite de la clase B, sin reserva térmica) y **crítico 155 °C** (límite de la clase F).
  - Se adopta la regla de Montsinger: la vida del aislamiento se reduce a la mitad por cada ~10 °C de exceso. Por eso el umbral de alerta está en la clase inferior.
- **Alternativas:** alerta en 140 °C y disparo en 155 °C, que es un ajuste típico de RTD para clase F. Se descarta por menos conservador.
- **Fuentes:** IEC (2022); IEC (2007); NEMA (2021). Los valores 130/155 °C y la regla de los 10 °C aparecen en ALL-TEST Pro (s. f.) y en Evans (s. f.). Bonnett y Soukup (1992) cubren el mecanismo de falla del estator.
- **Confianza:** alta.

## D-006 – Desbalance de tensión/corriente
- **Contexto:** pérdida de fase, contactores dañados y aislamiento degradado producen desbalance.
- **Decisión:**
  - NEMA MG-1 limita el desbalance de **tensión** al 1 %. Por encima hay que reducir la potencia del motor.
  - El desbalance de **corriente** es 6–10 veces el de tensión.
  - El calentamiento adicional se estima en 2·(%desbalance)² %.
  - Umbrales de desbalance de corriente: nominal 0–2 %, **alerta 5 %** (equivale a un desbalance de tensión < 1 %) y **crítico 10 %** (≈ 1–1.7 % de tensión, fuera del límite NEMA, o pérdida parcial de fase).
- **Alternativas:** 10 %/20 %, que es un criterio de campo común pero menos conservador.
- **Conflicto:** una fuente escribe "1 % de tensión produce 6–10 % de corriente" y otras dicen "6–10 veces". A 1 % las dos lecturas coinciden, así que no cambia los umbrales.
- **Fuentes:** NEMA (2021), vía ALL-TEST Pro (s. f.) y Evans (s. f.); Bonnett y Soukup (1992).
- **Confianza:** media.

## D-007 – Umbrales de corriente y factor de servicio
- **Contexto:** paros por sobrecorriente y sobrecarga mecánica.
- **Decisión:**
  - La corriente se expresa en % de la corriente nominal de placa (In).
  - **Alerta 105 %** (por encima de la potencia nominal, dentro del factor de servicio).
  - **Crítico 115 %**, que coincide con el factor de servicio NEMA 1.15, el ajuste usual de la protección térmica.
  - La subcarga (`alerta_baja`) depende del activo, porque la física de la caída de corriente cambia:
    - motor: 40 %;
    - bomba: 75 %, porque la potencia de una bomba centrífuga cae con el caudal (D-014);
    - compresor: 50 %, que corresponde a funcionar descargado (D-017);
    - prensa: 30 %;
    - banda: 30 %, que corresponde a funcionar en vacío tras una rotura (D-025).
  - En la banda, la alerta queda en 100 % porque un desvío añade arrastre (D-024).
- **Alternativas:** usar solo el disparo del relé térmico (125 % In), que es tardío.
- **Fuentes:** NEMA (2021); IEC (2022), que define el servicio S1 nominal; Malloy Electric (s. f.), donde la sobrecorriente a velocidad constante indica causas mecánicas.
- **Confianza:** media. Los valores de subcarga son supuestos del agente basados en la física, con confianza baja.

## D-008 – Temperatura de rodamientos de motor
- **Contexto:** se necesitan umbrales para la lubricación deficiente y el desgaste de rodamientos.
- **Decisión:** nominal 45–75 °C, **alerta 90 °C** y **crítico 95 °C** (rodamientos antifricción con RTD).
- **Conflicto:**
  - TECO-Westinghouse da una alarma de 90–110 °C y un disparo de 95–120 °C.
  - Un manual de motores Siemens da 95/105 °C para antifricción.
  - Se toma el **extremo inferior** (90/95), que es el más conservador.
- **Fuentes:** TECO-Westinghouse (2008), leída por el Revisor con `pdftotext` (rodamientos antifricción engrasados: admisible 80–90 °C, alarma 90–110 °C, disparo 95–120 °C; son valores recomendados); Siemens (s. f.), que el Revisor no pudo abrir (HTTP 403), de modo que sus 95/105 °C siguen sin verificar; Acoem (s. f.-a), según la cual la temperatura sube en las etapas tardías.
- **Confianza:** media.

## D-009 – Temperatura de rodamientos de bomba y tambor de banda
- **Decisión:** nominal 45–68 °C, **alerta 82 °C** y **crítico 88 °C** en la bomba. Los mismos umbrales se aplican al tambor motriz de la banda.
- **Conflicto:** los valores para motores (D-008) son más altos. Se usan los de bomba (KSB GIW: normal 60–68 °C, alarma 180 °F ≈ 82 °C, paro 190 °F ≈ 88 °C) porque son los más conservadores y específicos de bombas.
- **Conflicto registrado en la revisión:** una nota técnica de GIW, vista solo en el extracto del buscador, propone 93 °C de alarma y 115 °C de paro para reducir falsas alarmas. Se mantiene 82/88 °C por ser lo más conservador.
- **Fuentes:** KSB GIW (s. f.), cuyo sitio no respondió al Revisor: 180/190 °F se confirmaron solo en el extracto del buscador y el rango normal de 60–68 °C no se confirmó; TECO-Westinghouse (2008), como contraste.
- **Confianza:** media. Para el tambor de la banda la confianza es baja, porque el valor de bomba se extrapola.

## D-010 – Indicadores de defecto de rodamiento (curtosis, alta frecuencia, etapas)
- **Contexto:** "ese rodamiento ya se va", "el motor está cantando", "cascabeleo". El defecto incipiente no aparece en la velocidad RMS global.
- **Decisión:**
  1. Se usa el modelo de **4 etapas**:
     - (1) ultrasonido o alta frecuencia;
     - (2) frecuencias de defecto en la envolvente;
     - (3) armónicos y bandas laterales, con temperatura en ascenso;
     - (4) vibración global alta y temperatura muy alta.
  2. **Curtosis:** ≈ 3 en una señal sana (gaussiana). **Alerta ≥ 4** y **crítico ≥ 6** (impactos).
  3. **Energía de alta frecuencia o envolvente** relativa a la línea base: **alerta 2×**, **crítico 4×**.
  4. La temperatura del rodamiento sube **8–15 °C** sobre la línea base al comienzo de la etapa tardía, por eso `retardo_frac = 0.7` en el simulador.
   - **Corrección 2026-11-05 (D-042):** hasta el momento de la falla (etapa 4, "temperatura muy alta") el aumento supera esos 8–15 °C. La firma termina en +35 °C (rodamiento) y +25 °C (husillo), de modo que alcanza el nivel de disparo y activa `temp_rodamiento_alta` / `temp_husillo_alta`. Con +15 °C la firma nunca llegaba a la alerta de 90 °C (motor) ni de 82 °C (bomba).
- **Alternativas:** umbrales absolutos en gE de envolvente, que dependen del sensor y de la máquina.
- **Conflictos:**
  - La banda de la etapa 1 difiere entre fuentes: 20–60 kHz (Acoem) frente a 250–350 kHz (UE Systems). No afecta al simulador, que usa una variable relativa.
  - Las relaciones 2×/4× **no** salen de una norma: son práctica de la industria. Revisión 2026-11-05: Filippenko et al. (2002) fijan advertencia en el doble y alarma en cuatro veces la línea base, y Vibromera (2025) da 2×/4×/8× como límites específicos de máquina. Ambas se leyeron.
  - La curtosis de 4 tiene segunda fuente: Zhou et al. (2023) la dan como umbral usual en ingeniería, con la advertencia de que Ku ≤ 4 no garantiza un rodamiento sano. El crítico de 6 sigue sin fuente.
- **Fuentes:** Randall y Antoni (2011); Dyer y Stewart (1978), que proponen la curtosis para detectar daño de rodamientos; Acoem (s. f.-a), que el Revisor no pudo abrir; UE Systems (s. f.), leída; Smith y Randall (2015); Zhou et al. (2023); Filippenko et al. (2002); Vibromera (2025).
- **Confianza:** media, incluidos los factores 2×/4× (antes baja) y la alerta de curtosis; baja para la curtosis crítica de 6.

## D-011 – Firmas espectrales de desbalanceo y desalineación
- **Contexto:** "desalineación y desbalanceo de ejes (vibración creciente)". El simulador produce rasgos espectrales simples.
- **Decisión:**
  - **Desbalanceo:** la componente 1X radial domina (fracción ≥ 0.8 de la energía) y la vibración axial es baja.
  - **Desalineación:** la amplitud 2X es ≥ 50 % de la 1X y la vibración axial es ≥ 50 % de la radial.
  - Los dos casos requieren además vibración global en alerta o creciente.
- **Alternativas:** usar solo la RMS global, que no distingue las dos fallas.
- **Fuentes:** Randall (2011); Piotrowski (2006). Ambos son textos de referencia consultados de memoria y no por web: las relaciones 0.5 son reglas prácticas. Revisión 2026-11-05: Fluke (2025), leída, confirma la parte cualitativa (desbalanceo con 1X alta; desalineación con 1X y 2X), pero no da las fracciones.
- **Confianza:** media. Las fracciones exactas tienen confianza baja.

## D-012 – Margen de NPSH
- **Contexto:** cavitación en bombas.
- **Decisión:**
  - Se usa la relación **NPSHA/NPSH3**. NPSH3 es la NPSH que produce una caída del 3 % en la altura.
  - Valores: nominal 1.5–3.0, **alerta ≤ 1.3** y **crítico ≤ 1.1**.
  - Texto leído por el Revisor (ANSI/HI 9.6.1-2017, secciones 9.6.1.2 y 9.6.1.5). La descripción anterior, "1.1 para bombas de catálogo o de proceso, 1.3 para algunas de mayor energía", era imprecisa; los valores de la norma para región preferente (POR) y permitida (AOR) son:

    | Aplicación (tabla de HI) | POR | AOR |
    |---|---|---|
    | Industrial general, 9.6.1.5.10 | 1.05 [0.6 m] | 1.1 [1.0 m] |
    | Agua de circulación o refrigeración, 9.6.1.5.3 | 1.05 | [1.0 m] |
    | Torre de enfriamiento, 9.6.1.5.3 | 1.1 | 1.3 |
    | Proceso químico, 9.6.1.5.2 | 1.1 | 1.1–1.2 |
    | Alimentación de caldera, 9.6.1.5.3 | 1.1–1.2 | 1.3–1.5 |

  - El **crítico de 1.1** es el mínimo en AOR para bombas industriales generales. La **alerta de 1.3** es el valor más alto aplicable a nuestra bomba de agua de proceso (torre de enfriamiento, AOR). Los dos valores quedan igual; la justificación cambia.
  - HI da márgenes de **diseño**, no umbrales de alarma, y pide además un margen mínimo en metros. Usarlos como alarma es una decisión del proyecto. La norma advierte que puede haber cavitación aun con NPSHA > NPSH3.
  - **Firma corregida (revisión):** `cavitacion` terminaba con la relación en 1.0 y la presión en 88 %. Por definición, con NPSHA = NPSH3 la caída de altura es del 3 %, de modo que una caída del 12 % exige una relación menor que 1. La firma pasa de **1.0 a 0.9**. El valor exacto es un supuesto de calibración.
- **Alternativas:** margen absoluto en metros, que depende de la bomba. Otra alternativa es exigir una relación de 2 a 10 para eliminar toda cavitación: es demasiado estricto y la mayoría de las bombas sanas lo violarían.
- **Conflicto:** A Marine Blog (2017) dice que suprimir toda la cavitación exigiría una relación de 2 a 10, a menudo mayor que 4 (antes se citaba como "2 a más de 4"). Esas cifras no están en el texto de HI. Se registran pero no se usan, porque generarían falsas alarmas.
- **Fuentes:** Hydraulic Institute (2017), leída; A Marine Blog (2017), leída, que resume la edición de 2012; Pumps & Systems (2012), no abierta en la revisión.
- **Confianza:** alta.

## D-013 – Firma de cavitación
- **Decisión:** la cavitación se reconoce por esta combinación:
  1. margen de NPSH bajo;
  2. vibración de **banda ancha en alta frecuencia** (~1–20 kHz), con ruido "de grava" por encima de ~1 kHz;
  3. **inestabilidad** de caudal y presión, medida como coeficiente de variación (alerta 5 %, crítico 10 %);
  4. **caída de la presión de descarga o de la altura**. Por definición, NPSH3 implica una caída del 3 % de la altura. Se fija la alerta en −5 % (95 % de la nominal) y el crítico en −10 %, para no confundir la cavitación con la variación normal de proceso.
- **Alternativas:** detectar solo por vibración global, que es poco específica.
- **Conflicto:** los umbrales de coeficiente de variación (5/10 %) son supuestos del agente. La idea de usar el coeficiente de variación de la presión de succión para detectar cavitación viene de una patente de Yokogawa Electric (Ogawa et al., 2022); la atribución anterior a Ebara era un error. La patente usa la presión de succión y no el caudal, fija el umbral por múltiplo de un valor estable y solo da un dato: coeficiente menor que 0.005 sin burbujas visibles. No se halló segunda fuente para 5/10 %.
- **Fuentes:** Hydraulic Institute (2017), leída para NPSH3 y para los efectos en altura, ruido y vibración; Brennen (1994), de memoria; Inspenet (s. f.), leída, que solo sostiene "> 1 kHz" y la inestabilidad; Al-Hashmi et al. (2017), leída, que sostiene la banda de 1–20 kHz; Ogawa et al. (2022).
- **Confianza:** alta para la firma cualitativa; baja para los umbrales de coeficiente de variación.

## D-014 – Firma de obstrucción de bomba
- **Decisión:**
  - Una obstrucción de succión o de impulsor reduce el caudal (alerta ≤ 90 %, crítico ≤ 80 %).
  - En una bomba centrífuga de flujo radial, la potencia absorbida **disminuye** al bajar el caudal, así que la corriente baja (subcarga al 75 % In).
  - La obstrucción de succión además reduce el NPSHA y puede llevar a cavitación.
- **Alternativas:** asumir que la corriente aumenta, lo cual es incorrecto para bombas radiales y solo vale en algunas de flujo axial.
- **Fuentes:** Brennen (1994); Karassik et al. (2008) y la física de la curva de potencia, consultados de memoria y no por web. SKAB incluye cierres parciales de válvula con caída de caudal (Katser y Kozitsin, 2020).
- **Confianza:** media.

## D-015 – Desgaste de sello mecánico
- **Decisión:**
  - Variable `fuga_sello_ml_h`: nominal 0–1 ml/h, **alerta 3 ml/h** (≈ 1 gota por minuto) y **crítico 9 ml/h** (≈ 3 gotas por minuto).
  - **Corrección (Revisor, 2026-11-05):** antes nominal 0–2, alerta 5 y crítico 20 ml/h. Las fuentes halladas ponen la fuga aceptable y la grave por debajo de esos valores: CIRCOR (2018) acepta hasta 10 gotas por hora (≈ 0.5 ml/h) y Pumps & Systems (2011) trata 3 gotas por minuto como fuga mayor que exige parar la bomba, según la regla de California. Se aplica el valor más conservador. La conversión usa 1 gota ≈ 0.05 ml, que es un supuesto.
  - La vibración elevada y la operación en seco son las causas principales.
- **Alternativas:** no modelar el sello. Se descarta porque el enunciado lo exige.
- **Hueco:** Industrial Monitor Direct (s. f.-b) atribuye a API 682 límites de 0.5–3 ml/h, sin que se pudiera contrastar con la norma; sirve solo como orden de magnitud y para la alerta. CIRCOR habla de bombas de fluido térmico. La alerta sigue siendo una inferencia.
- **Fuentes:** CIRCOR (2018); Pumps & Systems (2011); Industrial Monitor Direct (s. f.-b); Bloch y Budris (2004), sobre causas de falla de sellos, consultado de memoria.
- **Confianza:** media para el orden de magnitud y el crítico (antes baja); baja para la alerta de 3 ml/h.

## D-016 – Temperatura de descarga del compresor de tornillo
- **Decisión:**
  - Rango normal 75–95 °C, **alerta 100 °C** y **crítico 110 °C**.
  - Causas: enfriador sucio, aceite bajo o degradado, filtros obstruidos, termostática que no envía aceite al enfriador, ventilación deficiente y separador obstruido.
- **Conflicto:** los puntos de paro varían por fabricante. Fabrico (s. f.-e) da una banda normal de 75–100 °C con paro 10–15 °C por encima, y Unitec-D (2026) señala que por encima de 105 °C se compromete el aceite. Se elige 110 °C, el extremo inferior del paro.
- **Revisión (2026-11-05):** los valores se mantienen, pero sus fuentes eran incorrectas. El artículo de Air Compressor Services es de un compresor diésel portátil D185 y no da ninguna cifra; Atlas Copco tampoco. Edmac bloqueó el acceso (HTTP 403), así que el rango "77–93 °C" no se pudo confirmar y se retiró. Esas dos fuentes siguen valiendo para las causas.
- **Fuentes:** Fabrico (s. f.-e) y Unitec-D (2026), para los valores; Air Compressor Services (s. f.) y Atlas Copco (s. f.), para las causas; Edmac (s. f.), no verificada.
- **Confianza:** media.

## D-017 – Pérdida de presión en compresor de tornillo
- **Decisión:**
  - Presión de descarga en % de la consigna (7.5 bar): **alerta ≤ 93 %** (≈ 7.0 bar) y **crítico ≤ 85 %** (≈ 6.4 bar).
  - Se distinguen tres causas por su firma:
    - **fugas de red:** el compresor pasa más tiempo en carga (D-019);
    - **válvula de admisión** que no abre: la máquina "trabaja" descargada, con corriente baja;
    - **separador obstruido:** diferencial alto (D-018).
  - El procedimiento de aislamiento (compresor contra red) separa la oferta de la demanda.
- **Alternativas:** una sola falla genérica, "pérdida de presión". Se descarta por no ser accionable.
- **Fuentes:** Anglian Compressors (s. f.); Fabrico (s. f.-a); U.S. Department of Energy (2003).
- **Confianza:** media. El valor de 93 % es elección del agente, con confianza baja.

## D-018 – Diferencial del separador de aceite
- **Decisión:** nominal 0.1–0.4 bar, **alerta 0.55 bar** (8 psi) y **crítico 1.0 bar**.
- **Corrección (Revisor, 2026-11-05):** la alerta pasa de 0.7 a 0.55 bar. MaintainX (s. f.) reproduce el procedimiento de Gardner Denver: cambiar el elemento con 8 psi o más. El buscador mostró además un manual Sullair con 0.7 bar y un manual Gardner Denver con 0.55 bar de aviso y 1 bar de paro, que no se pudieron abrir. Las fuentes discrepan y se aplica el valor más conservador. El crítico de 1 bar coincide con la vida de servicio de 1 bar Δp que publica Nuvair (s. f.).
- **Hueco:** el límite real depende del fabricante y del elemento; ninguna norma lo fija.
- **Fuentes:** MaintainX (s. f.); Nuvair (s. f.); Anglian Compressors (s. f.), que recomienda medir el diferencial.
- **Confianza:** media para el crítico de 1 bar (antes baja); baja para la alerta, que tiene una sola fuente leída.

## D-019 – Fugas de la red de aire y tiempo en carga
- **Decisión:**
  - En plantas sin programa de mantenimiento, las fugas suelen consumir el **20–30 %** de la producción de aire, y la meta es < 10 %.
  - En el simulador, una fuga aumenta el tiempo en carga: nominal 40–75 %, **alerta ≥ 85 %** y **crítico ≥ 95 %**, con presión a la baja.
  - El evento confusor "pico de demanda" (D-037) imita esta firma de forma transitoria.
- **Fuentes:** U.S. Department of Energy (2003), confirmada en catálogo pero no leída; Compressed Air Challenge (2026), leída: "sometimes" 20–30 %, 20 % típico en plantas sin mantenimiento y meta < 10 %; Anglian Compressors (s. f.), leída.
- **Confianza:** media.

## D-020 – Temperatura del aceite hidráulico
- **Decisión:**
  - Nominal 40–55 °C, **alerta 60 °C** y **crítico 70 °C**.
  - `alerta_baja` de 20 °C para el aceite frío, con viscosidad alta (D-023).
- **Conflicto:**
  - La hoja de datos Parker de la válvula reductora proporcional VMY da 60 °C como temperatura máxima de operación y 70 °C como máxima del fluido. Antes se citaba como válvulas direccionales D1FB/D3FB, y el documento de esa URL no es de esas válvulas.
  - Power & Motion menciona 82–85 °C como límite para sellos y mangueras.
  - Se elige el valor **más conservador**, el de los componentes más sensibles (válvulas).
- **Hueco:** la regla de "vida del aceite a la mitad por cada 10 °C" tiene una temperatura base distinta en cada fuente (40, 60 o 75 °C), así que solo se usa cualitativamente.
- **Fuentes:** Parker Hannifin (s. f.); Power & Motion (s. f.-a, s. f.-b); Hydraulics & Pneumatics (s. f.).
- **Confianza:** media.

## D-021 – Limpieza del aceite hidráulico (ISO 4406)
- **Decisión:**
  - Objetivo **ISO 4406 18/16/13**, que es lo que indica la hoja de datos Parker de la válvula VMY.
  - Se monitorea el tercer código (partículas ≥ 14 µm): nominal ≤ 13, **alerta 14** y **crítico 15**.
  - Cada código adicional equivale aproximadamente al doble de partículas, así que +2 códigos son ≈ 4× la contaminación.
- **Conflicto:** el objetivo 17/15/12, más estricto y común en guías de servoválvulas, no se pudo verificar. Se usa 18/16/13, que sí está verificado, y queda pendiente endurecerlo si el Revisor encuentra fuente.
- **Fuentes:** ISO (2021); Parker Hannifin (s. f.).
- **Confianza:** media.

## D-022 – Fugas externas e internas en la prensa
- **Decisión:**
  - **Externa:** el nivel del tanque baja (alerta ≤ 85 %, crítico ≤ 75 %) y la presión cae (≤ 90 % de la receta).
  - **Interna** (bypass del sello del pistón o de la válvula):
    - caída de presión en retención (alerta 5 bar/min, crítico 10 bar/min);
    - tiempo de ciclo alto (alerta +10 %, crítico +20 %);
    - temperatura del aceite en aumento, porque la fuga convierte energía en calor; las fuentes sugieren 5–10 °C de diferencia en el cilindro afectado.
  - Diagnóstico: prueba de bypass en fin de carrera y aislamiento de válvulas.
- **Hueco:** los umbrales numéricos de caída de presión y de nivel son **supuestos** del agente, con confianza baja. La firma cualitativa sí tiene dos fuentes.
- **Revisión (2026-11-05):** no se halló un límite general en bar/min: depende de la especificación del fabricante y de normas de cilindros que no se pudieron leer. Los 5/10 bar/min y el nivel de tanque siguen como supuestos. Machinery Lubrication sostiene la lentitud y la prueba de caudal, pero no menciona calor; el calor y los 5–10 °C solo vienen de FridayParts.
- **Fuentes:** Machinery Lubrication (s. f.); FridayParts (s. f.); Fabrico (s. f.-c). Las tres se leyeron.
- **Confianza:** media para la firma; baja para los números.

## D-023 – Interpretación de "la prensa está dura"
- **Decisión:**
  - Se interpreta como **resistencia hidráulica**: más presión de trabajo (≥ 110 % de la receta) y más tiempo de ciclo para la misma operación.
  - Causas candidatas, en orden: válvula direccional o proporcional pegada o lenta (barniz, partículas), contaminación, y aceite frío con viscosidad alta.
  - Una fuga interna haría la prensa "floja" (presión baja, deriva), así que recibe un FC bajo en el léxico.
- **Alternativas:**
  - Interpretarla como fuga interna. No encaja con la física.
  - Interpretarla como dureza del material de la pieza. Sería un problema de proceso, fuera del alcance.
- **Fuentes:** Parker Hannifin (s. f.), que vincula la limpieza del aceite con el funcionamiento de la válvula; Machinery Lubrication (s. f.); Carroll (2013), leída, según la cual el primer síntoma del barniz es la operación errática de los actuadores, que parecen pegados aunque lo que no se mueve libre es el carrete; física de la viscosidad. No hay fuente que defina la expresión ni que ligue el carrete pegado con presión alta.
- **Confianza:** baja.

## D-024 – Corrimiento de banda
- **Decisión:**
  - Causas: empalme no escuadrado, rodillos o tambores fuera de escuadra o trabados, carga descentrada, banda acopada y acumulación de material.
  - Síntomas: desvío lateral, desgaste de bordes y derrame. La corriente del motor sube por el arrastre adicional.
  - Umbrales de desvío lateral: nominal 0–10 mm, **alerta 25 mm** y **crítico 50 mm**, que es cuando suelen actuar los interruptores de desalineación.
- **Hueco:** no se halló un valor numérico normativo de desvío (CEMA no se consultó por ser de pago). Los mm son supuestos del agente. Revisión 2026-11-05: los interruptores expresan su punto de actuación en grados de la palanca (4B, s. f.-a: 20° de alarma y 35° de paro), no en mm, así que no hay segunda fuente.
- **Fuentes:** Martin Engineering (s. f.-a, s. f.-b); Continental (s. f.); Fabrico (s. f.-b).
- **Confianza:** media para la firma; baja para los mm.

## D-025 – Deslizamiento y rotura de banda
- **Decisión:**
  - **Deslizamiento** (velocidad del tambor frente a la de la banda): **alerta 2 %** y **crítico 5 %**. Sus causas son tensión baja, recubrimiento del tambor gastado y agua o material entre banda y tambor.
  - **Rotura:** la velocidad de la banda baja a ≤ 10 % con el motor en marcha, y la corriente cae a la de vacío (≤ 30 % In).
  - Precursor opcional: el empalme dañado da un golpe periódico que eleva la curtosis.
- **Hueco:** no se encontró fuente con valores de deslizamiento para alarma. El único dato leído es un interruptor de 4B (s. f.-b), que actúa con una caída del 20 % de la velocidad, muy por encima de 2/5 %; se conservan como supuesto conservador. La rotura se deduce de la física (sin carga, sin par).
- **Fuentes:** Martin Engineering (s. f.-b), sobre el empalme como causa de problemas; física de la transmisión por fricción (Euler-Eytelwein, conocimiento general).
- **Confianza:** baja.

## D-026 – Falla de rodillos ("cascabeleo en la línea")
- **Decisión:**
  - Un rodillo trabado actúa como barra de fricción, desvía la banda y aumenta el arrastre.
  - Un rodillo con el rodamiento dañado produce impactos, que elevan la curtosis y causan el traqueteo.
  - Firma: curtosis ≥ 4, corriente en aumento y desvío lateral tardío.
- **Fuentes:** Martin Engineering vía World Fertilizer (2022); Fabrico (s. f.-b); Randall y Antoni (2011), sobre los impactos.
- **Confianza:** media.

## D-027 – Desgaste de herramienta CNC
- **Decisión:**
  - Vida de la herramienta: **alerta 200 min** y **crítico 240 min** de corte acumulado, tomada del modo TWF de AI4I 2020 (falla o reemplazo aleatorio entre 200 y 240 min).
  - Con el desgaste del flanco sube la fuerza de corte y, con ella, la carga y la corriente del husillo. Carga relativa a la línea base de la operación: **alerta 1.2×** y **crítico 1.4×**.
- **Conflicto:** no se verificó un porcentaje de aumento de corriente en la literatura: el 20 %/40 % es elección del agente. El estudio de gemelo digital normaliza la corriente, pero no da un umbral.
- **Fuentes:** Matzka (2020); UCI Machine Learning Repository (2020); Teti et al. (2010); Industrial Monitor Direct (s. f.-a).
- **Confianza:** media para los minutos; baja para el factor de carga.

## D-028 – Rotura de herramienta y colisión ("golpes en CNC")
- **Decisión:**
  - **Rotura:** caída súbita de la carga (≤ 0.5× en pleno corte) con un pico de vibración ≥ 5 g. Los estudios con sensor de corriente detectan la rotura en 1–3 s, por anomalías en el dominio de la frecuencia.
  - **Colisión:** pico ≥ 5 g (crítico 10 g) con carga ≥ 1.4×.
  - La corriente sola no detecta el astillado; para eso se necesita la vibración.
- **Hueco:** los umbrales en g son supuestos del agente. Revisión 2026-11-05: no se halló un valor publicado para colisiones, que se ajustan por máquina. MTD Media (s. f.) da 2.5 y 4 G para desgaste de rodamientos de husillo, lo que deja el nominal ≤ 2 g en un orden razonable, pero no sostiene 5/10 g.
- **Fuentes:** Teti et al. (2010); Lai et al. (2025), leída: detección en 1–3 s por anomalías de frecuencia, en ensayos que simulan la rotura retirando la carga o golpeando la herramienta; Industrial Monitor Direct (s. f.-a), que sostiene lo del astillado.
- **Confianza:** media para la firma; baja para los g.

## D-029 – Chatter y sobrecalentamiento de husillo
- **Decisión:**
  - **Chatter:** carga fluctuante (coeficiente de variación ≥ 10 %) y vibración de alta frecuencia ≥ 2×. Se corrige cambiando la velocidad hacia un lóbulo estable o reduciendo la profundidad o el voladizo.
  - **Husillo:** nominal 25–40 °C, **alerta 50 °C** y **crítico 60 °C**.
  - Para la vibración del cabezal se usa el proxy de ISO 20816-3 (D-003).
- **Hueco:** no hay fuente verificada para las temperaturas del husillo ni para el coeficiente de variación. Son **supuestos**. La búsqueda de la revisión tampoco los halló: los límites dependen del fabricante del rodamiento y del constructor del husillo, y los umbrales de chatter se ajustan empíricamente.
- **Fuentes:** Altintas (2012); Teti et al. (2010).
- **Confianza:** baja.

## D-030 – Fallas de variador ("está disparando por nada")
- **Decisión:**
  - Causas de disparos intermitentes con carga normal: rampas de aceleración demasiado cortas, datos de motor mal cargados, cable largo sin reactancia, falla a tierra por aislamiento o cable degradado, sobretensión del bus DC por regeneración y sobretemperatura.
  - Umbrales:
    - disparos: **alerta ≥ 1 en 24 h**, **crítico ≥ 3 en 24 h**;
    - THD de tensión: **alerta 8 %**, el límite de IEEE 519-2014 para barras ≤ 1 kV; **crítico 12 %**, que es 1.5 veces ese límite, lo admitido en periodos cortos;
    - bus DC: alerta 115 % y **crítico 125 %**;
    - disipador: alerta 75 °C y crítico 85 °C.
- **Corrección (Revisor, 2026-11-05):** el crítico del bus DC pasa de 130 % a 125 %. Flexa Systems (2026a, 2026b) da un disparo de unos 820 VDC en variadores de clase 480 V. Con un bus nominal de 1.35 × 480 ≈ 648 V, eso es ≈ 127 %: un crítico de 130 % quedaba **por encima del disparo real** y el síntoma nunca se vería. El cálculo es del Revisor.
- **Revisión de la THD:** PowerMonitors (s. f.) reproduce la tabla de IEEE 519-2014 (≤ 1 kV: 5 % individual y 8 % THD) y la tolerancia de 1.5 veces. Ya no viene de memoria. El límite aplica en el punto de acoplamiento común, no en bornes del variador; aquí se usa como referencia.
- **Disipador:** los disparos de 85–95 °C que da Flexa Systems sostienen que 75/85 °C es conservador. Las dos páginas son del mismo sitio y cuentan como una sola fuente.
- **Conflicto:** los códigos de falla y los niveles de disparo del bus DC dependen del fabricante y de la serie (por ejemplo, ABB ACS355 y ACS880 numeran distinto).
- **Fuentes:** IEEE (2014), vista por citas; PowerMonitors (s. f.); Flexa Systems (2026a, 2026b); Malloy Electric (s. f.), no abierta en la revisión (HTTP 503); Fabrico (s. f.-f), leída; Precision Electric (2025).
- **Confianza:** media para la THD (antes alta en el texto: es una norma vista por citas); baja para el bus DC, la temperatura y el conteo de disparos.

## D-031 – Fallas de contactor
- **Decisión:**
  - Contactos picados, bornes flojos o una fase abierta producen un desbalance de corriente fuerte (≥ 10 %) o una pérdida de fase.
  - El motor sigue girando con dos fases, con corrientes elevadas y calentamiento rápido del devanado.
  - Firma: desbalance crítico + temperatura de devanado alta, con forma intermitente.
- **Fuentes:** Bonnett y Soukup (1992), sobre el *single phasing* como causa de falla del estator; NEMA (2021), vía ALL-TEST Pro (s. f.).
- **Confianza:** media.

## D-032 – Degradación de aislamiento ("huele a quemado")
- **Decisión:**
  - El olor a barniz indica una degradación térmica del aislamiento que ya está en curso.
  - Firma: temperatura del devanado ≥ 130 °C (D-005), desbalance en aumento por cortos entre espiras, y corriente en aumento en la etapa tardía. La degradación es lenta y exponencial (meses).
  - Si la observación coincide con una medición alta, se le da un FC de 0.8 (regla R08).
- **Fuentes:** Bonnett y Soukup (1992); IEEE Motor Reliability Working Group (1985); IEC (2007).
- **Confianza:** media.

## D-033 – Ventilación obstruida vs. lubricación deficiente
- **Contexto:** el enunciado agrupa "sobrecalentamiento por lubricación o ventilación obstruida". Para que el diagnóstico explique algo, hay que separar las dos causas.
- **Decisión:**
  - **Ventilación obstruida:** el devanado se calienta aunque la corriente es normal (`corriente_en_rango`). El exceso de temperatura no viene de la carga sino de la falta de refrigeración.
  - **Lubricación:** el rodamiento se calienta y la energía de alta frecuencia sube, por la fricción metal-metal, con el devanado normal.
- **Fuentes:** IEC (2022), sobre la refrigeración IC y el calentamiento; Bonnett y Soukup (1992); TECO-Westinghouse (2008); Acoem (s. f.-a).
- **Confianza:** media.

## D-034 – Factores de certeza (MYCIN)
- **Decisión:**
  - Modelo de **factores de certeza de MYCIN**:
    - FC de la conclusión = FC de la regla × mín(FC de las premisas);
    - combinación de dos conclusiones positivas: FC₁ + FC₂·(1 − FC₁).
  - FC asignados a las reglas:
    - 0.85–0.90: umbral normativo y firma multivariable;
    - 0.75–0.80: ≥ 2 fuentes y firma específica;
    - 0.65–0.70: fuentes secundarias o firma parcialmente ambigua;
    - 0.60: heurística o premisa percibida.
  - Una regla con un síntoma percibido nunca supera 0.80.
- **Alternativas:** probabilidades bayesianas, que no hay datos para estimar; lógica difusa completa, más compleja de explicar.
- **Fuentes:** Shortliffe y Buchanan (1975); Buchanan y Shortliffe (1984).
- **Confianza:** alta para el método; media para los valores, que son juicio del agente calibrado con las confianzas de las D-NNN.

## D-035 – Escalas FMEA
- **Decisión:**
  - S, O y D en escala 1–10, con NPR = S·O·D.
  - Las escalas se adaptan de IEC 60812 y del manual AIAG-VDA (tablas en `fmea.md`).
  - La ocurrencia se apoya en estadísticas de fallas cuando existen: en motores, los rodamientos y el estator son las causas más frecuentes según IEEE (1985).
  - El NPR se usa solo para priorizar. El manual AIAG-VDA de 2019 recomienda la prioridad de acción (AP) en lugar del NPR; se registra como mejora posible.
- **Fuentes:** IEC (2018); AIAG y VDA (2019); IEEE Motor Reliability Working Group (1985).
- **Confianza:** media. Los valores S/O/D concretos son juicio del agente, con confianza baja.

## D-036 – Datasets públicos para calibrar el simulador
- **Decisión:** se usan como **referencia de forma y rango**, no como datos de entrenamiento:
  - **AI4I 2020:** vida de herramienta 200–240 min y reglas de falla por potencia, disipación y sobreesfuerzo.
  - **NASA IMS:** degradación exponencial tardía de rodamientos, en ensayos de vida completa a 2000 rpm y 6000 lb.
  - **CWRU:** firmas de impacto y curtosis por tamaño de defecto (0.007–0.021 in).
  - **C-MAPSS:** estructura de vida completa con desgaste inicial variable y ruido.
  - **SKAB:** bomba de circulación con cavitación, desbalanceo y cierre de válvula, con variables casi idénticas a las nuestras.
  - **MIMII:** el sonido como fuente del síntoma percibido.
  - **UCI sistemas hidráulicos:** referencia para la prensa (D-048).
  - Detalle en [datasets_referencia.md](datasets_referencia.md).
- **Fuentes:** Matzka (2020); Lee et al. (2007); Qiu et al. (2006); Smith y Randall (2015); Saxena et al. (2008); Katser y Kozitsin (2020); Purohit et al. (2019); Helwig et al. (2015a).
- **Confianza:** media.

## D-037 – Formas de degradación y eventos confusores
- **Decisión:**
  - **Exponencial** (k ≈ 4) para fatiga y degradación acumulativa: rodamientos, aislamiento, sellos, fuga interna y rodillos. Así lo muestran IMS y C-MAPSS y lo recogen las revisiones de pronóstico.
  - **Lineal** para ensuciamiento y desgaste por uso: ventilación, enfriadores, separador, contaminación y herramienta, como en AI4I.
  - **Escalón** para eventos: rotura, colisión, sobrecarga y chatter.
  - **Intermitente** para fallas eléctricas y de válvulas: contactor, variador y válvula de admisión.
  - **Sigmoide** para la cavitación, que tiene un umbral de inicio.
  - Las duraciones son rangos plausibles, no medidos.
  - Se incluyen **eventos confusores** (arranque en frío, pico de demanda, cambio de lote, picos espurios, sensores faltantes) para generar falsas alarmas realistas.
- **Fuentes:** Lei et al. (2018); Qiu et al. (2006); Saxena et al. (2008); Matzka (2020).
- **Confianza:** media para las formas; baja para las duraciones.

## D-038 – Método de formalización del léxico
- **Decisión:** cada expresión se trata así:
  1. Se identifica el **fenómeno físico** que la persona percibe: sonido, olor, temperatura o comportamiento.
  2. Se buscan en las fuentes los **mecanismos de falla** que producen ese fenómeno.
  3. Se traducen a **síntomas medibles** y a la dirección del cambio de cada variable.
  4. Se listan los candidatos con un **fc_max ≤ 0.6**, porque la expresión es ambigua y depende del técnico y del turno.
  - La desambiguación la hacen las reglas con síntomas medidos.
  - Las reglas que incluyen un síntoma percibido están limitadas a FC ≤ 0.8 (D-034).
- **Alternativas:** una correspondencia uno a uno de expresión a falla, como en el ejemplo del plan. Se descarta porque oculta la ambigüedad real (por ejemplo, "cantando" puede ser un rodamiento o el variador).
- **Fuentes:** Buchanan y Shortliffe (1984), sobre la evidencia incierta en sistemas expertos; las decisiones técnicas que cita cada expresión.
- **Confianza:** media. "La prensa está dura" tiene confianza baja (D-023).

## D-039 – Rol de la base de conocimiento en la explicabilidad
- **Decisión:**
  - Las reglas y la ontología cumplen dos funciones:
    1. **validación experta** de las alertas del modelo DL (fusión M3), para reducir falsas alarmas;
    2. **explicación** en el vocabulario del dominio: síntoma → modo de falla → acción.
  - Esto complementa la explicación por atribución del modelo (SHAP o gradientes integrados).
  - Siguiendo a Kusiak (2024), la explicación se diseña para que pueda **combinarse entre unidades y activos**. El concepto de XAI federada propone agregar explicaciones de modelos locales igual que el aprendizaje federado agrega modelos. Aquí se adopta en forma reducida: explicaciones comparables por tipo de activo y por unidad.
- **Alternativas:** solo XAI post hoc. Las revisiones señalan que la falta de vínculo con el conocimiento del dominio limita su utilidad en mantenimiento.
- **Fuentes:** Kusiak (2024); Cummins et al. (2024); Matzka (2020).
- **Confianza:** media.

## D-040 – Variables relativas (`_pct`, `_rel`) en lugar de absolutas
- **Decisión:**
  - La presión, el caudal, la corriente, la carga del husillo, el tiempo de ciclo y la energía de alta frecuencia se expresan como **porcentaje del nominal o de la consigna**, o como **relación a la línea base** de la unidad.
  - Así las reglas sirven para todas las unidades de un mismo tipo aunque difieran en tamaño, y el simulador no necesita curvas de cada máquina.
- **Consecuencia:** el generador debe mantener una línea base por unidad (por ejemplo, las primeras semanas sanas), igual que la práctica de monitoreo basada en tendencias.
- **Fuentes:** ISO (2018), sobre líneas base y alarmas por cambio; Randall (2011).
- **Confianza:** media.

## D-041 – Holgura mecánica (modo de falla nuevo)
- **Contexto:** "esto está cascabeleando" (EXP04) puede ser un rodamiento, un rodillo o una **holgura** de componentes. La Fase 1 la dejó como hueco: no tenía modo propio, de modo que el motor, la bomba y el compresor no tenían forma de explicar un traqueteo sin falla de rodamiento.
- **Decisión:**
  - Se agrega `holgura_mecanica` para `motor_electrico`, `bomba_centrifuga` y `compresor_tornillo` (componente `base_anclajes`). No se incluye la banda ni el CNC: no tienen la razón 2X/1X y su holgura se confunde con rodillos o con el husillo.
  - **Firma:** vibración impulsiva (curtosis ≥ 4), componente 2X ≥ 50 % de 1X y vibración global en zona C. Según las fuentes, la holgura aparece como una serie de armónicos de la velocidad de giro (2X, 3X o más) que cambian de forma impredecible con la carga, con impactos en la forma de onda y fase inestable. Que 2X y 3X superen el 50 % de 1X como signo de mayor severidad no está en las fuentes citadas (revisión 2026-11-05): es una regla práctica vista en un extracto de buscador de un manual sin abrir. El umbral de 0.5 se hereda de D-011.
  - **Separación de otras fallas** (las reglas son conjunciones y no admiten premisas negadas): la firma del simulador mantiene en nivel nominal la razón axial/radial (distingue la desalineación), la fracción 1X (distingue el desbalanceo) y la energía de alta frecuencia (distingue el rodamiento). Si en datos reales dos reglas disparan a la vez, la combinación MYCIN y la fusión M3 resuelven la ambigüedad.
  - **Acciones:** reapriete con torque, reparación de base o regrout, calzar pata coja, reemplazo de rodamiento o acople con ajuste estrecho y medición de vibración posterior a la corrección.
  - **Reglas:** R46–R48 con FC 0.6, el extremo inferior de la política, porque la firma es heurística.
  - **FMEA:** S = 6, D = 4 y O = 4 (motor y bomba) o 3 (compresor); NPR de 96, 96 y 72.
- **Alternativas:** subsumirla en `desalineacion_eje` (se pierde la acción de reapriete y el diagnóstico diferencial); modelar subarmónicos 0.5X (la variable no existe en el simulador y subiría la complejidad).
- **Conflictos:**
  - Las fuentes distinguen tipos de holgura (de rotor, estructural y de ajuste del eje con subarmónicos 0.5X, 1.5X…). Se modela un solo modo, genérico.
  - Ninguna fuente consultada da la curtosis de la holgura. Que la curtosis suba se infiere de los impactos de la forma de onda; el valor de 5.0 en la firma es un supuesto.
- **Fuentes:** Fluke (2025), sobre armónicos, impactos, fase inestable, causas y acciones; Acoem (s. f.-b), sobre los tipos de holgura, con dos pulsos por revolución en el tipo B y muchos armónicos en el tipo C; D-011, para la razón 2X/1X. Las dos se leyeron en la revisión.
- **Confianza:** media para la firma cualitativa; baja para la curtosis y los umbrales numéricos. Las dos fuentes son guías de fabricantes de instrumentos, no normas.

## D-042 – Cierre de huecos de cobertura y coherencia firma ↔ reglas
- **Contexto:** al comenzar la Fase 2 se verificó, de forma cruzada y con un test, que las reglas pueden dispararse con las firmas del simulador. Se encontraron tres tipos de huecos: modos de la FMEA sin regla, variables ausentes en algunos activos y firmas cuyo valor final no alcanzaba el umbral de los síntomas de sus propias reglas (ERR-010).
- **Decisión:**
  1. **Reglas nuevas R41–R45** para los cinco modos de la FMEA que no tenían regla:

     | Regla | Activo | Modo | Premisas | FC |
     |---|---|---|---|---|
     | R41 | bomba | `desbalanceo_rotor` | vibración en alerta + 1X dominante | 0.70 |
     | R42 | compresor | `desalineacion_eje` | vibración en alerta + 2X elevada + axial alta | 0.70 |
     | R43 | banda | `desgaste_rodamiento` | vibración impulsiva + temperatura de rodamiento alta | 0.65 |
     | R44 | banda | `sobrecarga_mecanica` | sobrecorriente | 0.70 |
     | R45 | CNC | `desgaste_rodamiento` | impulsiva + alta frecuencia + temperatura de husillo alta | 0.65 |

     Los FC siguen la política de D-034: la banda y el CNC quedan en 0.65 porque el umbral del tambor y del husillo se extrapola (D-009, D-029).
  2. **Variables nuevas** en `compresor_tornillo`: `vib_2x_1x_ratio` y `vib_axial_radial_ratio`, con los mismos umbrales que motor y bomba (D-011). Sin ellas, la fila FMEA de desalineación del compresor no podía medirse.
  3. **Componentes:** se agregan `carga_accionada` (motor) y `base_anclajes` (motor, bomba y compresor) a `assets.yaml`. Los modos pueden declarar `componentes_por_activo` cuando un activo llama distinto al componente: CNC → `rodamientos_husillo`, compresor → `elemento_tornillo`, bomba → `impulsor`, banda → `motorreductor`.
  4. **Firmas corregidas** para que el valor final alcance los umbrales de sus síntomas:

     | Modo | Variable | Antes | Ahora | Valor final (antes → ahora) | Umbral |
     |---|---|---|---|---|---|
     | `desgaste_rodamiento` | `temp_rodamiento_c` | +15 | +35 | motor 75 → 95; bomba 71.5 → 91.5 | 90 / 82 |
     | `desgaste_rodamiento` | `temp_husillo_c` | +15 | +25 | 47.5 → 57.5 | 50 |
     | `falla_contactor` | `temp_devanado_c` | +35 | +50 | 120 → 135 | 130 |
     | `sobrecarga_mecanica` | `temp_devanado_c` | +40 | +50 | 125 → 135 | 130 |
     | `degradacion_aislamiento` | `corriente_pct` | +8 | +30 | 85.5 → 107.5 | 105 |
     | `falla_variador` | `temp_variador_c` | +25 | +30 | 72.5 → 77.5 | 75 |
     | `fuga_interna_cilindro` | `temp_aceite_c` | +10 | +15 | 57.5 → 62.5 | 60 |
     | `valvula_hidraulica_pegada` | `iso4406_14um_codigo` | +2 | +3 | 13.5 → 14.5 | 14 |
     | `desalineacion_banda` | `corriente_pct` | +12 | +33 | 79.5 → 100.5 | 100 |
     | `falla_rodillo` | `corriente_pct` | +18 | +35 | 85.5 → 102.5 | 100 |

     En nueve de los diez casos se eligió el cambio mínimo que cruza el umbral con un margen pequeño; `temp_rodamiento_c` se fijó en el nivel de disparo, que es donde termina un rodamiento al fallar (D-010). Los umbrales de `assets.yaml` no se tocaron, porque se apoyan en normas y fuentes (D-003 a D-030). Las magnitudes de la firma son supuestos de calibración y, a diferencia de los umbrales, se revisarán contra los datos sintéticos en la Fase 3.
  5. **Convención:** una variable de la firma que el activo no define se ignora (la firma es compartida entre activos). Para cada activo, la firma debe alcanzar los síntomas medidos de su fila FMEA y de las premisas de sus reglas. Lo verifica `tests/test_conocimiento.py`.
- **Alternativas:** subir los umbrales de alerta en lugar de las firmas (se descarta: contradice las normas citadas); eliminar las filas FMEA sin regla (se descarta: pierden el diagnóstico de esos modos).
- **Revisión (Revisor, 2026-11-05):** las 10 firmas alcanzan sus umbrales y R41–R48 se pueden disparar. Tres observaciones:
  - `degradacion_aislamiento` +30 % de corriente y `desalineacion_banda` +33 puntos son aumentos grandes para esos mecanismos. Se aceptan como calibración porque la FMEA pide `corriente_alta`, con confianza baja; conviene revisarlos en la Fase 3.
  - El +35 °C al fallar tiene respaldo cualitativo en UE Systems (s. f.), leída: en la etapa 4 la temperatura se dispara.
  - Comprobar solo el valor final no basta: varias reglas chocaban antes del final o se sumaban sin independencia (D-045).
- **Hueco que sigue abierto:** la lubricación deficiente fuera del motor se subsume en `desgaste_rodamiento` (ERR-004).
- **Fuentes:** D-003, D-007, D-009, D-010, D-011, D-021, D-022, D-024, D-029, D-030 y D-032 (las decisiones que ya respaldaban las reglas y umbrales afectados).
- **Confianza:** media para las reglas; baja para las magnitudes de las firmas (calibración del simulador).

## D-043 – Semántica del motor de reglas (fusificación, factores de certeza y traza)
- **Contexto:** la Fase 2 implementa `kb/rules_engine.py`. D-034 fijó el modelo MYCIN pero no cómo se convierte una lectura de sensor en un síntoma, ni qué pasa con datos faltantes, tendencias y observaciones del técnico.
- **Decisión:**
  1. **Fusificación nítida por defecto.** Cada variable medida produce síntomas con un grado en [0, 1]: 1 si cruza el umbral de `assets.yaml` (comparación inclusiva) y 0 si no. Un parámetro opcional `margen_suave` agrega una rampa lineal bajo el umbral, de ancho `margen_suave × |umbral − borde nominal|` (limitada a la distancia alerta–crítico en el nivel crítico). La rampa nunca llega al rango nominal, de modo que la operación normal no activa síntomas con ningún margen.
  2. **Niveles:** `alerta` y `critico` según la dirección de la variable; `alerta_baja` es la cola inferior; `en_rango` es la franja entre `alerta_baja` y `alerta` (síntoma de operación normal, p. ej. `corriente_en_rango`); `tendencia` compara el valor con la **línea base** de la unidad (D-040) y exige un cambio ≥ 25 % del límite de alerta (D-004). Sin línea base no hay tendencia.
  3. **Datos faltantes** (None o NaN): el síntoma no se activa y la variable se lista en `datos_faltantes`. Las variables que el activo no define se ignoran y se reportan como `variables_desconocidas`.
  4. **Observaciones del técnico:** son síntomas percibidos con grado 1. Entran por el léxico (D-038) y solo sirven de premisa de reglas de FC ≤ 0.8 (D-034). Una expresión sin síntomas medidos **no produce diagnóstico**; sus modos candidatos (`fc_max` ≤ 0.6) se informan aparte como `candidatos_lexico`.
  5. **Encadenamiento:** una regla se dispara si todas sus premisas tienen grado > 0. FC de la premisa = mínimo de los grados; FC de la conclusión = `fc` × FC de la premisa. Las conclusiones del mismo modo se combinan con MYCIN, y el resultado queda siempre por debajo de 1. Si las evidencias son +1 y −1, el FC es 0.
  6. **Traza:** cada regla disparada guarda sus premisas con el valor real, el umbral y el operador. También se informan las reglas **parciales** (algunas premisas cumplidas) y qué les falta, para explicar por qué un modo no se concluyó.
- **Alternativas:** lógica difusa completa con inferencia de Mamdani (más difícil de explicar a técnicos y sin datos para ajustar las funciones de pertenencia); probabilidades bayesianas (no hay datos de campo para estimar las tablas); premisas negadas en las reglas (se evitan: la separación entre modos parecidos se logra con la firma y con la fusión M3, D-041).
- **Verificación:** `tests/test_rules_engine.py` comprueba cada una de las 48 reglas con un caso positivo, un caso al que le falta una premisa y la operación normal en los 6 activos (punto medio y bordes del rango nominal). Sobre el valor final de las 41 firmas del simulador, el modo correcto está entre las conclusiones en 41 de 41 casos y es la conclusión principal en 39 de 41. Los dos casos restantes son ambigüedades reales: `falla_valvula_admision` (0.70) contra `fuga_aire_red` (0.75) en el compresor, y `valvula_hidraulica_pegada` (0.65) contra `contaminacion_aceite_hidraulico` (0.90) en la prensa, porque comparten síntomas.
- **Revisión (Revisor, 2026-11-05):**
  - Los dos casos "ambiguos" tenían solución con datos ya medidos: D-045 los resuelve y el resultado sobre las firmas pasa a 41 de 41. Los conteos anteriores quedan como registro de la Fase 2; ahora son 55 reglas.
  - MYCIN solo acepta una premisa con CF > 0.2, y este motor acepta cualquier grado > 0. Buchanan y Shortliffe (1984, cap. 10) explican que ese corte es pragmático y no es central al modelo. Solo importa con `margen_suave`; se acepta la diferencia.
  - Evitar premisas negadas sigue vigente: los síntomas `en_rango` son mediciones positivas y no se activan sin dato.
- **Fuentes:** Shortliffe y Buchanan (1975); Buchanan y Shortliffe (1984); D-004, D-034, D-038 y D-040.
- **Confianza:** alta para el método; media para el ancho de la rampa, que es opcional y no se usa por defecto.

## D-044 – Diseño de la ontología OWL y validación con HermiT
- **Contexto:** el plan pide una ontología editable en Protégé, generada desde los YAML (fuente única de verdad, AGENTS.md §7), con consultas de dominio y validación de consistencia.
- **Decisión:**
  1. **Generación, no edición.** `kb/ontology.py` construye la ontología con Owlready2 en un `World` propio y la guarda como RDF/XML en `knowledge/ontology/metaltech.owl`. Un test comprueba que el archivo versionado coincide con lo que generan hoy los YAML.
  2. **Clases.** Las 13 del plan (`Activo` con una subclase por tipo, `Componente`, `Sensor`, `Variable`, `Sintoma` con `SintomaMedido` y `SintomaPercibido`, `ModoFalla`, `Causa`, `Accion`, `Regla`, `ExpresionColoquial`, `Tecnico`, `Turno`, `Alerta`) más `FilaFMEA`. Esta última conserva las relaciones de la FMEA **por tipo de activo**: sin ella, un modo como `desgaste_rodamiento` mezclaría los síntomas, causas y acciones de cinco activos distintos.
  3. **Individuos.** Los activos son las **unidades** (16 en total), con sus componentes y un sensor por variable. Los componentes y las variables se instancian por tipo de activo (`bomba_centrifuga__impulsor`). Los técnicos se anonimizan (T01–T08 e I01–I02) y los turnos son tres, como indica el enunciado; no hay datos personales (Ley 1581 de 2012). `Alerta` queda sin individuos: se crean en tiempo de ejecución con `sustentadaPor`.
  4. **Propiedades.** Las del plan (`tieneComponente`, `monitoreadoPor`, `mide`, `manifiesta`, `causadoPor`, `mitigadoPor`, `refiereA`, `sustentadaPor`, `severidad`, `umbral`) más auxiliares (`concluye`, `tienePremisa`, `afectaComponente`, `sugiereModo`, `sobreVariable` y las de `FilaFMEA`). Todas tienen dominio y rango. `umbral` agrupa `umbralAlerta`, `umbralCritico` y `umbralAlertaBaja`.
  5. **Axiomas que permiten razonar.** Las clases de nivel superior son **disjuntas**, igual que `SintomaMedido` y `SintomaPercibido` y los tipos de activo; `mide`, `concluye`, `modoDeFila` y `componenteDeFila` son **funcionales**. Así HermiT detecta individuos mal clasificados y valores en conflicto.
  6. **Validación en dos niveles.** (a) `validar_estructura()`, en Python y sin Java: conteos contra los YAML, cada modo con síntomas, causas, acciones, componentes y reglas, cada regla con conclusión, premisas y fuente, y NPR coherente. (b) `validar_con_hermit()`: consistencia lógica y ausencia de clases insatisfacibles. Los tests de HermiT usan un JDK portable en `.tools/jdk17` (`scripts/instalar_jdk.py`, con verificación SHA-256) y se omiten si no hay Java.
  7. **Consultas.** Síntomas, causas, acciones, componentes y reglas de un modo (en general o para un tipo de activo); diagnóstico diferencial por síntoma; expresiones por síntoma o modo; sensores por unidad; ficha de un modo (`detalle_modo`) y grafo de nodos y aristas para la web (`grafo`).
- **Hallazgo durante la validación:** la primera versión declaraba `umbral` como propiedad funcional. Como `umbralAlerta` y `umbralCritico` son subpropiedades, cada variable acumulaba dos valores de una propiedad funcional y HermiT declaró la ontología inconsistente (ERR-011). Se corrigió haciendo `umbral` no funcional. La validación estructural en Python no lo habría detectado.
- **Alternativas:** una clase por modo de falla (explosión de clases sin beneficio de razonamiento); ontología escrita a mano en Protégé (se desincroniza de las reglas); usar solo la validación en Python (no prueba la lógica OWL).
- **Revisión (Revisor, 2026-11-05):** diseño aceptado. Lamy (2017) y Glimm et al. (2014) existen con esos datos en Crossref; su contenido no se leyó. Los conteos de clases y unidades son coherentes con el plan y con `assets.yaml` (16 unidades). Tras esta revisión hay que regenerar `metaltech.owl`, porque cambiaron umbrales, reglas y síntomas.
- **Fuentes:** Lamy (2017), sobre Owlready y la programación orientada a ontologías en Python; Glimm et al. (2014), sobre HermiT y su cumplimiento de la semántica directa de OWL 2.
- **Confianza:** alta.

## D-045 – Discriminadores `en_rango` en reglas que chocaban
- **Contexto:** la revisión lógica halló reglas que se disparaban juntas sin que nada las distinguiera, aunque los datos para separarlas ya se medían.
- **Decisión:** se agregan cuatro síntomas medidos de nivel `en_rango` (`curtosis_en_rango`, `temp_rodamiento_en_rango`, `desbalance_en_rango`, `presion_sistema_en_rango`) y una premisa en seis reglas:

  | Regla | Premisa agregada | Problema que resuelve |
  |---|---|---|
  | R01 | `desbalance_en_rango` | Ventilación se disparaba con falla de contactor y de aislamiento. Una obstrucción no desbalancea las fases (D-033) |
  | R02 | `curtosis_en_rango` | **Contradicción:** con rodamiento en etapa 4, R02 pedía relubricar y R04 decía no relubricar |
  | R03 | `temp_rodamiento_en_rango` | R03 estaba subsumida en R04 y las dos se combinaban como evidencia independiente (0.975). Ahora separan etapas y no se suman |
  | R22 | `corriente_en_rango` | La válvula de admisión se diagnosticaba como fuga de red. Con fuga, el compresor carga normal; con válvula cerrada, la corriente cae (D-017) |
  | R27 | `presion_sistema_en_rango` | La válvula pegada se diagnosticaba como contaminación. R27 estaba incluida en R28 con mayor FC |
  | R40 | `curtosis_en_rango` | Empate entre husillo sobrecalentado y rodamiento: R40 estaba incluida en R45 |

- **Resultado:** sobre el valor final de las 41 firmas, el modo correcto es el principal en 41 de 41 casos (antes 38 con el empate de R40/R45 y 39 según D-043). A lo largo de la degradación queda un solo cruce breve: `falla_valvula_admision` aparece como fuga entre t ≈ 0.80 y 0.83.
- **Se acepta sin cambio:**
  - R07 está incluida en R09: el desbalance crítico implica el de alerta. Ambas concluyen modos distintos, R09 tiene mayor FC y el diagnóstico diferencial tiene sentido.
  - R13 y R14, y también R10 y R11, comparten evidencia y su combinación MYCIN sobrestima algo el FC. Se declara como limitación del modelo.
- **Alternativas:** premisas negadas, descartadas en D-043; dejar el desempate a la fusión M3, lo que debilita M0 como línea base.
- **Fuentes:** D-017, D-033, D-041, D-043; física de cada falla. Los criterios de separación son inferencias del Revisor.
- **Confianza:** media.

## D-046 – Ajuste de los FC a la política de D-034
- **Contexto:** D-034 reserva 0.85–0.90 para un umbral normativo con firma multivariable, y 0.75–0.80 para ≥ 2 fuentes y firma específica. Varias reglas superaban su evidencia.
- **Decisión:**

  | Regla | Modo | FC antes | FC ahora | Motivo |
  |---|---|---|---|---|
  | R04 | `desgaste_rodamiento` | 0.90 | 0.85 | Multivariable, pero sin umbral normativo (D-010) |
  | R17 | `desgaste_sello_mecanico` | 0.80 | 0.70 | Una premisa y alerta con una sola fuente (D-015) |
  | R25 | `fuga_hidraulica_externa` | 0.85 | 0.75 | Umbrales supuestos (D-022) |
  | R27 | `contaminacion_aceite_hidraulico` | 0.90 | 0.80 | El objetivo sale de una hoja de datos, no de una norma (D-021) |
  | R30 | `sobrecalentamiento_aceite_hidraulico` | 0.85 | 0.80 | Una premisa, fuentes secundarias (D-020) |
  | R31 | `desalineacion_banda` | 0.80 | 0.70 | Una premisa y mm supuestos (D-024) |
  | R32 | `deslizamiento_banda` | 0.75 | 0.65 | Una premisa y porcentajes supuestos (D-025) |
  | R33 | `rotura_banda` | 0.90 | 0.80 | Física clara, sin norma ni fuente numérica (D-025) |
  | R36 | `desgaste_herramienta` | 0.85 | 0.80 | La vida viene de un dataset sintético y el factor de carga es supuesto (D-027) |
  | R37 | `rotura_herramienta` | 0.80 | 0.75 | Umbrales en g supuestos (D-028) |
  | R38 | `colision_husillo` | 0.85 | 0.80 | Umbrales en g supuestos (D-028) |

- **Sin cambio:** ninguna regla con síntoma percibido supera 0.80. R21 queda en 0.80 pese a la alerta de D-018, porque la firma combina dos variables específicas.
- **Fuentes:** D-034 y las decisiones citadas en la tabla.
- **Confianza:** media: los FC siguen siendo juicio, ahora alineado con la política.

## D-047 – Reglas para síntomas sin uso y campo `uso` del catálogo
- **Contexto:** 14 síntomas del catálogo no estaban en ninguna regla. Entre ellos había datos de la FMEA de variador y síntomas percibidos del léxico que nunca podían sumar evidencia.
- **Decisión:**
  - **R49–R55** usan siete de ellos. R49 y R50 usan `tension_bus_dc_alta` y `temp_variador_alta`. R51–R55 usan los cinco percibidos que faltaban, siempre junto a un síntoma medido (D-038) y con FC ≤ 0.70.
  - Los otros siete llevan `uso` en el catálogo. `severidad`: `vibracion_critica`, `temp_devanado_critica`, `temp_rodamiento_critica`, `temp_descarga_critica` y `desgaste_herramienta_limite` gradúan la urgencia de un modo ya concluido. `contexto`: `temp_aceite_alta` y `temp_aceite_baja`, útil esta última para vetar el confusor de arranque en frío en M3.
  - Las reglas percibidas de rodamiento y variador se escriben solo para el motor. En los otros activos el léxico sigue informando candidatos.
- **Corrección de léxico:** EXP08 declaraba bomba y banda, que no tienen variables de variador; queda solo en `motor_electrico` (D-002).
- **Fuentes:** D-016, D-024, D-030, D-034 y D-038.
- **Confianza:** media.

## D-048 – Dataset UCI de sistemas hidráulicos para la prensa
- **Contexto:** la Fase 1 dejó pendiente evaluar este dataset, porque ningún dataset cubría la prensa.
- **Decisión:** **se adopta como referencia de forma y rango, no como fuente de umbrales.**
  - Sirve para la dinámica de presión, caudal, temperatura y potencia en ciclos repetidos, y para tres fallas análogas: enfriador degradado (`sobrecalentamiento_aceite_hidraulico`), retardo de válvula (`valvula_hidraulica_pegada`) y fuga interna de la bomba, parecida a `fuga_interna_cilindro` en efecto pero no en componente.
  - No cubre fuga externa, contaminación por partículas ni cilindro. Es un banco de pruebas y no una prensa, y sus ciclos de carga son constantes.
  - Detalle en [datasets_referencia.md](datasets_referencia.md).
- **Fuentes:** Helwig et al. (2015a, 2015b). La ficha de UCI se leyó; del artículo solo se confirmaron los metadatos en Crossref.
- **Confianza:** media.

## D-049 – Tarea de predicción o detección por modo de falla
- **Contexto:** con H = 24 h y ventana de 6 h, varias fallas no se pueden predecir: el desgaste de herramienta dura 3.3–4 h, la cavitación 1–48 h, y un escalón no tiene precursor. El equipo eligió el horizonte por tipo de falla.
- **Decisión:**
  - `tarea: deteccion` si la forma es `escalon` o la duración mínima es menor que H: `sobrecarga_mecanica`, `cavitacion`, `falla_valvula_admision`, `rotura_banda`, `desgaste_herramienta`, `rotura_herramienta`, `colision_husillo` y `vibracion_chatter`. Los otros 23 modos son `prediccion`.
  - Etiqueta de predicción: las últimas H horas antes de la falla. Etiqueta de detección: desde que la forma principal del modo alcanza el 10 % de su firma (umbral supuesto).
  - `escalon_en: final` para las roturas, que ocurren tras precursores; `inicio` para sobrecarga, chatter y colisión, cuya condición dura el episodio.
  - `falla_lubricacion_rodamiento`: temperatura de rodamiento delta 30 → 35 °C. Con 30 solo llegaba a 90 °C en el instante de la falla; con 35 alcanza el nivel de disparo de 95 °C, igual que los demás modos de rodamiento (D-008, D-042).
- **Alternativas:** horizonte único de 24 h, descartado porque obliga a alargar artificialmente esas fallas o a evaluar lo imposible.
- **Fuentes:** D-008, D-037, D-042. La división es una decisión de diseño; el 10 % es un supuesto.
- **Confianza:** media.

## D-050 – Supuestos y límites del simulador
- **Decisión:**
  - Interpretaciones que D-037 no fijaba: sigmoide con k = 10; intermitente como pulsos de 1 a 3 pasos con tasa creciente y amplitud de 60 a 100 % de la firma.
  - Duraciones log-uniformes dentro de `duracion_h`; severidad de 0.95 a 1.15 por episodio, de modo que algunas fallas no alcanzan el umbral exacto.
  - 36 meses por unidad: con 12 no caben episodios suficientes, porque un motor acumula cerca de 7500 h de degradación por ronda de modos.
  - Una sola falla por unidad a la vez; es una simplificación.
  - Partición temporal común con purga de ventana + horizonte antes de cada corte. No hay partición por unidad porque varios activos solo tienen 2 unidades; se aparta del plan.
  - Regla contra el sesgo: **las firmas se calibran con M0 y con la física, nunca mirando el resultado de M3**.
- **Pendiente:** contraste numérico de las formas con los datasets públicos (D-036); hasta ahora las formas se basan en lo descrito en la literatura.
- **Fuentes:** D-036, D-037. Los parámetros son supuestos de diseño.
- **Confianza:** baja en los valores numéricos; media en la estructura.

## D-051 – Umbrales de vibración para bombas (ISO 10816-7 vía Europump)
- **Contexto:** ISO 20816-3 excluye las bombas rotodinámicas, así que 2.8/4.5 mm/s era un proxy fuera de alcance (D-003). El equipo no tiene acceso a las normas; se consultaron por fuentes públicas ([normas_fuentes_externas.md](normas_fuentes_externas.md)).
- **Decisión:** `bomba_centrifuga.vib_rms_mm_s`: alerta 2.8 → **5.1** y crítico 4.5 → **8.5** mm/s (Categoría II, ≤ 200 kW; la bomba es de 22 kW). Alerta = entrada a zona C y crítico = entrada a zona D, como en D-003. La tendencia queda en 0.25 × 5.1 = 1.275 mm/s por cálculo (D-004; confianza baja, el 25 % no se leyó en la parte 7).
  - Las firmas de vibración compartidas pasan a `tipo: frac_alerta`, proporcionales a la alerta del activo. Los demás activos conservan sus valores.
- **Alternativas:** Categoría I (4.0/6.6), reservada a servicio más crítico; mantener el proxy.
- **Fuentes:** Europump (2013), fuente sectorial que resume ISO 10816-7. Las Tablas A.1 y A.2 oficiales no se leyeron.
- **Confianza:** media.

## D-052 – Dificultad del simulador calibrada con datos públicos
- **Contexto:** la calibración inicial daba 100 % de detección a M0 y 0 % de alarmas en sano (ERR-020), por construcción.
- **Decisión:** se contrastó con AI4I 2020 y SKAB ([contraste_datasets.csv](../../reports/tables/contraste_datasets.csv)) y se ajustó:
  - Severidad 0.8–1.15: en AI4I la herramienta falla entre 198 y 253 min (mediana 214.5), una dispersión amplia alrededor del valor típico.
  - Firma incompleta: cada variable salvo la primera se omite con probabilidad 0.2 y varía ±10 %. En SKAB, varias anomalías no mueven canales que cabría esperar.
  - Señal sana sin recorte, centros por unidad más dispersos y deriva de sensor (15 % de la media banda cada 180 días; supuesto).
  - Excursiones operativas (0.5 por semana; supuesto): una variable sube hacia la alerta sin haber falla.
  - El ruido **no** se aumentó: la variación en sano de SKAB a 10 min (1–3 % en la mayoría de canales) es menor que la del simulador; SKAB es un banco estable.
  - Válvula hidráulica: `tiempo_ciclo_pct` pasa a forma lineal, porque una válvula lenta alarga el ciclo de forma sostenida (D-023). R27 exige además `tiempo_ciclo_en_rango`, y así la contaminación no compite cuando el ciclo ya está alterado.
- **Límites:** NASA IMS no se contrastó por su tamaño; SKAB es una sola bomba en banco y la ventana libre de anomalías da solo 17 muestras de 10 min.
- **Regla:** ningún valor se ajustó mirando resultados de M1–M3 (D-050).
- **Fuentes:** D-023, D-036, D-050; datasets AI4I 2020 y SKAB.
- **Confianza:** media en la estructura; baja en los parámetros marcados como supuesto.

## D-053 – Ventanas y entrenamiento de los modelos
- **Decisión:**
  - Un modelo por tipo de activo, porque los sensores y modos difieren. Entradas: solo sensores, con imputación hacia atrás en el tiempo y normalización calculada solo con entrenamiento.
  - Ventana de 6 h cada hora, y además una ventana en cada instante de falla, para que las fallas de un paso no caigan entre dos ventanas. La etiqueta es la más reciente desde la ventana anterior. Se descartan ventanas que crucen particiones o reparaciones.
  - Solo en entrenamiento se conservan 10 ventanas normales por cada ventana con falla; validación y test quedan intactos.
  - Pérdida focal con pesos por raíz de la frecuencia. Arquitectura elegida por F1 macro de **validación**; test no decide nada. Calibración por temperatura en validación.
- **Limitación:** una sola semilla (42) en esta fase; test tiene entre 12 y 29 episodios por activo y clases con solo 5 a 125 ventanas. Los intervalos de confianza con 5 semillas quedan para la Fase 7.
- **Fuentes:** D-049, D-050; configuración en `configs/train.yaml`.
- **Confianza:** media.

## D-054 – Ventanas grises y métricas de aviso temprano
- **Contexto:** las ventanas con degradación en curso a más de H de la falla estaban etiquetadas `normal`, y el 99.1 % de las "falsas alarmas" eran avisos tempranos correctos (ERR-023).
- **Decisión (del equipo):**
  - Esas ventanas son **grises**: no se entrenan ni entran al F1 ni a la falsa alarma.
  - La falsa alarma se mide solo con equipo sano, incluidos los confusores.
  - Sobre las ventanas grises se reporta aparte: porcentaje de ventanas y de episodios con aviso del modo correcto, y anticipación mediana en horas.
- **Alternativas:** clase adicional de degradación; etiquetar toda la degradación como la falla; dejarlas como normales.
- **Fuentes:** D-049, D-053.
- **Confianza:** media.

## D-055 – Confusores multivariable, más unidades y ajustes con datos públicos
- **Decisión (del equipo):**
  - **Confusores multivariable:** 11 condiciones de operación sin falla (carga alta sostenida, ambiente caluroso, punto de operación estrangulado, nivel bajo en succión, demanda sostenida de aire, lote pesado, sobrecarga temporal, desvío transitorio, material duro, programa agresivo) que mueven varias variables con subida y bajada graduales. Están en `failure_modes.yaml`; frecuencias y magnitudes son supuestos físicos y **no se iteraron mirando resultados**.
  - **Unidades:** 16 → 32. La última unidad de cada tipo queda solo para evaluación (`test_unidad`), además del corte temporal: mide la generalización a una máquina no vista y corrige la desviación del plan registrada en D-050.
  - **Omisión de firma:** 0.2 → 0.4, para acercarse a SKAB (33 % de canales con cambio de 1 desviación). Sigue siendo menos que lo observado (60 % esperado en el simulador).
  - **Herramienta:** severidad propia 0.72–0.95, con falla cerca de 215 min como en AI4I; el valor 240 de la firma se conserva como referencia del nivel crítico.
- **Fuentes:** D-036, D-050, D-052; AI4I 2020 y SKAB. Confusores: inferencia física.
- **Confianza:** media en la estructura; baja en los parámetros.

## D-056 – Integración del conocimiento: M0, M2 y M3
- **Decisión:**
  - **Conocimiento por ventana:** el motor de reglas recibe el último paso sin normalizar, la línea base de puesta en marcha (mediana de los primeros 14 días de la unidad; solo sensores, también para la unidad reservada) y las expresiones de técnicos de las 6 h previas.
  - **M0:** las certezas por clase, normalizadas; sin reglas disparadas, la clase es normal.
  - **M2:** la arquitectura de M1 de cada activo con una rama que recibe certezas de falla y grados de síntoma, combinada antes de la salida. Se reentrena con la misma semilla y criterio que M1.
  - **M3:** `alfa * p_M1 + (1 - alfa) * certeza_reglas`, con veto opcional (una alerta sin respaldo de reglas con certeza < 0.3 vuelve a normal).
  - **Criterio fijado antes de ver test:** mayor F1 macro de validación sobre `alfa` en {0.3, …, 0.8} y veto sí/no; empate, menor falsa alarma.
- **Resultado de la elección:** alfa entre 0.6 y 0.8 y **ningún activo eligió el veto**. Tres activos eligieron 0.8, el borde de la rejilla; no se amplió para no ajustar la rejilla después de ver resultados.
- **Limitación:** una semilla; las diferencias de F1 entre M1, M2 y M3 son de centésimas y pueden caer dentro de la variación entre semillas (Fase 7).
- **Fuentes:** D-043, D-053, D-054; configuración `fusion` en `configs/train.yaml`.
- **Confianza:** media.

---

## Resumen de conflictos registrados

| Tema | Valores en conflicto | Elección | Decisión |
|---|---|---|---|
| Vibración, tipo de soporte | rígido 1.4/2.8/4.5 vs. flexible 2.3/4.5/7.1 mm/s | rígido (más conservador) | D-003 |
| Número de bloques de OSA-CBM | 6 / 7 / 8 | 6 bloques + presentación | D-001 |
| Desbalance de corriente | "6–10 veces" vs. "6–10 %" a 1 % de tensión | equivalentes a 1 % | D-006 |
| Temperatura de rodamientos de motor | 90–110/95–120 (TECO) vs. 95/105 (Siemens) | 90/95 | D-008 |
| Rodamientos de bomba vs. de motor | 82/88 (KSB) vs. 90/95 | 82/88 en bomba y banda | D-009 |
| Banda de la etapa 1 de rodamiento | 20–60 kHz vs. 250–350 kHz | variable relativa | D-010 |
| Margen de NPSH | 1.05–1.5 (tablas de HI) vs. 2–10 (supresión total, A Marine Blog) | 1.3/1.1 | D-012 |
| Paro del compresor | 105 °C (riesgo para el aceite) vs. 110–115 °C (banda + 10–15 °C) | 110 °C | D-016 |
| Diferencial del separador | 0.55 bar (Gardner Denver) vs. 0.7 bar (Sullair, sin abrir) | 0.55 bar | D-018 |
| Fuga de sello | ≤ 0.5 ml/h (CIRCOR) vs. 0.5–3 ml/h (blog sobre API 682) vs. 9 ml/h como fuga mayor | 3/9 ml/h | D-015 |
| Rodamientos de bomba | 82/88 °C (KSB, blog) vs. 93/115 °C (nota de GIW, sin abrir) | 82/88 °C | D-009 |
| Aceite hidráulico máximo | 60/70 °C (Parker) vs. 82–85 °C | 60/70 °C | D-020 |
| Base de la regla de 10 °C del aceite | 40 / 60 / 75 °C | solo cualitativa | D-020 |
| Limpieza ISO 4406 | 18/16/13 (Parker, verificado) vs. 17/15/12 (no verificado) | 18/16/13 | D-021 |
| Año del dataset IMS | 2006 (artículo de Qiu) vs. 2007 (repositorio) | se citan ambos | D-036 |
| Aumento de temperatura de rodamiento al fallar | +8–15 °C (D-010) vs. umbrales de alerta 82–90 °C | +35 °C al momento de la falla | D-042 |

---

## Referencias (APA 7)

> Nota: en el texto se usan las siglas ISO, IEC, NEMA, IEEE y AIAG y VDA para las organizaciones que aquí figuran con su nombre completo. Salvo ANSI/HI 9.6.1, leída en copia pública, las normas son de pago y no se leyó su texto completo; sus valores se tomaron de las fuentes secundarias indicadas en cada decisión. Los DOI y los datos de libros se verificaron en Crossref, Open Library o DataCite el 2026-11-05 (ERR-005). Las marcas entre corchetes dicen qué se verificó; se retiran en el documento final.
- 4B Components. (s. f.-a). *Bulldog belt misalignment switch* [Hoja de datos]. https://www.go4b.com/usa/datasheets/Bulldog-datasheet-USA.pdf
- 4B Components. (s. f.-b). *M300 Slipswitch* [Hoja de datos]. https://www.go4b.com/usa/datasheets/M300%20Slipswitch_Datasheet_060225.pdf
- Acoem. (s. f.-a). *Do you know the 4 stages of bearing failure?* https://www.acoem.com/en/blog/do-you-know-the-4-stages-of-bearing-failure/
- Acoem. (s. f.-b). *3 types of mechanical looseness: What you need to know*. https://www.acoem.com/en/?p=1172
- Air Compressor Services. (s. f.). *D185 high discharge temperature: What it means and what usually causes it*. https://aircompressorservices.com/blogs/blog/d185-high-discharge-temperature
- Al-Hashmi, S., Mohammed, A., Nasir, I., & Elhaj, M. (2017). Spectrum analysis of vibration signals for cavitation monitoring. *Journal of Pure & Applied Sciences, 16*(1), 11–15. https://doi.org/10.51984/jopas.v16i1.16
- ALL-TEST Pro. (s. f.). *Eliminate voltage unbalance*. https://alltestpro.com/eliminate-voltage-unbalance/
- Altintas, Y. (2012). *Manufacturing automation: Metal cutting mechanics, machine tool vibrations, and CNC design* (2.ª ed.). Cambridge University Press. [datos verificados en Crossref; contenido de memoria]
- Anglian Compressors. (s. f.). *Troubleshooting low pressure in your air compressor*. https://angliancompressors.com/blog/troubleshooting-low-pressure-in-your-air-compressor/
- Atlas Copco. (s. f.). *Compressor overheating* [Entrada de blog]. https://www.atlascopco.com/en-ca/compressors/air-compressor-blog/compressor-overheating
- Automotive Industry Action Group & Verband der Automobilindustrie. (2019). *Failure mode and effects analysis – FMEA handbook* (1.ª ed.). Automotive Industry Action Group. [existencia verificada; contenido no leído]
- Bloch, H. P., & Budris, A. R. (2004). *Pump user's handbook: Life extension*. Fairmont Press. [datos verificados en Open Library; contenido de memoria]
- Bonnett, A. H., & Soukup, G. C. (1992). Cause and analysis of stator and rotor failures in three-phase squirrel-cage induction motors. *IEEE Transactions on Industry Applications, 28*(4), 921–937. https://doi.org/10.1109/28.148460
- Brennen, C. E. (1994). *Hydrodynamics of pumps*. Concepts ETI; Oxford University Press. [datos verificados en Open Library; contenido de memoria]
- Buchanan, B. G., & Shortliffe, E. H. (Eds.). (1984). *Rule-based expert systems: The MYCIN experiments of the Stanford Heuristic Programming Project*. Addison-Wesley.
- Carroll, J. (2013, octubre). *FM Hydraulics* [Reimpresión de artículo sobre barniz en sistemas hidráulicos]. Schaeffer Manufacturing. https://www.schaefferoil.com/cmss_files/attachmentlibrary/FM-Hydraulics.pdf
- Case Western Reserve University. (s. f.). *Bearing data center*. https://engineering.case.edu/bearingdatacenter
- CIRCOR International. (2018). *The ABC's of mechanical seal leaks and impact on thermal fluid operations*. https://www.circor.com/sites/default/files/imported-files/ABCs_of_Mechanical_Seal_Leaks.pdf
- Compressed Air Challenge. (2026). *Compressed air system leaks* (Fact Sheet #7, Rev. 1). https://www.compressedairchallenge.org/data/sites/1/media/library/factsheets2026/fact-sheet-7-compressed-air-system-leaks_updated2026.pdf
- Continental. (s. f.). *Causes of belt mistracking*. https://continental-industry.com/belt-mistracking
- Cummins, L., Sommers, A., Ramezani, S. B., Mittal, S., Jabour, J., Seale, M., & Rahimi, S. (2024). *Explainable predictive maintenance: A survey of current methods, challenges and opportunities* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2401.07871
- Dyer, D., & Stewart, R. M. (1978). Detection of rolling element bearing damage by statistical vibration analysis. *Journal of Mechanical Design, 100*(2), 229–235. https://doi.org/10.1115/1.3453905
- Edmac. (s. f.). *Why is my air compressor overheating?* https://www.edmac.com/en/blog/post/why-is-my-air-compressor-overheating
- Europump. (2013). *Pump vibration standards guidelines* (1.ª ed.). https://www.europump.net/files/Publications/Guides/Guidelines%200n%20Pump%20Vibration%20First%20edition%20Final%20July%202013.pdf
- Evans, J. (s. f.). *Three-phase voltage variation & unbalance*. Pumps & Systems. https://www.pumpsandsystems.com/three-phase-voltage-variation-unbalance-last-two-parts
- Fabrico. (s. f.-a). *Air compressor troubleshooting*. https://www.fabrico.io/blog/air-compressor-troubleshooting/
- Fabrico. (s. f.-b). *Conveyor belt mistracking causes and fixes*. https://www.fabrico.io/blog/conveyor-belt-mistracking-causes-and-fixes/
- Fabrico. (s. f.-c). *Hydraulic cylinder drift troubleshooting*. https://www.fabrico.io/blog/hydraulic-cylinder-drift-troubleshooting/
- Fabrico. (s. f.-d). *ISO 10816-3 vibration severity*. https://www.fabrico.io/blog/iso-10816-3-vibration-severity/
- Fabrico. (s. f.-e). *Rotary screw compressor maintenance: Oil, air-end and bearings*. https://www.fabrico.io/blog/screw-compressor-maintenance/
- Fabrico. (s. f.-f). *VFD overcurrent fault troubleshooting*. https://www.fabrico.io/es/blog/vfd-overcurrent-fault-troubleshooting/
- Filippenko, A., Brown, S., & Neal, A. (2002). *Vibration analysis for predictive maintenance of rotating machines* (U.S. Patent No. 6,370,957 B1). U.S. Patent and Trademark Office. https://patents.google.com/patent/US6370957
- Flexa Systems. (2026a). *PowerFlex 70 fault codes: F12, F48, F64 & more*. https://flexa-systems.com/blogs/news/powerflex-70-fault-codes-complete-guide
- Flexa Systems. (2026b). *Yaskawa A1000 fault codes: oC, Uv, oH complete guide*. https://flexa-systems.com/blogs/news/yaskawa-a1000-fault-codes-complete-guide
- Fluke. (2025, 18 de agosto). *Mechanical looseness: What it is and how to detect it*. https://www.fluke.com/en-au/learn/blog/predictive-maintenance/mechanical-looseness-what-it-is-how-to-detect
- FridayParts. (s. f.). *How to check if a hydraulic cylinder is leaking internally*. https://www.fridayparts.com/blog/how-to-check-if-a-hydraulic-cylinder-is-leaking-internally
- Glimm, B., Horrocks, I., Motik, B., Stoilos, G., & Wang, Z. (2014). HermiT: An OWL 2 reasoner. *Journal of Automated Reasoning, 53*(3), 245–269. https://doi.org/10.1007/s10817-014-9305-1
- Helwig, N., Pignanelli, E., & Schütze, A. (2015a). *Condition monitoring of hydraulic systems* [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CW21
- Helwig, N., Pignanelli, E., & Schütze, A. (2015b). Condition monitoring of a complex hydraulic system using multivariate statistics. En *2015 IEEE International Instrumentation and Measurement Technology Conference (I2MTC) Proceedings* (pp. 210–215). IEEE. https://doi.org/10.1109/I2MTC.2015.7151267
- Hydraulic Institute. (2017). *ANSI/HI 9.6.1-2017: Rotodynamic pumps – Guideline for NPSH margin*. https://law.resource.org/pub/us/cfr/ibr/inc/ansi/ansi.hi.9.6.1.2017.pdf [leída]
- Hydraulics & Pneumatics. (s. f.). *How well do you know your hydraulic fluid?* https://www.hydraulicspneumatics.com/200/TechZone/HydraulicFluids/Article/False/70639/TechZone-HydraulicFluids
- IEEE Motor Reliability Working Group. (1985). Report of large motor reliability survey of industrial and commercial installations, Part I. *IEEE Transactions on Industry Applications, IA-21*(4), 853–864. https://doi.org/10.1109/TIA.1985.349532
- Industrial Monitor Direct. (s. f.-a). *CNC tool wear monitoring methods: Load, acoustic, and probe*. https://industrialmonitordirect.com/blogs/knowledgebase/cnc-tool-wear-monitoring-methods-load-acoustic-and-probe
- Industrial Monitor Direct. (s. f.-b). *Allowable mechanical seal leakage: API 682 standards and calculation*. https://industrialmonitordirect.com/blogs/knowledgebase/allowable-mechanical-seal-leakage-api-682-standards-and-calculation
- INN. (s. f.). *ISO 20816-3:2022* [Ficha de la norma con su alcance]. Instituto Nacional de Normalización. https://ecommerce.inn.cl/iso-20816-3202283628
- Inspenet. (s. f.). *Cavitation phenomenon on industrial pumps*. https://inspenet.com/en/articles/cavitationphenomenon-on-industrial-pumps/
- Institute of Electrical and Electronics Engineers. (2014). *IEEE Std 519-2014 – IEEE recommended practice and requirements for harmonic control in electric power systems*. [vista por citas: PowerMonitors, s. f.]
- International Electrotechnical Commission. (2007). *IEC 60085:2007 Electrical insulation – Thermal evaluation and designation*.
- International Electrotechnical Commission. (2018). *IEC 60812:2018 Failure modes and effects analysis (FMEA and FMECA)*.
- International Electrotechnical Commission. (2022). *IEC 60034-1:2022 Rotating electrical machines – Part 1: Rating and performance*.
- International Organization for Standardization. (2003). *ISO 13374-1:2003 Condition monitoring and diagnostics of machines – Data processing, communication and presentation – Part 1: General guidelines*.
- International Organization for Standardization. (2016). *ISO 20816-1:2016 Mechanical vibration – Measurement and evaluation of machine vibration – Part 1: General guidelines*.
- International Organization for Standardization. (2018). *ISO 17359:2018 Condition monitoring and diagnostics of machines – General guidelines*.
- International Organization for Standardization. (2021). *ISO 4406:2021 Hydraulic fluid power – Fluids – Method for coding the level of contamination by solid particles*.
- International Organization for Standardization. (2022). *ISO 20816-3:2022 Mechanical vibration – Measurement and evaluation of machine vibration – Part 3: Industrial machinery with a power rating above 15 kW and operating speeds between 120 r/min and 30 000 r/min*. [reemplazada por la edición de 2026; ver D-003]
- Jardine, A. K. S., Lin, D., & Banjevic, D. (2006). A review on machinery diagnostics and prognostics implementing condition-based maintenance. *Mechanical Systems and Signal Processing, 20*(7), 1483–1510. https://doi.org/10.1016/j.ymssp.2005.09.012
- Karassik, I. J., Messina, J. P., Cooper, P., & Heald, C. C. (2008). *Pump handbook* (4.ª ed.). McGraw-Hill. [datos verificados en Open Library; contenido de memoria]
- Katser, I. D., & Kozitsin, V. O. (2020). *SKAB – Skoltech anomaly benchmark* [Conjunto de datos]. Kaggle. https://doi.org/10.34740/KAGGLE/DSV/1693952
- KSB GIW. (s. f.). *Why anti-friction bearings are heating up*. https://giw.ksb.com/blog/why-anti-friction-bearings-are-heating-up
- Kusiak, A. (2024). Federated explainable artificial intelligence (fXAI): A digital manufacturing perspective. *International Journal of Production Research, 62*(1–2), 171–182. https://doi.org/10.1080/00207543.2023.2238083
- Lai, C.-H., Huang, S.-H., Wu, T.-E., & Lai, C.-C. (2025). A study on tool breakage detection technology based on current sensing and non-contact signal analysis. *Sensors, 25*(13), Artículo 3880. https://doi.org/10.3390/s25133880
- Lamy, J.-B. (2017). Owlready: Ontology-oriented programming in Python with automatic classification and high level constructs for biomedical ontologies. *Artificial Intelligence in Medicine, 80*, 11–28. https://doi.org/10.1016/j.artmed.2017.07.002
- Lee, J., Qiu, H., Yu, G., Lin, J., & Rexnord Technical Services. (2007). *IMS bearing data set* [Conjunto de datos]. NASA Prognostics Data Repository, NASA Ames Research Center. https://data.phmsociety.org/nasa/
- Lei, Y., Li, N., Guo, L., Li, N., Yan, T., & Lin, J. (2018). Machinery health prognostics: A systematic review from data acquisition to RUL prediction. *Mechanical Systems and Signal Processing, 104*, 799–834. https://doi.org/10.1016/j.ymssp.2017.11.016
- Machinery Lubrication. (s. f.). *Hydraulic equipment slowdown – Nailing internal leakage*. https://www.machinerylubrication.com/Articles/Print/550
- MaintainX. (s. f.). *Gardner Denver rotary gas compressor SSE* [Procedimientos de mantenimiento]. https://www.getmaintainx.com/assets/gardner-denver/rotary-gas-compressor-sse
- Malloy Electric. (s. f.). *Industrial variable frequency drive troubleshooting guide*. https://www.malloyelectric.com/vfd-troubleshooting-guide
- A Marine Blog. (2017, 10 de agosto). *NPSH – How much is enough? (theory and exam)*. https://amarineblog.com/2017/08/10/npsh-how-much-is-enough/
- Martin Engineering. (s. f.-a). *Causes of conveyor belt mistracking*. https://foundations.martin-eng.com/knowledge/causes-of-conveyor-belt-mistracking
- Martin Engineering. (s. f.-b). *Root causes of belt mistracking*. https://blog.martin-eng.com/root-causes-of-belt-mistracking
- Matzka, S. (2020). Explainable artificial intelligence for predictive maintenance applications. En *2020 Third International Conference on Artificial Intelligence for Industries (AI4I)* (pp. 69–74). IEEE. https://doi.org/10.1109/AI4I49448.2020.00023
- MTD Media. (s. f.). *Avoiding spindle failure*. MTDCNC. https://mtdcnc.com/news/gti-spindle/avoiding-spindle-failure
- National Electrical Manufacturers Association. (2021). *ANSI/NEMA MG 1-2021 Motors and generators*.
- Nuvair. (s. f.). *Air/oil separator element for Rotair RVG10*. https://www.nuvair.com/rotair-air-oil-separator-rvg-10.html
- Ogawa, H., Konada, S., Tanaka, N., & Matsuda, T. (2022). *Apparatus and method for detecting occurrence of cavitation* (U.S. Patent No. 11,415,124 B2). U.S. Patent and Trademark Office. https://patents.google.com/patent/US11415124
- Oxmaint. (s. f.). *Water treatment vibration monitoring software: ISO 10816 guide*. https://oxmaint.com/industries/government/water-treatment-vibration-monitoring-software-iso-10816-guide
- Parker Hannifin. (s. f.). *Proportional pressure reducing valve VMY100K06NV1P* [Hoja de datos alojada por RS Components]. https://docs.rs-online.com/8c42/A700000015896018.pdf
- Piotrowski, J. (2006). *Shaft alignment handbook* (3.ª ed.). CRC Press. [datos verificados en Open Library; contenido de memoria]
- Power & Motion. (s. f.-a). *3 big problems caused by hot-running hydraulics*. https://www.powermotiontech.com/blog/3-big-problems-caused-hot-running-hydraulics
- Power & Motion. (s. f.-b). *The grave danger of energy contamination*. https://www.powermotiontech.com/hydraulics/hydraulic-fluids/article/21887494/the-grave-danger-of-energy-contamination
- PowerMonitors. (s. f.). *Updates and changes made to the IEEE 519 in the 2014 release*. https://powermonitors.com/whitepapers/updates-changes-ieee-519-2014/
- Precision Electric. (2025). *VFD ground fault trip and short circuit faults: Causes, detection and best practices*. https://www.precision-elec.com/wp-content/uploads/2025/06/VFD-Ground-Fault-Trip-and-Short-Circuit-Faults-Causes-Detection-and-Best-Practices.pdf
- Pumps & Systems. (2011, 17 de diciembre). *What determines seal leakage?* https://www.pumpsandsystems.com/what-determines-seal-leakage
- Pumps & Systems. (2012). *Hydraulic Institute publishes ANSI/HI 9.6.1–2012 rotodynamic pumps guideline for NPSH margin*. https://www.pumpsandsystems.com/?p=9219
- Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K., & Kawaguchi, Y. (2019). MIMII dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. En *Proceedings of the Detection and Classification of Acoustic Scenes and Events 2019 Workshop (DCASE2019)* (pp. 209–213). https://archive.nyu.edu/handle/2451/60761
- Qiu, H., Lee, J., Lin, J., & Yu, G. (2006). Wavelet filter-based weak signature detection method and its application on rolling element bearing prognostics. *Journal of Sound and Vibration, 289*(4–5), 1066–1090. https://doi.org/10.1016/j.jsv.2005.03.007
- Ran, Y., Zhou, X., Lin, P., Wen, Y., & Deng, R. (2019). *A survey of predictive maintenance: Systems, purposes and approaches* [Preprint]. arXiv. https://arxiv.org/abs/1912.07383
- Randall, R. B. (2011). *Vibration-based condition monitoring: Industrial, aerospace and automotive applications*. Wiley. https://doi.org/10.1002/9780470977668 [contenido de memoria]
- Randall, R. B., & Antoni, J. (2011). Rolling element bearing diagnostics—A tutorial. *Mechanical Systems and Signal Processing, 25*(2), 485–520. https://doi.org/10.1016/j.ymssp.2010.07.017
- Saxena, A., Goebel, K., Simon, D., & Eklund, N. (2008). Damage propagation modeling for aircraft engine run-to-failure simulation. En *2008 International Conference on Prognostics and Health Management* (pp. 1–9). IEEE. https://doi.org/10.1109/PHM.2008.4711414
- SFS. (s. f.). *ISO/FDIS 20816-3* [Registro de catálogo]. Suomen Standardisoimisliitto. https://store.sfs.fi/fi/isofdis-20816-3
- Shortliffe, E. H., & Buchanan, B. G. (1975). A model of inexact reasoning in medicine. *Mathematical Biosciences, 23*(3–4), 351–379. https://doi.org/10.1016/0025-5564(75)90047-4
- Siemens. (s. f.). *Siemens 880 user's manual* [Manual de motor, tabla de temperaturas de rodamientos]. https://manualzilla.com/doc/6980939/siemens-880-user-s-manual?page=10
- Smith, W. A., & Randall, R. B. (2015). Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study. *Mechanical Systems and Signal Processing, 64–65*, 100–131. https://doi.org/10.1016/j.ymssp.2015.04.021
- TECO-Westinghouse. (2008). *RTD alarm & trip settings* [Tabla técnica]. https://www.tecowestinghouse.com/Stock_Motor_PDF/RTD_Alarm_Trip_Settings.pdf
- Teti, R., Jemielniak, K., O'Donnell, G., & Dornfeld, D. (2010). Advanced monitoring of machining operations. *CIRP Annals, 59*(2), 717–739. https://doi.org/10.1016/j.cirp.2010.05.010
- U.S. Department of Energy. (2003). *Improving compressed air system performance: A sourcebook for industry*. Office of Energy Efficiency and Renewable Energy; Compressed Air Challenge. [datos verificados en Open Library; contenido visto vía Compressed Air Challenge, 2026]
- UCI Machine Learning Repository. (2020). *AI4I 2020 predictive maintenance dataset* [Conjunto de datos]. https://doi.org/10.24432/C5HS5C
- UE Systems. (s. f.). *Reduce unplanned downtime: Learn the warning signs of bearing failure*. https://www.uesystems.com/reduce-unplanned-downtime-learn-the-wearning-signs-of-bearing-failure/
- Unitec-D. (2026). *Troubleshooting screw compressor high discharge temperature*. https://www.unitecd.com/en/troubleshooting-screw-compressor-high-discharge-temperature/
- Vibromera. (s. f.). *ISO 20816-3* [Entrada de glosario]. https://vibromera.eu/glossary/iso-20816-3
- Vibromera. (2025). *Alarm level in vibration monitoring: Threshold guide*. https://vibromera.eu/?p=20619
- World Fertilizer. (2022, 14 de octubre). *Martin Engineering: Identifying and addressing conveyor idler issues*. https://www.worldfertilizer.com/materials-handling/14102022/martin-engineering-identifying-and-addressing-conveyor-idler-issues/
- Zhou, Z., Sun, J., Cai, W., & Liu, W. (2023). Test investigation and rule analysis of bearing fault diagnosis in induction motors. *Energies, 16*(2), Artículo 699. https://doi.org/10.3390/en16020699
