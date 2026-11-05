# Registro de decisiones de conocimiento (ADR) – Metal Tech

> **Autor:** agente Investigador, Fase 1 · **Fecha:** 2026-10-29 · **Estado:** borrador, pendiente de la revisión cruzada del agente Revisor.
> **Técnica:** revisión documental asistida por agente (búsqueda web y lectura de fuentes). No hubo entrevistas ni participación de personas.
> **Archivos que dependen de este registro:** [`configs/assets.yaml`](../../configs/assets.yaml), [`configs/failure_modes.yaml`](../../configs/failure_modes.yaml), [`knowledge/rules/rules.yaml`](../rules/rules.yaml), [`knowledge/lexicon/expresiones.yaml`](../lexicon/expresiones.yaml), [`fmea.yaml`](fmea.yaml) / [`fmea.md`](fmea.md), [`matriz_adquisicion.md`](matriz_adquisicion.md), [`datasets_referencia.md`](datasets_referencia.md).

## Reglas de decisión aplicadas

1. Cada umbral y cada regla tiene respaldo de **≥ 2 fuentes o 1 norma**. Cuando no se alcanza, la decisión se marca con confianza **baja** y queda como supuesto explícito.
2. Si las fuentes no coinciden, se elige el valor **más conservador**, es decir, el que alerta antes, y el conflicto se registra en la decisión.
3. Las normas ISO, IEC, NEMA, HI e IEEE son de pago. Sus valores se tomaron de **fuentes secundarias que las citan**, y así se indica en cada caso. Se recomienda verificar contra el texto oficial si la universidad tiene acceso.
4. **Confianza:**
   - **alta:** norma, o ≥ 2 fuentes independientes concordantes, más física clara.
   - **media:** fuentes secundarias concordantes, o una norma solo vista por citas.
   - **baja:** valor heurístico o supuesto del agente con una sola fuente o ninguna verificable.

## Índice

| ID | Tema | Confianza |
|---|---|---|
| D-001 | Marco de monitoreo de condición (ISO 17359 / ISO 13374) | alta |
| D-002 | Alcance de activos | media |
| D-003 | Zonas de severidad de vibración (ISO 20816-3) | alta |
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
| D-015 | Desgaste de sello mecánico | baja |
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
| D-030 | Fallas de variador | baja |
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
- **Fuentes:** ISO (2022), con valores vía Fabrico (s. f.-a) y Oxmaint (s. f.); ISO (2016).
- **Confianza:** alta para motor, bomba y compresor; baja para el CNC.

## D-004 – Criterio de cambio de vibración (tendencia)
- **Contexto:** el enunciado habla de "vibración creciente". Un valor absoluto en zona B puede ocultar un deterioro rápido.
- **Decisión:**
  - Se define `vibracion_creciente` como un aumento respecto a la línea base sana de la unidad **≥ 25 % del límite B/C** (0.25 × 2.8 = 0.7 mm/s).
  - Corresponde al "criterio II" (cambio de magnitud) de la serie ISO 10816/20816, que considera significativo un cambio del 25 % del valor del límite B/C aunque no se cambie de zona.
- **Alternativas:** pendiente lineal mínima por semana; doble de la línea base, que es la práctica común de software de monitoreo.
- **Fuentes:** ISO (2016), parte 1, criterio de cambio. El agente no pudo leer el texto oficial: el 25 % proviene de su conocimiento previo de la norma y debe verificarse. Randall (2011) respalda el uso de tendencias respecto a la línea base.
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
- **Fuentes:** TECO-Westinghouse (2008), con contenido leído a través del extracto del buscador porque el PDF no se pudo leer; Siemens (s. f.); Acoem (s. f.), según la cual la temperatura sube en las etapas tardías.
- **Confianza:** media.

## D-009 – Temperatura de rodamientos de bomba y tambor de banda
- **Decisión:** nominal 45–68 °C, **alerta 82 °C** y **crítico 88 °C** en la bomba. Los mismos umbrales se aplican al tambor motriz de la banda.
- **Conflicto:** los valores para motores (D-008) son más altos. Se usan los de bomba (KSB GIW: normal 60–68 °C, alarma 180 °F ≈ 82 °C, paro 190 °F ≈ 88 °C) porque son los más conservadores y específicos de bombas.
- **Fuentes:** KSB GIW (s. f.); TECO-Westinghouse (2008), como contraste.
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
  4. La temperatura del rodamiento sube **8–15 °C** sobre la línea base solo en la etapa tardía, por eso `retardo_frac = 0.7` en el simulador.
