<!--
Fuente del documento APA 7 (Fase 10). Se convierte a Word y PDF con:
    python scripts/generar_documento.py --pdf
Sintaxis:
  # / ## / ###          títulos APA de nivel 1, 2 y 3
  párrafo normal        sangría de primera línea de 1.27 cm
  - item / 1. item      listas
  | a | b |             tablas; la línea anterior "Tabla: título" y la siguiente "Nota: ..." (opcional)
  ![título](ruta)       figura; la línea siguiente "Nota: ..." (opcional)
  {{v:clave}}           cifra calculada desde reports/ (scripts/generar_documento.py, valores())
  {{tabla:nombre}}      tabla generada; {{figura:nombre}} figura generada
  {{portada}} {{resumen}} {{indice}} {{salto}} {{referencias}}
  *cursiva*  **negrita**  `código`
Los [corchetes con PENDIENTE] marcan datos que el equipo debe completar.
-->

{{portada}}

{{resumen}}
Las fallas no programadas en plantas manufactureras se diagnostican a menudo con la experiencia de los técnicos, que no siempre coincide con los datos de los sensores. Este trabajo integra un modelo de aprendizaje profundo con una base de conocimiento experto para predecir fallas y explicarlas en la planta ficticia Metal Tech. Un agente de inteligencia artificial adquirió el conocimiento por revisión documental, sin entrevistas, y lo formalizó en una FMEA, un léxico de expresiones de técnicos, {{v:reglas}} reglas con factores de certeza y una ontología OWL. Con datos sintéticos de {{v:unidades}} máquinas se entrenaron redes MLP, CNN1D y LSTM, y se compararon cuatro sistemas: solo reglas, solo aprendizaje profundo, conocimiento como entrada del modelo y fusión del modelo con las reglas. En una máquina no vista durante el entrenamiento, la fusión alcanzó un F1 macro de {{v:f1_m3_nv}}, frente a {{v:f1_m1_nv}} del modelo solo y {{v:f1_m0_nv}} de las reglas solas, y redujo las falsas alarmas ante condiciones confusoras de {{v:fa_m1_nv}} a {{v:fa_m3_nv}}. Cada alerta se explica con las variables más influyentes, según gradientes integrados, y con las reglas que la respaldan; en una evaluación exploratoria con agentes, la explicación híbrida fue preferida en todos los casos. El aporte del conocimiento experto estuvo más en la explicación y la reducción de falsas alarmas que en la capacidad de detectar. Se discuten los sesgos del simulador, la equidad entre turnos y el marco legal colombiano.
Palabras clave: mantenimiento predictivo, aprendizaje profundo, sistemas expertos, ontologías, inteligencia artificial explicable
{{/resumen}}

{{indice}}

# Introducción

El mantenimiento de una planta manufacturera depende de dos fuentes de información que rara vez se encuentran: los datos de los sensores instalados en los equipos y la experiencia de los técnicos que los reparan. Los sensores miden con precisión temperatura, vibración, corriente, presión y caudal, pero sus lecturas se consultan de forma aislada. Los técnicos, por su parte, diagnostican con los sentidos y con la memoria de fallas pasadas: "el motor está cantando", "la bomba está golpeando". Ese conocimiento es valioso, pero informal, y cambia de un turno a otro y de una persona a otra. El resultado son intervenciones tardías, falsas alarmas y cambios innecesarios de repuestos (Jardine et al., 2006; Zonta et al., 2020).

La ingeniería del conocimiento ofrece herramientas para formalizar esa experiencia: ontologías que fijan el vocabulario del dominio, reglas que expresan el razonamiento del experto y factores de certeza que representan la confianza en cada conclusión (Studer et al., 1998; Shortliffe y Buchanan, 1975). El aprendizaje profundo, en cambio, aprende patrones directamente de las series de los sensores sin que nadie los escriba, aunque sus decisiones son difíciles de explicar (LeCun et al., 2015; Barredo Arrieta et al., 2020). Este trabajo explora cómo combinar ambos enfoques para que un sistema prediga fallas con la precisión de los datos y las explique con el lenguaje del mantenimiento.

El documento presenta el desarrollo de un prototipo para la planta ficticia Metal Tech. Se construyó una base de conocimiento de {{v:modos}} modos de falla y {{v:reglas}} reglas, una ontología OWL, un simulador de datos sintéticos, modelos de aprendizaje profundo por tipo de activo, cuatro estrategias de integración comparadas entre sí, métodos de explicación, una API, una web demostrativa y una landing de presentación. Todo el conocimiento se adquirió por revisión documental realizada por agentes de inteligencia artificial, sin entrevistas, y todos los datos son sintéticos.

# Planteamiento del problema

## Contexto

Metal Tech es una empresa de manufactura metálica con 240 empleados en tres turnos. Desde 2019 cuenta con sensores de temperatura, vibración, corriente, presión y caudal en sus activos críticos: motores eléctricos, bombas centrífugas, compresores de tornillo, prensas hidráulicas, bandas transportadoras y centros de mecanizado CNC. Su área de mantenimiento tiene un jefe, dos planificadores, ocho técnicos electromecánicos y dos instrumentistas.

A pesar de la sensorización, la planta sufre fallas no programadas: sobrecalentamiento de motores, desalineación y desbalanceo, desgaste de rodamientos y sellos, cavitación en bombas, pérdida de presión en compresores, fugas hidráulicas, desgaste de herramientas, rotura de bandas y disparos de variadores. Los criterios informales de los técnicos no siempre coinciden con los umbrales de los sensores y dependen del turno y de la persona.

## Pregunta orientadora

¿Cómo integrar un modelo de *Deep Learning* con una base de conocimiento experto para predecir fallas y generar diagnósticos explicables en una planta manufacturera?

## Delimitación

