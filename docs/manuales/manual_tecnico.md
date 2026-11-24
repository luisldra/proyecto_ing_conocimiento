# Manual técnico

Cómo está construido el sistema y cómo extenderlo: agregar una regla, un síntoma, un modo de falla, una expresión de técnico o un activo, y qué regenerar después. Antes de cambiar algo, lea el protocolo de [AGENTS.md](../../AGENTS.md) y busque en [ERRORES.md](../agentes/ERRORES.md) si el problema ya ocurrió.

## 1. Principios del diseño

- **Fuente única de verdad:** el conocimiento vive en los YAML de `configs/` y `knowledge/`. La ontología OWL **se genera** desde ellos y nunca se edita a mano.
- **Trazabilidad:** toda regla, umbral y firma cita decisiones (`D-NNN`) de [decisiones.md](../../knowledge/acquisition/decisiones.md); cada alerta lleva sus reglas y variables.
- **Reproducibilidad:** semillas fijas en `configs/train.yaml`; cada resultado se regenera con un comando.
- **Nada escrito a mano en los entregables:** la landing, el documento y el póster leen sus cifras de `reports/tables/`.
- **Las pruebas protegen la coherencia:** `tests/test_conocimiento.py` falla si una regla, firma, síntoma o fila de la FMEA queda inconsistente.

## 2. Arquitectura de `src/metaltech/`

| Módulo | Archivo | Responsabilidad |
|---|---|---|
| **kb** | `base.py` | Carga y une los YAML en `BaseConocimiento` (`cargar_base()`): activos, síntomas, modos, reglas, léxico y FMEA |
| | `lexicon.py` | Traduce el texto del técnico a síntomas percibidos (expresiones y variantes) |
| | `rules_engine.py` | Fusificación de variables a síntomas, encadenamiento hacia adelante, FC de MYCIN y traza |
| | `ontology.py` | Genera `metaltech.owl` con owlready2, la valida (HermiT opcional) y responde consultas (`Ontologia.cargar()`, ficha de modo, grafo) |
| **data** | `generator.py` | Simulador: señal por turno, degradaciones, confusores, deriva, faltantes, observaciones de técnicos y partición |
| | `calibracion.py` | Mide la dificultad del simulador (M0 por modo, falsas alarmas, acierto de técnicos) |
| | `features.py` | Ventanas de 6 h, normalización, estadísticas para el MLP, ventanas grises y submuestreo de normales |
| **models** | `mlp.py`, `cnn1d.py`, `lstm.py` | Las tres arquitecturas |
| | `con_conocimiento.py` | Rama que recibe certezas y síntomas (M2) |
| | `train.py` | Entrenamiento con pérdida focal, parada temprana, calibración por temperatura y elección por F1 de validación |
| | `evaluate.py` | Métricas: F1, precisión, recall, falsas alarmas y aviso temprano |
| **hybrid** | `conocimiento.py` | Ejecuta el motor de reglas sobre cada ventana (con línea base y observaciones) |
| | `fusion.py` | Fusión M3, veto, diagnóstico híbrido y texto de la explicación |
| | `comparar.py` | Compara M0–M3 y elige α y veto en validación |
| **xai** | `explain.py` | Gradientes integrados (Captum) y métricas de fidelidad, concordancia y estabilidad |
| | `evaluacion_humana.py` | Formulario y análisis de la evaluación de explicaciones |
| **metrics** | `intervalos.py`, `equidad.py`, `impacto.py`, `latencia.py` | Evaluación final (Fase 7) |
| **api** | `main.py`, `servicio.py`, `esquemas.py` | FastAPI; `servicio.py` concentra la lógica que comparten la API y la web |
| **dashboard** | `app.py`, `inicio.py`, `pages/`, `comun.py`, `cliente.py` | Web Streamlit; `cliente.py` usa la API HTTP o, si no responde, la API dentro del proceso |
| | `proceso.py` | Verifica los enlaces entre MEMORIA y ERRORES |

Los [diagramas de flujo](diagramas_flujo.md) muestran cómo se conectan.

## 3. Formatos de los YAML

### Variable de un activo (`configs/assets.yaml` → `activos.<activo>.variables`)

