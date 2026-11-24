# Manual de la API

API REST en FastAPI para consultar la base de conocimiento, predecir y diagnosticar fallas con explicación. Es la misma API que usa la web demostrativa.

```bash
uvicorn metaltech.api.main:app          # http://127.0.0.1:8000
```

- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs. Ahí se puede probar cada endpoint desde el navegador.
- Formato: JSON en UTF-8. Sin autenticación: es una demo local, no se expone a internet.
- Los modelos se cargan al arrancar; el primer arranque tarda unos segundos.
- Los ejemplos de respuesta de este manual son reales y están recortados (`…`).

## Resumen de endpoints

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/health` | Estado y modelos cargados |
| GET | `/assets` | Todos los activos con sus variables, umbrales y modos de falla |
| GET | `/assets/{activo}` | Un activo |
| GET | `/kb/rules?activo=&modo=` | Reglas, filtrables por activo y modo de falla |
| GET | `/kb/failure/{modo}?activo=` | Ficha de un modo de falla desde la ontología |
| GET | `/kb/lexicon` | Expresiones de técnicos y su traducción |
| GET | `/kb/ontology/graph?activo=` | Nodos y aristas de la ontología |
| POST | `/predict` | Probabilidades del modelo (M1) para una ventana |
| POST | `/diagnose` | Diagnóstico de M0, M1 y M3 con explicación |
| POST | `/simulate` | Genera una ventana con una falla inyectada y la diagnostica |
| GET | `/reports/{nombre}` | Tablas de resultados |

**Activos válidos:** `motor_electrico`, `bomba_centrifuga`, `compresor_tornillo`, `prensa_hidraulica`, `banda_transportadora`, `centro_cnc`. Los modos de falla de cada activo salen de `GET /assets/{activo}` (campo `modos`).

## Consultas de la base de conocimiento

### `GET /health`

```json
{"estado": "ok", "modelos": ["bomba_centrifuga", "…"], "activos": 6}
```

### `GET /assets/{activo}`

Devuelve el nombre del activo, sus `unidades`, sus `variables` (con `unidad`, `direccion`, rango `nominal`, umbrales `alerta` y `critico`, y `fuentes`), sus `modos` de falla, el `modelo` elegido y si está `disponible`.

```json
{
  "nombre": "Bomba centrífuga de refrigerante/agua de proceso",
  "unidades": ["bomba_centrifuga_01", "…"],
  "variables": {"vib_rms_mm_s": {"unidad": "mm/s RMS", "direccion": "alta", "nominal": [0.5, 1.4], "alerta": 5.1, "critico": 8.5, "fuentes": […]}, "…": {}},
  "modos": ["cavitacion", "…"],
  "modelo": "cnn1d",
  "disponible": true
}
```

### `GET /kb/rules?activo=bomba_centrifuga&modo=cavitacion`

```json
[{"id": "R13", "activo": "bomba_centrifuga", "si": ["margen_npsh_bajo", "vibracion_hf_alta", "caudal_inestable"],
  "entonces": "cavitacion", "fc": 0.85, "accion": "Revisar NPSH disponible: …", "fuentes": ["…"]}]
```

### `GET /kb/failure/cavitacion`

Ficha del modo desde la ontología:

```json
{"id": "cavitacion", "nombre": "Cavitación por NPSH disponible insuficiente", "activos": ["bomba_centrifuga"],
 "forma_degradacion": "sigmoide", "severidad": 8, "sintomas": ["caudal_inestable", "…"], "causas": ["filtro_succion_obstruido", "…"],
 "acciones": ["inspeccionar_erosion_impulsor", "…"], "componentes": ["bomba_centrifuga__impulsor"], "reglas": ["R13", "…"],
 "expresiones": ["esto está cascabeleando", "…"], "fmea": [{"activo": "bomba_centrifuga", "severidad": 8, "ocurrencia": 5, "deteccion": 4, "npr": 160}]}