- **Activos:** {{v:activos}} tipos y {{v:unidades}} unidades simuladas. Los puentes grúa, mencionados en el escenario, quedan fuera del alcance.
- **Datos:** exclusivamente sintéticos, generados por un simulador calibrado con literatura y con los conjuntos públicos AI4I 2020 y SKAB (Matzka, 2020; Katser y Kozitsin, 2020). No se usan datos de una planta real ni datos personales.
- **Conocimiento:** obtenido por revisión documental asistida por agentes. No hubo técnicos ni expertos disponibles para entrevistas ni para validar las reglas. Las normas ISO e IEC de pago se consultaron a través de fuentes públicas secundarias.
- **Tarea:** clasificar, para cada ventana de 6 horas de lecturas, si el activo está sano o qué modo de falla ocurrirá en las próximas 24 horas (predicción), o cuál está ocurriendo cuando la falla es súbita (detección).
- **Alcance del prototipo:** recomienda acciones, no las ejecuta. Es una demostración local, sin integración con sistemas de la planta.

# Justificación

Desde el punto de vista práctico, una falla no detectada cuesta varias veces más que una reparación planificada, y una falsa alarma consume horas de técnico y repuestos (Zonta et al., 2020). Un sistema que anticipe las fallas y, al mismo tiempo, evite alarmas innecesarias tiene un impacto directo sobre la disponibilidad y el costo de mantenimiento, que son los indicadores con los que opera Metal Tech.

Desde el punto de vista de la ingeniería del conocimiento, el problema obliga a recorrer el ciclo completo de la disciplina: adquirir conocimiento heurístico, representarlo de forma explícita, razonar con incertidumbre e integrarlo con un modelo aprendido (Schreiber et al., 2000). La integración de conocimiento previo con aprendizaje automático es hoy un área activa de investigación (von Rueden et al., 2021), y su aplicación al mantenimiento predictivo explicable sigue abierta (Cummins et al., 2024; Kusiak, 2024).

Desde el punto de vista ético, un sistema que recomienda intervenir una máquina debe explicar sus razones para que una persona pueda decidir con criterio, y no debe convertirse en un instrumento para vigilar a los trabajadores (Ferrara, 2024; Parasuraman y Riley, 1997). Las explicaciones con reglas y variables, junto con el análisis de sesgos, responden a esa exigencia.

# Objetivos

## Objetivos generales

1. Desarrollar un sistema híbrido que integre un modelo de aprendizaje profundo con una base de conocimiento experto (ontología y reglas con factores de certeza) para predecir fallas y generar diagnósticos explicables en la planta Metal Tech.
2. Evaluar si la integración del conocimiento experto mejora el desempeño, la explicabilidad y la reducción de falsas alarmas frente al modelo solo, considerando sus sesgos, su equidad y su marco ético y legal.

## Objetivos específicos

1. Adquirir y formalizar el conocimiento de fallas, síntomas, causas y acciones de los seis tipos de activo en una FMEA, un léxico de expresiones de técnicos, un conjunto de reglas con factores de certeza y una ontología OWL, con respaldo documental verificable.
2. Construir un simulador de datos sintéticos y entrenar modelos de aprendizaje profundo (MLP, CNN1D y LSTM), comparando cuatro sistemas: solo reglas (M0), solo aprendizaje profundo (M1), conocimiento como entrada del modelo (M2) y fusión del modelo con las reglas (M3).
3. Implementar un prototipo (API y web demostrativa) que muestre cada diagnóstico con sus variables y reglas, y medir F1, precisión, recall, latencia, explicabilidad, falsas alarmas, equidad e impacto.

# Marco teórico

## Inteligencia artificial y representación del conocimiento

La inteligencia artificial estudia agentes que perciben su entorno y actúan para alcanzar objetivos (Russell y Norvig, 2021). Dentro de ella, la ingeniería del conocimiento se ocupa de construir sistemas que razonan con conocimiento experto explícito. Studer et al. (1998) la describen como un proceso de modelado: el conocimiento no se "extrae" de la cabeza del experto, sino que se construye un modelo que reproduce su comportamiento en la resolución de problemas. CommonKADS organiza ese proceso en modelos de organización, tarea, agente, conocimiento, comunicación y diseño (Schreiber et al., 2000).

El conocimiento puede ser declarativo (qué es una cavitación), procedimental (cómo verificar el margen de NPSH) o heurístico (si la bomba golpea, probablemente cavita). Este proyecto representa los tres: la ontología y la FMEA guardan el declarativo, las acciones recomendadas el procedimental y las reglas el heurístico.

## Ontologías

Una ontología es una especificación explícita de una conceptualización (Gruber, 1993): define las clases de un dominio, sus relaciones y sus restricciones, de forma que personas y programas compartan el mismo vocabulario. El lenguaje OWL permite además que un razonador compruebe la consistencia lógica del modelo. En mantenimiento, una ontología une activos, componentes, sensores, síntomas, modos de falla, causas y acciones, y permite consultar, por ejemplo, qué síntomas manifiesta una falla o qué acciones la mitigan.

## Sistemas expertos, factores de certeza e inferencia

Un sistema experto combina una base de conocimiento con un motor de inferencia. En el encadenamiento hacia adelante, el motor parte de los hechos observados y dispara las reglas cuyas premisas se cumplen hasta llegar a conclusiones (Russell y Norvig, 2021). MYCIN introdujo los factores de certeza (FC) para razonar con evidencia incierta: cada regla tiene un FC entre 0 y 1, la certeza de una conclusión es el FC de la regla multiplicado por la certeza de sus premisas, y dos reglas que apoyan la misma conclusión se combinan como FC = FC1 + FC2 · (1 − FC1) (Shortliffe y Buchanan, 1975; Buchanan y Shortliffe, 1984). El modelo no es probabilístico en sentido estricto, pero es simple, trazable y fácil de explicar, que es lo que se busca aquí.

