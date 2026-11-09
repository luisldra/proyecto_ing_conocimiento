# Avances del proyecto: Fases 3 y 4

**Proyecto:** Mantenimiento predictivo explicable en la planta Metal Tech (Ingeniería del Conocimiento 2026-2)
**Estado a la fecha (2026-11-08):** Fases 0 a 4 terminadas. La Fase 5 (fusión de modelo y reglas) aún no se abre.
**Versión descrita:** commit `b820e2a`

Este documento explica qué se construyó en las dos últimas fases, por qué se tomó cada decisión, qué resultados hay y para qué sirve cada archivo del repositorio. Sirve para que cualquier integrante entienda el avance sin leer el código.

---

## 1. Resumen

| Fase | Qué produjo | Estado |
|---|---|---|
| 0. Preparación | Repositorio, entorno, manual de agentes | Hecha |
| 1. Adquisición del conocimiento | 55 decisiones justificadas, FMEA, léxico de técnicos | Hecha y revisada |
| 2. Ontología y reglas | Ontología OWL y motor de 55 reglas con factores de certeza | Hecha |
| **3. Datos sintéticos** | Simulador de 32 máquinas durante 36 meses, calibrado con datos públicos | **Hecha** |
| **4. Deep Learning** | 18 modelos entrenados (MLP, CNN1D, LSTM para 6 tipos de activo) | **Hecha y corregida** |
| 5 en adelante | Fusión, explicabilidad, API, web, documento APA | Pendiente |

**Resultado principal.** Con los modelos elegidos, el F1 macro promedio es **0.919** en el conjunto de test y **0.930** en máquinas que el modelo nunca vio. Las reglas solas detectan el 67.5 % de las fallas predecibles y el 55.5 % de las de detección.

