# Datasets públicos de referencia para calibrar el simulador

> Agente Investigador, Fase 1 (2026-10-29). Decisión asociada: **D-036** (y D-037 para formas de degradación). Referencias completas en [decisiones.md](decisiones.md).
> **Uso previsto:** estos datasets **no** se usan para entrenar el modelo de Metal Tech, que trabaja con datos sintéticos. Sirven para dar **forma temporal, rangos y relaciones entre variables** realistas a las firmas de `configs/failure_modes.yaml`, y como posible validación externa en trabajo futuro.

## Resumen

| Dataset | Tipo | Activo análogo en Metal Tech | Modos de falla que calibra | Licencia / acceso |
|---|---|---|---|---|
| AI4I 2020 (UCI) | Sintético tabular, 10 000 filas | Centro CNC (y lógica de fallas por umbral) | `desgaste_herramienta`, `sobrecarga_mecanica`, fallas por potencia | CC BY 4.0, UCI id 601 |
| CWRU Bearing | Vibración real de banco de ensayo, 12/48 kHz | Rodamientos de motor y bomba | `desgaste_rodamiento` (firma de impacto) | Libre, Case Western Reserve University |
| NASA IMS Bearings | Vibración de vida completa (run-to-failure) | Rodamientos (todos los activos) | `desgaste_rodamiento` (forma de degradación) | Libre, NASA Prognostics Data Repository |
| NASA C-MAPSS | Simulación de turbofán, vida completa | Estructura de vida completa / RUL | Degradación genérica, RUL | Libre, NASA |
| MIMII | Audio de máquinas, 16 kHz, 8 canales | Bomba, válvulas, ventiladores, rieles | Síntomas percibidos (sonido) | CC BY 4.0, Zenodo 3384388 |
| SKAB | Series multivariadas de una bomba de circulación | Bomba centrífuga | `cavitacion`, `desbalanceo_rotor`, `obstruccion_bomba` | Libre, GitHub waico/SKAB |
| UCI Condition Monitoring of Hydraulic Systems | Multisensor de banco hidráulico real, ciclos de 60 s | Prensa hidráulica | `sobrecalentamiento_aceite_hidraulico`, `valvula_hidraulica_pegada`; parcial para `fuga_interna_cilindro` | CC BY 4.0, UCI id 447 |

---

## 1. AI4I 2020 Predictive Maintenance Dataset (UCI)
- **Origen:** Matzka (2020); UCI Machine Learning Repository (2020). Es sintético, pensado para replicar una máquina de fresado real.
- **Variables (14 columnas):**
  - UDI y Product ID;
  - tipo de producto: L, M o H, en proporción 50/30/20 %;
  - temperatura del aire [K];
  - temperatura del proceso [K];
  - velocidad de rotación [rpm];
  - par [Nm];
  - desgaste de herramienta [min];
  - etiqueta *Machine failure* y 5 etiquetas de modo de falla: TWF, HDF, PWF, OSF y RNF.
- **Fallas y reglas de generación** (según la ficha de UCI):
  - **TWF (desgaste de herramienta):** la herramienta se reemplaza o falla en un instante aleatorio entre **200 y 240 min**. Se observan 120 casos. El desgaste aumenta en 5, 3 o 2 min por ciclo según el producto (H, M o L).
  - **HDF (disipación de calor):** falla si la diferencia entre la temperatura de proceso y la del aire es **< 8.6 K** y la velocidad es **< 1380 rpm**. 115 casos.
  - **PWF (potencia):** falla si par × velocidad angular queda **< 3500 W** o **> 9000 W**. 95 casos.
  - **OSF (sobreesfuerzo):** falla si desgaste × par supera **11 000 / 12 000 / 13 000 min·Nm** para L, M y H. 98 casos.
  - **RNF (aleatoria):** 0.1 % de probabilidad.
- **Rangos típicos:**
  - temperatura del aire alrededor de 300 K;
  - temperatura del proceso unos 10 K por encima;
  - velocidad del orden de 1 200–2 900 rpm, derivada de una potencia de ~2 860 W con ruido;
  - par de ~40 Nm ± 10.
  - El dataset tiene un desbalance fuerte: ~3.4 % de fallas.
- **Cómo nos sirve:**
  1. Fija la vida de la herramienta CNC en 200–240 min (D-027).
  2. Es un ejemplo citable de **fallas definidas por reglas físicas**, lo que hace posible la comparación M0 (solo reglas) frente a M1 (solo DL).
  3. Da una referencia de desbalance de clases para la Fase 4.
- **Limitación:** no tiene series temporales ni vibración, y la falla se etiqueta sin horizonte de anticipación.

