# Matriz de adquisición del conocimiento – Metal Tech

> Agente Investigador, Fase 1 (2026-10-29). Referencias completas en [decisiones.md](decisiones.md).
> **Declaración:** todo el conocimiento proviene de **revisión documental asistida por agente**: búsqueda web, lectura de fuentes técnicas, normas citadas por fuentes secundarias y datasets públicos. **No se entrevistó a ninguna persona** y no se recogieron datos personales. Las expresiones coloquiales son las del enunciado del curso y no se atribuyen a técnicos reales.

## Técnicas de adquisición

| Código | Técnica | Descripción |
|---|---|---|
| T1 | Revisión documental asistida por agente: normas | Valores normativos obtenidos de fuentes secundarias que citan la norma, porque el texto oficial es de pago |
| T2 | Revisión documental asistida por agente: literatura científica | Artículos y libros de diagnóstico, pronóstico, XAI y sistemas expertos |
| T3 | Revisión documental asistida por agente: guías de fabricantes y técnicas | Blogs técnicos, manuales y hojas de datos (SKF/Acoem, Atlas Copco, Parker, KSB, Martin Engineering, etc.) |
| T4 | Análisis de datasets públicos | Lectura de fichas y artículos de los datasets para extraer rangos y formas de degradación |
| T5 | Razonamiento físico del agente | Deducción a partir de principios (curva de potencia de bombas, fricción, Montsinger) cuando no hay fuente directa; siempre con confianza baja o media |

## Validación aplicada

| Código | Validación |
|---|---|
| V1 | Triangulación: ≥ 2 fuentes concordantes o 1 norma |
| V2 | Resolución de conflictos por el valor más conservador, registrada en la D-NNN |
| V3 | Coherencia cruzada automática entre YAML: IDs de síntomas, modos y activos, NPR = S·O·D, cobertura modo ↔ FMEA ↔ regla y firma ↔ umbrales (`tests/test_conocimiento.py`, desde 2026-11-05) |
| V4 | Revisión cruzada por el agente Revisor (hecha el 2026-11-05; ver [revision.md](revision.md)) |
| V5 | Confirmación con datasets públicos (pendiente, en la Fase 3) |

## Matriz