- **Alternativas:** umbrales absolutos en gE de envolvente, que dependen del sensor y de la máquina.
- **Conflictos:**
  - La banda de la etapa 1 difiere entre fuentes: 20–60 kHz (Acoem) frente a 250–350 kHz (UE Systems). No afecta al simulador, que usa una variable relativa.
  - Las relaciones 2×/4× **no** salen de una norma: son práctica de la industria. Ese punto tiene confianza baja.
- **Fuentes:** Randall y Antoni (2011); Dyer y Stewart (1978), que proponen la curtosis para detectar daño de rodamientos; Acoem (s. f.); UE Systems (s. f.); Smith y Randall (2015).
- **Confianza:** media en general; baja para los factores 2×/4×.

## D-011 – Firmas espectrales de desbalanceo y desalineación
- **Contexto:** "desalineación y desbalanceo de ejes (vibración creciente)". El simulador produce rasgos espectrales simples.
- **Decisión:**
  - **Desbalanceo:** la componente 1X radial domina (fracción ≥ 0.8 de la energía) y la vibración axial es baja.
  - **Desalineación:** la amplitud 2X es ≥ 50 % de la 1X y la vibración axial es ≥ 50 % de la radial.
  - Los dos casos requieren además vibración global en alerta o creciente.
- **Alternativas:** usar solo la RMS global, que no distingue las dos fallas.
- **Fuentes:** Randall (2011); Piotrowski (2006). Ambos son textos de referencia consultados de memoria y no por web: las relaciones 0.5 son reglas prácticas.
- **Confianza:** media. Las fracciones exactas tienen confianza baja.

## D-012 – Margen de NPSH
- **Contexto:** cavitación en bombas.
- **Decisión:**
  - Se usa la relación **NPSHA/NPSH3**. NPSH3 es la NPSH que produce una caída del 3 % en la altura.
  - Valores: nominal 1.5–3.0, **alerta ≤ 1.3** y **crítico ≤ 1.1**.
  - ANSI/HI 9.6.1 da relaciones mínimas típicas de **1.1–1.3** según la aplicación: 1.1 para bombas de catálogo o de proceso, 1.3 para algunas de mayor energía. El crítico se fija en el mínimo de la guía y la alerta en el extremo superior del rango.
- **Alternativas:** margen absoluto en metros, que depende de la bomba. Otra alternativa es exigir 2–4 para eliminar toda cavitación: es demasiado estricto y la mayoría de las bombas sanas lo violarían.
- **Conflicto:** las relaciones de 2 a más de 4 para "supresión total" de la cavitación vienen de una fuente secundaria. Se registran pero no se usan, porque generarían falsas alarmas.
- **Fuentes:** Hydraulic Institute (2017); Pumps & Systems (2012); A Marine Blog (2017).
- **Confianza:** alta.

## D-013 – Firma de cavitación
- **Decisión:** la cavitación se reconoce por esta combinación:
  1. margen de NPSH bajo;
  2. vibración de **banda ancha en alta frecuencia** (~1–20 kHz), con ruido "de grava" por encima de ~1 kHz;
  3. **inestabilidad** de caudal y presión, medida como coeficiente de variación (alerta 5 %, crítico 10 %);
  4. **caída de la presión de descarga o de la altura**. Por definición, NPSH3 implica una caída del 3 % de la altura. Se fija la alerta en −5 % (95 % de la nominal) y el crítico en −10 %, para no confundir la cavitación con la variación normal de proceso.
- **Alternativas:** detectar solo por vibración global, que es poco específica.
- **Conflicto:** los umbrales de coeficiente de variación (5/10 %) son supuestos del agente. La idea de usar el coeficiente de variación de la presión de succión para detectar cavitación viene de una patente (Ebara, US11415124B2), pero sin valores.
- **Fuentes:** Hydraulic Institute (2017); Brennen (1994); Inspenet (s. f.); Google Patents (2022).
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
  - Variable `fuga_sello_ml_h`: nominal 0–2 ml/h, **alerta 5 ml/h** (≈ 1–2 gotas por minuto) y **crítico 20 ml/h**.
  - La vibración elevada y la operación en seco son las causas principales.
- **Alternativas:** no modelar el sello. Se descarta porque el enunciado lo exige.
- **Hueco:** no se encontró una fuente abierta con tasas de fuga admisibles en ml/h. API 682 trata emisiones en otros términos. Es un **supuesto** del agente.
- **Fuentes:** Bloch y Budris (2004), sobre causas de falla de sellos, consultado de memoria. No hay una segunda fuente verificada.
- **Confianza:** baja.