## Aprendizaje automático y aprendizaje profundo

El aprendizaje profundo aprende representaciones jerárquicas de los datos mediante redes neuronales de varias capas (LeCun et al., 2015). Para series de sensores se usan tres familias: el perceptrón multicapa (MLP), que recibe estadísticas resumidas de la ventana; las redes convolucionales de una dimensión (CNN1D), que detectan patrones locales en el tiempo; y las redes LSTM, que mantienen una memoria de largo plazo y capturan tendencias (Hochreiter y Schmidhuber, 1997). Las fallas son eventos raros, por lo que el entrenamiento necesita técnicas para el desbalance de clases, como la pérdida focal (Lin et al., 2017).

## Integración de conocimiento y aprendizaje

El aprendizaje automático informado incorpora conocimiento previo en el proceso de aprendizaje: en los datos, en la arquitectura, en la función de pérdida o en la validación de las salidas (von Rueden et al., 2021). Este proyecto compara dos de esas vías: el conocimiento como entrada adicional del modelo (M2) y como validación posterior de sus salidas mediante una fusión ponderada (M3), frente a cada enfoque por separado (M0 y M1).

## Inteligencia artificial explicable

La inteligencia artificial explicable (XAI) busca que las decisiones de un modelo sean comprensibles para quien las usa (Barredo Arrieta et al., 2020). Los gradientes integrados atribuyen la predicción a cada variable de entrada integrando el gradiente a lo largo de un camino desde una línea base, y cumplen propiedades deseables como la completitud (Sundararajan et al., 2017). En mantenimiento, Kusiak (2024) propone explicaciones que puedan combinarse entre unidades de manufactura, y Cummins et al. (2024) muestran que la mayoría de trabajos de mantenimiento predictivo explicable no evalúan sus explicaciones con usuarios. Matzka (2020) mostró que un modelo de mantenimiento predictivo puede explicarse con reglas derivadas de los datos de AI4I 2020.

## Mantenimiento predictivo

El mantenimiento basado en condición decide las intervenciones a partir del estado medido del equipo, con tres etapas: adquisición de datos, procesamiento y toma de decisiones (Jardine et al., 2006). La norma ISO 17359 describe el procedimiento general de un programa de monitoreo de condición, e ISO 13374 su arquitectura de procesamiento por bloques (International Organization for Standardization, 2003, 2018). En la industria 4.0 el mantenimiento predictivo integra sensores, modelos y sistemas de información (Zonta et al., 2020). Alimam et al. (2023) plantean, en la industria 5.0, gemelos que integran al ser humano con la máquina, y Friston et al. (2024) proponen ecosistemas de inteligencia en que agentes humanos y artificiales comparten creencias; ambos enfoques sostienen que el sistema debe apoyar a la persona y no reemplazarla.

## Ética, sesgos y marco legal

Los sistemas de IA pueden amplificar pequeñas diferencias de los datos en desigualdades grandes (Ferrara, 2024; Mehrabi et al., 2022). En el diagnóstico asistido, además, existe el sesgo de automatización: la tendencia a seguir la recomendación del sistema sin verificarla (Parasuraman y Riley, 1997). En Colombia, las observaciones de un técnico son datos personales protegidos por la Ley 1581 de 2012 y el Decreto 1377 de 2013 (Congreso de Colombia, 2012; Ministerio de Comercio, Industria y Turismo, 2013), y la Superintendencia de Industria y Comercio (2024) fijó lineamientos para su tratamiento en sistemas de IA. La política nacional de IA (Departamento Nacional de Planeación, 2019, 2025) y el Marco Ético (Presidencia de la República de Colombia, 2021) orientan hacia la transparencia y el control humano. El Reglamento europeo de IA, usado aquí como referencia, exige transparencia y supervisión humana a los sistemas de alto riesgo (Unión Europea, 2024; Comisión Europea, 2026). La seguridad y salud en el trabajo (Ministerio del Trabajo, 2014, 2019) exige además gestionar los cambios y mantener los equipos. El desarrollo del equipo socio-técnico también importa: Ciriello et al. (2024) muestran que la creatividad en equipos de desarrollo surge de la interacción entre personas y herramientas, lo que aplica al trabajo del equipo con agentes de IA.

# Metodología

## Enfoque de aprendizaje basado en problemas y proyectos

El trabajo siguió el aprendizaje basado en problemas y en proyectos (ABP/ABPr): un problema auténtico y abierto, el de Metal Tech, guía la construcción de un artefacto que el equipo diseña, prueba y presenta (Kokotsaki et al., 2016). El equipo de cuatro integrantes se repartió por roles: conocimiento y control de calidad, datos y modelos, API y web, y documentación. Además, el trabajo se organizó con agentes de IA con roles definidos (investigador, revisor de conocimiento, datos, *backend*, *frontend*, documentación y control de calidad) bajo un manual común. Cada tarea quedó registrada en una bitácora y cada error en una base de errores.

## Marcos de referencia

Se combinaron tres marcos. CommonKADS guía el modelado del conocimiento (Schreiber et al., 2000); CRISP-DM guía la parte de datos y modelos: comprensión, preparación, modelado y evaluación (Wirth y Hipp, 2000); e ISO 17359 con la arquitectura de ISO 13374 ordena el sistema de monitoreo, desde la adquisición de datos hasta las recomendaciones. El plan se ejecutó en once fases, de la preparación del repositorio a los manuales.

## Adquisición del conocimiento

No hubo entrevistas: la planta es ficticia y el equipo no tenía acceso a técnicos. Un agente investigador consultó normas (a través de fuentes públicas), literatura científica, guías de fabricantes y conjuntos de datos públicos, y tomó cada decisión de la base de conocimiento con estas reglas:

- cada regla y cada umbral debía tener al menos dos fuentes concordantes o una norma;
- ante fuentes en conflicto, se elegía el valor más conservador y se registraba el conflicto;
- cada expresión coloquial del enunciado se tradujo a síntomas a partir de la física de la falla.

Las {{v:decisiones}} decisiones quedaron registradas con alternativas, fuentes en formato APA y nivel de confianza, con {{v:referencias_kb}} referencias. Un segundo agente revisor buscó reglas sin sustento, contradicciones y huecos de cobertura. La matriz de adquisición se resume en el Anexo A.

## Diseño del artefacto

El artefacto se diseñó en capas independientes: los archivos YAML de la base de conocimiento son la fuente única de verdad; la ontología OWL se genera desde ellos; el simulador genera los datos; los modelos se entrenan por tipo de activo; la capa híbrida combina modelos y reglas; y la API sirve los resultados a la web. Todo experimento se regenera con un comando y una semilla fija.

## Validación

- **Pruebas automáticas:** {{v:pruebas}} pruebas verifican el generador, la coherencia entre reglas, síntomas, FMEA y ontología (incluida la consistencia lógica con el razonador HermiT), los modelos, la fusión, las métricas, la API, la web y la landing.
- **Partición sin fuga:** partición temporal 60/20/20 con purga entre cortes y una unidad de cada tipo reservada, nunca vista en entrenamiento.
- **Selección en validación:** la arquitectura y los parámetros de fusión se eligieron con el F1 de validación, antes de ver el conjunto de prueba.
- **Varias semillas:** M1, M2 y M3 se entrenaron con cinco semillas; se reportan intervalos t del 95 %.
- **Métricas:** F1 macro, precisión, recall, falsa alarma con y sin condiciones confusoras, aviso temprano, latencia, fidelidad, concordancia y estabilidad de las explicaciones, equidad e impacto económico simulado.
- **Evaluación de explicaciones:** como no había personas disponibles, el instrumento diseñado para técnicos se aplicó a un panel de cinco agentes con perfiles de la planta, con control de sesgo por longitud. Sus resultados se presentan como exploratorios y no como evaluación humana.

# Desarrollo del artefacto

## Arquitectura

La Figura 1 resume la arquitectura. El simulador produce series de sensores que se convierten en ventanas de 6 horas (36 lecturas cada 10 minutos). Cada ventana pasa por dos caminos: el modelo de aprendizaje profundo de su tipo de activo, que entrega probabilidades por modo de falla, y el motor de reglas, que traduce las lecturas en síntomas y dispara reglas con factores de certeza. La capa de fusión combina ambos y genera un diagnóstico con las variables más influyentes, las reglas que lo respaldan, las causas probables y la acción recomendada desde la ontología.

{{figura:arquitectura}}

## Base de conocimiento

La base de conocimiento cubre seis tipos de activo. La Tabla 1 resume su contenido. La FMEA enlaza cada modo de falla con su componente, síntomas, causas, acciones y número de prioridad de riesgo; el léxico traduce las expresiones de los técnicos a síntomas formales y a modos de falla candidatos. Por ejemplo, "la bomba está golpeando" se traduce al síntoma percibido de golpeteo, cuyos candidatos son la cavitación, la obstrucción de succión y el defecto de rodamiento.

{{tabla:conocimiento}}

{{tabla:lexico}}

## Ontología

La ontología se genera con owlready2 desde los YAML y se valida con el razonador HermiT. La Tabla 3 muestra sus clases principales y sus relaciones. Gracias a ella, la API responde consultas como la ficha completa de un modo de falla (síntomas, causas, acciones, reglas y fila de la FMEA) y la web dibuja el grafo de conocimiento de cada activo.

{{tabla:ontologia}}

## Reglas y motor de inferencia

Las reglas son conjunciones de síntomas que concluyen un modo de falla con un FC. Un síntoma se activa cuando una variable cruza su umbral, con una rampa suave alrededor del umbral que da un grado entre 0 y 1. La certeza de la premisa es el mínimo de los grados, y la de la conclusión, el FC de la regla por esa certeza; varias reglas sobre el mismo modo se combinan con la fórmula de MYCIN. El FC de cada regla sigue una política explícita: 0.85–0.90 para umbrales normativos con firma física específica, 0.75–0.80 con dos fuentes concordantes, 0.65–0.70 con fuentes secundarias y 0.60 para heurísticas. Las reglas con síntomas percibidos por técnicos no superan 0.80, por el sesgo de turno. Un ejemplo es la regla R13:

> SI margen de NPSH bajo Y vibración de alta frecuencia alta Y caudal inestable, ENTONCES cavitación por NPSH disponible insuficiente (FC = 0.85). Acción: revisar el NPSH disponible (nivel del depósito, válvula y filtro de succión, temperatura del líquido) y evitar operar lejos del punto de mejor eficiencia (Hydraulic Institute, 2017).

El motor devuelve una traza: qué reglas se dispararon, con qué valores reales y con qué certeza. Las {{v:reglas}} reglas se listan en el Anexo B.

## Datos sintéticos

El simulador genera, para cada una de las {{v:unidades}} unidades, 36 meses de lecturas cada 10 minutos: {{v:filas}} filas, {{v:episodios}} episodios de falla y {{v:observaciones}} observaciones de técnicos. Las señales sanas siguen un ciclo de carga por turno, con ruido y deriva de sensor. Cada falla se inyecta con una forma de degradación (lineal, exponencial, sigmoide, escalón o intermitente) sobre las variables de su firma, con severidad variable y omisiones aleatorias de parte de la firma. Se añadieron condiciones confusoras, como carga alta sostenida o ambiente caluroso, que imitan fallas sin serlo, y observaciones de técnicos ficticios cuyo acierto depende de la persona y baja de noche. La dificultad se contrastó con AI4I 2020 y SKAB (Matzka, 2020; Katser y Kozitsin, 2020). Una regla de protección fijó que ningún parámetro del simulador se ajustara mirando los resultados de los modelos. La ficha de datos está en el Anexo F.

