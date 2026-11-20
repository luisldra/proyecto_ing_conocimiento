# Informe de sesgos, limitaciones y marco legal – Metal Tech

> Fase 9 del [plan](../docs/PLAN.md). Fecha: 2026-11-20.
> Todas las cifras salen de `reports/tables/` (5 semillas, intervalos t del 95 %). Las decisiones citadas (D-NNN) están en [decisiones.md](../knowledge/acquisition/decisiones.md).
> Este informe alimenta las secciones de Discusión, Ética y Limitaciones del documento APA.

## 1. Alcance

El sistema es un **prototipo académico**. Se entrenó y evaluó solo con datos **sintéticos** de una planta ficticia, y el conocimiento experto proviene de **revisión documental hecha por agentes**, no de entrevistas. Nada de lo que sigue demuestra que funcionaría en una planta real; el informe dice qué tan lejos está de eso y por qué.

**Principio de uso:** el sistema **recomienda**; la decisión de intervenir o detener un equipo es siempre de una persona responsable.

## 2. Resumen de riesgos

| # | Riesgo | Evidencia | Gravedad | Mitigación en el prototipo | Estado |
|---|---|---|---|---|---|
| 1 | Circularidad entre simulador y reglas | Las firmas parten de los mismos umbrales que usan las reglas (D-042) | Alta | Firmas incompletas, severidad variable, deriva, contraste con AI4I y SKAB | Reducido, no eliminado |
| 2 | Confusores optimistas | El modelo aprende los confusores del mismo generador con que se evalúa | Alta | Se reportan aparte; máquina no vista | Abierto |
| 3 | Sesgo de técnico y turno | La observación incorrecta duplica la falsa alarma de M0 | Media | M3 pondera poco el texto; las observaciones se seudonimizan | Medido |
| 4 | Brecha entre activos | M0: 21.8 puntos de acierto; M3: 5.7 puntos | Media | Un modelo por activo | Medido |
| 5 | Sobreconfianza en la automatización | Probabilidades cercanas al 100 % sin respaldo de reglas (panel, D-059) | Media | El texto dice cuándo ninguna regla respalda la alerta | Parcial |
| 6 | El conocimiento aporta poco al F1 | M3 − M1 = +0.8 puntos en máquina no vista; las reglas como veto hunden el F1 | Media | Se reporta tal cual; la ganancia está en falsas alarmas | Hallazgo |
| 7 | Deriva de datos | Solo deriva simulada (15 % cada 180 días) | Media | Línea base por unidad | Abierto |
| 8 | Evaluación optimista | Pares que comparten datos; panel de agentes no humano | Media | Intervalos entre semillas como medida principal | Declarado |
| 9 | Límites de la explicación | Gradientes integrados fuera de distribución al anular sensores | Baja | Comparación contra azar | Declarado |
| 10 | Seguridad de la demo | Sin autenticación ni control de carga | Baja (demo local) | Uso local | Declarado |

## 3. Sesgos de los datos sintéticos

**3.1 Circularidad entre simulador y reglas (riesgo 1).** El simulador genera cada falla a partir de firmas que se basan en los mismos umbrales que conocen las reglas (D-042). Así, M0 y las ramas de conocimiento de M2 y M3 juegan "en casa". Para reducirlo:
- cada variable de la firma, salvo la principal, se omite con probabilidad 0.4 (D-055);
- la severidad varía entre 0.8 y 1.15, y algunas fallas no alcanzan el umbral;
- hay deriva de sensor y excursiones operativas sin falla (D-052).

El efecto se nota: M0 solo detecta el 68.1 % de las fallas (`impacto_resumen.json`). Aun así, **el desempeño de M0 y de M3 no es evidencia de lo que pasaría con fallas reales**, cuyas firmas no tienen por qué coincidir con las reglas.

**3.2 Firmas más completas que las reales.** Durante una anomalía de SKAB solo el 33 % de los canales se mueve al menos una desviación; en el simulador se espera un 60 % (D-055). Las fallas simuladas son más fáciles de reconocer que las reales.