## D-016 – Temperatura de descarga del compresor de tornillo
- **Decisión:**
  - Rango normal 75–95 °C (≈ 77–93 °C según la fuente), **alerta 100 °C** y **crítico 110 °C**.
  - Causas: enfriador sucio, aceite bajo o degradado, filtros obstruidos, termostática que no envía aceite al enfriador, ventilación deficiente y separador obstruido.
- **Conflicto:** los puntos de paro varían por fabricante; habitualmente rondan 110–120 °C. No se halló el valor de un manual específico, así que se elige el **inferior** (110 °C).
- **Fuentes:** Air Compressor Services (s. f.); Atlas Copco (s. f.); Edmac (s. f.).
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
- **Fuentes:** Anglian Compressors (s. f.); Fabrico (s. f.-b); U.S. Department of Energy (2003).
- **Confianza:** media. El valor de 93 % es elección del agente, con confianza baja.

## D-018 – Diferencial del separador de aceite
- **Decisión:** nominal 0.1–0.4 bar, **alerta 0.7 bar** (≈ 10 psi) y **crítico 1.0 bar**.
- **Hueco:** las fuentes consultadas dicen "comparar con el máximo del fabricante" sin dar un número. El valor de 0.7 bar (10 psi) es un criterio de reemplazo habitual en manuales de compresores que el agente recuerda, pero **no pudo verificarlo**.
- **Fuentes:** Anglian Compressors (s. f.), que recomienda medir el diferencial y cambiar el elemento por horas.
- **Confianza:** baja.

## D-019 – Fugas de la red de aire y tiempo en carga
- **Decisión:**
  - En plantas sin programa de mantenimiento, las fugas suelen consumir el **20–30 %** de la producción de aire, y la meta es < 10 %.
  - En el simulador, una fuga aumenta el tiempo en carga: nominal 40–75 %, **alerta ≥ 85 %** y **crítico ≥ 95 %**, con presión a la baja.
  - El evento confusor "pico de demanda" (D-037) imita esta firma de forma transitoria.
- **Fuentes:** U.S. Department of Energy (2003); Anglian Compressors (s. f.).
- **Confianza:** media.

## D-020 – Temperatura del aceite hidráulico
- **Decisión:**
  - Nominal 40–55 °C, **alerta 60 °C** y **crítico 70 °C**.
  - `alerta_baja` de 20 °C para el aceite frío, con viscosidad alta (D-023).
- **Conflicto:**
  - Las hojas de datos de válvulas proporcionales Parker dan 60 °C como temperatura máxima de operación y 70 °C como máxima del fluido en algunos modelos.
  - Power & Motion menciona 82–85 °C como límite para sellos y mangueras.
  - Se elige el valor **más conservador**, el de los componentes más sensibles (válvulas).
- **Hueco:** la regla de "vida del aceite a la mitad por cada 10 °C" tiene una temperatura base distinta en cada fuente (40, 60 o 75 °C), así que solo se usa cualitativamente.
- **Fuentes:** Parker Hannifin (s. f.); Power & Motion (s. f.-a, s. f.-b); Hydraulics & Pneumatics (s. f.).
- **Confianza:** media.

## D-021 – Limpieza del aceite hidráulico (ISO 4406)
- **Decisión:**
  - Objetivo **ISO 4406 18/16/13**, que es lo que exigen las hojas de datos Parker de válvulas proporcionales.
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
- **Fuentes:** Machinery Lubrication (s. f.); FridayParts (s. f.); Fabrico (s. f.-c).
- **Confianza:** media para la firma; baja para los números.

## D-023 – Interpretación de "la prensa está dura"
- **Decisión:**
  - Se interpreta como **resistencia hidráulica**: más presión de trabajo (≥ 110 % de la receta) y más tiempo de ciclo para la misma operación.
  - Causas candidatas, en orden: válvula direccional o proporcional pegada o lenta (barniz, partículas), contaminación, y aceite frío con viscosidad alta.
  - Una fuga interna haría la prensa "floja" (presión baja, deriva), así que recibe un FC bajo en el léxico.
- **Alternativas:**
  - Interpretarla como fuga interna. No encaja con la física.
  - Interpretarla como dureza del material de la pieza. Sería un problema de proceso, fuera del alcance.
- **Fuentes:** Parker Hannifin (s. f.), que vincula la limpieza del aceite con el funcionamiento de la válvula; Machinery Lubrication (s. f.); física de la viscosidad. No hay fuente que defina la expresión.
- **Confianza:** baja.