## Modelos de aprendizaje profundo

Se entrenó un modelo por tipo de activo, porque los sensores y los modos de falla difieren. Para cada activo se probaron MLP, CNN1D y LSTM con pérdida focal, pesos por clase, parada temprana y calibración por temperatura, y se eligió la arquitectura con mayor F1 macro de validación (Tabla 4). Las ventanas con degradación en curso a más de 24 horas de la falla se trataron como "grises": no se usan para entrenar ni para medir F1, y se evalúan aparte como aviso temprano.

{{tabla:modelos}}

## Integración del conocimiento

Se compararon cuatro sistemas:

- **M0, solo reglas:** las certezas del motor de reglas, normalizadas por clase.
- **M1, solo aprendizaje profundo:** el modelo elegido para cada activo.
- **M2, conocimiento como entrada:** la arquitectura de M1 con una rama adicional que recibe las certezas de las reglas y los grados de los síntomas.
- **M3, fusión:** puntaje = α · p(M1) + (1 − α) · certeza de las reglas, con un veto opcional para alertas sin respaldo de reglas. α y el veto se eligieron en validación (Tabla 4).

## Explicabilidad

Cada alerta de M3 se explica combinando dos fuentes. Los gradientes integrados (Sundararajan et al., 2017) indican qué sensores pesaron más en la decisión del modelo, y la traza del motor de reglas indica qué reglas la respaldan y con qué valores. A eso se suman las causas y acciones de la ontología y, si existe, la observación del técnico. Cuando ninguna regla respalda la alerta, el texto lo dice explícitamente. Un ejemplo real del conjunto de prueba:

> {{v:ejemplo}}

## Prototipo

El prototipo tiene tres piezas:

- **API (FastAPI):** diez puntos de acceso para consultar activos, reglas, léxico, ontología y reportes, predecir, diagnosticar y simular una falla. Valida cada solicitud y documenta su uso en `/docs`.
- **Web demostrativa (Streamlit):** ocho páginas: estado de la planta, simulador en vivo, explicación de la alerta, base de conocimiento con grafo de la ontología, comparación de modelos, equidad e impacto, explorador de datos, y bitácora y errores. En el simulador (Figura 2) se elige un activo, un modo de falla y su severidad, o se escribe la observación de un técnico, y se ve el diagnóstico de los cuatro sistemas con su explicación.
- **Landing de presentación:** una página estática publicada en GitHub Pages que presenta lo realizado, lo consultado y lo logrado, con cifras generadas desde los reportes.

{{figura:web_simulador}}

# Resultados

## Pruebas

Las {{v:pruebas}} pruebas automáticas pasan. Además, cada página de la web se recorrió con un navegador automatizado (Playwright) en 57 acciones, sin errores de consola, y la landing se revisó en escritorio, móvil y modo oscuro.

## Métricas de clasificación

La Tabla 5 resume el desempeño en la unidad reservada de cada tipo, la prueba más exigente porque el modelo nunca vio esa máquina. La Figura 3 muestra el F1 macro con su intervalo de confianza en los dos conjuntos de prueba.

{{tabla:resultados}}

{{figura:f1}}

Los tres sistemas con aprendizaje profundo superan ampliamente al sistema de reglas solo: el F1 macro pasa de {{v:f1_m0_nv}} (M0) a {{v:f1_m1_nv}} (M1) y {{v:f1_m3_nv}} (M3). La Tabla 6 muestra las diferencias pareadas. M3 mejora a M1 en {{v:dif_f1_m3_m1}} puntos de F1 (IC 95 %: {{v:dif_f1_m3_m1_ic}}), una diferencia pequeña pero consistente. M2 no se diferencia de M1 de forma significativa.

{{tabla:diferencias}}

## Reducción de falsas alarmas

La mayor ganancia del conocimiento experto está en las falsas alarmas ante condiciones confusoras (Figura 4). En la unidad no vista, la tasa baja de {{v:fa_m1_nv}} con M1 a {{v:fa_m3_nv}} con M3, una reducción de {{v:fa_red_rel}} relativa, frente a {{v:fa_m0_nv}} del sistema de reglas solo. En eventos de falsa alarma por unidad y año, M3 genera {{v:ev_fa_m3}} frente a {{v:ev_fa_m1}} de M1 y {{v:ev_fa_m0}} de M0.

{{figura:falsas}}

## Aviso temprano e impacto

Con los sistemas de aprendizaje profundo se detecta cerca del 99 % de las fallas ({{v:detect_m3}} con M3), frente a {{v:detect_m0}} con M0. La Tabla 7 muestra el costo relativo por unidad y año, en unidades de una reparación planificada, bajo tres supuestos sobre el costo de una falla no detectada. M3 tiene el menor costo en los tres escenarios y ahorra entre {{v:ahorro_r3}} y {{v:ahorro_r9}} frente al sistema de reglas solo.

{{tabla:impacto}}

## Latencia

En la API local, el percentil 95 del peor activo es de {{v:lat_sin}} por diagnóstico sin explicación y {{v:lat_con}} con la explicación completa (gradientes integrados y traza de reglas), por debajo del objetivo de 200 ms.

## Explicabilidad