| # | Fuente | Técnica | Conocimiento obtenido | Tipo | Validación | Decisiones |
|---|---|---|---|---|---|---|
| 1 | ISO 17359:2018 | T1 | Procedimiento del programa de monitoreo de condición: selección de equipos, mediciones, alarmas, diagnóstico | Procedimental | V1 (norma) | D-001, D-002, D-040 |
| 2 | ISO 13374-1 / OSA-CBM (Ran et al., 2019) | T1, T2 | Bloques funcionales: adquisición → manipulación → detección de estado → salud → pronóstico → recomendaciones | Declarativo | V1, V2 (número de bloques) | D-001 |
| 3 | ISO 20816-3 (vía Fabrico, Vibromera, Oxmaint; alcance vía INN) | T1 | Zonas A/B/C/D por grupo y soporte: 1.4/2.8/4.5 mm/s (Grupo 2, rígido). Excluye compresores de tornillo y no lista bombas: ahí es proxy | Declarativo | V1, V2, V4 | D-003 |
| 4 | ISO 20816-1 (vía Fabrico, Vibromera) | T1 | Criterio de cambio del 25 % del límite B/C | Heurístico | V1 (norma, vista por citas), V4 | D-004 |
| 5 | IEC 60034-1, IEC 60085, NEMA MG-1 (vía ALL-TEST Pro, Evans) | T1, T3 | Clases térmicas B/F (130/155 °C), regla de los 10 °C, desbalance de tensión del 1 % y corriente de 6–10×, factor de servicio 1.15 | Declarativo | V1, V2 | D-005, D-006, D-007 |
| 6 | Bonnett y Soukup (1992); IEEE MRWG (1985) | T2 | Mecanismos de falla de estator y rotor; distribución de fallas de motores | Declarativo | V1 | D-002, D-031, D-032 |
| 7 | TECO-Westinghouse; Siemens; KSB GIW | T3 | Alarma y disparo de temperatura de rodamientos (motor 90/95 °C; bomba 82/88 °C) | Declarativo | V1, V2 | D-008, D-009 |
| 8 | Randall y Antoni (2011); Dyer y Stewart (1978); Acoem; UE Systems | T2, T3 | Curtosis ≈ 3 en una señal sana; 4 etapas de falla de rodamiento; temperatura tardía | Declarativo + heurístico | V1, V2 (bandas de la etapa 1) | D-010 |
| 9 | Randall (2011); Piotrowski (2006) | T2 | Firmas 1X de desbalanceo, 2X y axial de desalineación | Heurístico | V1 (por memoria) | D-011 |
| 10 | ANSI/HI 9.6.1-2017 (texto leído en copia pública); A Marine Blog | T1 | Definición de NPSH3 (caída del 3 % de la altura); tablas de margen por aplicación, de 1.05 a 1.5 | Declarativo | V1, V2, V4 | D-012 |
| 11 | Brennen (1994); Inspenet; Al-Hashmi et al. (2017); Ogawa et al. (2022) | T2, T3 | Firma de cavitación: banda ancha de 1–20 kHz, inestabilidad de caudal y presión, caída de altura | Declarativo | V1, V4 | D-013 |
| 12 | Karassik et al. (2008); SKAB | T2, T4, T5 | Obstrucción: caudal y potencia a la baja en bombas radiales | Declarativo | V1 (parcial) | D-014 |
| 13 | CIRCOR (2018); Pumps & Systems (2011); Industrial Monitor Direct; Bloch y Budris (2004) | T2, T3 | Causas del desgaste de sellos; fuga aceptable y fuga mayor en gotas | Heurístico | V1 parcial; alerta con confianza baja | D-015 |
| 14 | Fabrico; Unitec-D; Air Compressor Services; Atlas Copco | T3 | Temperatura de descarga normal (75–100 °C), paro y causas del sobrecalentamiento | Declarativo + procedimental | V1, V2, V4 | D-016 |
| 15 | Anglian Compressors; Fabrico; Compressed Air Challenge (2026); MaintainX; Nuvair | T3 | Causas de la pérdida de presión (válvula de admisión, separador, fugas); prueba de aislamiento; fugas del 20–30 %; diferencial del separador de 8 psi y 1 bar | Procedimental + heurístico | V1, V4 | D-017, D-018, D-019 |
| 16 | Parker Hannifin; Power & Motion; Hydraulics & Pneumatics | T3 | Temperatura máxima del aceite de 60/70 °C; limpieza 18/16/13; daño a sellos > 82 °C | Declarativo | V1, V2 | D-020, D-021 |
| 17 | ISO 4406:2021 | T1 | Códigos de contaminación (cada código ≈ 2× partículas) | Declarativo | V1 (norma) | D-021 |
| 18 | Machinery Lubrication; FridayParts; Fabrico | T3 | Fuga interna: lentitud, deriva, calor; prueba de bypass en fin de carrera | Procedimental | V1 | D-022, D-023 |
| 19 | Martin Engineering; Continental; World Fertilizer; Fabrico | T3 | Causas y síntomas del corrimiento de banda; rodillos trabados | Declarativo + procedimental | V1 | D-024, D-025, D-026 |
| 20 | AI4I 2020 (Matzka, 2020; UCI) | T4 | Vida de herramienta de 200–240 min; fallas definidas por reglas físicas | Declarativo | V1 | D-027, D-036 |
| 21 | Teti et al. (2010); Lai et al. (2025); Industrial Monitor Direct | T2, T3 | Corriente y potencia del husillo frente a desgaste; detección de rotura en 1–3 s; la corriente no capta el astillado | Declarativo + heurístico | V1 | D-027, D-028 |
| 22 | Altintas (2012) | T2 | Chatter regenerativo; lóbulos de estabilidad | Declarativo + procedimental | Sin V1 en umbrales: confianza baja | D-029 |
| 23 | IEEE 519-2014 (vía PowerMonitors); Flexa Systems; Malloy Electric; Fabrico; Precision Electric | T1, T3 | THD ≤ 8 % (≤ 1 kV) y tolerancia de 1.5 veces; disparo de bus DC de unos 820 VDC; causas de disparos | Procedimental + heurístico | V1 (THD), resto baja | D-030 |
| 24 | Shortliffe y Buchanan (1975); Buchanan y Shortliffe (1984) | T2 | Modelo de factores de certeza y combinación MYCIN | Procedimental (inferencia) | V1 | D-034, D-038 |
| 25 | IEC 60812:2018; AIAG-VDA (2019) | T1 | Escalas S/O/D y NPR o prioridad de acción | Procedimental | V1 (por memoria) | D-035 |
| 26 | NASA IMS (Lee et al., 2007; Qiu et al., 2006); CWRU (Smith y Randall, 2015) | T4 | Degradación exponencial tardía; firma de impacto por tamaño de defecto | Declarativo | V1 | D-010, D-036, D-037 |
| 27 | C-MAPSS (Saxena et al., 2008) | T4 | Estructura de vida completa; desgaste inicial variable; RUL | Declarativo | V1 | D-036, D-037 |
| 28 | MIMII (Purohit et al., 2019) | T4 | Firma acústica de fallas en bombas y válvulas, base de los síntomas percibidos | Declarativo | V1 | D-036, D-038 |
| 29 | SKAB (Katser y Kozitsin, 2020) | T4 | Bomba con cavitación, desbalance y cierre de válvula; las mismas variables que el simulador | Declarativo | V1, V5 pendiente | D-013, D-014, D-036 |
| 30 | Lei et al. (2018); Jardine et al. (2006) | T2 | Proceso de pronóstico de extremo a extremo; formas de degradación | Declarativo | V1 | D-001, D-037 |
| 31 | Kusiak (2024); Cummins et al. (2024); Matzka (2020) | T2 | XAI en manufactura; XAI federada; explicaciones vinculadas al dominio | Declarativo | V1 | D-039 |
| 32 | Física de la falla (curva de potencia, fricción, viscosidad, Montsinger) | T5 | Direcciones de cambio cuando no hay fuente numérica | Heurístico | Sin V1: confianza baja | D-007, D-014, D-023, D-025 |
| 33 | Fluke (2025); Acoem (s. f.-b) | T3 | Holgura mecánica: armónicos 2X/3X de la velocidad de giro, impactos, fase inestable, causas y acciones | Declarativo + procedimental | V1 parcial (2 guías de fabricantes de instrumentos, sin norma); la curtosis es supuesto | D-041 |
| 34 | Zhou et al. (2023); Filippenko et al. (2002); Vibromera (2025) | T2, T3 | Umbral de curtosis de 4; alarmas de 2× y 4× la línea base | Heurístico | V1, V4 | D-010 |
| 35 | Helwig et al. (2015a, 2015b) | T4 | Banco hidráulico: enfriador, válvula, fuga de bomba y acumulador | Declarativo | V1 parcial, V5 pendiente | D-036, D-048 |

## Distribución por tipo de conocimiento

| Tipo | Dónde queda representado | Ejemplos |
|---|---|---|
| Declarativo | `assets.yaml` (umbrales), `failure_modes.yaml` (firmas), FMEA, ontología (Fase 2) | "Zona C empieza en 2.8 mm/s"; "la clase F son 155 °C" |
| Procedimental | Campo `accion` de `rules.yaml`, acciones de la FMEA | "Prueba de bypass en fin de carrera"; "prueba de aislamiento del compresor" |
| Heurístico | `rules.yaml` (FC), `expresiones.yaml` (fc_max), criterios de tendencia | "Una curtosis ≥ 4 indica impactos"; "'cantando' es un rodamiento o el variador" |
