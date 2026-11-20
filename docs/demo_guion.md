# Guion de la demostración (10 a 15 minutos)

> Fase 10. Para la sustentación del Proyecto 3. Ajustar al esquema presentado en clase (Anexo H del documento).
> Las cifras son las de `reports/` al 2026-11-20; si se regeneran los resultados, revisar con la landing o el documento.

## Antes de empezar (preparación, 10 minutos antes)

1. Abrir una terminal en la raíz del repositorio y activar el entorno (`.venv\Scripts\Activate.ps1`).
2. Levantar la API: `uvicorn metaltech.api.main:app`. Comprobar http://127.0.0.1:8000/health.
3. Levantar la web: `streamlit run src/metaltech/dashboard/app.py`. Abrir http://localhost:8501 y visitar una vez cada página para que carguen los modelos.
4. Tener abiertas tres pestañas del navegador:
   - la landing (https://luisldra.github.io/proyecto_ing_conocimiento/);
   - la web en **Simulador**;
   - el documento PDF o el póster.
5. Aumentar el zoom del navegador al 125 % para que se lea desde el fondo del salón.

**Plan B:** si la API no responde, la web carga la misma API dentro del proceso, y basta con `streamlit run`. Si la web no carga, se presenta con la landing, las capturas de `docs/documento_APA/figuras/` y el póster.

## Reparto

| Bloque | Tiempo | Presenta | Qué se muestra |
|---|---|---|---|
| 1. Contexto y problema | 2 min | David | Landing: portada y reto |
| 2. Conocimiento y ontología | 3 min | Alejandro | Web: Base de conocimiento |
| 3. Simulación en vivo | 4 min | Junio | Web: Simulador y Explicación |
| 4. Resultados | 3 min | Luis David | Web: Modelos y comparación; Equidad e impacto |
| 5. Ética, limitaciones y cierre | 2 min | David | Landing: ética; póster |
| Preguntas | 1–5 min | Todos | |

## 1. Contexto y problema (2 min)

**Pantalla:** landing, sección de portada y luego "El reto".

- Metal Tech es una planta ficticia con sensores en motores, bombas, compresores, prensas, bandas y CNC. Los datos se miran por separado y los técnicos diagnostican con frases como "la bomba está golpeando".
- La pregunta del proyecto: cómo integrar Deep Learning con una base de conocimiento experto para predecir fallas **y explicarlas**.
- Aclarar desde el inicio dos condiciones: **no hubo entrevistas**, porque el conocimiento se adquirió con un agente investigador que revisó fuentes, y **todos los datos son sintéticos**.

## 2. Conocimiento y ontología (3 min)

**Pantalla:** web → **Base de conocimiento**.

1. Elegir el activo *Bomba centrífuga* y la sección **Reglas**. Mostrar la regla **R13** (cavitación, FC 0.85), con su acción y su fuente.
2. Explicar en una frase el factor de certeza: la regla aporta su FC multiplicado por la certeza de sus síntomas, y varias reglas sobre la misma falla se combinan como en MYCIN.
3. Sección **Léxico de técnicos**: "la bomba está golpeando" se traduce en golpeteo percibido, con cavitación, obstrucción o rodamiento como candidatos.
4. Sección **Ontología**, con el grafo de la bomba: activo → componentes → modos de falla → síntomas, causas y acciones.
5. Cifras: 55 reglas, 31 modos de falla, 75 decisiones documentadas y 126 referencias.

## 3. Simulación en vivo (4 min)

**Pantalla:** web → **Simulador**.

1. Elegir **Bomba centrífuga** y **Cavitación por NPSH disponible insuficiente**, con avance y severidad en 1.0. Pulsar **Diagnosticar**.
2. Leer las tres tarjetas: M0 (solo reglas), M1 (solo modelo) y M3 (fusión) identifican la cavitación.
3. Bajar a **Explicación**:
   - pesos de los sensores: el margen de NPSH es el que más pesa;
   - reglas R14 y R13 con sus **valores reales** frente al umbral;
   - acciones sugeridas y causas posibles.
4. Bajar a la ventana de sensores: el margen de NPSH cae bajo el umbral de alerta y la vibración de alta frecuencia sube.
5. **Caso contrario:** elegir **operación normal**. Ningún sistema da alerta.
6. **Observación del técnico:** escribir o elegir "el motor está cantando" en un motor y mostrar cómo la observación aparece en la explicación, pero no decide sola.

Mensaje clave: *el modelo detecta; las reglas dicen por qué y qué hacer.*

## 4. Resultados (3 min)

**Pantalla:** web → **Modelos y comparación**, y luego **Equidad e impacto**.

1. F1 macro en la **máquina nunca vista**: M0 0.656, M1 0.932, M2 0.934 y M3 **0.940** (5 semillas, intervalo del 95 %).
2. Falsas alarmas ante condiciones confusoras: de 4.2 % con M1 a **3.1 %** con M3, un 27 % menos. El sistema de reglas solo tiene 17.3 %.
3. El hallazgo honesto: el conocimiento **casi no sube el F1** (+0.8 puntos), pero reduce falsas alarmas y explica. Usado como veto, rechaza alertas correctas.
4. Equidad: una observación incorrecta del técnico duplica la falsa alarma del sistema de reglas solo (1.05 % → 2.08 %); en M3 casi no cambia.
5. Latencia: 79 ms (p95) para un diagnóstico con explicación completa.

## 5. Ética, limitaciones y cierre (2 min)

**Pantalla:** landing, sección de ética; al final, el póster.

- El sistema **recomienda**; una persona decide. No ejecuta paros.
- Las observaciones de los técnicos **nunca se usan para evaluarlos** (Ley 1581 de 2012, D-063).
- Limitaciones:
  - datos sintéticos;
  - reglas sin validar por técnicos;
  - explicaciones evaluadas con un panel de agentes, no con personas.
- Cierre: la fusión fue la mejor integración; el siguiente paso es validar con técnicos y datos reales.

## Preguntas probables

| Pregunta | Respuesta corta | Dónde mostrarlo |
|---|---|---|
| ¿Por qué no entrevistaron técnicos? | La planta es ficticia y no había técnicos disponibles. Un agente revisó fuentes con la regla de 2 fuentes o 1 norma; cada decisión está documentada | `knowledge/acquisition/decisiones.md` |
| ¿Los resultados valen para una planta real? | No. Son datos sintéticos; el informe de sesgos explica por qué | `reports/sesgos_limitaciones.md` |
| ¿Por qué M3 y no M2? | M2 no mejoró a M1 de forma significativa; M3 sí, sobre todo en falsas alarmas | Tabla 6 del documento |
| ¿El simulador favorece a las reglas? | Sí, en parte: es el principal sesgo. Se redujo con firmas incompletas y severidad variable | Informe de sesgos, sección 3 |
| ¿Cómo se evaluó la explicabilidad? | Fidelidad, concordancia con la firma y con las reglas, estabilidad, y un panel exploratorio de agentes | Tabla 8 y Tabla 9 |
| ¿Qué pasa con los datos de los técnicos? | Seudónimos, sin datos sensibles y nunca para evaluar personas | Acta ética, D-062 a D-064 |