La Tabla 8 resume las métricas de las explicaciones. Los tres sensores con más peso coinciden con la firma real de la falla en el {{v:xai_firma}} de los casos, frente al {{v:xai_azar}} al azar, y con las variables de las reglas disparadas en el {{v:xai_reglas}}. Al anular esos tres sensores, la probabilidad de la clase cae en promedio un {{v:fidelidad}}, frente a un {{v:fidelidad_azar}} al anular tres al azar. Las explicaciones son estables ante ruido pequeño.

{{tabla:xai}}

## Validación con expertos y usuarios

No hubo técnicos ni evaluadores humanos disponibles. El instrumento de evaluación, una comparación pareada y a ciegas entre la explicación del modelo solo y la explicación híbrida para 12 alertas, se aplicó a un panel de cinco agentes con perfiles de la planta: técnico electromecánico, jefe de mantenimiento, instrumentista, ingeniero de confiabilidad y supervisor de turno. La Tabla 9 muestra que la explicación híbrida obtuvo mejores puntajes en las tres dimensiones y fue la preferida en los 60 pares. Un control con dos versiones del mismo contenido, una con relleno, no mostró sesgo por longitud. Estos resultados son una validación exploratoria: los cinco perfiles son el mismo modelo de lenguaje y sus respuestas no son independientes. El instrumento para personas, con consentimiento informado, está listo para aplicarse (Anexo E).

{{tabla:panel}}

El panel también dejó hallazgos cualitativos que se incorporaron al sistema: las acciones sin regla aparecían como identificadores técnicos y ahora se muestran en lenguaje natural; además, señaló que las probabilidades cercanas al 100 % sin respaldo de reglas y los valores apenas por encima del umbral generan desconfianza.

## Equidad

La Tabla 10 muestra el desempeño por grupo. Una observación incorrecta del técnico duplica la falsa alarma del sistema de reglas solo ({{v:fa_sin_obs_m0}} sin observación frente a {{v:fa_obs_inc_m0}} con una observación incorrecta), mientras que en M3 el efecto casi desaparece ({{v:fa_sin_obs_m3}} frente a {{v:fa_obs_inc_m3}}). La brecha de acierto de M3 entre turnos es de {{v:brecha_turno}} puntos. Entre tipos de activo, la brecha baja de 21.8 puntos con M0 a 5.7 con M3; el compresor de tornillo es el activo más difícil.

{{tabla:equidad}}

## Análisis de errores

Los errores de clasificación se concentran en pocas clases (Tabla 11). La cavitación tiene solo tres ventanas de soporte en prueba, por lo que su F1 no es confiable. La falla de la válvula de admisión del compresor se confunde con la operación normal en ambos sentidos: hay fallas que pasan como normales y ventanas sanas marcadas como esa falla. Es un modo de detección, con muy poco tiempo de firma antes de la falla. En el desgaste de herramienta del CNC, cerca de la mitad de las ventanas con falla se clasifican como normales: su severidad simulada se calibró con AI4I 2020 y es menor que la de otros modos, así que su firma es débil.

{{tabla:peores_clases}}

Durante el desarrollo se registraron 31 errores en la base de errores del proyecto, con su causa raíz y prevención. Los más relevantes para los resultados fueron:

- **ERR-020:** la primera versión del simulador daba 100 % de detección al sistema de reglas, porque las firmas coincidían exactamente con los umbrales. Se corrigió con firmas incompletas, severidad variable y contraste con datos públicos.
- **ERR-023:** el 99.1 % de las "falsas alarmas" eran avisos tempranos correctos de una degradación en curso. Se creó la categoría de ventanas grises.
- **ERR-024:** la métrica de estabilidad de las explicaciones era siempre 1 con el nivel de ruido inicial. Se reemplazó por una curva con varios niveles.

# Discusión

## Respuesta a la pregunta orientadora

La integración que funcionó fue la fusión posterior (M3): el modelo de aprendizaje profundo aporta la capacidad de detectar y las reglas aportan prudencia y explicación. El conocimiento experto no mejoró de forma importante el F1 ({{v:dif_f1_m3_m1}} puntos), pero sí redujo las falsas alarmas ante condiciones confusoras en un {{v:fa_red_rel}} y permitió explicar cada alerta con reglas, valores reales y acciones. Incorporar el conocimiento como entrada del modelo (M2) no dio una mejora significativa. Usar las reglas como veto tampoco funcionó: con su cobertura actual, el veto rechazaba alertas correctas y el F1 de validación caía a 0.47–0.69, por lo que ningún activo lo eligió. Este hallazgo coincide con la observación de von Rueden et al. (2021) de que el beneficio del conocimiento previo depende de su calidad y cobertura.

## Relación con los riesgos definidos (RA/R1–R6)

El proyecto identificó un riesgo transversal de aplicación indebida (RA) y seis riesgos específicos (R1–R6), que agrupan el registro de riesgos del informe de sesgos y limitaciones. RA es el más grave porque no depende del desempeño del modelo, sino del uso que se le dé: si el sistema se usara para evaluar a los técnicos o para detener máquinas sin intervención humana, causaría daño aunque sus predicciones fueran correctas. La Tabla 12 resume cada riesgo con su evidencia y su mitigación.

