# Entrega – Proyecto 3: Mantenimiento predictivo explicable (Metal Tech)

**Curso:** Ingeniería del Conocimiento 2026-2 · Facultad de Inteligencia Artificial e Ingenierías · Universidad de Caldas
**Docente:** Ing. Wilson Fernando López Cardona
**Equipo:** Alejandro Pineda Gomez · Luis David Rodríguez Arias · Ivan Junior Echeverri Gomez · David Ramirez Cruz
**Fecha de entrega:** 30 de noviembre de 2026

> Todos los datos del proyecto son **sintéticos**. El sistema es un prototipo académico: recomienda, y una persona decide.

## Contenido de esta carpeta

| Archivo | Qué es |
|---|---|
| [01_Documento_APA.pdf](01_Documento_APA.pdf) | Documento final en APA 7 con las 15 secciones del enunciado y los anexos A–H |
| [01_Documento_APA.docx](01_Documento_APA.docx) | El mismo documento en Word |
| [02_Poster_A1.pdf](02_Poster_A1.pdf) | Póster A1 vertical |
| [03_Guion_presentacion.pdf](03_Guion_presentacion.pdf) | Guion de la presentación: 7 intervenciones, máximo 2 por integrante, 14 minutos más preguntas |
| [04_Informe_sesgos_y_limitaciones.pdf](04_Informe_sesgos_y_limitaciones.pdf) | Informe de sesgos, riesgos RA/R1–R6, limitaciones y marco legal |
| [05_Acta_etica.pdf](05_Acta_etica.pdf) | Acta ética firmada por el equipo |
| [06_Puesta_en_marcha.pdf](06_Puesta_en_marcha.pdf) | Cómo instalar y ejecutar el prototipo |
| [07_Manual_usuario_web.pdf](07_Manual_usuario_web.pdf) | Manual de la web demostrativa, página por página |
| [08_Manual_API.pdf](08_Manual_API.pdf) | Manual de la API con ejemplos |

## Enlaces

| Recurso | Enlace |
|---|---|
| Landing de presentación (esquema de la exposición) | https://luisldra.github.io/proyecto_ing_conocimiento/ |
| Repositorio GitHub (código, datos reproducibles, README) | https://github.com/luisldra/proyecto_ing_conocimiento |
| Manuales completos, con diagramas de flujo | https://github.com/luisldra/proyecto_ing_conocimiento/tree/main/docs/manuales |

## Lista de verificación contra el enunciado

### Entregables técnicos

| Pide el enunciado | Dónde está |
|---|---|
| Documento PDF | `01_Documento_APA.pdf` |
| Repositorio GitHub con README | Enlace al repositorio; README en la raíz |
| Prototipo funcional | API FastAPI y web Streamlit de 8 páginas en el repositorio; se ejecutan con `06_Puesta_en_marcha.pdf` |
| Demo de 10–15 minutos | `03_Guion_presentacion.pdf` (14 minutos) |
| Póster | `02_Poster_A1.pdf` |

### Resultado esperado del Proyecto 3

| Pide el enunciado | Dónde está |
|---|---|
| Modelo de red neuronal o Deep Learning entrenado con datos sintéticos | MLP, CNN1D y LSTM por tipo de activo (documento, sección Desarrollo del artefacto) |
| Base de conocimiento de fallas y reglas de diagnóstico | 31 modos de falla, 55 reglas con factores de certeza y ontología OWL (documento, Anexos B y C) |
| API o tablero de prototipo | API y web demostrativa (`07_Manual_usuario_web.pdf`, `08_Manual_API.pdf`) |
| Métricas de predicción y explicabilidad | F1, precisión, recall, latencia, fidelidad, concordancia, estabilidad (documento, Resultados) |
| Informe de sesgos y limitaciones | `04_Informe_sesgos_y_limitaciones.pdf` |
| Comparación modelo solo vs. modelo + conocimiento experto | M0 · M1 · M2 · M3 con 5 semillas (documento, Tablas 5 y 6) |
| Métricas: F1, precisión, recall, latencia, explicabilidad, reducción de falsas alarmas, equidad e impacto | Documento, Resultados (Tablas 5 a 11) |
| Cobertura: Deep Learning, industria, ética y marco legal | Documento, Marco teórico y Discusión; informe de sesgos, sección 9 |

### Estructura del documento (15 puntos)

| # | Sección | En el documento |
|---|---|---|
| 1 | Portada institucional | Página 1 |
| 2 | Resumen y palabras clave | Página 2 |
| 3 | Introducción | Sección Introducción |
| 4 | Planteamiento del problema | Contexto, pregunta orientadora y delimitación |
| 5 | Justificación | Sección Justificación |
| 6 | Objetivos (2 generales y 3 específicos) | Sección Objetivos |
| 7 | Marco teórico | IA, representación del conocimiento, ontologías, sistemas expertos, inferencia, ML/DL, XAI, ética |
| 8 | Metodología | ABP/ABPr, CommonKADS, CRISP-DM, adquisición del conocimiento, diseño y validación |
| 9 | Desarrollo del artefacto | Arquitectura, base de conocimiento, ontología, reglas, modelos y prototipo |
| 10 | Resultados | Pruebas, métricas, validación, equidad y análisis de errores |
| 11 | Discusión | Respuesta a la pregunta, riesgos RA/R1–R6, ética, sesgos y limitaciones |
| 12 | Conclusiones y recomendaciones | Sección final |
| 13 | Referencias APA 7 | 43 referencias, orden alfabético y sangría francesa |
| 14 | Anexos | A matriz de adquisición · B reglas · C ontología · D código · E consentimiento · F datos sintéticos · G acta ética |
| 15 | Presentación | Anexo H y `03_Guion_presentacion.pdf` (esquema: la landing) |

## Cómo se regenera esta carpeta

Los archivos de esta carpeta son copias generadas y no se editan aquí. Se edita la fuente y se ejecuta:

```bash
python scripts/generar_documento.py --pdf    # documento APA
python scripts/generar_poster.py             # póster
python scripts/preparar_entrega.py           # copia y convierte todo a entrega/
```