```

### `GET /kb/lexicon` y `GET /kb/ontology/graph?activo=…`

El léxico devuelve una lista con `id`, `expresion`, `variantes`, `sintoma_percibido`, `activos`, `fisica`, `sintomas_formales`, `variables`, `modos_falla_candidatos` y `decisiones`. El grafo devuelve `{"nodos": [{"id", "tipo", "etiqueta"}], "aristas": [{"origen", "relacion", "destino"}]}`.

## Predicción y diagnóstico

### La ventana de sensores

`/predict` y `/diagnose` reciben una **ventana**: un objeto con **todos** los sensores del activo y **36 lecturas crudas** por sensor (6 horas, una cada 10 minutos, de la más antigua a la más reciente). Un valor `null` toma el último valor conocido. Los nombres de los sensores son las claves de `variables` en `GET /assets/{activo}`. Por ejemplo, la bomba centrífuga usa:

`vib_rms_mm_s`, `vib_hf_rel`, `vib_curtosis`, `vib_1x_frac`, `vib_2x_1x_ratio`, `vib_axial_radial_ratio`, `temp_rodamiento_c`, `corriente_pct`, `npsh_margen_ratio`, `caudal_pct`, `caudal_cv_pct`, `presion_descarga_pct`, `fuga_sello_ml_h`.

La forma más fácil de obtener una ventana válida es pedirla a `/simulate`.

### `POST /predict`

Cuerpo: `activo` y `ventana`. Respuesta: el modo más probable y la probabilidad de cada clase según M1.

```json
{"activo": "bomba_centrifuga", "modo": "cavitacion", "probabilidades": {"normal": 5.4e-11, "cavitacion": 1.0, "desalineacion_eje": 2.4e-14, "…": 0}}
```

### `POST /diagnose`

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `activo` | texto | sí | Tipo de activo |
| `ventana` | objeto | sí | 36 lecturas por sensor |
| `texto` | texto | no | Observación del técnico, por ejemplo "la bomba está golpeando" |
| `unidad` | texto | no | Unidad, para usar su línea base de puesta en marcha |
| `explicar` | booleano | no (por defecto `true`) | Calcula el peso de cada sensor con gradientes integrados (más lento) |

Respuesta:

```json
{
  "activo": "bomba_centrifuga",
  "sistemas": {"M0": {"modo": "cavitacion", "certeza": 0.99}, "M1": {"modo": "cavitacion", "probabilidad": 1.0}, "M3": {"modo": "cavitacion", "puntaje": 0.999}},
  "probabilidades_modelo": {"cavitacion": 1.0, "…": 0},
  "certezas_reglas": {"cavitacion": 0.996},
  "reglas_parciales": [{"id": "…", "modo": "…", "cumplidas": […], "faltantes": […]}],
  "diagnostico": {
    "modo": "cavitacion", "nombre": "Cavitación por NPSH disponible insuficiente",
    "puntaje": 0.999, "probabilidad_modelo": 1.0, "certeza_reglas": 0.996, "respaldo_reglas": true,
    "reglas": [{"id": "R14", "fc": 0.9, "premisas": [{"sintoma": "margen_npsh_insuficiente", "variable": "npsh_margen_ratio", "valor": 0.9, "umbral": 1.1, "operador": "<="}, "…"]}, "…"],
    "causas": ["…"], "acciones": ["…"], "origen_accion": "regla disparada",
    "expresiones": ["la bomba está golpeando"], "alternativas": […],
    "variables_influyentes": [{"variable": "npsh_margen_ratio", "peso": 0.33, "en_reglas": true}, "…"]
  }
}
```

Cómo leerla:
- `sistemas` resume la decisión de cada sistema; `diagnostico` es la explicación de M3.
- `respaldo_reglas: false` significa que **ninguna regla** respalda la alerta: el modelo la detecta solo y conviene verificar más.
- `origen_accion` dice si la acción viene de una regla disparada o de las reglas del mismo modo de falla.
- `reglas_parciales` son reglas a las que les faltan premisas.

### `POST /simulate`

| Campo | Tipo | Por defecto | Descripción |
|---|---|---|---|
| `activo` | texto | — | Tipo de activo |
| `modo` | texto o `null` | `null` | Modo de falla; vacío = operación normal |
| `avance` | 0 a 1 | 1.0 | Punto de la degradación al final de la ventana (1 = falla) |
| `severidad` | 0.5 a 1.5 | 1.0 | Multiplica el cambio de la firma |
| `texto` | texto | `null` | Observación del técnico |
| `semilla` | entero | 0 | Semilla del ruido |
| `explicar` | booleano | `true` | Calcula los pesos de los sensores |

Responde lo mismo que `/diagnose` y además `ventana` (la ventana generada), `modo_simulado`, `avance` y `severidad`.

### `GET /reports/{nombre}`

Devuelve una tabla de `reports/tables/` como lista de filas. Nombres: `comparacion`, `semillas`, `intervalos`, `diferencias`, `equidad`, `brechas`, `impacto`, `latencia`, `xai`, `calibracion`, `evaluacion_agentes`.

## Ejemplos

### curl

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/kb/rules?activo=bomba_centrifuga&modo=cavitacion"
curl -X POST http://127.0.0.1:8000/simulate -H "Content-Type: application/json" \
     -d '{"activo": "bomba_centrifuga", "modo": "cavitacion", "explicar": false}'
```

En PowerShell use `curl.exe` y comillas dobles escapadas, o `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/simulate -ContentType "application/json" `
  -Body '{"activo": "bomba_centrifuga", "modo": "cavitacion", "explicar": false}'
```

### Python

```python
import httpx

api = "http://127.0.0.1:8000"
sim = httpx.post(f"{api}/simulate", json={"activo": "bomba_centrifuga", "modo": "cavitacion"}, timeout=60).json()

# Diagnosticar la misma ventana con la observación de un técnico
d = httpx.post(f"{api}/diagnose", json={"activo": "bomba_centrifuga", "ventana": sim["ventana"],
                                        "texto": "la bomba está golpeando"}, timeout=60).json()
diag = d["diagnostico"]
print(diag["nombre"], round(diag["puntaje"], 3), "respaldada por reglas:", diag["respaldo_reglas"])
for a in diag["acciones"]:
    print("-", a)
```

## Errores

| Código | Cuándo | Ejemplo de `detail` |
|---|---|---|
| 404 | Activo, modo o reporte desconocido | `"activo desconocido: x"`; `"modo de falla desconocido: x"`; `"reporte no disponible: x. Opciones: [...]"` |
| 422 | Ventana inválida o campo fuera de rango | `"faltan sensores: [...]"`; `"cada sensor necesita 36 lecturas (10 min, 6 h): {...}"`; para `avance` o `severidad` fuera de rango, el detalle estándar de validación de FastAPI |

## Rendimiento

En un equipo de escritorio, con la API local, el percentil 95 del peor activo es de unos 21 ms por diagnóstico sin explicación y unos 79 ms con explicación (`reports/tables/latencia_api_resumen.json`). La medida se repite con `python -m metaltech.metrics.latencia --api http://127.0.0.1:8000`.