Tabla: Riesgos del sistema y su tratamiento
| Código | Riesgo | Evidencia | Mitigación | Estado |
|---|---|---|---|---|
| RA | Aplicación indebida: evaluar o vigilar a los técnicos, o automatizar paros y funciones de seguridad | Las observaciones identifican técnico y turno; el Reglamento europeo considera de alto riesgo evaluar trabajadores | Las observaciones solo diagnostican equipos; seudónimos; el sistema recomienda y una persona decide; no ejecuta acciones | Mitigado por diseño |
| R1 | Circularidad entre simulador y reglas | Las firmas de falla parten de los umbrales que conocen las reglas | Firmas incompletas, severidad variable, deriva, contraste con AI4I 2020 y SKAB | Reducido, no eliminado |
| R2 | Evaluación optimista | Los confusores se aprenden del mismo generador; las semillas no cambian los datos | Máquina no vista, intervalos entre semillas y resultados declarados como sintéticos | Abierto |
| R3 | Sesgo de técnico y turno | Una observación incorrecta lleva la falsa alarma de M0 de {{v:fa_sin_obs_m0}} a {{v:fa_obs_inc_m0}} | M3 pondera poco el texto ({{v:fa_sin_obs_m3}} frente a {{v:fa_obs_inc_m3}}); FC de reglas percibidas ≤ 0.80 | Medido y acotado |
| R4 | Brecha entre tipos de activo | Brecha de acierto de 21.8 puntos con M0 y 5.7 con M3 | Un modelo por activo; ampliar reglas en compresor y CNC | Medido |
| R5 | Sobreconfianza en la automatización | Probabilidades cercanas al 100 % sin respaldo de reglas | La explicación dice cuándo ninguna regla respalda la alerta; probabilidad y certeza por separado | Parcial |
| R6 | Deriva de datos y operación | Sin monitoreo de deriva; la API no tiene autenticación | Línea base por unidad; requisitos previos a uso real | Abierto |
Nota: el detalle de cada riesgo está en `reports/sesgos_limitaciones.md`. RA se mitiga con decisiones de diseño (D-062 a D-069), no con métricas.

## Ética

El sistema recomienda y una persona decide. No ejecuta paros ni órdenes de trabajo, y cada explicación muestra sus límites. La decisión ética más importante del proyecto es que las observaciones de los técnicos se usan solo para diagnosticar los equipos y nunca para evaluar a las personas. Esa decisión responde a la vez a la protección de datos personales, a la dignidad laboral y a la clasificación de riesgo del Reglamento europeo, que considera de alto riesgo los sistemas que evalúan el desempeño de trabajadores (Unión Europea, 2024). Los técnicos se identifican con seudónimos y no se recogen datos sensibles. En una planta real se requerirían la autorización informada de los técnicos y la integración con la gestión del cambio del sistema de seguridad y salud en el trabajo (Ministerio del Trabajo, 2014, 2019). La gestión de riesgos sigue el marco del NIST (National Institute of Standards and Technology, 2023), y las normas ISO/IEC de IA se citan como referencia sin declarar conformidad (International Electrotechnical Commission, 2021, 2023a, 2023b). El acta ética está en el Anexo G.

## Sesgos

El sesgo más importante es la circularidad entre simulador y reglas: las firmas de falla se basan en los mismos umbrales que conocen las reglas, de modo que los sistemas con conocimiento juegan "en casa". Se redujo con firmas incompletas, severidad variable y deriva, pero no se eliminó. Las condiciones confusoras se aprenden del mismo generador con que se evalúan, por lo que la baja falsa alarma es optimista. El sesgo de técnico y turno se inyectó a propósito y se midió: afecta sobre todo al sistema de reglas solo, que toma la observación del técnico como evidencia. Finalmente, la sobreconfianza en las probabilidades cercanas al 100 % es un riesgo de sesgo de automatización (Parasuraman y Riley, 1997), mitigado en parte porque la explicación dice cuándo ninguna regla respalda la alerta.

## Limitaciones

- Los datos son sintéticos: los resultados no demuestran el desempeño en una planta real.
- Ninguna regla fue validada por un técnico, y las normas de pago se consultaron por fuentes secundarias.
- La evaluación de explicaciones se hizo con agentes y no con personas.
- Los intervalos de confianza reflejan la variación entre semillas, no la de otros datos.
- Algunas clases tienen muy poco soporte en prueba.
- El prototipo no monitorea la deriva de los datos ni registra las decisiones humanas, y no tiene autenticación.

El detalle de cada riesgo y su mitigación está en el informe de sesgos y limitaciones del repositorio (`reports/sesgos_limitaciones.md`).

# Conclusiones y recomendaciones

## Conclusiones

1. Es posible integrar un modelo de aprendizaje profundo con una base de conocimiento experto en un sistema que prediga fallas y las explique con variables, reglas, causas y acciones. La fusión posterior (M3) logró el mejor F1 en la máquina no vista ({{v:f1_m3_nv}}) y la menor falsa alarma ante confusores ({{v:fa_m3_nv}}).
2. El aporte del conocimiento experto está más en la explicación y en la reducción de falsas alarmas que en la capacidad de detectar. El sistema de reglas solo detecta menos de siete de cada diez fallas, y como veto rechaza alertas correctas.
3. La explicación híbrida fue preferida en la evaluación exploratoria, sobre todo cuando una regla respalda la alerta. Esto sugiere que el valor de la base de conocimiento para el usuario crece con su cobertura.
4. La adquisición del conocimiento por agentes, con trazabilidad completa a fuentes, permitió construir una base de {{v:reglas}} reglas sin acceso a expertos, pero no sustituye su validación.
5. Las decisiones éticas de diseño, como no evaluar personas, mantener la supervisión humana y explicar los límites, son tan parte del artefacto como el código.

## Recomendaciones

1. Validar las reglas y la ontología con técnicos de mantenimiento y con el texto oficial de las normas antes de cualquier uso real.
2. Reentrenar y recalibrar los modelos con datos reales etiquetados de la planta.
3. Aplicar la evaluación de explicaciones con técnicos reales, usando el instrumento preparado.
4. Ampliar la cobertura de las reglas en los activos y modos con peor desempeño (compresor de tornillo y fallas rápidas del CNC) antes de volver a probar el veto.
5. Agregar detección de deriva, registro de las decisiones humanas, autenticación y pruebas de carga a la API.
6. Revisar los riesgos RA/R1–R6 antes de cualquier piloto, empezando por los abiertos (R2 y R6).