**3.3 Confusores aprendidos del mismo generador (riesgo 2).** Las 11 condiciones que imitan fallas, como carga alta sostenida o ambiente caluroso, son supuestos físicos. El modelo las ve en entrenamiento con la misma forma que en test, así que su falsa alarma baja (M3: 3.1 % en máquina no vista) es **optimista**. Un confusor real distinto de los simulados no está cubierto.

**3.4 Simplificaciones de estructura.**
- Una sola falla por unidad a la vez; en planta pueden coexistir.
- Clases con muy poco soporte: la cavitación tiene 2 episodios en test. Su F1 por clase no es confiable.
- Desbalance fuerte: 2.4 % de filas positivas.
- 36 meses por unidad y 32 unidades: no hay envejecimiento de flota, cambios de proceso ni mantenimientos parciales.
- Los parámetros numéricos (duraciones, frecuencias, magnitudes) tienen confianza **baja** (D-050); la estructura tiene confianza media.

**Regla de protección aplicada:** ningún parámetro del simulador se ajustó mirando resultados de M1, M2 o M3 (D-050, D-052). Sin esa regla, el simulador se habría acomodado al modelo.

## 4. Sesgo de técnico y turno

**4.1 Lo que se inyectó.** Las observaciones de los técnicos son ficticias (T01–T08, I01–I02). Su acierto depende del técnico y baja de noche **por diseño**: 75.0 % de noche frente a 84–86 % de día. Por técnico va del 65.0 % (T08 de noche) al 97.7 % (T08 de mañana) (`calibracion_observaciones.csv`). Es un sesgo puesto a propósito para medir equidad, **no una afirmación sobre personas reales**.

**4.2 Lo que se midió** (`equidad_grupos.csv`, `equidad_brechas.csv`; brecha = mejor grupo menos peor grupo):

| Grupo | Sistema | Acierto en fallas | Falsa alarma |
|---|---|---|---|
| Sin observación | M0 | 52.3 % | 1.05 % |
| Observación incorrecta | M0 | 75.3 % | **2.08 %** |
| Sin observación | M3 | 95.7 % | 0.28 % |
| Observación incorrecta | M3 | 97.2 % | 0.32 % |

- **Una observación incorrecta duplica la falsa alarma de M0**, de 1.05 % a 2.08 %. El sistema experto puro toma el texto del técnico como evidencia, y un técnico que se equivoca arrastra al sistema.
- En M3 el efecto casi desaparece (0.28 % frente a 0.32 %) porque la fusión pondera las reglas con 1 − α, entre 0.2 y 0.4.
- El acierto alto de M0 con observación, incorrecta o no, se explica porque los técnicos suelen hablar cuando ya hay síntomas. **No significa** que la observación incorrecta ayude.

**4.3 Turno.**
- La brecha de acierto de M3 entre turnos es de 2.2 puntos, y el peor turno es la tarde (94.7 %), no la noche (96.9 %).
- La falsa alarma es mayor de noche (0.40 % frente a 0.20–0.23 %), una diferencia de 0.21 puntos.
- Los modelos de sensores no leen el turno, y el sesgo nocturno solo afecta las observaciones, que M3 casi no usa. Por eso el sesgo inyectado no pasa al resultado de M3.
- La causa de la diferencia en falsa alarma nocturna **no se determinó**. Una hipótesis es el ciclo de carga por turno del simulador; queda como pregunta abierta.

**4.4 Riesgo en una planta real.** Si las observaciones se asociaran a técnicos con nombre, el sistema podría usarse para evaluar a las personas ("el técnico X se equivoca más"). El prototipo no lo hace: identifica con seudónimos y no calcula indicadores por técnico fuera del análisis de equidad del sistema. La sección 9 recoge las restricciones legales.

## 5. Brecha entre tipos de activo

