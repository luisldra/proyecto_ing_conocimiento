# Normas consultadas por fuentes públicas externas

> **Fecha de consulta:** 2026-11-08 · **Agente:** Investigador · **Relacionado:** D-003, D-004, D-012, D-030, H-01, H-02, ERR-001, ERR-015.
> **Estado:** propuesta. No se modificó ningún umbral, decisión ni YAML.

## Tipos de fuente

| Tipo | Significado |
|---|---|
| **Vista previa oficial** | Muestra de la norma publicada por un catálogo (iTeh). Texto literal, solo de las primeras páginas: prólogo, alcance y parte de la cláusula 3. Ninguna de las muestras leídas llega a los anexos con las zonas. |
| **Catálogo** | Ficha de un organismo o distribuidor: título, fecha y estado. |
| **Secundaria sectorial** | Asociación o fabricante que reproduce valores de la norma. |
| **Secundaria** | Blog, artículo técnico o ponencia. |

Una fuente cuenta aquí solo si se abrió y dice lo indicado. Lo visto únicamente en el extracto del buscador se marca como **no abierta** y no sustenta ningún cambio.

## Resumen de cambios recomendados

| D-NNN | Activo y variable | Antes (alerta / crítico) | Después (alerta / crítico) | Condición |
|---|---|---|---|---|
| D-003 | `bomba_centrifuga`, `vib_rms_mm_s` | 2.8 / 4.5 mm/s | **5.1 / 8.5 mm/s** | Categoría II, ≤ 200 kW (la bomba es de 22 kW). Requiere recalibrar las firmas de la bomba en `failure_modes.yaml` |
| D-004 | `vibracion_creciente` en la bomba | 0.7 mm/s | 1.275 mm/s (0.25 × 5.1), cálculo propio | Solo si se adopta el cambio anterior. El 25 % no se leyó en la parte 7 |
| D-003 | Texto del conflicto 3 | "20816-3 excluye máquinas herramienta" | Las máquinas herramienta **no aparecen** ni entre las cubiertas ni entre las excluidas | Sin cambio numérico |

Los demás valores quedan sin cambio.

## 1. ISO 20816-3:2026 frente a la edición 2022

| Aspecto | Valor actual en el proyecto | Qué dice la fuente | Tipo de fuente | URL | Referencia APA 7 | Cambio recomendado |
|---|---|---|---|---|---|---|
| Vigencia | ISO 20816-3:2026 publicada el 2026-10-28, según SFS (D-003) | ISO 20816-3:2026-10, marcada como nueva, reemplaza a ISO 20816-3:2022-10; 24 páginas. No da el día ni describe los cambios | Catálogo | https://www.dinmedia.de/en/standard/iso-20816-3/407861129 | DIN Media. (2026). *ISO 20816-3:2026-10*. https://www.dinmedia.de/en/standard/iso-20816-3/407861129 | Sin cambio. Citar la edición 2026 como vigente y declarar que no se leyó |
| Alcance, 2022 | Motores, compresores rotativos y transportadores incluidos; tornillo excluido (vía INN) | Más de 15 kW y 120–30 000 r/min. Cubre *rotary compressors*, motores eléctricos con acople flexible, *rolls and mills*, *conveyors*, ventiladores. No cubre *rotordynamic pumps* (remite a ISO 10816-7) ni *rotary positive displacement compressors (e. g. screw compressors)* | Vista previa oficial | https://cdn.standards.iteh.ai/samples/78311/30f79c7c3eca41c1ad7b4321a447bd39/ISO-20816-3-2022.pdf | International Organization for Standardization. (2022). *Mechanical vibration — Measurement and evaluation of machine vibration — Part 3* (ISO 20816-3:2022) [Vista previa]. iTeh Standards. | Sin cambio numérico. Citar esta vista previa además de INN. La redacción de D-003 sobre bombas debe ser más fuerte: quedan fuera todas las rotodinámicas, no solo las de impulsor en el eje |
| Cambios de la edición 2026 | No revisados (H-02) | **No abierta.** Extractos de iTeh en el buscador indican: segunda edición; alcance ampliado a Grupo 3 con potencia ≤ 15 kW; zonas del Grupo 3 en nueva Tabla A.3; resumen de zonas en Tabla A.4; retiro de las recomendaciones de TRIP de 6.5.3. La página de iTeh se abrió pero no devolvió contenido | Extracto del buscador | https://standards.iteh.ai/catalog/standards/iso/028d0601-c70d-4257-ac31-eb5fdc7b60ee/iso-20816-3-2026 | No citar hasta leerla | Sin cambio. Pista útil: si se confirma el Grupo 3, podría cubrir la CNC de 15 kW; hay que leer la Tabla A.3 |
| Zonas de los Grupos 1 y 2 en 2026 | Grupo 2 rígido: 1.4 / 2.8 / 4.5 mm/s | No se encontró ninguna fuente, ni abierta ni en extractos, que dé los valores de 2026 o afirme que cambiaron. Las muestras no llegan al Anexo A | No disponible | — | — | Sin cambio. Sigue abierto |
| Página oficial de ISO | — | iso.org respondió HTTP 403 a todas las solicitudes (fichas 89922 y 78311). Los extractos aún muestran FDIS, en conflicto con DIN Media, que ya lista la publicada | No abierta | https://www.iso.org/standard/89922.html | — | — |