{{referencias}}

# Anexos

## Anexo A. Matriz de adquisición del conocimiento

Todo el conocimiento proviene de revisión documental asistida por agentes. Las técnicas fueron revisión de normas a través de fuentes secundarias (T1), literatura científica (T2), guías de fabricantes (T3), análisis de conjuntos de datos públicos (T4) y razonamiento físico del agente (T5). Las validaciones fueron triangulación de al menos dos fuentes o una norma (V1), resolución de conflictos por el valor más conservador (V2), coherencia automática entre archivos (V3), revisión cruzada por un agente revisor (V4) y contraste con conjuntos de datos públicos (V5). La matriz completa y las {{v:decisiones}} decisiones con sus fuentes están en `knowledge/acquisition/` del repositorio.

{{tabla:matriz}}

## Anexo B. Reglas de diagnóstico

{{tabla:reglas}}

## Anexo C. Ontología

La ontología completa está en `knowledge/ontology/metaltech.owl` (formato OWL, abrible en Protégé) y se regenera con `python -m metaltech.kb.ontology`. Sus clases y propiedades se resumen en la Tabla 3. Las propiedades de objeto son: {{v:propiedades_objeto}}.

## Anexo D. Código

El código, los datos de configuración, las pruebas y la documentación están en {{v:repositorio}}. La landing de presentación está publicada en https://luisldra.github.io/proyecto_ing_conocimiento/. El README describe la instalación y los comandos; los módulos principales son `data` (simulador y ventanas), `kb` (base de conocimiento, léxico, motor de reglas y ontología), `models`, `hybrid` (M0–M3), `xai`, `metrics`, `api` y `dashboard`.

## Anexo E. Consentimiento informado

Texto que se entrega a cada evaluador antes de la evaluación de explicaciones con personas:

> Usted está invitado a participar en una evaluación académica del curso Ingeniería del Conocimiento (Universidad de Caldas). Leerá 12 alertas de un sistema de mantenimiento predictivo ficticio, con datos sintéticos, y calificará qué tan claras y útiles le parecen sus explicaciones. Le tomará unos 20 minutos.
>
> Su participación es voluntaria y puede retirarse en cualquier momento sin dar razones. No se registra su nombre: sus respuestas se identifican con un código (E01, E02…). Solo se registra su perfil (estudiante, docente o técnico). Las respuestas se usarán únicamente en el informe y la presentación del proyecto, en forma agregada, de acuerdo con la Ley 1581 de 2012 de protección de datos personales.
>
> No hay riesgos previstos ni respuestas correctas o incorrectas. Si tiene preguntas, puede dirigirlas al equipo del proyecto.
>
> ☐ He leído la información anterior y acepto participar. Código asignado: ______ Fecha: ______

## Anexo F. Ficha de los datos sintéticos

- **Origen:** simulación con `python -m metaltech.data.generator` y semilla 42; no proviene de ninguna planta real ni contiene datos personales.
- **Contenido:** 36 meses cada 10 minutos, {{v:unidades}} unidades, {{v:filas}} filas, {{v:episodios}} episodios de falla y {{v:observaciones}} observaciones de técnicos ficticios (T01–T08, I01–I02).
- **Partición:** temporal 60/20/20 con purga entre cortes; la última unidad de cada tipo se reserva solo para evaluación.
- **Supuestos:** formas, duraciones y magnitudes basadas en literatura, contrastadas con AI4I 2020 y SKAB; confusores y deriva supuestos.
- **Limitaciones:** firmas más completas que las reales; una falla por unidad a la vez; clases desbalanceadas (2.4 % de filas positivas); el menor acierto nocturno de los técnicos es un sesgo inyectado para medir equidad.
- **Reproducibilidad:** con la misma semilla y configuración el resultado es idéntico; un manifiesto guarda los conteos y el SHA-256 de cada archivo.

## Anexo G. Acta ética

**Declaración de datos.** Todos los datos de sensores, fallas, técnicos y turnos son sintéticos y ficticios. No se recogió ningún dato personal. Los conjuntos públicos de referencia se usaron solo para contrastar el simulador.

**Origen del conocimiento.** La base de conocimiento proviene de revisión documental hecha por agentes de IA, con fuentes citadas. No hubo entrevistas ni participación de técnicos, y ninguna regla fue validada por un técnico.

**Uso de IA.** El equipo usó agentes de IA para investigar fuentes, escribir código y documentación y evaluar explicaciones. El proceso quedó registrado en la bitácora y en la base de errores del repositorio, incluidos los errores de los agentes.

**Compromisos de diseño.** El sistema recomienda y una persona decide; no ejecuta funciones de seguridad de las máquinas; las observaciones de los técnicos nunca se usan para evaluar personas; los técnicos se identifican con seudónimos y no se recogen datos sensibles; en una planta real se pediría autorización informada y se integraría el sistema a la gestión de seguridad y salud en el trabajo; cada alerta muestra sus variables, reglas y límites.

Firmado por el equipo: Alejandro Pineda Gomez, Luis David Rodríguez Arias, Ivan Junior Echeverri Gomez y David Ramirez Cruz.

## Anexo H. Esquema de la presentación

La presentación usa como esquema la landing del proyecto (https://luisldra.github.io/proyecto_ing_conocimiento/) y recorre sus secciones en orden: el reto, lo consultado, la arquitectura, los resultados, una alerta explicada, ética y limitaciones, y el equipo. Entre la arquitectura y los resultados se hace la demostración en vivo en la web demostrativa. Dura de 10 a 15 minutos y sigue el guion de `docs/demo_guion.md`: contexto y problema (2 min), base de conocimiento y ontología (3 min), simulación de una falla en vivo (4 min), resultados (3 min), y ética, limitaciones y cierre (2 min).