| Sistema | Brecha de acierto | Peor activo | Brecha de falsa alarma | Peor activo |
|---|---|---|---|---|
| M0 | 21.8 puntos | centro CNC | 6.2 puntos | compresor |
| M1 | 5.6 | compresor | 1.1 | compresor |
| M3 | 5.7 | compresor | 1.1 | compresor |

- Las reglas cubren peor el centro CNC, cuyas fallas de herramienta son rápidas y de tipo detección (D-049).
- Con DL la brecha baja a cerca de 5.7 puntos, y el compresor de tornillo es el activo más difícil.
- En máquina vista frente a no vista la brecha de M3 es de 0.4 puntos: no hay pérdida al pasar a una unidad no entrenada **del mismo simulador**.

## 6. Sobreconfianza en la automatización y aporte real del conocimiento

**6.1 Qué aporta el conocimiento** (máquina no vista, `intervalos_diferencias.csv`):

| Comparación | F1 macro | Falsa alarma con confusor |
|---|---|---|
| M3 − M1 | **+0.8 puntos** (IC 95 %: +0.3 a +1.2) | **−1.1 puntos** (−1.4 a −0.9); de 4.2 % a 3.1 % |
| M2 − M1 | +0.2 (−0.7 a +1.1), no significativo | −0.7 (−1.8 a +0.4), no significativo |
| M3 − M0 | +28.3 (+27.8 a +28.9) | −14.2 (−15.3 a −13.2) |

- La ganancia del conocimiento **no está en el F1** sino en **reducir falsas alarmas ante confusores**: cerca de un 27 % relativo frente a M1.
- M2, que recibe el conocimiento como entrada, no mejora a M1 de forma significativa.

**6.2 Las reglas no sirven como validador.** El plan proponía que las reglas confirmaran o vetaran alertas. En validación (`fusion_parametros.json`) ocurre esto:
- con veto, el F1 macro cae a 0.47–0.69 en todos los activos;
- con α < 0.6, es decir, cuando las reglas pesan tanto o más que el modelo, el F1 queda entre 0.47 y 0.70;
- ningún activo eligió el veto, y α quedó entre 0.6 y 0.8;
- tres activos eligieron 0.8, el borde de la rejilla, que no se amplió para no ajustarla después de ver resultados (D-056).

En la práctica M3 es M1 con una corrección moderada de las reglas. La lectura honesta es que **las reglas, con la cobertura actual, aportan explicación y algo de prudencia, pero no la capacidad de detectar**.

**6.3 Riesgo de sobreconfianza.**
- El modelo da probabilidades cercanas al 100 % en alertas que ninguna regla respalda. El panel de agentes lo señaló como fuente de desconfianza (D-059, hallazgo 4).
- Los valores apenas sobre el umbral (130.05 frente a 130) se presentan como evidencia aunque estén dentro del error del sensor (hallazgo 5).
- Un operador que confíe en una cifra del 99 % puede saltarse la verificación.

Mitigaciones del prototipo:
- la explicación dice explícitamente cuando ninguna regla respalda la alerta;
- se muestran la certeza de las reglas y la probabilidad del modelo por separado;
- el sistema no ejecuta nada: aun cuando la acción sugerida es un paro y bloqueo, la decide y la hace una persona;
- la web rotula los resultados como datos sintéticos.

Quedan pendientes para una versión real: mostrar un margen alrededor del umbral y señalar la baja certeza en la interfaz. La calibración por temperatura (D-053) no basta frente a datos fuera de distribución.

## 7. Deriva de datos

- El simulador incluye deriva de sensor (15 % de la media banda cada 180 días, supuesto) y una línea base por unidad (mediana de los primeros 14 días, D-056).
- El prototipo **no monitorea la deriva** ni avisa cuando las entradas salen del rango de entrenamiento.
- En planta, un cambio de producto, un recambio de sensor o una reparación cambian la línea base. El modelo seguiría prediciendo con confianza sobre datos que no conoce.
- **Requisito antes de uso real:** detectar entradas fuera de distribución, recalcular la línea base tras cada mantenimiento y reentrenar periódicamente con validación temporal.