## 2. CWRU Bearing Data Center
- **Origen:** Case Western Reserve University (s. f.); estudio de referencia de Smith y Randall (2015).
- **Variables:** aceleración en el extremo de accionamiento (DE), en el lado opuesto (FE) y en la base, muestreada a 12 kHz o 48 kHz. También registra la velocidad del motor y la carga.
- **Banco:** motor de 2 hp con rodamiento SKF 6205-2RS en el lado de accionamiento. Carga de 0–3 hp y velocidad de ~1797 a 1730 rpm.
- **Fallas:** defectos sembrados por electroerosión de **0.007, 0.014 y 0.021 in** (además de 0.028 en algunos casos), en pista interna, pista externa y bola.
- **Frecuencias de defecto del 6205**, cálculo del agente con multiplicadores de una fuente secundaria: BPFO ≈ 3.585 × fr y BPFI ≈ 5.415 × fr. A 1797 rpm (fr ≈ 29.95 Hz) dan BPFO ≈ 107 Hz y BPFI ≈ 162 Hz.
- **Cómo nos sirve:** muestra que los defectos localizados elevan la **curtosis** y la energía de alta frecuencia antes que la RMS global. Eso respalda los síntomas `vibracion_impulsiva` y `vibracion_hf_alta` y su orden de aparición en el simulador (D-010).
- **Limitación:** los defectos son artificiales (sin evolución en el tiempo) y Smith y Randall (2015) señalan que algunos registros son ambiguos. No da la forma de la degradación.

## 3. NASA IMS Bearings (Universidad de Cincinnati)
- **Origen:** Lee et al. (2007); Qiu et al. (2006).
- **Banco:** 4 rodamientos Rexnord ZA-2115 de doble hilera en un eje a **2000 rpm**, con carga radial de **6000 lb**. Lubricación forzada.
- **Variables:** aceleración, con registros de 1 s (20 480 puntos a 20 kHz) tomados cada 10 min.
- **Fallas (3 ensayos de vida completa):**
  - ensayo 1: pista interna (rodamiento 3) y elemento rodante (rodamiento 4);
  - ensayos 2 y 3: pista externa (rodamientos 1 y 3).
- **Forma de la degradación:** largo periodo estable y crecimiento **exponencial** al final. En el ensayo 2 (unos 7 días), la degradación visible ocupa aproximadamente el último 20–30 % de la vida. Es una estimación del agente a partir de la literatura y debe verificarse con los datos.
- **Cómo nos sirve:**
  - Su muestreo de 10 min coincide con el del simulador.
  - Justifica la forma `exponencial` con aparición tardía de RMS y temperatura (`retardo_frac` de 0.5–0.7) en `desgaste_rodamiento` (D-037).
- **Limitación:** las condiciones son constantes y no hay variables de proceso (temperatura, corriente).

## 4. NASA C-MAPSS (Turbofan Engine Degradation Simulation)
- **Origen:** Saxena et al. (2008).
- **Variables:** 26 columnas: id del motor, ciclo, 3 ajustes operativos y 21 sensores (temperaturas, presiones, velocidades, flujos).
- **Subconjuntos:** FD001–FD004. FD001 tiene 100 motores de entrenamiento y 100 de prueba, con 1 modo de falla y 1 condición de operación.
- **Fallas:** degradación de HPC y del ventilador. Cada motor empieza con un desgaste inicial distinto y desconocido, y los datos incluyen ruido. En el entrenamiento la serie llega hasta la falla; en la prueba se trunca y se acompaña de la RUL real.
- **Cómo nos sirve:**
  1. Es el patrón para la **estructura de etiquetas**: horizonte H y RUL opcional.
  2. Muestra cómo modelar la **variabilidad entre unidades** (desgaste inicial distinto).
  3. Su partición por unidad sirve de modelo para evitar fugas de información (Fase 3).
- **Limitación:** es otro dominio (aeronáutico) y es simulado, así que sus rangos no se trasladan.

## 5. MIMII (Malfunctioning Industrial Machine Investigation and Inspection)
- **Origen:** Purohit et al. (2019), Hitachi; DCASE 2019.
- **Variables:** audio de 16 bits a **16 kHz**, grabado con una matriz de 8 micrófonos en segmentos de 10 s, con ruido de fábrica añadido a varios niveles de SNR.
- **Máquinas:** válvulas, **bombas**, ventiladores y rieles deslizantes, con 7 modelos de cada una.
- **Fallas simuladas:** contaminación, fuga, desbalance rotatorio y daño de riel, más correa floja y falta de grasa en los rieles.
- **Cómo nos sirve:**
  - Da evidencia de que las fallas tienen una **firma acústica** detectable. Eso justifica modelar las expresiones de los técnicos ("golpeando", "cascabeleando", "cantando") como síntomas percibidos con cierta probabilidad de acierto (D-038).
  - Se podría extender a un modelo de audio, pero eso queda fuera del alcance.
- **Limitación:** no tiene etiquetas de severidad ni series de proceso.