## D-024 – Corrimiento de banda
- **Decisión:**
  - Causas: empalme no escuadrado, rodillos o tambores fuera de escuadra o trabados, carga descentrada, banda acopada y acumulación de material.
  - Síntomas: desvío lateral, desgaste de bordes y derrame. La corriente del motor sube por el arrastre adicional.
  - Umbrales de desvío lateral: nominal 0–10 mm, **alerta 25 mm** y **crítico 50 mm**, que es cuando suelen actuar los interruptores de desalineación.
- **Hueco:** no se halló un valor numérico normativo de desvío (CEMA no se consultó por ser de pago). Los mm son supuestos del agente.
- **Fuentes:** Martin Engineering (s. f.-a, s. f.-b); Continental (s. f.); Fabrico (s. f.-d).
- **Confianza:** media para la firma; baja para los mm.

## D-025 – Deslizamiento y rotura de banda
- **Decisión:**
  - **Deslizamiento** (velocidad del tambor frente a la de la banda): **alerta 2 %** y **crítico 5 %**. Sus causas son tensión baja, recubrimiento del tambor gastado y agua o material entre banda y tambor.
  - **Rotura:** la velocidad de la banda baja a ≤ 10 % con el motor en marcha, y la corriente cae a la de vacío (≤ 30 % In).
  - Precursor opcional: el empalme dañado da un golpe periódico que eleva la curtosis.
- **Hueco:** no se encontró fuente con valores de deslizamiento. La rotura se deduce de la física (sin carga, sin par).
- **Fuentes:** Martin Engineering (s. f.-a), sobre el empalme como causa de problemas; física de la transmisión por fricción (Euler-Eytelwein, conocimiento general).
- **Confianza:** baja.

## D-026 – Falla de rodillos ("cascabeleo en la línea")
- **Decisión:**
  - Un rodillo trabado actúa como barra de fricción, desvía la banda y aumenta el arrastre.
  - Un rodillo con el rodamiento dañado produce impactos, que elevan la curtosis y causan el traqueteo.
  - Firma: curtosis ≥ 4, corriente en aumento y desvío lateral tardío.
- **Fuentes:** Martin Engineering vía World Fertilizer (2022); Fabrico (s. f.-d); Randall y Antoni (2011), sobre los impactos.
- **Confianza:** media.

## D-027 – Desgaste de herramienta CNC
- **Decisión:**
  - Vida de la herramienta: **alerta 200 min** y **crítico 240 min** de corte acumulado, tomada del modo TWF de AI4I 2020 (falla o reemplazo aleatorio entre 200 y 240 min).
  - Con el desgaste del flanco sube la fuerza de corte y, con ella, la carga y la corriente del husillo. Carga relativa a la línea base de la operación: **alerta 1.2×** y **crítico 1.4×**.
- **Conflicto:** no se verificó un porcentaje de aumento de corriente en la literatura: el 20 %/40 % es elección del agente. El estudio de gemelo digital normaliza la corriente, pero no da un umbral.
- **Fuentes:** Matzka (2020); UCI Machine Learning Repository (2020); Teti et al. (2010); Industrial Monitor Direct (s. f.).
- **Confianza:** media para los minutos; baja para el factor de carga.

## D-028 – Rotura de herramienta y colisión ("golpes en CNC")
- **Decisión:**
  - **Rotura:** caída súbita de la carga (≤ 0.5× en pleno corte) con un pico de vibración ≥ 5 g. Los estudios con sensor de corriente detectan la rotura en 1–3 s, por anomalías en el dominio de la frecuencia.
  - **Colisión:** pico ≥ 5 g (crítico 10 g) con carga ≥ 1.4×.
  - La corriente sola no detecta el astillado; para eso se necesita la vibración.
- **Hueco:** los umbrales en g son supuestos del agente.
- **Fuentes:** Teti et al. (2010); estudio de detección de rotura por corriente (2025, PMC12251610); Industrial Monitor Direct (s. f.).
- **Confianza:** media para la firma; baja para los g.

## D-029 – Chatter y sobrecalentamiento de husillo
- **Decisión:**
  - **Chatter:** carga fluctuante (coeficiente de variación ≥ 10 %) y vibración de alta frecuencia ≥ 2×. Se corrige cambiando la velocidad hacia un lóbulo estable o reduciendo la profundidad o el voladizo.
  - **Husillo:** nominal 25–40 °C, **alerta 50 °C** y **crítico 60 °C**.
  - Para la vibración del cabezal se usa el proxy de ISO 20816-3 (D-003).