**Advertencia.** Estas cifras son optimistas: el modelo se entrena y se evalúa con datos del mismo simulador (ver la [sección 6](#6-qué-tan-confiables-son-los-resultados)). No deben presentarse como desempeño en una planta real.

---

## 2. Contexto: lo que ya existía

El enunciado pide predecir fallas con Deep Learning, integrar el conocimiento experto y comparar **modelo solo contra modelo más conocimiento**. Antes de estas fases ya estaban:

- **La base de conocimiento** (`knowledge/` y `configs/`): por cada activo, sus variables con umbrales, sus modos de falla, causas y acciones. Salió de revisión documental, sin entrevistas.
- **El motor de reglas** (`src/metaltech/kb/`): dado un conjunto de lecturas, concluye qué falla hay y con qué certeza. A este sistema experto se le llama **M0**.

Los 4 sistemas que el proyecto va a comparar:

| Sistema | Descripción | Estado |
|---|---|---|
| M0 | Solo reglas | Listo y medido |
| M1 | Solo Deep Learning | **Listo (Fase 4)** |
| M2 | Conocimiento como entradas adicionales del modelo | Fase 5 |
| M3 | Fusión de la probabilidad del modelo y la certeza de las reglas | Fase 5 |

---

## 3. Fase 3: el simulador

### 3.1 Por qué existe
No hay datos reales de Metal Tech, y el enunciado admite datos sintéticos. El simulador fabrica las lecturas de los sensores a partir de la base de conocimiento.

### 3.2 Qué genera
Con `python -m metaltech.data.generator` (cerca de 1 minuto):

- 36 meses de lecturas cada 10 minutos para **32 unidades**: 8 motores, 6 bombas, 4 compresores, 4 prensas, 6 bandas y 4 centros CNC.
- **5 049 216 filas**, con 2.4 % de filas etiquetadas como falla.
- **1075 episodios de falla** de 31 modos distintos, con al menos 13 por combinación de activo y modo.
- **2220 observaciones de técnicos**, escritas con las expresiones del enunciado ("la bomba está golpeando").

Con la misma semilla el resultado es idéntico. La ficha de datos completa está en [data/README.md](../data/README.md).

### 3.3 Cómo se simula cada componente

| Componente | Cómo funciona |
|---|---|
| Señal sana | Ciclo de carga por turno y domingos, ruido, estacionalidad en temperaturas y deriva de sensores que se reinicia cada 180 días |
| Fallas | Cada modo modifica sus variables con una curva propia: lineal, exponencial, sigmoide, escalón o intermitente |
| Variabilidad | Severidad distinta en cada episodio; algunas variables de la firma no se manifiestan (40 %) |
| Eventos que imitan fallas | Picos espurios, sensores sin dato y 11 condiciones de operación normal que mueven varias variables, como carga alta sostenida o ambiente caluroso |
| Observaciones de técnicos | El acierto depende de cada técnico y baja de noche. Los grupos rotan de turno cada semana |

### 3.4 Decisiones importantes

| Decisión | Motivo | Registro |
|---|---|---|
| Separar fallas en **predicción** (23 modos) y **detección** (8 modos) | Algunas no se pueden anticipar 24 h: una colisión no da aviso y el desgaste de herramienta dura unas 4 h | D-049 |
| Partición temporal con purga | Evita que datos futuros se filtren al entrenamiento | D-050 |
| Vibración de bombas en 5.1/8.5 mm/s | ISO 20816-3 excluye las bombas; se adoptó ISO 10816-7 por la guía de Europump | D-051 |
| Hacer el simulador más exigente | Al principio las reglas acertaban el 100 % porque las firmas se construyeron para activarlas | D-052 |
| Duplicar a 32 unidades y reservar una de cada tipo | Más fallas en test y una prueba real de máquina no vista | D-055 |

**Regla contra el sesgo:** los parámetros del simulador se ajustan con física y datos públicos, nunca mirando el resultado del sistema híbrido. Si no, la comparación final estaría amañada a favor de lo que se quiere demostrar.

### 3.5 Contraste con datos públicos
Con `python scripts/contrastar_datasets.py` se compara el simulador con AI4I 2020 y SKAB:

| Medida | Dato público | Simulador | Lectura |
|---|---|---|---|
| Desgaste de herramienta al fallar, mediana | 214.5 min | 212.1 min | Coincide |
| Variación en sano, vibración | 2.03 % | 9.67 % | Aceptada: SKAB es un banco de laboratorio estable |
| Variación en sano, corriente | 1.11 % | 2.89 % | Aceptada por la misma razón |
| Variación en sano, caudal | 1.20 % | 0.99 % | Similar |
| Canales que cambian durante una anomalía | 33.3 % | 60 % (por diseño) | Las firmas siguen siendo más completas que las reales |

No se contrastó con NASA IMS ni con el dataset hidráulico de UCI.

### 3.6 Resultado de las reglas solas (M0)

| Medida | Valor |
|---|---|
| Fallas de predicción detectadas | 67.5 % |
| Fallas de detección detectadas | 55.5 % |
| Anticipación mediana en predicción | 60.5 h |
| Episodios con confusión hacia otra falla | 11.3 % |
| Alarmas en operación sana sin eventos | 0 % |
| Alarmas durante eventos que imitan fallas | 16.72 % en promedio |

Los casos más difíciles para las reglas son la válvula de admisión del compresor (13.3 %), la holgura mecánica del motor (22.7 %) y la desalineación de bomba (23.8 %). En eventos confusores, el compresor llega a 56.53 % de alarmas.

---

## 4. Fase 4: los modelos de Deep Learning

### 4.1 De lecturas a ventanas
El modelo no ve una lectura aislada, sino una **ventana de 6 horas** (36 lecturas), cada hora.

- **Solo entran sensores.** Columnas como `estado` o `horas_a_falla` dicen la respuesta, y usarlas sería hacer trampa.
- Las ventanas no cruzan particiones ni reparaciones.
- La normalización se calcula solo con datos de entrenamiento.
- Se agrega una ventana en el instante de cada falla, para no perder eventos de 10 minutos.

### 4.2 Las tres arquitecturas

| Modelo | Qué recibe | Idea |
|---|---|---|
| MLP | 7 estadísticas por variable | Línea base simple |
| CNN1D | La ventana completa | Detecta patrones locales y eventos cortos |
| LSTM | La ventana completa | Sigue la evolución en el tiempo |

Se entrena **un modelo por tipo de activo**, porque cada uno tiene sensores y fallas distintos. Eso da 3 arquitecturas por 6 activos: 18 entrenamientos, con la semilla 42. La arquitectura se elige con **validación**; el conjunto de test no decide nada.

### 4.3 La corrección más importante
En el primer entrenamiento el F1 fue 0.60 y la tasa de falsa alarma, 5.74 %. Al revisar esas alarmas:

- El **99.1 %** ocurría con una degradación real en curso.
- En el **98.8 %** de ellas el modelo había identificado la falla correcta.
- Con el equipo realmente sano, la tasa era de solo **0.11 %**.

El modelo avisaba bien, pero antes de las 24 h, y esas ventanas estaban marcadas "normal": los aciertos se contaban como errores. El equipo decidió (D-054) tratar esas **ventanas grises** así:

- No se entrenan ni cuentan en F1 ni en falsa alarma.
- Se miden aparte como **aviso temprano**.

### 4.4 Resultados finales de M1

| Activo | Modelo | F1 test | F1 máquina no vista |
|---|---|---|---|
| Motor eléctrico | MLP | 0.966 | 0.949 |
| Bomba centrífuga | CNN1D | 0.854 | 0.967 |
| Compresor de tornillo | MLP | 0.882 | 0.929 |
| Prensa hidráulica | CNN1D | 0.985 | 0.973 |
| Banda transportadora | CNN1D | 0.964 | 0.969 |
| Centro CNC | LSTM | 0.863 | 0.791 |
| **Promedio** | | **0.919** | **0.930** |

| Medida (promedio por activo) | Test | Máquina no vista |
|---|---|---|
| Precisión macro | 0.912 | 0.921 |
| Recall macro | 0.935 | 0.952 |
| Episodios con aviso temprano correcto | 83.1 % | 84.2 % |
| Anticipación mediana | 159.9 h | 178.2 h |

| Falsa alarma (ventanas agregadas) | Test | Máquina no vista |
|---|---|---|
| Equipo sano, sin eventos confusores | 0.08 % | 0.27 % |
| Durante eventos confusores | 2.12 % | 2.28 % |

**Las tres arquitecturas rinden parecido.** En promedio, entre 0.900 y 0.914 de F1 en test.

**Casos débiles en test:**

| Clase | F1 | Comentario |
|---|---|---|
| Cavitación en bomba | 0.22 | Solo 3 ventanas de 2 episodios; no es concluyente |
| Válvula de admisión del compresor | 0.48 | |
| Desgaste de herramienta CNC | 0.50 | |
| Desalineación de bomba | 0.71 | Se confunde con desbalanceo, físicamente parecido |

Además, el centro CNC avisa de forma temprana en solo 47–62 % de los episodios.

---

## 5. Decisiones y errores registrados

Las decisiones completas están en [decisiones.md](../knowledge/acquisition/decisiones.md), y los errores en [ERRORES.md](agentes/ERRORES.md).

| Decisión | Tema |
|---|---|
| D-049 | Predicción o detección por modo de falla |
| D-050 | Supuestos y límites del simulador |
| D-051 | Umbrales de vibración para bombas |
| D-052 | Dificultad del simulador calibrada con datos públicos |
| D-053 | Ventanas y entrenamiento |
| D-054 | Ventanas grises y aviso temprano |
| D-055 | Confusores multivariable, 32 unidades y ajustes con datos públicos |

| Error | Qué pasó | Estado |
|---|---|---|
| ERR-019 | Pruebas de trayectoria mal planteadas | Resuelto |
| ERR-020 | Simulador demasiado fácil para las reglas | Resuelto |
| ERR-021 | Cifra de anticipación calculada con un método incorrecto | Resuelto |
| ERR-022 | Script de cambios aplicado a medias | Resuelto |
| ERR-023 | La métrica de falsa alarma contaba avisos correctos | Resuelto |

---

## 6. Qué tan confiables son los resultados

1. **Mismo generador.** El modelo aprende y se evalúa con datos del mismo simulador, incluida la "máquina no vista". También aprendió los eventos confusores, así que su baja falsa alarma es optimista.
2. **Una sola semilla.** Faltan los intervalos de confianza con 5 semillas (Fase 7).
3. **Pocos casos en algunas clases.** La cavitación tiene 2 episodios en test.
4. **Parámetros supuestos.** Duraciones, magnitudes y frecuencias de confusores salen de literatura y razonamiento físico, no de mediciones de una planta.
5. **Normas sin texto oficial.** No hay acceso institucional. Salvo ANSI/HI 9.6.1, los valores provienen de fuentes secundarias públicas (ver [normas_fuentes_externas.md](../knowledge/acquisition/normas_fuentes_externas.md)).
6. **Poco margen para el híbrido.** M1 ya tiene pocas falsas alarmas. La reducción con M3 frente a M1 puede resultar pequeña y debe reportarse tal como salga.
7. **Un dato no regenerable por comando.** La falsa alarma separada por eventos confusores (sección 4.4) y el desglose de la sección 4.3 se calcularon con scripts temporales que no están en el repositorio. Conviene incorporarlos en la Fase 7.

---

## 7. Guía de archivos del repositorio

Lo que **no** se versiona (se regenera por comando): `data/synthetic/`, `data/external/`, `checkpoints/`, `.venv/` y `.tools/`.

### Raíz

| Archivo | Para qué sirve |
|---|---|
| `AGENTS.md` | Manual de trabajo: protocolo, roles, convenciones y comandos |
| `CLAUDE.md` | Hace que Claude Code cargue `AGENTS.md` |
| `README.md` | Instalación y ejecución |
| `requirements.txt` | Dependencias de Python |
| `pyproject.toml` | Configuración del paquete, `pytest` y `ruff` |
| `.gitignore` | Lo que Git no debe guardar |
| `PROYECTOS FINALES INGENIERIA DEL CONOCIMIENTO.pdf` | Enunciado |

### `configs/`: parámetros

| Archivo | Para qué sirve |
|---|---|
| `assets.yaml` | Activos, unidades, variables, umbrales y catálogo de 68 síntomas |
| `failure_modes.yaml` | 31 modos de falla con su firma, duración y tarea, y los eventos confusores |
| `train.yaml` | Parámetros del simulador, ventanas, modelos y entrenamiento |

### `knowledge/`: base de conocimiento

| Archivo | Para qué sirve |
|---|---|
| `acquisition/decisiones.md` | Las 55 decisiones, con alternativas, fuentes APA y confianza |
| `acquisition/fmea.yaml` y `fmea.md` | Análisis de modos de falla: 41 filas |
| `acquisition/matriz_adquisicion.md` | Fuentes consultadas y qué conocimiento aportó cada una |
| `acquisition/datasets_referencia.md` | Los 7 datasets públicos de referencia |
| `acquisition/revision.md` | Revisión cruzada: 38 hallazgos |
| `acquisition/normas_fuentes_externas.md` | Consulta de normas por fuentes públicas |
| `rules/rules.yaml` | Las 55 reglas |
| `lexicon/expresiones.yaml` | 10 expresiones de técnicos traducidas a síntomas |
| `ontology/metaltech.owl` | Ontología generada desde los YAML; se abre con Protégé |
| `ontology/README.md` | Clases, propiedades y consultas de la ontología |

### `src/metaltech/`: código

| Archivo | Para qué sirve | Fase |
|---|---|---|
| `proceso.py` | Verifica que los errores citados en MEMORIA existan en ERRORES | 0 |
| `kb/base.py` | Carga los YAML en un solo objeto; calcula valores nominales y finales | 2 |
| `kb/lexicon.py` | Reconoce las expresiones de los técnicos en un texto | 2 |
| `kb/rules_engine.py` | Motor de reglas (M0): síntomas, factores de certeza y traza | 2 |
| `kb/ontology.py` | Genera y consulta la ontología | 2 |
| **`data/generator.py`** | **Simulador: señales, fallas, confusores, observaciones y partición** | 3 |
| **`data/calibracion.py`** | **Mide a M0 sobre los datos generados** | 3 |
| **`data/features.py`** | **Construye y normaliza las ventanas; marca las grises** | 4 |
| **`models/mlp.py`, `cnn1d.py`, `lstm.py`** | **Las tres arquitecturas** | 4 |
| **`models/train.py`** | **Entrena, elige arquitectura y guarda resultados** | 4 |
| **`models/evaluate.py`** | **F1, precisión, recall, falsa alarma y aviso temprano** | 4 |

Las carpetas `hybrid/`, `xai/`, `metrics/`, `api/` y `dashboard/` están vacías: corresponden a fases futuras.

### `scripts/`

| Archivo | Para qué sirve |
|---|---|
| `instalar_jdk.py` | Instala un JDK portable para el razonador HermiT |
| `contrastar_datasets.py` | Descarga AI4I y SKAB y compara con el simulador |

### `tests/`: 542 pruebas

| Archivo | Pruebas | Qué verifica |
|---|---|---|
| `test_conocimiento.py` | 13 | Coherencia entre YAML y trazabilidad a decisiones |
| `test_entorno.py` | 24 | Dependencias y configuración |
| `test_proceso.py` | 2 | Verificador de MEMORIA y ERRORES |
| `test_lexicon.py` | 50 | Reconocimiento de expresiones |
| `test_rules_engine.py` | 351 | Cada regla, los factores de certeza y las trayectorias |
| `test_ontology.py` | 24 | Ontología y razonador HermiT |
| **`test_generator.py`** | **55** | **Formas de falla, reproducibilidad, etiquetas, confusores y partición** |
| **`test_modelos.py`** | **23** | **Ausencia de fuga de información, ventanas grises y modelos** |
| `conftest.py` | – | Configuración compartida de las pruebas |

### `reports/tables/`: resultados

| Archivo | Contenido |
|---|---|
| `calibracion_resumen.json` | Resumen de la calibración |
| `calibracion_m0_por_modo.csv` | Desempeño de las reglas por activo y falla |
| `calibracion_falsas_alarmas.csv` | Alarmas de las reglas con y sin confusores |
| `calibracion_observaciones.csv` | Acierto por turno y técnico |
| `contraste_datasets.csv` | Comparación con datos públicos |
| `modelos_resultados.csv` | Métricas de los 18 modelos por partición |
| `modelos_por_clase.csv` | Métricas por falla |
| `modelos_seleccion.json` | Arquitectura elegida por activo |
| `modelos_confusion_{activo}.csv` | Matrices de confusión |

### `data/` y `docs/`

| Archivo | Para qué sirve |
|---|---|
| `data/README.md` | Ficha de datos: columnas, supuestos y limitaciones |
| `docs/PLAN.md` | Plan maestro por fases |
| `docs/agentes/MEMORIA.md` | Bitácora de tareas |
| `docs/agentes/ERRORES.md` | Base de conocimiento de errores |
| `docs/AVANCES_FASES_3_Y_4.md` | Este documento |

---

## 8. Cómo reproducir todo

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e . --no-deps
python scripts/instalar_jdk.py              # solo para las pruebas con HermiT

python -m metaltech.kb.ontology             # regenera la ontología
python -m metaltech.data.generator          # genera los datos
python -m metaltech.data.calibracion        # mide las reglas
python scripts/contrastar_datasets.py       # compara con datos públicos
python -m metaltech.models.train            # entrena los 18 modelos (cerca de 25 min en CPU)

pytest
ruff check .
python -m metaltech.proceso
```

---

## 9. Pendientes

| Tema | Responsable sugerido |
|---|---|
| Consultar al docente qué significa RA/R1–R6 y la fecha de entrega | Equipo |
| Fase 5: fusión M0–M3 y comparación modelo contra modelo + conocimiento | Luis David |
| Fase 6: explicabilidad (SHAP, gradientes integrados) | Luis David |
| Fase 7: 5 semillas, intervalos de confianza, equidad, latencia e incorporar al repositorio las medidas de la sección 6 | Luis David y Alejandro |
| Contraste con NASA IMS y UCI hidráulico | Alejandro |
| API y web demostrativa | Junio |
| Documento APA, póster y landing | David |

**Responsables del equipo:** Alejandro (conocimiento y QA), Luis David (datos y modelos), Junio (API y web demostrativa), David (documento APA, póster y landing).
