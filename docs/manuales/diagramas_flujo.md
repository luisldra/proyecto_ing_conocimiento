# Diagramas de flujo

Los diagramas usan Mermaid: GitHub los dibuja al abrir este archivo y VS Code los muestra con una extensión de Mermaid. Cada uno trae una explicación breve.

## 1. Flujo general del sistema

De los datos al diagnóstico explicado. El conocimiento experto y el modelo trabajan en paralelo y se combinan al final (M3).

```mermaid
flowchart LR
    subgraph Conocimiento
        F[Fuentes: normas, literatura, datasets] --> I[Agente investigador]
        I --> D[decisiones.md]
        D --> Y[YAML: activos, modos, reglas, léxico, FMEA]
        Y --> O[Ontología OWL]
    end
    subgraph Datos
        S[Simulador] --> P[(data/synthetic)]
        P --> V[Ventanas de 6 h]
    end
    V --> M1[M1: MLP / CNN1D / LSTM]
    V --> R[M0: motor de reglas con FC]
    Y --> R
    R -. certezas como entrada .-> M2[M2: modelo con rama de conocimiento]
    V --> M2
    M1 --> F3[M3: fusión α·p + 1−α·certeza]
    R --> F3
    F3 --> X[Diagnóstico explicado]
    O --> X
    X --> API[API FastAPI] --> W[Web demostrativa]
```

## 2. Un diagnóstico, de la ventana a la explicación

Lo que pasa cuando la web o un programa llama a `POST /diagnose`.

```mermaid
flowchart TD
    A[Solicitud: activo, 36 lecturas por sensor, texto opcional] --> B{¿Sensores completos y 36 valores?}
    B -- no --> E[Error 422 con los sensores que faltan]
    B -- sí --> C[Rellenar vacíos con el último valor conocido]
    C --> D[Normalizar con estadísticas de entrenamiento]
    D --> M1[M1: probabilidad por modo de falla]
    C --> R[Motor de reglas: síntomas, reglas disparadas, certezas]
    T[Texto del técnico] --> L[Léxico: síntoma percibido] --> R
    M1 --> F[M3: puntaje = α·p + 1−α·certeza]
    R --> F
    F --> G{¿Puntaje máximo es normal?}
    G -- sí --> N[Operación normal]
    G -- no --> H[Alerta del modo con mayor puntaje]
    H --> IG[Gradientes integrados: peso de cada sensor]
    H --> RT[Traza: reglas con valores reales y umbrales]
    H --> ON[Ontología: causas y acciones]
    IG --> X[Explicación en texto: variables, reglas y acción]
    RT --> X
    ON --> X
    X --> Z[Una persona decide la intervención]
```

## 3. Motor de reglas con factores de certeza

Cómo se calcula la certeza de cada modo de falla (MYCIN).

```mermaid
flowchart TD
    A[Valor de cada variable] --> B[Comparar con su umbral: alerta, crítico o en rango]
    B --> C[Grado del síntoma entre 0 y 1, con rampa suave cerca del umbral]
    T[Expresión del técnico] --> P[Síntoma percibido con su grado]
    C --> D[Para cada regla: certeza de la premisa = mínimo de los grados]
    P --> D
    D --> E{¿Todas las premisas activas?}
    E -- no --> Q[Regla no disparada; se lista si casi se cumple]
    E -- sí --> F[Certeza de la conclusión = FC de la regla × certeza de la premisa]
    F --> G[Combinar reglas del mismo modo: FC = FC1 + FC2 · 1 − FC1]
    G --> H[Certeza por modo de falla + traza con valores reales]
```

## 4. Generación de datos y entrenamiento

El camino que siguen los comandos de la [puesta en marcha](puesta_en_marcha.md#4-regenerar-datos-modelos-y-reportes).

```mermaid
flowchart LR
    C[configs/*.yaml] --> G[data.generator]
    G --> P[(Parquet: sensores, episodios, observaciones)]
    P --> W[Ventanas 6 h; partición temporal 60/20/20 + máquina reservada]
    W --> GR{¿Degradación a más de 24 h de la falla?}
    GR -- sí --> GV[Ventana gris: solo aviso temprano]
    GR -- no --> TR[models.train: MLP, CNN1D, LSTM por activo]
    TR --> SEL[Elegir arquitectura por F1 de validación]
    SEL --> CMP[hybrid.comparar: M0, M2 y M3; α y veto en validación]
    CMP --> EV[metrics: intervalos, equidad, impacto, latencia]
    CMP --> XAI[xai.explain]
    EV --> T[(reports/tables)]
    XAI --> T
```

## 5. Trabajo de los agentes

El protocolo de [AGENTS.md](../../AGENTS.md), sección 6.

```mermaid
flowchart TD
    A[Leer AGENTS.md, Estado actual de MEMORIA e índice de ERRORES] --> B{¿El problema ya está en ERRORES?}
    B -- sí --> C[Aplicar su prevención]
    B -- no --> D[Ejecutar la tarea dentro del rol y la fase]
    C --> D
    D --> E[Verificar: pytest y la verificación de la fase]
    E --> F{¿Hubo un error, propio o del entorno?}
    F -- sí --> G[Crear ERR-NNN en ERRORES]
    F -- no --> H[Entrada en MEMORIA y reescribir Estado actual]
    G --> H
    H --> I[python -m metaltech.proceso: enlaces consistentes]
    I --> J[Commit local; el equipo hace el push]
```

## 6. De un cambio a los entregables

Qué regenerar según lo que cambió.

```mermaid
flowchart TD
    A{¿Qué cambió?} --> K[YAML de conocimiento]
    A --> S[Simulador o configs/train.yaml]
    A --> T[Texto del documento o del póster]
    K --> O[metaltech.kb.ontology] --> CMP[hybrid.comparar y métricas]
    S --> G[data.generator] --> TR[models.train] --> CMP
    CMP --> L[generar_datos_landing.py]
    CMP --> DOC[generar_documento.py --figuras --pdf]
    CMP --> POS[generar_poster.py]
    T --> DOC
    T --> POS
    L --> PUSH[Push a main: GitHub Actions publica la landing]
```

## 7. Publicación de la landing

```mermaid
flowchart LR
    A[Cambio en landing/] --> B[Push a main]
    B --> C[GitHub Actions: landing.yml]
    C --> D[Sube solo la carpeta landing/]
    D --> E[GitHub Pages]
    E --> F[luisldra.github.io/proyecto_ing_conocimiento]
```

`landing.yml` es el único flujo de publicación. No use las plantillas que sugiere GitHub Pages: publican todo el repositorio ([ERR-030](../agentes/ERRORES.md)).