```yaml
vib_rms_mm_s:
  unidad: mm/s RMS
  direccion: alta          # alta: la falla la sube; baja: la falla la baja
  nominal: [0.5, 1.4]      # rango sano
  alerta: 2.8
  critico: 4.5
  fuentes: [D-003]
```

### Síntoma (`configs/assets.yaml` → `sintomas`)

```yaml
vibracion_alerta:
  tipo: medido             # medido (sobre una variable) o percibido (lo reporta un técnico)
  variable: vib_rms_mm_s
  nivel: alerta            # alerta, critico o en_rango
  descripcion: Velocidad RMS en zona C (ISO 20816-3)
```

### Modo de falla (`configs/failure_modes.yaml` → `modos_falla`)

```yaml
sobrecalentamiento_ventilacion:
  nombre: Sobrecalentamiento por ventilación obstruida
  activos: [motor_electrico]
  componente: ventilacion
  firma:                                   # cómo cambia cada variable al degradarse
    - {variable: temp_devanado_c, direccion: "+", cambio: {tipo: delta, valor: 60}, forma: lineal, retardo_frac: 0.0}
    - {variable: temp_rodamiento_c, direccion: "+", cambio: {tipo: delta, valor: 12}, forma: lineal, retardo_frac: 0.3}
  degradacion: {forma: lineal, duracion_h: [168, 720]}
  sintomas: [temp_devanado_alta, corriente_en_rango]
  fuentes: [D-005, D-033, D-037]
```

### Regla (`knowledge/rules/rules.yaml`)

```yaml
- id: R01
  activo: motor_electrico
  si: [temp_devanado_alta, corriente_en_rango, desbalance_en_rango]   # conjunción de síntomas
  entonces: sobrecalentamiento_ventilacion
  fc: 0.7
  accion: "Inspeccionar y limpiar rejillas, aletas y ventilador; …"
  fuentes: [D-005, D-033, D-045]
```

Política del FC (D-034, D-046): 0.85–0.90 umbral normativo con firma específica; 0.75–0.80 con dos o más fuentes concordantes; 0.65–0.70 con fuentes secundarias o firma ambigua; 0.60 heurística. Las reglas con síntomas percibidos no superan 0.80.

### Expresión de técnico (`knowledge/lexicon/expresiones.yaml`)

```yaml
- id: EXP01
  expresion: el motor está cantando
  variantes: [está chillando, está silbando, zumba raro]
  sintoma_percibido: ruido_agudo_percibido
  activos: [motor_electrico, bomba_centrifuga, compresor_tornillo]
  fisica: "Por qué la frase corresponde a ese síntoma…"
  sintomas_formales: [...]
  variables: [{variable: vib_hf_rel, cambio: aumenta}]
  modos_falla_candidatos: [{id: falla_lubricacion_rodamiento, fc_max: 0.5}]
  decisiones: [D-0NN]
```

### Fila de la FMEA (`knowledge/acquisition/fmea.yaml` → `<activo>`)

```yaml
- componente: estator_devanado
  modo_falla: degradacion_aislamiento
  sintomas: [temp_devanado_alta, desbalance_corriente_alto, corriente_alta, olor_quemado_percibido]
  causas: [sobrecarga_sostenida, perdida_de_fase, …]
  acciones: [prueba_megohmetro_e_indice_polarizacion, …]
  severidad: 9
  ocurrencia: 4
  deteccion: 5
  npr: 180            # = severidad × ocurrencia × detección
  fuentes: [D-005, D-006, D-032]
```

## 4. Recetas

Después de **cualquier** cambio en un YAML:

```bash
python -m metaltech.kb.ontology        # regenera la ontología
pytest tests/test_conocimiento.py tests/test_rules_engine.py tests/test_ontology.py
```

### Agregar una regla

1. Documente la decisión en `decisiones.md` (nueva `D-NNN`, con al menos 2 fuentes o 1 norma).
2. Agregue la regla en `rules.yaml` con un `id` nuevo, síntomas que existan en el catálogo, el `fc` según la política y `fuentes`.
3. Compruebe que la firma del modo de falla active las premisas: si no, la regla nunca se dispara (`test_firma_activa_las_premisas_de_cada_regla`, [ERR-010](../agentes/ERRORES.md)).
4. Regenere la ontología y corra las pruebas.
5. Regenere la comparación (`python -m metaltech.hybrid.comparar --todas`) y las métricas: M0 y M3 cambian.

