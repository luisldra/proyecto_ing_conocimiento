# Formulario de evaluación de explicaciones

Para cada alerta lea las dos explicaciones y califique cada afirmación de 1 a 5
(1 = totalmente en desacuerdo, 5 = totalmente de acuerdo). Después indique cuál prefiere.
Las dos explicaciones corresponden a la misma alerta; no hay respuestas correctas.

Afirmaciones:
- **Comprensibilidad:** Entiendo por qué el sistema emitió esta alerta.
- **Utilidad:** La explicación me ayuda a decidir qué hacer con el equipo.
- **Confianza:** Confiaría en esta alerta para programar una intervención.

## Alerta A01 – banda transportadora

Unidad banda_transportadora_01, 2026-06-12 03:50:00.

**Explicación 1.** Alerta de deslizamiento (patinaje) banda-tambor (puntaje 89%). El modelo se apoyó sobre todo en deslizamiento_pct (71%), velocidad_banda_pct (17%), temp_rodamiento_c (5%). La respalda la regla R32: deslizamiento_pct = 5.88 (>= 2). Un técnico reportó: "hay cascabeleo en la línea". Acción sugerida: Verificar tensión de la banda (contrapeso/tensor), recubrimiento del tambor motriz y presencia de material o agua entre banda y tambor.