## 8. Límites de la evaluación y de la explicación

**Evaluación:**
- Los pares activo-semilla comparten datos, así que los valores p de Wilcoxon son optimistas. La medida principal es el intervalo entre 5 semillas (D-060).
- La semilla cambia el entrenamiento, **no los datos**: los intervalos no incluyen la variación de otro conjunto simulado.
- Los costos del impacto son relativos y supuestos: falla no detectada = 3, 5 o 9 veces una reparación planificada, y falsa alarma = 0.1. Por eso se reportan con sensibilidad.
- La latencia (p95 de 79.2 ms con explicación) es local, de un solo proceso y sin concurrencia.

**Evaluación de explicaciones:**
- No hubo personas disponibles. El instrumento se aplicó con un **panel de 5 agentes** que son el mismo modelo de lenguaje, así que sus respuestas no son independientes (D-059).
- La preferencia de 60 de 60 por la explicación híbrida es una validación exploratoria y **no sustituye a técnicos reales**.
- El instrumento para personas, con consentimiento informado, está listo en [docs/evaluacion_humana/](../docs/evaluacion_humana/README.md).

**Explicación (D-057):**
- Los tres sensores con más peso según gradientes integrados coinciden con la firma real en el 74.6 % de los casos, frente al 33.0 % al azar, y con las variables de las reglas disparadas en el 67.5 %.
- Anular sensores para medir fidelidad lleva la entrada fuera de distribución y puede exagerar la caída.
- La estabilidad ante ruido aleatorio no garantiza robustez ante perturbaciones dirigidas.
- Hubo atribuciones poco físicas, como la corriente pesando en una falla de rodamiento, que el panel detectó.

**Conocimiento:**
- Sin acceso a las normas ISO, los umbrales se tomaron de fuentes públicas secundarias ([normas_fuentes_externas.md](../knowledge/acquisition/normas_fuentes_externas.md)). Por ejemplo, ISO 10816-7 se leyó vía Europump (D-051).
- Ninguna regla fue validada por un técnico.

## 9. Marco legal y normativo

Consulta hecha por el agente investigador el 2026-11-20 en fuentes públicas. El detalle, las marcas de verificación y las referencias APA están en D-062 a D-075. **El prototipo no trata datos personales reales**, así que hoy no le aplican obligaciones de tratamiento. La tabla dice qué exigiría cada norma en una planta real y cómo responde el diseño.

| Norma | Qué exige o recomienda | Respuesta del diseño | Decisión |
|---|---|---|---|
| Ley Estatutaria 1581 de 2012 | Las observaciones, el turno y el identificador del técnico son datos personales. Principios de finalidad, circulación restringida y seguridad; autorización previa e informada | Seudónimos; uso exclusivo para diagnosticar el activo; sin datos sensibles | D-062, D-063, D-064 |
| Decreto 1377 de 2013 (compilado en el Decreto 1074 de 2015) | Datos pertinentes, autorización al recolectar, política de tratamiento, supresión al cumplir la finalidad, responsabilidad demostrada | Aviso y autorización en una planta real; este informe y el acta ética como evidencia | D-065, D-066, D-075 |
| Circular Externa SIC 002 de 2024 | En IA: minimización, análisis de riesgos, evaluación de impacto, anonimización | Entrenamiento solo con datos sintéticos; registro de riesgos (sección 2) | D-066 |
| Ley 1266 de 2008 | Hábeas data financiero y comercial | No aplica | D-067 |
| CONPES 3975 (2019), CONPES 4144 (2025) y Marco Ético de IA (2021) | Orientación no vinculante: ética, transparencia, control humano, IA que apoya al trabajador | Explicación de cada alerta y supervisión humana | D-069, D-070, D-074 |
| Proyecto de Ley 025 de 2026 Cámara | Propone niveles de riesgo; no es ley a 2026-11-20 | No evaluar personas evita la categoría de alto riesgo | D-074 |
| Reglamento (UE) 2024/1689 (AI Act), como referencia | Art. 13 (transparencia), art. 14 (supervisión humana); alto riesgo si evalúa trabajadores o es componente de seguridad | No sería de alto riesgo; se adoptan los arts. 13 y 14 como buena práctica; no ejecuta funciones de seguridad | D-068, D-069, D-070 |
| ISO/IEC 42001 e ISO/IEC 23894 (2023) | Sistema de gestión y gestión de riesgos de IA | Citadas sin declarar conformidad; marco operativo NIST AI RMF 1.0 | D-072 |
| ISO/IEC TR 24027 (2021) | Medición del sesgo, incluido el sesgo de automatización | Equidad por activo, turno y observación, nunca por persona (secciones 4–6) | D-073 |
| Decreto 1072 de 2015 (SG-SST) y Resolución 0312 de 2019 | Identificación de peligros de máquinas, mantenimiento de equipos, gestión del cambio antes de implementar | La implantación sería un cambio gestionado; las recomendaciones alimentan el plan de mantenimiento sin reemplazarlo | D-069, D-071 |
| Código Sustantivo del Trabajo, art. 59 | Prohíbe actos contra la dignidad del trabajador | Sin rankings ni métricas por técnico | D-063 |

