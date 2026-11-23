# Acta ética del proyecto

**Proyecto:** Mantenimiento predictivo explicable en la planta ficticia Metal Tech (Proyecto 3, Ingeniería del Conocimiento 2026-2, Universidad de Caldas).
**Docente:** Ing. Wilson Fernando López Cardona.
**Fecha:** 2026-11-20.

## 1. Declaración de datos

1. Todos los datos de sensores, fallas, técnicos y turnos son **sintéticos**. Se generaron por simulación (`python -m metaltech.data.generator`) y no provienen de ninguna planta real.
2. Los técnicos (T01–T08, I01–I02) y sus observaciones son **ficticios**. El menor acierto nocturno se inyectó a propósito para analizar equidad y no describe a personas reales.
3. No se recogió ningún dato personal. Los únicos datos externos son conjuntos públicos de referencia (AI4I 2020, SKAB y otros), usados solo para contrastar el simulador, según sus licencias.

## 2. Origen del conocimiento

1. La base de conocimiento (reglas, umbrales, FMEA, léxico) proviene de **revisión documental hecha por agentes de IA**, con fuentes citadas en [decisiones.md](../../knowledge/acquisition/decisiones.md). **No hubo entrevistas** ni participación de técnicos.
2. Sin acceso a las normas ISO de pago, sus valores se tomaron de fuentes públicas secundarias. Cada caso está marcado en la decisión correspondiente.
3. Ninguna regla ha sido validada por un técnico de mantenimiento. Esa validación es un requisito antes de cualquier uso real.

## 3. Uso de inteligencia artificial en el trabajo

1. El equipo usó agentes de IA para investigar fuentes, escribir código y documentación, y evaluar explicaciones.
2. La evaluación de explicaciones se hizo con un **panel de agentes** y se rotula como tal, nunca como evaluación humana (D-059).
3. El proceso queda registrado paso a paso en [MEMORIA.md](../agentes/MEMORIA.md), y los errores, también los de los agentes, en [ERRORES.md](../agentes/ERRORES.md).

## 4. Compromisos de diseño

| Compromiso | Decisión |
|---|---|
| El sistema **recomienda**; una persona decide y ejecuta toda intervención o paro | D-069 |
| El sistema no ejecuta funciones de seguridad de las máquinas | D-068 |
| Las observaciones de los técnicos se usan solo para diagnosticar equipos, **nunca para evaluar personas** | D-063 |
| Los técnicos se identifican con seudónimos; no se recogen datos sensibles | D-062, D-064 |
| En una planta real se pediría autorización informada (Ley 1581 de 2012) y se integraría al SG-SST | D-065, D-071 |
| Cada alerta muestra sus variables, reglas y límites; se dice cuándo ninguna regla la respalda | D-070 |
| Los resultados se presentan con sus límites; no se afirma desempeño en una planta real | [sesgos_limitaciones.md](../../reports/sesgos_limitaciones.md) |

## 5. Evaluación con personas

Si se aplica la evaluación de explicaciones con personas, se seguirá el procedimiento y el **consentimiento informado** de [docs/evaluacion_humana/README.md](../evaluacion_humana/README.md): participación voluntaria, códigos anónimos (E01, E02…), uso agregado y referencia a la Ley 1581 de 2012. Los autores del proyecto no participan como evaluadores.

## 6. Firmas del equipo

Los integrantes firman esta acta con su nombre:

| Integrante | Responsabilidad |
|---|---|
| Alejandro Pineda Gomez | Conocimiento y QA |
| Luis David Rodríguez Arias | Datos y modelos |
| Ivan Junior Echeverri Gomez | API y web demostrativa |
| David Ramirez Cruz | Documento APA, póster y landing |