**Explicación 2.** Alerta de deslizamiento (patinaje) banda-tambor (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron deslizamiento_pct (71%), velocidad_banda_pct (17%), temp_rodamiento_c (5%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A02 – banda transportadora

Unidad banda_transportadora_01, 2026-11-17 17:40:00.

**Explicación 1.** Alerta de rotura de banda o de empalme (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron velocidad_banda_pct (61%), vib_curtosis (21%), corriente_pct (8%).

**Explicación 2.** Alerta de rotura de banda o de empalme (puntaje 70%). El modelo se apoyó sobre todo en velocidad_banda_pct (61%), vib_curtosis (21%), corriente_pct (8%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: paro_y_bloqueo

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A03 – bomba centrifuga

Unidad bomba_centrifuga_01, 2026-06-10 20:50:00.

**Explicación 1.** Alerta de holgura mecánica (anclajes flojos, base degradada, ajuste de rodamiento o acople suelto) (puntaje 92%). El modelo se apoyó sobre todo en vib_curtosis (52%), vib_2x_1x_ratio (22%), vib_rms_mm_s (13%). La respalda la regla R47: vib_rms_mm_s = 6.65 (>= 5.1); vib_curtosis = 4.86 (>= 4); vib_2x_1x_ratio = 0.75 (>= 0.5). Acción sugerida: Revisar anclaje de la bancada, grout y soportes de tubería; verificar ajuste del rodamiento y del acople antes de intervenir el impulsor.

**Explicación 2.** Alerta de holgura mecánica (anclajes flojos, base degradada, ajuste de rodamiento o acople suelto) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron vib_curtosis (52%), vib_2x_1x_ratio (22%), vib_rms_mm_s (13%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A04 – bomba centrifuga

Unidad bomba_centrifuga_01, 2026-11-30 00:50:00.

**Explicación 1.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron vib_hf_rel (44%), vib_curtosis (32%), temp_rodamiento_c (10%).

**Explicación 2.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (puntaje 80%). El modelo se apoyó sobre todo en vib_hf_rel (44%), vib_curtosis (32%), temp_rodamiento_c (10%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: analisis_envolvente

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A05 – centro cnc

Unidad centro_cnc_01, 2026-08-25 13:50:00.

**Explicación 1.** Alerta de vibración regenerativa (chatter) (puntaje 88%). El modelo se apoyó sobre todo en carga_husillo_cv_pct (80%), vib_rms_mm_s (8%), vib_hf_rel (5%). La respalda la regla R39: carga_husillo_cv_pct = 16.76 (>= 10); vib_hf_rel = 3.04 (>= 2). Acción sugerida: Ajustar velocidad de husillo hacia un lóbulo estable, reducir la profundidad de corte o el voladizo de la herramienta.

**Explicación 2.** Alerta de vibración regenerativa (chatter) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron carga_husillo_cv_pct (80%), vib_rms_mm_s (8%), vib_hf_rel (5%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A06 – centro cnc

Unidad centro_cnc_01, 2026-07-24 17:50:00.

**Explicación 1.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron vib_hf_rel (76%), vib_rms_mm_s (12%), desgaste_herramienta_min (7%).

**Explicación 2.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (puntaje 60%). El modelo se apoyó sobre todo en vib_hf_rel (76%), vib_rms_mm_s (12%), desgaste_herramienta_min (7%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: analisis_envolvente

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A07 – compresor tornillo

Unidad compresor_tornillo_01, 2026-07-04 05:50:00.

**Explicación 1.** Alerta de saturación/obstrucción del elemento separador de aceite (puntaje 96%). El modelo se apoyó sobre todo en dp_separador_bar (73%), presion_descarga_pct (8%), temp_descarga_c (5%). La respalda la regla R21: dp_separador_bar = 1.11 (>= 0.55); presion_descarga_pct = 90.33 (<= 93). Acción sugerida: Reemplazar el elemento separador de aceite según el diferencial del fabricante; revisar el arrastre de aceite.

**Explicación 2.** Alerta de saturación/obstrucción del elemento separador de aceite (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron dp_separador_bar (73%), presion_descarga_pct (8%), temp_descarga_c (5%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A08 – compresor tornillo

Unidad compresor_tornillo_02, 2026-11-19 14:50:00.

**Explicación 1.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (probabilidad del modelo 99%). Los sensores con más peso en la predicción fueron vib_hf_rel (62%), corriente_pct (14%), vib_rms_mm_s (5%).

**Explicación 2.** Alerta de desgaste/defecto localizado de rodamiento (pista o elemento rodante) (puntaje 79%). El modelo se apoyó sobre todo en vib_hf_rel (62%), corriente_pct (14%), vib_rms_mm_s (5%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: analisis_envolvente

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A09 – motor electrico

Unidad motor_electrico_01, 2026-08-17 08:50:00.

**Explicación 1.** Alerta de degradación térmica del aislamiento del devanado (puntaje 87%). El modelo se apoyó sobre todo en temp_devanado_c (47%), desbalance_corriente_pct (18%), corriente_pct (15%). La respalda la regla R07: temp_devanado_c = 130.05 (>= 130); desbalance_corriente_pct = 7.06 (>= 5). Acción sugerida: Medir resistencia de aislamiento (megóhmetro) e índice de polarización; revisar la tensión de alimentación por fase.

**Explicación 2.** Alerta de degradación térmica del aislamiento del devanado (probabilidad del modelo 99%). Los sensores con más peso en la predicción fueron temp_devanado_c (47%), desbalance_corriente_pct (18%), corriente_pct (15%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A10 – motor electrico

Unidad motor_electrico_01, 2026-06-10 17:50:00.

**Explicación 1.** Alerta de desalineación de ejes/acople (probabilidad del modelo 98%). Los sensores con más peso en la predicción fueron vib_rms_mm_s (44%), vib_axial_radial_ratio (42%), vib_2x_1x_ratio (3%).

**Explicación 2.** Alerta de desalineación de ejes/acople (puntaje 69%). El modelo se apoyó sobre todo en vib_rms_mm_s (44%), vib_axial_radial_ratio (42%), vib_2x_1x_ratio (3%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: alineacion_laser

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A11 – prensa hidraulica

Unidad prensa_hidraulica_01, 2026-07-19 19:50:00.

**Explicación 1.** Alerta de válvula direccional/proporcional pegada o lenta ("prensa dura") (puntaje 93%). El modelo se apoyó sobre todo en presion_sistema_pct (44%), tiempo_ciclo_pct (22%), iso4406_14um_codigo (13%). La respalda la regla R28: iso4406_14um_codigo = 14.00 (>= 14); tiempo_ciclo_pct = 113.59 (>= 110); presion_sistema_pct = 114.88 (>= 110). Acción sugerida: Revisar la respuesta de la válvula proporcional/direccional (corriente de bobina vs. posición); limpiar o reemplazar la válvula y filtrar el aceite.

**Explicación 2.** Alerta de válvula direccional/proporcional pegada o lenta ("prensa dura") (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron presion_sistema_pct (44%), tiempo_ciclo_pct (22%), iso4406_14um_codigo (13%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A12 – prensa hidraulica

Unidad prensa_hidraulica_01, 2026-09-21 02:50:00.

**Explicación 1.** Alerta de fuga hidráulica externa (manguera, racor, sello de vástago) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron nivel_tanque_pct (52%), presion_sistema_pct (16%), corriente_pct (9%).

**Explicación 2.** Alerta de fuga hidráulica externa (manguera, racor, sello de vástago) (puntaje 80%). El modelo se apoyó sobre todo en nivel_tanque_pct (52%), presion_sistema_pct (16%), corriente_pct (9%). Ninguna regla la respalda todavía: es una alerta solo del modelo. Acción sugerida: bloqueo_y_aislamiento_de_energia

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A13 – motor electrico

Unidad motor_electrico_01, 2026-09-22 10:50:00.

**Explicación 1.** Alerta de lubricación deficiente de rodamientos (falta, exceso o grasa degradada) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron temp_rodamiento_c (64%), vib_1x_frac (5%), thd_tension_pct (5%).

**Explicación 2.** Alerta de lubricación deficiente de rodamientos (falta, exceso o grasa degradada) (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron temp_rodamiento_c (64%), vib_1x_frac (5%), thd_tension_pct (5%). Esta alerta fue generada automáticamente por el sistema de monitoreo de condición de la planta a partir del análisis de las señales registradas durante la ventana de observación más reciente.

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---

## Alerta A14 – compresor tornillo

Unidad compresor_tornillo_01, 2026-12-25 22:50:00.

**Explicación 1.** Alerta de desalineación de ejes/acople (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron vib_rms_mm_s (42%), vib_axial_radial_ratio (29%), vib_2x_1x_ratio (17%). Esta alerta fue generada automáticamente por el sistema de monitoreo de condición de la planta a partir del análisis de las señales registradas durante la ventana de observación más reciente.

**Explicación 2.** Alerta de desalineación de ejes/acople (probabilidad del modelo 100%). Los sensores con más peso en la predicción fueron vib_rms_mm_s (42%), vib_axial_radial_ratio (29%), vib_2x_1x_ratio (17%).

| | Comprensibilidad | Utilidad | Confianza |
|---|---|---|---|
| Explicación 1 | | | |
| Explicación 2 | | | |

Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual

---