**Conclusiones del marco legal:**
- La línea que más importa es **no usar el sistema para evaluar a los técnicos** (D-063). Esa línea protege los datos personales, la dignidad laboral y la clasificación de riesgo a la vez.
- Ninguna norma colombiana regula hoy de forma específica la IA industrial. El marco aplicable es el de protección de datos, el SG-SST y la política pública no vinculante.
- **Lo que no se pudo verificar** está listado al final de D-075. Por ejemplo, la numeración compilada del Decreto 1074 y el articulado del proyecto de ley no se leyeron en el texto oficial. Debe revisarse antes de citarlo en el documento final.

## 10. Requisitos antes de usar el sistema en una planta real

1. Reentrenar y recalibrar con datos reales etiquetados de la planta. El simulador solo sirve para el desarrollo.
2. Validar cada regla con técnicos y con las normas originales, y registrar su firma o aprobación.
3. Aplicar la evaluación humana con técnicos reales (instrumento listo).
4. Agregar detección de deriva y de entradas fuera de distribución.
5. Mantener la supervisión humana: ninguna acción de paro automático y registro de quién aceptó o descartó cada alerta.
6. Seudonimizar a los técnicos, informarles la finalidad del tratamiento de sus observaciones y no usarlas para evaluar su desempeño (sección 9).
7. Integrar el sistema a la gestión del cambio y al SG-SST de la planta (sección 9).
8. Agregar autenticación, registro de auditoría y pruebas de carga a la API.

## 11. Trazabilidad

| Afirmación | Fuente |
|---|---|
| Intervalos y diferencias entre sistemas | `reports/tables/intervalos_sistemas.csv`, `intervalos_diferencias.csv` |
| Equidad por turno, observación, activo y máquina | `reports/tables/equidad_grupos.csv`, `equidad_brechas.csv` |
| Acierto de técnicos por turno | `reports/tables/calibracion_observaciones.csv` |
| Rejilla de fusión y veto | `reports/tables/fusion_parametros.json` |
| Explicabilidad | `reports/tables/xai_metricas.csv` |
| Panel de agentes | `reports/tables/evaluacion_agentes_resumen.json`, D-059 |
| Impacto y latencia | `reports/tables/impacto_resumen.json`, `latencia_api_resumen.json` |
| Supuestos del simulador | [data/README.md](../data/README.md), D-042, D-050, D-052, D-055 |
| Marco legal | D-062 a D-075 y sus referencias en [decisiones.md](../knowledge/acquisition/decisiones.md) |
| Compromisos éticos del equipo | [docs/etica/acta_etica.md](../docs/etica/acta_etica.md) |