### Agregar un síntoma

1. Si mide una variable nueva, agréguela antes al activo (sección 3).
2. Agregue el síntoma en `sintomas` con `tipo`, `variable` y `nivel`.
3. Úselo en al menos una regla: `test_conocimiento.py` revisa la cobertura y la decisión D-047 exige que ningún síntoma quede sin uso.

### Agregar un modo de falla

1. Documente la decisión con sus fuentes.
2. Agréguelo en `failure_modes.yaml` con `firma`, `degradacion`, `sintomas` y `fuentes`.
3. Agregue su fila en `fmea.yaml` y al menos una regla en `rules.yaml`: `test_cada_modo_activo_tiene_fila_fmea_y_regla`.
4. Regenere ontología, datos y modelos: el modelo tiene una clase nueva, así que hay que reentrenar (`data.generator` → `models.train` → `hybrid.comparar --todas` → métricas).

### Agregar una expresión de técnico

1. Agréguela en `expresiones.yaml` con su síntoma percibido, la física que la justifica y sus modos candidatos (`fc_max`).
2. Si el síntoma percibido es nuevo, agréguelo al catálogo con `tipo: percibido`.
3. Regenere la ontología. No hace falta reentrenar: M1 no usa el texto, y M0 y M3 lo leen al diagnosticar.

### Agregar un tipo de activo

Es el cambio más grande:
1. Activo en `assets.yaml` (unidades, componentes, variables con umbrales y fuentes) y sus síntomas.
2. Modos de falla, filas de la FMEA y reglas.
3. Regenerar la ontología: `ontology.py` crea sola la subclase del nuevo tipo de activo.
4. Regenerar datos y reentrenar todo.
5. Revisar la web y la API: los activos se leen de la base, pero los nombres visibles están en `NOMBRES_ACTIVO` de `dashboard/comun.py` (si falta, se muestra el identificador) y de `scripts/generar_documento.py`.

### Cambiar el simulador

No ajuste parámetros mirando resultados de M1–M3: las firmas se calibran con M0 y con la física (regla de D-050 y D-052). Después, regenere todo y revise `python -m metaltech.data.calibracion`.

### Actualizar los entregables tras nuevos resultados

```bash
python scripts/generar_datos_landing.py
python scripts/generar_documento.py --figuras --pdf
python scripts/generar_poster.py
pytest tests/test_landing.py tests/test_documento.py tests/test_sesgos.py
```

`test_sesgos.py` falla si las cifras escritas en `reports/sesgos_limitaciones.md` dejan de coincidir con las tablas: actualice el informe.

## 5. Pruebas

| Archivo | Protege |
|---|---|
| `test_conocimiento.py` | Coherencia entre reglas, síntomas, firmas, FMEA, léxico y decisiones |
| `test_rules_engine.py`, `test_lexicon.py` | Motor de reglas y léxico |
| `test_ontology.py` | Generación y consultas de la ontología; HermiT si hay Java |
| `test_generator.py` | Firmas presentes, partición sin fuga, reproducibilidad |
| `test_modelos.py`, `test_hibrido.py`, `test_xai.py` | Modelos, fusión y explicaciones |
| `test_metricas_fase7.py`, `test_evaluacion_humana.py` | Evaluación final y de explicaciones |
| `test_api.py`, `test_dashboard.py` | API y cada página de la web |
| `test_landing.py`, `test_documento.py`, `test_sesgos.py`, `test_manuales.py` | Entregables: cifras, citas, enlaces y comandos |
| `test_proceso.py`, `test_entorno.py` | MEMORIA ↔ ERRORES y entorno |

Las pruebas que necesitan datos, modelos o Java se omiten si faltan, con un mensaje que lo dice.

## 6. Registro del trabajo

Toda tarea termina con una entrada en [MEMORIA.md](../agentes/MEMORIA.md) y el bloque *Estado actual* reescrito. Todo error, propio o del entorno, va a [ERRORES.md](../agentes/ERRORES.md) como `ERR-NNN`. Verifique con `python -m metaltech.proceso` antes del commit.