## 2. ISO 10816-7 (bombas rotodinámicas)

Límites superiores de zona, valores eficaces de velocidad (mm/s) en partes no rotativas, según Europump (2013):

| Zona | Cat. I, ≤ 200 kW | Cat. I, > 200 kW | Cat. II, ≤ 200 kW | Cat. II, > 200 kW |
|---|---|---|---|---|
| A (límite A/B) | 2.5 | 3.5 | 3.2 | 4.2 |
| B (límite B/C) | 4.0 | 5.0 | **5.1** | 6.1 |
| C (límite C/D) | 6.6 | 7.6 | **8.5** | 9.5 |
| D | > 6.6 | > 7.6 | > 8.5 | > 9.5 |
| ALARM máxima (1.25 × límite de zona B) | 5.0 | 6.3 | 6.4 | 7.6 |
| TRIP máximo (1.25 × límite de zona C) | 8.3 | 9.5 | 10.6 | 11.9 |

| Aspecto | Valor actual en el proyecto | Qué dice la fuente | Tipo de fuente | URL | Referencia APA 7 | Cambio recomendado |
|---|---|---|---|---|---|---|
| Valores de zona | Proxy de 20816-3: alerta 2.8, crítico 4.5 (`bomba_centrifuga`, 22 kW) | Tabla anterior. Cat. II es para servicio general o menos crítico, como líquidos no peligrosos. El proyecto define alerta como entrada a zona C y crítico como entrada a zona D | Secundaria sectorial (asociación europea de fabricantes) | https://www.europump.net/files/Publications/Guides/Guidelines%200n%20Pump%20Vibration%20First%20edition%20Final%20July%202013.pdf | Europump. (2013). *Pump vibration standards guidelines* (1.ª ed.). https://www.europump.net/files/Publications/Guides/Guidelines%200n%20Pump%20Vibration%20First%20edition%20Final%20July%202013.pdf | **Alerta 2.8 → 5.1; crítico 4.5 → 8.5** en D-003. Confianza media: norma vista por una fuente sectorial, no por su Anexo A. Alternativa conservadora: Cat. I (4.0 / 6.6) |
| Segunda fuente | — | Misma tabla, declarada como resumen de Europump: **no es independiente**. Advierte que no sustituye a la norma | Secundaria (fabricante) | https://www.fbbombas.com.br/en/resources/articles/centrifugal-pump-vibration-iso-10816 | FB Bombas Engineering Team. (2026, 6 de noviembre). *Vibration in centrifugal pumps: ISO 10816-7 limits, causes and measurement points*. https://www.fbbombas.com.br/en/resources/articles/centrifugal-pump-vibration-iso-10816 | Citar solo como confirmación de transcripción |
| Alcance | "Límites por categoría, no verificado" (D-003) | Rotodinámicas industriales de más de 1 kW, horizontales y verticales, sin importar la flexibilidad del soporte. Distingue hasta y sobre 200 kW. Dos criterios: magnitud y cambio de magnitud. **Excluye** desplazamiento positivo, accionadas por motor alternativo, centrales hidráulicas > 1 MW, sólidos, lodos y sumergibles. El motor con acople flexible se evalúa aparte, con ISO 10816-3. Anexo A normativo, Tablas A.1 y A.2 no incluidas en la muestra | Vista previa oficial | https://cdn.standards.iteh.ai/samples/41726/6d70c56d3bcc4cc9b4b0e07895816fff/ISO-10816-7-2009.pdf | International Organization for Standardization. (2009). *Mechanical vibration — Evaluation of machine vibration by measurements on non-rotating parts — Part 7* (ISO 10816-7:2009) [Vista previa]. iTeh Standards. | Cerrar el conflicto 2 de D-003. **La unidad hidráulica de la prensa no puede usar estos valores**, si su bomba es de desplazamiento positivo: sigue como proxy |
| Sustitución | "Posiblemente sustituida" | FB Bombas: la norma sigue publicada y ISO registró el proyecto ISO 20816-7. La ficha oficial dio HTTP 403; extractos del buscador (no abierta) la muestran como ISO/AWI, en etapa inicial | Secundaria (fabricante) | https://www.iso.org/standard/92744.html (no abierta) | FB Bombas Engineering Team (2026), ya citada | Citar ISO 10816-7:2009 como vigente. Sin cambio |
| Tendencia (D-004) | 0.7 mm/s para todos los activos | La parte 7 tiene criterio de cambio de magnitud, pero el porcentaje no está en la muestra. Si se conserva la definición de D-004, en la bomba da 0.25 × 5.1 = 1.275 mm/s (cálculo propio) | Vista previa oficial | Igual que el alcance | International Organization for Standardization (2009) | **0.7 → 1.275 mm/s** solo si se adopta el cambio de zonas; confianza baja |

