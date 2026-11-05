# Ontología OWL de Metal Tech

`metaltech.owl` (RDF/XML, OWL 2) **se genera, no se edita a mano**: lo produce `src/metaltech/kb/ontology.py` desde `configs/` y `knowledge/` (fuente única de verdad). Si cambia un YAML, regenere el archivo; un test (`test_el_owl_versionado_esta_al_dia`) falla si quedan desincronizados. Diseño y justificación: [D-044](../acquisition/decisiones.md).

```bash
python -m metaltech.kb.ontology                       # genera y valida la estructura
python -m metaltech.kb.ontology --hermit              # además valida con HermiT (necesita Java)
python -m metaltech.kb.ontology --modo cavitacion --activo bomba_centrifuga   # ficha de un modo
python scripts/instalar_jdk.py                        # JDK 17 portable en .tools/ (solo Windows x64)
```

Para verlo en **Protégé**: *File → Open* y elija `metaltech.owl`. Las pestañas *Entities* y *DL Query* permiten navegar clases e individuos; el razonador HermiT viene incluido en Protégé.

## Clases

| Clase | Individuos | Qué representa |
|---|---|---|
| `Activo` (6 subclases por tipo) | 16 | Unidades físicas (4 motores, 3 bombas, 2 compresores, 2 prensas, 3 bandas, 2 CNC) |
| `Componente` | 37 | Componentes por tipo de activo (`bomba_centrifuga__impulsor`) |
| `Sensor` | 168 | Un sensor por variable y unidad |
| `Variable` | 60 | Variable por tipo de activo, con unidad, rango nominal y umbrales |
| `Sintoma` → `SintomaMedido`, `SintomaPercibido` | 63 | 54 medidos con umbral y 9 percibidos por el técnico |
| `ModoFalla` | 31 | Modos de falla con severidad máxima y forma de degradación |
| `Causa` / `Accion` | 127 / 108 | Causas y acciones de la FMEA |
| `Regla` | 48 | Reglas SI–ENTONCES con factor de certeza, acción y fuentes |
| `ExpresionColoquial` | 10 | Léxico de los técnicos |
| `FilaFMEA` | 41 | Relaciones de la FMEA por tipo de activo (severidad, ocurrencia, detección, NPR) |
| `Tecnico` / `Turno` | 10 / 3 | Personal ficticio y anonimizado (T01–T08, I01–I02) y los tres turnos |
| `Alerta` | 0 | Se instancia en tiempo de ejecución; se relaciona con `sustentadaPor` |

Las clases de nivel superior son **disjuntas** entre sí (y `SintomaMedido` con `SintomaPercibido`, y los tipos de activo entre sí).

## Propiedades

| Propiedad | Dominio → Rango | Notas |
|---|---|---|
| `tieneComponente` | Activo → Componente | |
| `monitoreadoPor` | Activo → Sensor | |
| `mide` | Sensor → Variable | funcional |
| `manifiesta` | ModoFalla → Sintoma | unión sobre los activos del modo |
| `causadoPor` | ModoFalla → Causa | |
| `mitigadoPor` | ModoFalla → Accion | |
| `afectaComponente` | ModoFalla → Componente | |
| `refiereA` | ExpresionColoquial → Sintoma | síntoma percibido y formales |
| `sugiereModo` | ExpresionColoquial → ModoFalla | |
| `concluye` / `tienePremisa` | Regla → ModoFalla / Sintoma | `concluye` es funcional |
| `sobreVariable` | SintomaMedido → Variable | |
| `sustentadaPor` | Alerta → Regla ∪ Variable | |
| `modoDeFila`, `componenteDeFila`, `sintomaDeFila`, `causaDeFila`, `accionDeFila` | FilaFMEA → … | detalle por tipo de activo |
| `severidad`, `ocurrencia`, `deteccion`, `npr` | datos (entero) | |
| `umbral` ⊃ `umbralAlerta`, `umbralCritico`, `umbralAlertaBaja` | Variable → decimal | `umbral` no es funcional (ERR-011) |
| `fcRegla`, `accionRecomendada`, `fuente`, `tipoActivo`, `identificador`, `nombre`… | datos | |

## Consultas desde Python

```python
from metaltech.kb.ontology import Ontologia
onto = Ontologia.cargar()
onto.sintomas_de_modo("cavitacion")                       # síntomas de un modo de falla
onto.acciones_de_modo("cavitacion", "bomba_centrifuga")   # acciones para una falla en un activo
onto.modos_de_sintoma("vibracion_hf_alta")                # diagnóstico diferencial
onto.detalle_modo("holgura_mecanica")                     # ficha completa
onto.grafo("bomba_centrifuga")                            # nodos y aristas para la web
```
