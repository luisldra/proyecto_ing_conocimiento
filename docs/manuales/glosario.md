# Glosario

Términos del dominio y técnicos que aparecen en el proyecto, en orden alfabético.

| Término | Significado |
|---|---|
| **α (alfa)** | Peso del modelo en la fusión M3: puntaje = α · probabilidad del modelo + (1 − α) · certeza de las reglas. Se eligió entre 0.6 y 0.8 por activo, en validación |
| **ABP / ABPr** | Aprendizaje basado en problemas y en proyectos: la metodología del curso |
| **Activo** | Tipo de equipo de la planta (motor eléctrico, bomba centrífuga, compresor de tornillo, prensa hidráulica, banda transportadora, centro CNC). Una **unidad** es una máquina concreta de ese tipo |
| **Agente** | Programa de IA con un rol definido (investigador, revisor, datos…) que trabajó en el proyecto siguiendo [AGENTS.md](../../AGENTS.md) |
| **AI4I 2020, SKAB** | Conjuntos de datos públicos de mantenimiento predictivo usados para contrastar el simulador, no para entrenar |
| **Aviso temprano** | Alerta del modo correcto en una ventana gris, es decir, más de 24 h antes de la falla |
| **Brecha** | Diferencia entre el mejor y el peor grupo (por ejemplo, entre turnos) en una métrica; mide la equidad |
| **Calibración por temperatura** | Ajuste de las probabilidades del modelo para que reflejen mejor su acierto real |
| **Captum** | Librería de PyTorch para explicar modelos; aquí, para los gradientes integrados |
| **Cavitación** | Formación y colapso de burbujas de vapor en una bomba cuando la presión de succión es insuficiente; suena como un golpeteo |
| **CNN1D** | Red neuronal convolucional de una dimensión: detecta patrones locales en las series de tiempo |
| **CommonKADS** | Metodología de ingeniería del conocimiento que organiza el trabajo en modelos (organización, tarea, conocimiento…) |
| **Concordancia** | Métrica de explicabilidad: qué tanto coinciden los sensores con más peso con la firma real de la falla o con las reglas disparadas |
| **Confusor** | Condición de operación sana que imita una falla (carga alta sostenida, ambiente caluroso…); prueba si el sistema da falsas alarmas |
| **CRISP-DM** | Proceso estándar de minería de datos: comprensión, preparación, modelado, evaluación y despliegue |
| **D-NNN** | Decisión documentada de la base de conocimiento, con alternativas, fuentes y confianza ([decisiones.md](../../knowledge/acquisition/decisiones.md)) |
| **Deriva** | Cambio lento de las mediciones o de la operación con el tiempo, que hace que el modelo vea datos distintos a los de su entrenamiento |
| **Detección / predicción** | Tarea de cada modo de falla: **predicción** si se puede anticipar 24 h antes; **detección** si es súbito y solo se reconoce cuando ocurre |
| **ERR-NNN** | Error documentado con su causa y prevención ([ERRORES.md](../agentes/ERRORES.md)) |
| **Encadenamiento hacia adelante** | Forma de inferencia que parte de los hechos (síntomas) y dispara las reglas cuyas premisas se cumplen |
| **F1 macro** | Promedio del F1 de cada clase; el F1 combina precisión y recall. "Macro" da el mismo peso a las clases raras |
| **Falsa alarma** | Alerta de falla en una ventana de equipo sano. "Con confusor" se mide en ventanas sanas con una condición que imita una falla |
| **FC (factor de certeza)** | Confianza entre 0 y 1 en una regla o conclusión, según el modelo de MYCIN |
| **Fidelidad** | Métrica de explicabilidad: cuánto cae la probabilidad al anular los sensores con más peso, comparado con anular sensores al azar |
| **Firma** | Cambio que produce un modo de falla en cada variable (cuánto, en qué dirección y con qué forma) |
| **FMEA** | Análisis de modos y efectos de falla: para cada modo, componente, síntomas, causas, acciones, severidad, ocurrencia, detección y NPR |
| **Fusificación** | Paso de un valor numérico a un grado de síntoma entre 0 y 1, con una rampa suave cerca del umbral |
| **Gradientes integrados (IG)** | Método de explicabilidad que atribuye la predicción a cada sensor integrando el gradiente desde una línea base |
| **HermiT** | Razonador OWL que comprueba la consistencia lógica de la ontología (requiere Java) |
| **Horizonte (H)** | Tiempo de anticipación de la predicción: 24 horas |
| **IC 95 %** | Intervalo de confianza del 95 %; aquí, t de Student entre 5 semillas |
| **Léxico** | Traducción de las expresiones de los técnicos ("la bomba está golpeando") a síntomas formales y modos candidatos |
| **Línea base** | Valor de referencia de cada variable en una unidad (mediana de sus primeros 14 días), para las variables relativas |
| **LSTM** | Red neuronal recurrente con memoria de largo plazo, adecuada para tendencias en series de tiempo |
| **M0, M1, M2, M3** | Los cuatro sistemas comparados: solo reglas, solo Deep Learning, conocimiento como entrada del modelo y fusión del modelo con las reglas |
| **Máquina no vista** | La unidad de cada tipo reservada solo para evaluación (`test_unidad`): mide la generalización a una máquina nueva |
| **MLP** | Perceptrón multicapa: red neuronal que recibe estadísticas resumidas de la ventana |
| **MYCIN** | Sistema experto médico de los años setenta que introdujo los factores de certeza. Dos reglas del mismo modo se combinan: FC = FC1 + FC2 · (1 − FC1) |
| **NPR** | Número de prioridad de riesgo de la FMEA = severidad × ocurrencia × detección |
| **NPSH** | Altura neta positiva de succión: margen de presión en la entrada de una bomba. Si es insuficiente, hay cavitación |
| **Ontología (OWL)** | Modelo formal del dominio (clases, relaciones e individuos) en el lenguaje OWL; aquí, `metaltech.owl` |
| **Panel de agentes** | Evaluación exploratoria de las explicaciones hecha con cinco agentes de IA con perfiles de la planta; no es una evaluación humana |
| **Partición temporal** | División de los datos por tiempo (60 % entrenamiento, 20 % validación, 20 % prueba) con una purga entre cortes, para evitar fuga de información |
| **Pérdida focal** | Función de pérdida que da más peso a los ejemplos difíciles; ayuda con clases raras |
| **Precisión / recall** | Precisión: de las alertas de una falla, cuántas eran esa falla. Recall: de las fallas reales, cuántas se detectaron |
| **RA / R1–R6** | Riesgos definidos del proyecto: RA, aplicación indebida (evaluar técnicos o automatizar paros), y R1–R6, riesgos específicos ([informe de sesgos](../../reports/sesgos_limitaciones.md)) |
| **Regla** | Conocimiento heurístico en forma SI síntomas ENTONCES modo de falla, con un FC, una acción y fuentes |
| **Respaldo de reglas** | Una alerta tiene respaldo si al menos una regla del mismo modo se disparó |
| **Semilla** | Número que fija el azar para que un resultado se pueda repetir. Se usaron 42 a 46 |
| **Severidad (simulador)** | Factor que multiplica el cambio de la firma de una falla; hace que unas fallas sean más evidentes que otras |
| **Síntoma medido / percibido** | Medido: condición sobre una variable de sensor. Percibido: lo que reporta un técnico (golpeteo, olor a quemado) |
| **Submuestreo** | En entrenamiento se conservan todas las ventanas con falla y 10 normales por cada una |
| **Traza** | Registro de qué reglas se dispararon, con qué valores reales y con qué certeza |
| **Veto** | Opción de M3 que anula alertas sin respaldo de reglas; ningún activo la eligió porque rechazaba alertas correctas |
| **Ventana** | Bloque de 6 horas de lecturas (36 valores cada 10 minutos por sensor) que el sistema diagnostica |
| **Ventana gris** | Ventana con degradación en curso a más de 24 h de la falla; no se entrena ni entra al F1, y se mide como aviso temprano |
| **XAI** | Inteligencia artificial explicable |