- **Hueco:** no hay fuente verificada para las temperaturas del husillo ni para el coeficiente de variación. Son **supuestos**.
- **Fuentes:** Altintas (2012); Teti et al. (2010).
- **Confianza:** baja.

## D-030 – Fallas de variador ("está disparando por nada")
- **Decisión:**
  - Causas de disparos intermitentes con carga normal: rampas de aceleración demasiado cortas, datos de motor mal cargados, cable largo sin reactancia, falla a tierra por aislamiento o cable degradado, sobretensión del bus DC por regeneración y sobretemperatura.
  - Umbrales:
    - disparos: **alerta ≥ 1 en 24 h**, **crítico ≥ 3 en 24 h**;
    - THD de tensión: **alerta 8 %**, el límite de IEEE 519-2014 para barras ≤ 1 kV; crítico 12 %;
    - bus DC: alerta 115 % y crítico 130 %;
    - disipador: alerta 75 °C y crítico 85 °C.
- **Conflicto:** los códigos de falla y los niveles de disparo del bus DC dependen del fabricante y de la serie (por ejemplo, ABB ACS355 y ACS880 numeran distinto).
- **Fuentes:** IEEE (2014), para la THD; Malloy Electric (s. f.); Fabrico (s. f.-e); Precision Electric (2025).
- **Confianza:** alta para la THD; baja para el bus DC, la temperatura y el conteo de disparos.

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
- **Fuentes:** IEC (2022), sobre la refrigeración IC y el calentamiento; Bonnett y Soukup (1992); TECO-Westinghouse (2008); Acoem (s. f.).
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
  - Detalle en [datasets_referencia.md](datasets_referencia.md).
- **Fuentes:** Matzka (2020); Lee et al. (2007); Qiu et al. (2006); Smith y Randall (2015); Saxena et al. (2008); Katser y Kozitsin (2020); Purohit et al. (2019).
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
| Margen de NPSH | 1.1–1.3 (HI) vs. 2–4 (supresión total) | 1.3/1.1 | D-012 |
| Paro del compresor | 110–120 °C según fabricante | 110 °C | D-016 |
| Aceite hidráulico máximo | 60/70 °C (Parker) vs. 82–85 °C | 60/70 °C | D-020 |
| Base de la regla de 10 °C del aceite | 40 / 60 / 75 °C | solo cualitativa | D-020 |
| Limpieza ISO 4406 | 18/16/13 (Parker, verificado) vs. 17/15/12 (no verificado) | 18/16/13 | D-021 |
| Año del dataset IMS | 2006 (artículo de Qiu) vs. 2007 (repositorio) | se citan ambos | D-036 |

---

## Referencias (APA 7)

> Nota: las normas (ISO, IEC, NEMA, HI, IEEE, AIAG-VDA) son de pago y no se leyó su texto completo. Sus valores se tomaron de las fuentes secundarias indicadas en cada decisión. Las fuentes marcadas "[consultada de memoria]" son obras de referencia ampliamente conocidas que el agente no pudo abrir en línea; deben verificarse antes del documento final.

