# Puesta en marcha

Cómo instalar el proyecto desde un clon limpio, regenerar datos y modelos, y levantar la API, la web y la landing.

## 1. Requisitos

| Requisito | Versión | Para qué | Obligatorio |
|---|---|---|---|
| Python | 3.11 o superior (probado con 3.14) | Todo el proyecto | Sí |
| Git | cualquiera reciente | Clonar el repositorio | Sí |
| Espacio en disco | unos 3 GB libres | Entorno, datos sintéticos y modelos | Sí |
| JDK 17 | 17 | Validar la ontología con el razonador HermiT | No (las pruebas `java` se omiten sin él) |
| Microsoft Word | cualquiera con exportar a PDF | Generar el PDF del documento APA | No (solo Fase 10) |
| Chromium de Playwright | el que instala Playwright | Revisar la web, figuras del documento y póster | No |

No hace falta GPU: todo corre en CPU.

## 2. Instalación

### Windows (PowerShell)

```powershell
git clone https://github.com/luisldra/proyecto_ing_conocimiento.git
cd proyecto_ing_conocimiento
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e . --no-deps
```

Si PowerShell no deja activar el entorno, ejecute una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### Windows (Git Bash), Linux o macOS

```bash
git clone https://github.com/luisldra/proyecto_ing_conocimiento.git
cd proyecto_ing_conocimiento
python -m venv .venv
source .venv/Scripts/activate      # Git Bash; en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
```

### Opcionales

```bash
python scripts/instalar_jdk.py                      # JDK 17 portable en .tools/ (Windows x64; no toca el sistema)
pip install playwright && python -m playwright install chromium
```

En Linux o macOS, en lugar de `instalar_jdk.py`, instale un JDK 17 y déjelo en el `PATH`.

## 3. Comprobar la instalación

```bash
python -m metaltech.kb.ontology        # genera y valida la ontología (unos segundos)
python -m metaltech.proceso            # MEMORIA y ERRORES consistentes
```

Las pruebas que dependen de datos y modelos se omiten hasta el paso 4. La suite completa (`pytest`) tarda de varios minutos a más de media hora según el equipo.

## 4. Regenerar datos, modelos y reportes

Los datos (`data/synthetic/`) y los modelos (`checkpoints/`) **no se versionan**. Se regeneran en este orden; cada paso usa lo que produjo el anterior:

| Paso | Comando | Produce | Tiempo aproximado |
|---|---|---|---|
| 1 | `python -m metaltech.data.generator` | `data/synthetic/*.parquet` y `manifest.json` | menos de 1 min |
| 2 | `python -m metaltech.data.calibracion` | `reports/tables/calibracion_*` | segundos |
| 3 | `python -m metaltech.models.train` | `checkpoints/` (M1 por activo) y `reports/tables/modelos_*` | unos 25 min en CPU |
| 4 | `python -m metaltech.hybrid.comparar --todas` | M2, fusión M3 y `reports/tables/comparacion_*` con 5 semillas | el paso más largo |
| 5 | `python -m metaltech.xai.explain` | `reports/tables/xai_*` | minutos |
| 6 | `python -m metaltech.metrics.intervalos` | `intervalos_*` | segundos |
| 7 | `python -m metaltech.metrics.equidad` | `equidad_*` | minutos |
| 8 | `python -m metaltech.metrics.impacto` | `impacto_*` | minutos |
| 9 | `python -m metaltech.metrics.latencia` | `latencia*` | minutos |

Con la misma semilla y configuración, el resultado es idéntico (el manifiesto guarda el SHA-256 de cada archivo). La [guía de comandos](guia_comandos.md) explica cada opción.

## 5. Levantar el prototipo

Abra dos terminales con el entorno activado:

```bash
uvicorn metaltech.api.main:app        # API en http://127.0.0.1:8000 (documentación en /docs)
streamlit run src/metaltech/dashboard/app.py    # web en http://localhost:8501
```

La web usa la API si está levantada; si no, carga la misma API dentro de su proceso. Para la demo basta con `streamlit run`.

**Verificar:** http://127.0.0.1:8000/health debe responder `{"estado": "ok", ...}` y la portada de la web debe mostrar las cifras principales.

La **landing** no necesita servidor: abra `landing/index.html` con doble clic o visite https://luisldra.github.io/proyecto_ing_conocimiento/.

## 6. Documento, póster y revisión

```bash
python scripts/generar_datos_landing.py              # landing/data.js tras cambiar resultados
python scripts/generar_documento.py --figuras --pdf  # documento APA (el PDF requiere Word)
python scripts/generar_poster.py                     # póster A1
python scripts/revisar_web.py --salida revision_web  # recorre la web con un navegador real
```

## 7. Problemas frecuentes

| Síntoma | Causa | Solución | Ver |
|---|---|---|---|
| `ModuleNotFoundError: metaltech` | Falta instalar el paquete | `pip install -e . --no-deps` con el entorno activado | — |
| `ModuleNotFoundError: yaml` u otra librería | Entorno sin dependencias | `pip install -r requirements.txt` | [ERR-006](../agentes/ERRORES.md) |
| Python distinto de 3.11 | El equipo usa 3.14 | Cualquier versión ≥ 3.11 funciona | [ERR-007](../agentes/ERRORES.md) |
| Pruebas `java` omitidas o HermiT no corre | No hay JDK | `python scripts/instalar_jdk.py` | [ERR-008](../agentes/ERRORES.md) |
| owlready2 no abre la ontología en una ruta con espacios | URI `file:///` con espacios | Use `Ontologia.cargar()`, que lee el archivo directamente | [ERR-013](../agentes/ERRORES.md) |
| Streamlit no se detiene con Ctrl+C en Windows | Vigilante de archivos | Ya desactivado en `.streamlit/config.toml`; si persiste, cierre la terminal | [ERR-027](../agentes/ERRORES.md) |
| La web dice que la API no responde | La API tarda en cargar modelos | Espere unos segundos o use la API en proceso (no levante uvicorn) | [ERR-028](../agentes/ERRORES.md) |
| Páginas vacías o error "faltan reports/tables" | No se regeneraron los reportes | Ejecute los pasos de la sección 4 | — |
| La landing publicada da 404 | GitHub Pages sin activar o flujo equivocado | Pages con *Source: GitHub Actions*; solo `landing.yml` | [ERR-030](../agentes/ERRORES.md) |
