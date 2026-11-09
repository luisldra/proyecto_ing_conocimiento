# Datos – Metal Tech

> **Declaración:** todos los datos de este proyecto son **sintéticos**, generados por simulación a partir de `configs/assets.yaml` y `configs/failure_modes.yaml`. No provienen de una planta real ni contienen datos personales. Los técnicos y turnos son ficticios (T01–T08, I01–I02).

## Cómo generarlos

```bash
python -m metaltech.data.generator      # data/synthetic/ (no se versiona; unos 25 s)
python -m metaltech.data.calibracion    # reports/tables/calibracion_*
```

Con la misma semilla y configuración el resultado es idéntico. `manifest.json` guarda los conteos y el SHA-256 de cada archivo.

## Contenido (semilla 42)

36 meses cada 10 min, 32 unidades, 5 049 216 filas, 1075 episodios de falla y 2220 observaciones de técnicos.

| Archivo | Contenido |
|---|---|
| `{activo}.parquet` | Una fila por unidad y paso: variables del activo y las columnas de abajo |
| `episodios.parquet` | Cada falla: unidad, modo, tarea, inicio, falla, duración, partición |
| `observaciones.parquet` | Expresión del técnico, turno, técnico, modo real y si la expresión era correcta |

| Columna | Significado |
|---|---|
| `estado` | `sano`, `degradacion`, `falla` o `reparacion` (en reparación los sensores son NaN) |
| `modo_activo` | Modo que se está degradando, aunque aún no sea detectable |
| `etiqueta` | Clase a aprender. Predicción: últimas 24 h antes de la falla. Detección: desde que la firma es observable (D-049) |
| `t_degradacion`, `horas_a_falla` | Avance del episodio y vida útil restante |
| `confusor` | Evento que imita una falla o defecto de medición; **no usar como entrada del modelo** |
| `particion` | `train`, `val`, `test` (60/20/20 temporal), `purga` (descartar) o `test_unidad` (la última unidad de cada tipo, nunca entrenada) |

`estado`, `modo_activo`, `t_degradacion`, `horas_a_falla` y `confusor` son verdad de terreno: usarlos como entradas sería fuga de información.

Las ventanas en `degradacion` a más de 24 h de la falla son **grises** (D-054): no se entrenan ni puntúan, y se miden aparte como aviso temprano.

## Supuestos y limitaciones (D-049, D-050)

- Las firmas, duraciones y parámetros son supuestos basados en literatura. Se contrastaron con AI4I 2020 y SKAB (`python scripts/contrastar_datasets.py`, D-052); no con NASA IMS ni con el dataset hidráulico de UCI.
- **Las firmas parten de umbrales que las reglas conocen (D-042).** Las firmas incompletas, la severidad variable y la deriva reducen ese efecto (M0 detecta 67.5 % en predicción y 55.5 % en detección), pero el resultado de M0 sigue sin ser evidencia de lo que pasaría en una planta real.
- Diferencias conocidas con los datos públicos: en SKAB solo un 33 % de los canales se mueve al menos 1 desviación durante una anomalía y aquí se espera un 60 %, así que nuestras firmas siguen siendo más completas; la variación en sano de vibración es mayor (9.7 % frente a 2 %), lo que se acepta porque SKAB es un banco de laboratorio estable. El desgaste de herramienta al fallar ya coincide (mediana 212 frente a 214 min).
- Los confusores son condiciones supuestas: el modelo los aprende del mismo generador con que se evalúa, de modo que su baja falsa alarma es optimista.
- Una sola falla por unidad a la vez. Algunas clases siguen con muy poco soporte en test: la cavitación tiene 2 episodios.
- Las clases están muy desbalanceadas: 2.4 % de filas positivas.
- Los técnicos rotan de turno cada semana; el acierto depende del técnico y baja de noche por diseño (75.0 % frente a 84–86 %): es un sesgo inyectado para analizar equidad, no una afirmación sobre personas reales.