## 6. SKAB (Skoltech Anomaly Benchmark)
- **Origen:** Katser y Kozitsin (2020).
- **Banco:** circuito de agua con **bomba** y motor eléctrico, con su sistema de control.
- **Variables (8):**
  - Accelerometer1RMS y Accelerometer2RMS (vibración, en g);
  - Current (corriente del motor, A);
  - Voltage (V);
  - Pressure (presión del circuito a la salida de la bomba, bar);
  - Temperature (cuerpo del motor, °C);
  - Thermocouple (fluido, °C);
  - RateRMS (caudal, L/min).
- **Fallas inducidas:** cierre parcial de válvulas, desbalance del eje de acople, reducción de potencia del motor, **cavitación** y perturbaciones de caudal.
- **Tamaño:** unos 34–35 archivos CSV en la v0.9. Cada archivo empieza con un tramo normal, y entre el 25 % y el 35 % de cada uno es anómalo. Las cifras totales difieren según la fuente.
- **Cómo nos sirve:**
  - Es el dataset **más parecido** a nuestra bomba: incluye las mismas magnitudes (vibración, corriente, presión, temperatura y caudal) y sus fallas corresponden a `cavitacion`, `desbalanceo_rotor` y `obstruccion_bomba` (cierre de válvula).
  - Se recomienda usarlo para calibrar la **forma sigmoide** de la cavitación y para comprobar que el cierre de válvula reduce el caudal y la corriente (D-013, D-014).
  - Es candidato a **validación externa** de la regla de cavitación (R13–R14).
- **Limitación:** es un banco pequeño de laboratorio, con episodios cortos (minutos), y no tiene NPSH medido.

---

## 7. Condition Monitoring of Hydraulic Systems (UCI)
- **Origen:** Helwig et al. (2015a, 2015b). Evaluado por el agente Revisor el 2026-11-05 (D-048). Se leyó la ficha de UCI; del artículo solo se confirmaron los metadatos.
- **Banco:** circuito hidráulico de trabajo más un circuito secundario de enfriamiento y filtrado. Repite ciclos de carga constantes de 60 s mientras se varía la condición de cuatro componentes.
- **Variables (2205 ciclos):**
  - presión PS1–PS6 (bar, 100 Hz);
  - potencia del motor EPS1 (W, 100 Hz);
  - caudal FS1–FS2 (l/min, 10 Hz);
  - temperatura TS1–TS4 (°C, 1 Hz);
  - vibración VS1 (mm/s, 1 Hz);
  - eficiencia y potencia de enfriamiento CE y CP, y factor de eficiencia SE (1 Hz).
- **Etiquetas por ciclo:**
  - enfriador: 3 %, 20 % o 100 %;
  - válvula: 100 %, 90 %, 80 % o 73 % (retardo de conmutación creciente);
  - fuga interna de la bomba: ninguna, débil o severa;
  - acumulador: 130, 115, 100 o 90 bar;
  - indicador de estabilidad del ciclo.
- **Cómo nos sirve:**
  - Es el único dataset abierto hallado con variables de nuestra prensa: presión, temperatura, potencia (proxy de corriente) y vibración en mm/s.
  - Puede calibrar la **relación entre variables** y la forma temporal de `sobrecalentamiento_aceite_hidraulico` y `valvula_hidraulica_pegada`.
  - Es candidato a **validación externa** de las reglas de la prensa en trabajo futuro.
- **Limitaciones:**
  - Es un banco de pruebas, no una prensa, y sus ciclos son de carga constante.
  - La fuga es de la bomba, no del cilindro, así que `fuga_interna_cilindro` solo se calibra en parte.
  - No cubre `fuga_hidraulica_externa` ni `contaminacion_aceite_hidraulico`: no hay nivel de tanque ni conteo de partículas.
  - Sus condiciones son niveles discretos, no trayectorias de degradación hasta la falla.
  - No aporta umbrales de alarma: sirve para forma y rango (D-048).

---

## Correspondencia con variables del simulador

| Variable Metal Tech | AI4I | CWRU | IMS | C-MAPSS | MIMII | SKAB | UCI hidráulico |
|---|---|---|---|---|---|---|---|
| `vib_rms_mm_s`, `vib_hf_rel`, `vib_curtosis` | – | ✔ | ✔ | – | (audio) | ✔ (RMS en g) | ✔ (solo mm/s, 1 Hz) |
| `temp_*` | ✔ (aire/proceso) | – | – | ✔ | – | ✔ | ✔ |
| `corriente_pct` | (par×vel.) | – | – | – | – | ✔ | (potencia del motor) |
| `presion_*`, `caudal_*` | – | – | – | ✔ (presiones) | – | ✔ | ✔ |
| `desgaste_herramienta_min` | ✔ | – | – | – | – | – | – |
| Síntomas percibidos | – | – | – | – | ✔ | – | – |

## Huecos
- Ningún dataset público abierto encontrado cubre **compresores de tornillo** ni **bandas transportadoras** con las variables del enunciado. Sus firmas se basan solo en literatura técnica (D-016 a D-026) y tienen confianza menor.
- La prensa queda cubierta solo en parte por el dataset UCI de sistemas hidráulicos (sección 7, D-048).