**Efecto en otros archivos (no modificados):**

- `configs/assets.yaml`: umbrales de `bomba_centrifuga`. Conviene revisar las descripciones de `vibracion_alerta` y `vibracion_critica`, que citan solo ISO 20816-3.
- `failure_modes.yaml`: las firmas de la bomba calibradas para cruzar 2.8/4.5 podrían dejar de disparar con 5.1/8.5.
- Regenerar la ontología si cambia un YAML.
- El rango nominal [0.5, 1.4] puede quedar igual, porque está dentro de la zona A.

## 3. Compresores de tornillo, prensas y CNC

| Máquina | Valor actual en el proyecto | Qué dice la fuente | Tipo de fuente | URL | Referencia APA 7 | Cambio recomendado |
|---|---|---|---|---|---|---|
| Compresor de tornillo | Proxy 2.8 / 4.5 (55 kW) | Excluido de ISO 10816-3:2009, igual que en la edición 2022 (punto 1) | Vista previa oficial | https://cdn.standards.iteh.ai/samples/50528/6b05d5f9b499455e883a91bacff92991/ISO-10816-3-2009.pdf | International Organization for Standardization. (2009). *Mechanical vibration — Evaluation of machine vibration by measurements on non-rotating parts — Part 3* (ISO 10816-3:2009) [Vista previa]. iTeh Standards. | Exclusión confirmada (ERR-015). Sin cambio numérico |
| Compresor de tornillo | — | Existe una guía específica: VDI 3836, complemento de DIN ISO 10816-3 (agosto de 2006; la bibliografía cita la edición 2012-02). Dos bandas de frecuencia (A: 10–1 000 Hz; B: 10 Hz a 2.2 veces la frecuencia de giro) y zonas I, II, III. También menciona EN ISO 10440-1/API 619, con límites distintos. La Tabla 1 de valores es una imagen y **no se pudo leer** | Secundaria (ponencia de ingenieros de BASF y Kötter) | https://ft.mb.tu-dortmund.de/storages/ft-mb/r/Publikationen/ICSM/2014/R._Schuhmann__R._Missal_et_al._2014_-_Large_industrial_screw_compressors.pdf | Schuhmann, R., Missal, R., Ochs, H., y Schmitt, T. (2014). *Large industrial screw compressors for refrigeration units: Experiences out of operation and maintenance*. TU Dortmund. | Registrar VDI 3836 como la guía aplicable en D-003. Sin cambio numérico hasta leer su tabla |
| Compresor de tornillo | — | Vibración normalmente admisible alta, "~ 8mm/sec"; valor general, sin atribuir a una tabla. Confirma la exclusión de ISO 10816-3 | Secundaria (artículo en LinkedIn) | https://www.linkedin.com/pulse/evaluation-vibrations-screw-compressors-mahyar-asadi-tabrizi | Asadi, M. (2020, 21 de febrero). *Evaluation of vibrations of screw compressors*. LinkedIn. https://www.linkedin.com/pulse/evaluation-vibrations-screw-compressors-mahyar-asadi-tabrizi | Sin cambio. Declarar en *Limitaciones* que 2.8/4.5 es probablemente conservador para un tornillo y puede aumentar las falsas alarmas |
| Prensa (unidad hidráulica) | Proxy 2.8 / 4.5 | No se halló norma pública con límites de vibración para prensas. Tampoco aparecen en la lista de cubiertas o excluidas de ISO 20816-3:2022. ISO 10816-7 excluye las bombas de desplazamiento positivo | Vista previa oficial (ausencia en el texto) | Las de ISO 20816-3:2022 e ISO 10816-7 | Ya citadas | Sin cambio; confianza baja |
| CNC (cabezal, 15 kW) | Proxy 2.8 / 4.5; D-003 dice que la norma "excluye máquinas herramienta" | ISO 20816-3:2022 no lista máquinas herramienta ni como cubiertas ni como excluidas. Su alcance es *above 15 kW*, así que 15 kW queda justo fuera. No se halló límite público de ISO para husillos; una tesis de DiVA con ese tema solo se vio en extracto (no abierta, conexión rechazada) | Vista previa oficial (ausencia en el texto) | Igual que ISO 20816-3:2022 | Ya citada | Sin cambio numérico. **Corregir el texto del conflicto 3 de D-003** |

