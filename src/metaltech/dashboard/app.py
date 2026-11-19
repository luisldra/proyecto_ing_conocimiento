"""Web demostrativa de Metal Tech (Streamlit). Uso: ``streamlit run src/metaltech/dashboard/app.py``."""

from __future__ import annotations

import streamlit as st

from metaltech.dashboard import cliente
from metaltech.dashboard.comun import json_reporte, pie

st.set_page_config(page_title="Metal Tech · Mantenimiento predictivo explicable", page_icon="🛠️", layout="wide")

st.title("Mantenimiento predictivo explicable en Metal Tech")
st.markdown(
    "**¿Cómo integrar un modelo de Deep Learning con una base de conocimiento experto para predecir fallas "
    "y generar diagnósticos explicables en una planta manufacturera?**"
)
st.markdown(
    "Esta web permite **probar** el sistema y **ver** cada pieza: la planta simulada, el diagnóstico de una "
    "falla con sus reglas y sensores, la base de conocimiento, la comparación de modelos, la equidad, el "
    "impacto, los datos y la bitácora del proyecto. Use el menú lateral."
)

intervalos = json_reporte("intervalos_resumen.json")
impacto = json_reporte("impacto_resumen.json")
latencia = json_reporte("latencia_resumen.json")
if intervalos and impacto:
    difs = {(d["particion"], d["comparacion"], d["metrica"]): d for d in intervalos["diferencias"]}
    f1 = difs[("test_unidad", "M3-M1", "f1_macro")]
    fa = difs[("test_unidad", "M3-M1", "falsa_alarma_con_confusor")]
    eventos = impacto["medias"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("F1 macro de M3 (máquina no vista)", f"{0.932 + f1['diferencia_media']:.3f}",
              f"{f1['diferencia_media']:+.3f} frente a M1")
    c2.metric("Falsa alarma con confusores", f"{fa['diferencia_media'] * 100:+.1f} puntos", "M3 frente a M1",
              delta_color="off")
    c3.metric("Eventos de falsa alarma por unidad-año", f"{eventos['M3']['eventos_falsa_alarma_por_unidad_anio']:.1f}",
              f"{eventos['M3']['eventos_falsa_alarma_por_unidad_anio'] - eventos['M1']['eventos_falsa_alarma_por_unidad_anio']:+.1f} frente a M1",
              delta_color="inverse")
    if latencia:
        c4.metric("Latencia p95 de M3", f"{latencia['por_sistema_p95_max_ms']['M3']:.1f} ms", "peor activo", delta_color="off")
    st.caption("Medias de 6 tipos de activo y 5 semillas. Detalle e intervalos en la página Modelos y comparación.")

st.subheader("Cómo funciona")
st.markdown(
    """
| Pieza | Qué hace |
|---|---|
| **Sensores** | Ventana de 6 h (36 lecturas cada 10 min) de vibración, temperatura, corriente, presión y caudal |
| **M1 · Deep Learning** | MLP, CNN1D o LSTM por tipo de activo: probabilidad de cada modo de falla |
| **M0 · Sistema experto** | 55 reglas con factores de certeza sobre síntomas medidos y lo que reporta el técnico |
| **M3 · Fusión** | Combina la probabilidad del modelo y la certeza de las reglas |
| **Explicación** | Sensores con más peso (gradientes integrados), reglas con valores reales, causas y acciones |
"""
)
st.info(f"Conexión: {cliente.estado()}. Inicie la API con `uvicorn metaltech.api.main:app` para usarla como servidor.")
pie()