- A Marine Blog. (2017, 10 de agosto). *NPSH – How much is enough? (theory and exam)*. https://amarineblog.com/2017/08/10/npsh-how-much-is-enough/
- Acoem. (s. f.). *Do you know the 4 stages of bearing failure?* https://www.acoem.com/en/blog/do-you-know-the-4-stages-of-bearing-failure/
- AIAG & VDA. (2019). *Failure mode and effects analysis – FMEA handbook* (1.ª ed.). Automotive Industry Action Group. [consultada de memoria]
- Air Compressor Services. (s. f.). *D185 high discharge temperature: What it means and what usually causes it*. https://aircompressorservices.com/blogs/blog/d185-high-discharge-temperature
- ALL-TEST Pro. (s. f.). *Eliminate voltage unbalance*. https://alltestpro.com/eliminate-voltage-unbalance/
- Altintas, Y. (2012). *Manufacturing automation: Metal cutting mechanics, machine tool vibrations, and CNC design* (2.ª ed.). Cambridge University Press. [consultada de memoria]
- Anglian Compressors. (s. f.). *Troubleshooting low pressure in your air compressor*. https://angliancompressors.com/blog/troubleshooting-low-pressure-in-your-air-compressor/
- Atlas Copco. (s. f.). *Compressor overheating* [Entrada de blog]. https://www.atlascopco.com/en-ca/compressors/air-compressor-blog/compressor-overheating
- Bloch, H. P., & Budris, A. R. (2004). *Pump user's handbook: Life extension*. Fairmont Press. [consultada de memoria]
- Bonnett, A. H., & Soukup, G. C. (1992). Cause and analysis of stator and rotor failures in three-phase squirrel-cage induction motors. *IEEE Transactions on Industry Applications, 28*(4), 921–937. https://doi.org/10.1109/28.148460
- Brennen, C. E. (1994). *Hydrodynamics of pumps*. Concepts ETI; Oxford University Press. [consultada de memoria]
- Buchanan, B. G., & Shortliffe, E. H. (Eds.). (1984). *Rule-based expert systems: The MYCIN experiments of the Stanford Heuristic Programming Project*. Addison-Wesley.
- Case Western Reserve University. (s. f.). *Bearing data center*. https://engineering.case.edu/bearingdatacenter
- Continental. (s. f.). *Causes of belt mistracking*. https://continental-industry.com/belt-mistracking
- Cummins, L., Sommers, A., Ramezani, S. B., Mittal, S., Jabour, J., Seale, M., & Rahimi, S. (2024). *Explainable predictive maintenance: A survey of current methods, challenges and opportunities* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2401.07871
- Dyer, D., & Stewart, R. M. (1978). Detection of rolling element bearing damage by statistical vibration analysis. *Journal of Mechanical Design, 100*(2), 229–235. [consultada de memoria; DOI no verificado]
- Edmac. (s. f.). *Why is my air compressor overheating?* https://www.edmac.com/en/blog/post/why-is-my-air-compressor-overheating
- Evans, J. (s. f.). *Three-phase voltage variation & unbalance*. Pumps & Systems. https://www.pumpsandsystems.com/three-phase-voltage-variation-unbalance-last-two-parts
- Fabrico. (s. f.-a). *ISO 10816-3 vibration severity*. https://www.fabrico.io/blog/iso-10816-3-vibration-severity/
- Fabrico. (s. f.-b). *Air compressor troubleshooting*. https://www.fabrico.io/blog/air-compressor-troubleshooting/
- Fabrico. (s. f.-c). *Hydraulic cylinder drift troubleshooting*. https://www.fabrico.io/ro/blog/hydraulic-cylinder-drift-troubleshooting/
- Fabrico. (s. f.-d). *Conveyor belt mistracking causes and fixes*. https://www.fabrico.io/blog/conveyor-belt-mistracking-causes-and-fixes/
- Fabrico. (s. f.-e). *VFD overcurrent fault troubleshooting*. https://www.fabrico.io/es/blog/vfd-overcurrent-fault-troubleshooting/
- FridayParts. (s. f.). *How to check if a hydraulic cylinder is leaking internally*. https://www.fridayparts.com/blog/how-to-check-if-a-hydraulic-cylinder-is-leaking-internally
- Google Patents. (2022). *US11415124B2 – Apparatus and method for detecting occurrence of cavitation*. https://patents.google.com/patent/US11415124
- Hydraulic Institute. (2017). *ANSI/HI 9.6.1-2017 Rotodynamic pumps guideline for NPSH margin*. https://law.resource.org/pub/us/cfr/ibr/inc/ansi/ansi.hi.9.6.1.2017.pdf
- Hydraulics & Pneumatics. (s. f.). *How well do you know your hydraulic fluid?* https://www.hydraulicspneumatics.com/200/TechZone/HydraulicFluids/Article/False/70639/TechZone-HydraulicFluids
- IEC. (2007). *IEC 60085:2007 Electrical insulation – Thermal evaluation and designation*. International Electrotechnical Commission.
- IEC. (2018). *IEC 60812:2018 Failure modes and effects analysis (FMEA and FMECA)*. International Electrotechnical Commission.
- IEC. (2022). *IEC 60034-1:2022 Rotating electrical machines – Part 1: Rating and performance*. International Electrotechnical Commission.
- IEEE. (2014). *IEEE Std 519-2014 – IEEE recommended practice and requirements for harmonic control in electric power systems*. Institute of Electrical and Electronics Engineers. [límite THD 8 % ≤ 1 kV, consultado de memoria]
- IEEE Motor Reliability Working Group. (1985). Report of large motor reliability survey of industrial and commercial installations, Part I. *IEEE Transactions on Industry Applications, IA-21*(4), 853–864. [consultada de memoria]
- Industrial Monitor Direct. (s. f.). *CNC tool wear monitoring methods: Load, acoustic, and probe*. https://industrialmonitordirect.com/blogs/knowledgebase/cnc-tool-wear-monitoring-methods-load-acoustic-and-probe
- Inspenet. (s. f.). *Cavitation phenomenon on industrial pumps*. https://inspenet.com/en/articles/cavitationphenomenon-on-industrial-pumps/
- ISO. (2003). *ISO 13374-1:2003 Condition monitoring and diagnostics of machines – Data processing, communication and presentation – Part 1: General guidelines*. International Organization for Standardization.
- ISO. (2016). *ISO 20816-1:2016 Mechanical vibration – Measurement and evaluation of machine vibration – Part 1: General guidelines*. International Organization for Standardization.
- ISO. (2018). *ISO 17359:2018 Condition monitoring and diagnostics of machines – General guidelines*. International Organization for Standardization.
- ISO. (2021). *ISO 4406:2021 Hydraulic fluid power – Fluids – Method for coding the level of contamination by solid particles*. International Organization for Standardization.
- ISO. (2022). *ISO 20816-3:2022 Mechanical vibration – Measurement and evaluation of machine vibration – Part 3: Industrial machinery with a power rating above 15 kW and operating speeds between 120 r/min and 30 000 r/min*. International Organization for Standardization.
- Jardine, A. K. S., Lin, D., & Banjevic, D. (2006). A review on machinery diagnostics and prognostics implementing condition-based maintenance. *Mechanical Systems and Signal Processing, 20*(7), 1483–1510. https://doi.org/10.1016/j.ymssp.2005.09.012
- Karassik, I. J., Messina, J. P., Cooper, P., & Heald, C. C. (2008). *Pump handbook* (4.ª ed.). McGraw-Hill. [consultada de memoria]
- Katser, I. D., & Kozitsin, V. O. (2020). *Skoltech Anomaly Benchmark (SKAB)* [Conjunto de datos]. GitHub. https://github.com/waico/SKAB
- KSB GIW. (s. f.). *Why anti-friction bearings are heating up*. https://giw.ksb.com/blog/why-anti-friction-bearings-are-heating-up
- Kusiak, A. (2024). Federated explainable artificial intelligence (fXAI): A digital manufacturing perspective. *International Journal of Production Research, 62*(1–2), 171–182. https://doi.org/10.1080/00207543.2023.2238083
- Lee, J., Qiu, H., Yu, G., Lin, J., & Rexnord Technical Services. (2007). *IMS bearing data set* [Conjunto de datos]. NASA Prognostics Data Repository, NASA Ames Research Center. https://data.phmsociety.org/nasa/
- Lei, Y., Li, N., Guo, L., Li, N., Yan, T., & Lin, J. (2018). Machinery health prognostics: A systematic review from data acquisition to RUL prediction. *Mechanical Systems and Signal Processing, 104*, 799–834. https://doi.org/10.1016/j.ymssp.2017.11.016
- Machinery Lubrication. (s. f.). *Hydraulic equipment slowdown – Nailing internal leakage*. https://www.machinerylubrication.com/Articles/Print/550
- Malloy Electric. (s. f.). *Industrial variable frequency drive troubleshooting guide*. https://www.malloyelectric.com/vfd-troubleshooting-guide
- Martin Engineering. (s. f.-a). *Root causes of belt mistracking*. https://blog.martin-eng.com/root-causes-of-belt-mistracking
- Martin Engineering. (s. f.-b). *Causes of conveyor belt mistracking*. https://foundations.martin-eng.com/knowledge/causes-of-conveyor-belt-mistracking
- Matzka, S. (2020). Explainable artificial intelligence for predictive maintenance applications. En *2020 Third International Conference on Artificial Intelligence for Industries (AI4I)* (pp. 69–74). IEEE. https://ieeexplore.ieee.org/abstract/document/9253083
- NEMA. (2021). *ANSI/NEMA MG 1-2021 Motors and generators*. National Electrical Manufacturers Association.
- Oxmaint. (s. f.). *Water treatment vibration monitoring software: ISO 10816 guide*. https://oxmaint.com/industries/government/water-treatment-vibration-monitoring-software-iso-10816-guide
- Parker Hannifin. (s. f.). *Proportional directional control valves D1FB/D3FB – Technical data* [Hoja de datos alojada por RS Components]. https://docs.rs-online.com/8c42/A700000015896018.pdf
- Piotrowski, J. (2006). *Shaft alignment handbook* (3.ª ed.). CRC Press. [consultada de memoria]
- Power & Motion. (s. f.-a). *3 big problems caused by hot-running hydraulics*. https://www.powermotiontech.com/blog/3-big-problems-caused-hot-running-hydraulics
- Power & Motion. (s. f.-b). *The grave danger of energy contamination*. https://www.powermotiontech.com/hydraulics/hydraulic-fluids/article/21887494/the-grave-danger-of-energy-contamination
- Precision Electric. (2025). *VFD ground fault trip and short circuit faults: Causes, detection and best practices*. https://www.precision-elec.com/wp-content/uploads/2025/06/VFD-Ground-Fault-Trip-and-Short-Circuit-Faults-Causes-Detection-and-Best-Practices.pdf
- Pumps & Systems. (2012). *Hydraulic Institute publishes ANSI/HI 9.6.1–2012 rotodynamic pumps guideline for NPSH margin*. https://www.pumpsandsystems.com/?p=9219
- Purohit, H., Tanabe, R., Ichige, K., Endo, T., Nikaido, Y., Suefusa, K., & Kawaguchi, Y. (2019). MIMII dataset: Sound dataset for malfunctioning industrial machine investigation and inspection. En *Proceedings of the Detection and Classification of Acoustic Scenes and Events 2019 Workshop (DCASE2019)* (pp. 209–213). https://archive.nyu.edu/handle/2451/60761
- Qiu, H., Lee, J., Lin, J., & Yu, G. (2006). Wavelet filter-based weak signature detection method and its application on rolling element bearing prognostics. *Journal of Sound and Vibration, 289*(4–5), 1066–1090. https://doi.org/10.1016/j.jsv.2005.03.007
- Ran, Y., Zhou, X., Lin, P., Wen, Y., & Deng, R. (2019). *A survey of predictive maintenance: Systems, purposes and approaches* [Preprint]. arXiv. https://arxiv.org/abs/1912.07383
- Randall, R. B. (2011). *Vibration-based condition monitoring: Industrial, aerospace and automotive applications*. Wiley. [consultada de memoria]
- Randall, R. B., & Antoni, J. (2011). Rolling element bearing diagnostics—A tutorial. *Mechanical Systems and Signal Processing, 25*(2), 485–520. https://doi.org/10.1016/j.ymssp.2010.07.017
- Saxena, A., Goebel, K., Simon, D., & Eklund, N. (2008). Damage propagation modeling for aircraft engine run-to-failure simulation. En *2008 International Conference on Prognostics and Health Management* (pp. 1–9). IEEE. https://doi.org/10.1109/PHM.2008.4711414
- Shortliffe, E. H., & Buchanan, B. G. (1975). A model of inexact reasoning in medicine. *Mathematical Biosciences, 23*(3–4), 351–379. https://doi.org/10.1016/0025-5564(75)90047-4
- Siemens. (s. f.). *Siemens 880 user's manual* [Manual de motor, tabla de temperaturas de rodamientos]. https://manualzilla.com/doc/6980939/siemens-880-user-s-manual?page=10
- Smith, W. A., & Randall, R. B. (2015). Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study. *Mechanical Systems and Signal Processing, 64–65*, 100–131. https://doi.org/10.1016/j.ymssp.2015.04.021
- Study on tool breakage detection. (2025). *A study on tool breakage detection technology based on current sensing and non-contact signal analysis*. PubMed Central. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12251610/ [autores y revista no verificados]
- TECO-Westinghouse. (2008). *RTD alarm & trip settings* [Tabla técnica]. https://www.tecowestinghouse.com/Stock_Motor_PDF/RTD_Alarm_Trip_Settings.pdf [valores leídos a través del extracto del buscador; el PDF no se pudo leer]
- Teti, R., Jemielniak, K., O'Donnell, G., & Dornfeld, D. (2010). Advanced monitoring of machining operations. *CIRP Annals, 59*(2), 717–739. https://doi.org/10.1016/j.cirp.2010.05.010
- U.S. Department of Energy. (2003). *Improving compressed air system performance: A sourcebook for industry*. Office of Energy Efficiency and Renewable Energy; Compressed Air Challenge. [consultada de memoria]
- UCI Machine Learning Repository. (2020). *AI4I 2020 predictive maintenance dataset* [Conjunto de datos]. https://archive.ics.uci.edu/dataset/601
- UE Systems. (s. f.). *Reduce unplanned downtime: Learn the warning signs of bearing failure*. https://www.uesystems.com/reduce-unplanned-downtime-learn-the-wearning-signs-of-bearing-failure/
- World Fertilizer. (2022, 14 de octubre). *Martin Engineering: Identifying and addressing conveyor idler issues*. https://www.worldfertilizer.com/materials-handling/14102022/martin-engineering-identifying-and-addressing-conveyor-idler-issues/