## 4. IEEE 519 (THD de tensión)

| Aspecto | Valor actual en el proyecto | Qué dice la fuente | Tipo de fuente | URL | Referencia APA 7 | Cambio recomendado |
|---|---|---|---|---|---|---|
| Límite ≤ 1 kV | `thd_tension_pct` alerta 8 % (D-030, IEEE 519-2014) | IEEE 519-2022, Tabla 1 (p. 17): V ≤ 1.0 kV, individual 5.0 %, THD 8.0 %, en el PCC | Secundaria (blog técnico de Comsys AB) | https://powerquality.blog/2023/06/01/power-quality-ieee-519-2022/ | PQBlog. (2023, 1 de junio). *Power quality – IEEE 519-2022*. https://powerquality.blog/2023/06/01/power-quality-ieee-519-2022/ | Sin cambio. Citar la edición 2022 además de la 2014 |
| Cambio 2014 → 2022 | No registrado | Los límites de tensión de la Tabla 1 son "exactly identical" en ambas ediciones | Secundaria (empresa de variadores) | https://mb-drive-services.com/what-has-changed-in-ieee-519-between-2014-and-2022-editions/ | MB Drive Services. (2026, 7 de enero). *What has changed in IEEE 519 between 2014 and 2022 editions?* https://mb-drive-services.com/what-has-changed-in-ieee-519-between-2014-and-2022-editions/ | Sin cambio |
| Crítico 12 % | 1.5 × 8 %, "periodos cortos" | Valores de percentil 99 diario de 3 s, menores que 1.5 veces la tabla; percentil 95 semanal de 10 min, menores que la tabla. Límites aplicables en el PCC. Fuente sobre la edición 2014 | Secundaria (blog técnico de Elspec) | https://powerquality.blog/2023/05/25/understanding-the-ieee-519-2014-standard-for-harmonics/ | PQBlog. (2023, 25 de mayo). *Understanding the IEEE 519–2014 standard for harmonics*. https://powerquality.blog/2023/05/25/understanding-the-ieee-519-2014-standard-for-harmonics/ | Sin cambio numérico. Precisar en D-030 que el 12 % corresponde a valores de 3 s; con muestreo de 10 min la referencia directa es el 8 % |

## Lo que no se pudo consultar

- **Texto oficial:** zonas de ISO 20816-3:2026 y 2022, Tablas A.1 y A.2 de ISO 10816-7, Tabla 1 de VDI 3836 e IEEE 519.
- **Sin acceso:** iso.org (HTTP 403); los catálogos SIST y VDI, ResearchGate, Academia.edu y varias páginas técnicas no resolvieron o rechazaron la conexión. Un resumen de VDI 3836 con valores (bandas A y B, 10/15 y 3/7 mm/s) quedó solo en extracto y **no se usa**.
- **Omitidas a propósito:** copias completas de normas de pago alojadas por terceros (aparecieron en los resultados de búsqueda). No se abrieron por ser de procedencia dudosa y no estar entre las fuentes pedidas; conseguir los textos por la biblioteca sigue siendo la vía correcta.
