# Evaluación humana de las explicaciones

**Objetivo:** medir si el conocimiento experto (reglas, observación del técnico y acción sugerida) hace que la explicación de una alerta sea más comprensible, útil y confiable que la del modelo solo. Es la evaluación humana prevista en la Fase 6 del plan (D-057, D-058).

**Estado:** el instrumento está listo y **todavía no se ha aplicado**. No hay resultados hasta que el equipo recoja respuestas reales.

## Diseño

- **12 alertas** reales del conjunto de test, 2 por tipo de activo: una que las reglas respaldan y otra que solo detecta el modelo.
- **Dos explicaciones por alerta**, sin decir cuál es cuál:
  - *Modelo solo:* la falla, su probabilidad y los 3 sensores con más peso.
  - *Híbrida:* lo anterior más la regla con sus valores reales, la observación del técnico si existe y la acción sugerida.
- **El orden se alterna** entre alertas para que la primera explicación no tenga ventaja. La correspondencia está en `clave.csv`, que **no se muestra a los evaluadores**.
- **Tres afirmaciones** de 1 a 5 por explicación (comprensibilidad, utilidad, confianza) y una preferencia por alerta.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `formulario.md` | Lo que se entrega a cada evaluador (se puede exportar a PDF o copiar a un formulario en línea) |
| `clave.csv` | Qué explicación es la híbrida en cada alerta. Solo para el análisis |
| `respuestas_plantilla.csv` | Formato en que se transcriben las respuestas |
| `respuestas.csv` | Se crea al transcribir las respuestas reales (no existe todavía) |

Se regeneran con `python -m metaltech.xai.evaluacion_humana preparar`.

## Procedimiento

1. **Evaluadores:** al menos 3, idealmente 5 o más. Pueden ser compañeros de otros grupos, el docente o, mejor aún, técnicos de mantenimiento. No deben participar los autores del proyecto.
2. **Consentimiento:** leer el texto de abajo y obtener la aceptación antes de empezar.
3. **Aplicación:** cada evaluador completa el formulario solo, en unos 20 minutos, sin ayuda del equipo.
4. **Transcripción:** copiar `respuestas_plantilla.csv` como `respuestas.csv`. Escribir una fila por evaluador, alerta y explicación (24 por evaluador):
   - `evaluador`: código anónimo (E01, E02…), nunca el nombre;
   - `perfil`: estudiante, docente o técnico;
   - `preferida`: 1, 2 o vacío si le da igual, y solo en la fila de la explicación 1.
5. **Análisis:** `python -m metaltech.xai.evaluacion_humana analizar`. Produce `reports/tables/evaluacion_humana.csv` y `evaluacion_humana_resumen.json` con:
   - media, mediana y porcentaje de acuerdo (4 o 5) por variante;
   - prueba de Wilcoxon pareada entre la explicación híbrida y la del modelo;
   - conteo de preferencias;
   - resultados separados según la alerta tenga o no respaldo de reglas.

## Limitaciones conocidas

- Con 3 a 5 evaluadores la muestra es pequeña: los resultados son exploratorios.
- El orden se alterna por alerta, pero es el mismo para todos los evaluadores.
- Las dos explicaciones no son idénticas en forma: la híbrida da el puntaje fusionado y la otra la probabilidad del modelo, porque son salidas distintas del sistema.
- Si los evaluadores no son técnicos, la utilidad y la confianza reflejan una opinión no experta.

## Consentimiento informado

> Usted está invitado a participar en una evaluación académica del curso Ingeniería del Conocimiento (Universidad de Caldas). Leerá 12 alertas de un sistema de mantenimiento predictivo **ficticio**, con datos **sintéticos**, y calificará qué tan claras y útiles le parecen sus explicaciones. Le tomará unos 20 minutos.
>
> Su participación es voluntaria y puede retirarse en cualquier momento sin dar razones. No se registra su nombre: sus respuestas se identifican con un código (E01, E02…). Solo se registra su perfil (estudiante, docente o técnico). Las respuestas se usarán únicamente en el informe y la presentación del proyecto, en forma agregada, de acuerdo con la Ley 1581 de 2012 de protección de datos personales.
>
> No hay riesgos previstos ni respuestas correctas o incorrectas. Si tiene preguntas, puede dirigirlas al equipo del proyecto.
>
> ☐ He leído la información anterior y acepto participar.
>
> Código asignado: ______  Fecha: ______
