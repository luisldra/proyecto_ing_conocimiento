# Guion de la presentación (14 minutos + preguntas)

> Proyecto 3 – Mantenimiento predictivo explicable en Metal Tech · Ingeniería del Conocimiento 2026-2 · Entrega: 2026-11-30.
> **Esquema:** la landing (https://luisldra.github.io/proyecto_ing_conocimiento/). Se recorren sus secciones en orden y la demo en vivo va en la sección *Prototipo*, después de la arquitectura.
> **Regla del equipo:** 4 personas, máximo 2 intervenciones cada una.

## Reparto

| # | Intervención | Presenta | Tiempo | Acumulado | Pantalla |
|---|---|---|---|---|---|
| 1 | Apertura: problema y pregunta | David Ramirez Cruz | 1:30 | 1:30 | Landing: Inicio y El reto |
| 2 | Lo consultado y la base de conocimiento | Alejandro Pineda Gomez | 2:30 | 4:00 | Landing: Conocimiento → web: Base de conocimiento |
| 3 | Método, datos y arquitectura | Luis David Rodríguez Arias | 2:00 | 6:00 | Landing: Método y Arquitectura |
| 4 | Prototipo y demostración en vivo | Ivan Junior Echeverri Gomez | 3:00 | 9:00 | Landing: Prototipo → web: Simulador |
| 5 | Resultados: modelo solo vs. modelo + conocimiento | Luis David Rodríguez Arias | 2:00 | 11:00 | Landing: Resultados |
| 6 | Explicabilidad, equidad y riesgos | Alejandro Pineda Gomez | 1:30 | 12:30 | Landing: Explicación y Ética |
| 7 | Cierre: límites, conclusiones y entregables | David Ramirez Cruz | 1:30 | 14:00 | Landing: Ética (final) y Equipo |
| — | Preguntas | Todos (ver tabla al final) | 1–5 min | | |

Intervenciones por persona: David 2, Alejandro 2, Luis David 2, Ivan Junior 1 (la más larga, la demo).

## Antes de empezar (15 minutos antes)

1. Un solo computador para toda la presentación; el control lo tiene quien presenta.
2. Terminal en la raíz del repositorio con el entorno activado (`.venv\Scripts\Activate.ps1`).
3. Levantar la API (`uvicorn metaltech.api.main:app`) y comprobar http://127.0.0.1:8000/health.
4. Levantar la web (`streamlit run src/metaltech/dashboard/app.py`) y visitar una vez el **Simulador** y la **Base de conocimiento** para que carguen los modelos.
5. Pestañas abiertas, en este orden: (1) landing publicada, (2) web en *Base de conocimiento*, (3) web en *Simulador*, (4) póster PDF.
6. Zoom del navegador al 125 %. Notificaciones del sistema desactivadas.
7. Una persona del equipo (la que no está hablando) lleva el cronómetro y avisa con una seña a los 30 segundos del límite.

**Plan B:** si la API no responde, la web usa la misma API dentro del proceso (basta `streamlit run`). Si la web no carga, Ivan Junior presenta la demo con la sección *Prototipo* de la landing y la Figura 2 del documento (captura del simulador). Si no hay internet, abrir `landing/index.html` con doble clic: funciona sin conexión.

---

## 1. Apertura: problema y pregunta — David (1:30)

**Pantalla:** landing, portada; bajar a *El reto*.

**Qué decir:**
- "Buenos días. Somos Alejandro, Luis David, Ivan Junior y David, y presentamos el Proyecto 3: mantenimiento predictivo explicable en la planta Metal Tech."
- Metal Tech tiene sensores en motores, bombas, compresores, prensas, bandas y CNC, pero los datos se miran por separado. Los técnicos diagnostican con los sentidos: *"el motor está cantando"*, *"la bomba está golpeando"*. Ese criterio cambia entre turnos y personas, y lleva a falsas alarmas e intervenciones tardías.
- Leer la pregunta de la portada: **¿cómo integrar un modelo de Deep Learning con una base de conocimiento experto para predecir fallas y generar diagnósticos explicables?**
- Señalar las cifras de la portada: "Al final les mostraremos de dónde salen estas cifras."
- Dos aclaraciones desde el inicio: **no hubo entrevistas** (la planta es ficticia y no había técnicos disponibles) y **todos los datos son sintéticos**.

**Transición:** "Si no había expertos a quién preguntar, ¿de dónde salió el conocimiento? Alejandro."

## 2. Lo consultado y la base de conocimiento — Alejandro (2:30)

**Pantalla:** landing, *Conocimiento*; luego pestaña de la web en **Base de conocimiento**.

**Qué decir:**
- Un agente investigador consultó normas por fuentes públicas (ISO 17359, ISO 20816, ANSI/HI 9.6.1…), literatura y datasets, con una regla: **cada regla y cada umbral con al menos dos fuentes o una norma**; si las fuentes chocan, el valor más conservador. Un segundo agente revisó todo de forma independiente.
- Señalar los contadores: 75 decisiones documentadas, 126 referencias, 55 reglas, 31 modos de falla.
- En la web, activo *Bomba centrífuga*, sección **Reglas**: mostrar **R13**: "SI margen de NPSH bajo Y vibración de alta frecuencia alta Y caudal inestable ENTONCES cavitación, con factor de certeza 0.85". Explicar en una frase: la certeza de la regla se multiplica por la de sus síntomas y varias reglas se combinan como en MYCIN.
- Sección **Léxico de técnicos**: "la bomba está golpeando" → golpeteo percibido → cavitación, obstrucción o rodamiento. "Una frase del técnico nunca diagnostica sola: sugiere, y los sensores confirman."
- Sección **Ontología**: el grafo une activo, componentes, fallas, síntomas, causas y acciones; está en OWL y la valida el razonador HermiT.

**Transición:** "Con el conocimiento listo faltaban los datos y los modelos. Luis David."

## 3. Método, datos y arquitectura — Luis David (2:00)

**Pantalla:** landing, *Método*; luego *Arquitectura*.

**Qué decir:**
- Método: ABP con CommonKADS para el conocimiento, CRISP-DM para los datos y modelos, y agentes de IA con roles, bitácora y base de errores; once fases.
- Datos: 32 máquinas simuladas, 36 meses cada 10 minutos, más de 5 millones de filas y 1075 fallas, con eventos que imitan fallas y técnicos ficticios. Una máquina de cada tipo se reserva y el modelo **nunca la ve**: es la prueba más exigente.
- Arquitectura (diagrama): la ventana de 6 horas va por dos caminos: el modelo de Deep Learning (MLP, CNN1D o LSTM según el activo) y el motor de reglas. Comparamos **cuatro sistemas**: M0 solo reglas, M1 solo modelo, M2 el conocimiento como entrada del modelo y **M3, la fusión** de la probabilidad del modelo con la certeza de las reglas.

**Transición:** "Ahora vamos a verlo funcionando. Ivan Junior."

## 4. Prototipo y demostración en vivo — Ivan Junior (3:00)

**Pantalla:** landing, *Prototipo* (10 segundos); luego pestaña de la web en **Simulador**.

**Qué decir y hacer:**
1. "Construimos una API y una web de 8 páginas; la web usa la misma API que cualquier otro sistema podría usar."
2. En el **Simulador**: *Bomba centrífuga*, falla **Cavitación por NPSH disponible insuficiente**, avance y severidad en 1.0. Pulsar **Diagnosticar**.
3. "Los tres sistemas en vivo, M0, M1 y M3, identifican la cavitación."
4. Bajar a **Explicación**: "El modelo se apoyó sobre todo en el margen de NPSH" (barras); "y lo respaldan las reglas R14 y R13, con el **valor real** de cada sensor frente a su umbral" (tablas); leer la acción sugerida.
5. Bajar a la ventana de sensores: el margen de NPSH cruza la línea de alerta y la vibración de alta frecuencia sube.
6. **Caso contrario:** cambiar a *operación normal* y diagnosticar: ningún sistema da alerta.
7. Si sobra tiempo: elegir en *Observación del técnico* "el motor está cantando" en un motor y mostrar que aparece en la explicación sin decidir sola.

**Mensaje clave:** "El modelo detecta; las reglas dicen por qué y qué hacer."

**Transición:** "Eso es un caso. ¿Qué pasa con miles de casos? Luis David."

## 5. Resultados — Luis David (2:00)

**Pantalla:** landing, *Resultados*.

**Qué decir:**
- En la máquina nunca vista, con 5 semillas: F1 macro de **0.940 con la fusión**, 0.932 con el modelo solo y 0.656 con las reglas solas.
- El hallazgo honesto: el conocimiento **casi no sube el F1** (+0.8 puntos), pero **reduce las falsas alarmas** ante eventos que imitan fallas: de 4.2 % a 3.1 %. En eventos por unidad y año, cerca de la mitad que el modelo solo.
- El conocimiento como entrada (M2) no mejoró al modelo, y usar las reglas como **veto** rechazaba alertas correctas: ningún activo lo eligió.
- La fusión detecta cerca del 99 % de las fallas y diagnostica con explicación en 79 ms.

**Transición:** "Un buen número no basta si nadie entiende la alerta. Alejandro."

## 6. Explicabilidad, equidad y riesgos — Alejandro (1:30)

**Pantalla:** landing, *Explicación*; luego *Ética* hasta la tabla de riesgos.

**Qué decir:**
- Cada alerta dice por qué: el 74.6 % de los sensores con más peso son los que la falla mueve de verdad (al azar sería 33 %).
- Un panel de cinco agentes con perfiles de planta prefirió la explicación híbrida en los 60 casos. **No son personas**: es exploratorio y así lo declaramos.
- Equidad: una observación incorrecta del técnico duplica la falsa alarma de las reglas solas; la fusión casi no cambia.
- Tabla de riesgos: el más grave es **RA, la aplicación indebida**: usar el sistema para evaluar a los técnicos o para detener máquinas sin una persona. Por diseño, las observaciones solo diagnostican equipos.

**Transición:** "Para cerrar, lo que el sistema no es. David."

## 7. Cierre: límites, conclusiones y entregables — David (1:30)

**Pantalla:** landing, *Ética* (columna derecha y marco legal); luego *Equipo* y recursos.

**Qué decir:**
- Límites: datos sintéticos, reglas sin validar por técnicos, normas consultadas por fuentes públicas, costos supuestos. El sistema **recomienda; el técnico decide**.
- Marco legal: Ley 1581 de protección de datos, SG-SST y el Reglamento europeo de IA como referencia.
- Conclusiones:
  1. Integrar Deep Learning y conocimiento experto es posible y la mejor forma fue la **fusión**.
  2. El conocimiento aporta **explicación y prudencia** más que detección.
  3. El siguiente paso es validar con técnicos y datos reales.
- Señalar los recursos: documento APA, póster, manuales, repositorio y carpeta de entrega.
- "Gracias. Quedamos atentos a sus preguntas."

---

## Preguntas: quién responde

| Tema | Responde | Respuesta corta | Dónde mostrarlo |
|---|---|---|---|
| ¿De dónde salió el conocimiento sin entrevistas? | Alejandro | Un agente revisó fuentes con la regla de 2 fuentes o 1 norma; cada decisión está documentada | `knowledge/acquisition/decisiones.md`; web: Base de conocimiento → Decisiones |
| ¿Qué es el factor de certeza? | Alejandro | Confianza de 0 a 1 de una regla; se combinan como en MYCIN | Web: Base de conocimiento → Reglas |
| ¿Por qué datos sintéticos? ¿Valen para una planta real? | Luis David | No hay datos de la planta; los resultados no prueban desempeño real (riesgos R1 y R2) | Informe de sesgos |
| ¿Por qué M3 y no M2? | Luis David | M2 no mejoró al modelo; M3 sí, sobre todo en falsas alarmas | Landing: Resultados |
| ¿Cómo se usa la API? ¿Funciona sin internet? | Ivan Junior | API local con documentación en `/docs`; la web funciona sin la API levantada | `docs/manuales/manual_api.md` |
| ¿Cómo se evaluaron las explicaciones? | Alejandro | Fidelidad, concordancia, estabilidad y un panel exploratorio de agentes | Web: Explicación |
| ¿Qué pasa con los datos de los técnicos? | David | Seudónimos, sin datos sensibles y nunca para evaluar personas (Ley 1581) | Acta ética; landing: Ética |
| ¿Qué falta para usarlo en una planta? | David | Validar reglas con técnicos, reentrenar con datos reales, monitorear deriva | Informe de sesgos, sección 10 |

## Consejos

- Hablar al público, no a la pantalla; quien no presenta no habla.
- Decir las cifras redondeadas en voz alta y dejar el detalle en pantalla.
- No leer la landing: señalar y resumir.
- Ensayar al menos una vez completo con cronómetro antes del 2026-11-30.
