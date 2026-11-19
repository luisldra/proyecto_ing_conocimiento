"""Portada de la web: la pregunta del proyecto, las cifras principales y cómo funciona."""

from __future__ import annotations

import streamlit as st

from metaltech.dashboard import cliente
from metaltech.dashboard.comun import json_reporte, pie, tabla

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

intervalos = tabla("intervalos_sistemas.csv")
impacto = json_reporte("impacto_resumen.json")
latencia_api = json_reporte("latencia_api_resumen.json")
if intervalos is not None and impacto is not None:
    def media(metrica: str, sistema: str) -> float:
        fila = intervalos[(intervalos["particion"] == "test_unidad") & (intervalos["metrica"] == metrica)
                          & (intervalos["sistema"] == sistema)]
        return float(fila["media"].iloc[0])

    f1_m3, f1_m1 = media("f1_macro", "M3"), media("f1_macro", "M1")
    fa_m3, fa_m1 = media("falsa_alarma_con_confusor", "M3"), media("falsa_alarma_con_confusor", "M1")
    ev_m3 = impacto["medias"]["M3"]["eventos_falsa_alarma_por_unidad_anio"]
    ev_m1 = impacto["medias"]["M1"]["eventos_falsa_alarma_por_unidad_anio"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("F1 macro · M3", f"{f1_m3:.3f}", f"{f1_m3 - f1_m1:+.3f} frente a M1",
              help="En las máquinas que el modelo nunca vio en el entrenamiento.")
    c2.metric("Falsa alarma · M3", f"{fa_m3:.1%}", f"{(fa_m3 - fa_m1) * 100:+.1f} puntos frente a M1", delta_color="inverse",
              help="Ventanas sanas con un evento que imita una falla, en máquinas nunca vistas.")
    c3.metric("Falsas alarmas al año · M3", f"{ev_m3:.1f}", f"{ev_m3 - ev_m1:+.1f} frente a M1", delta_color="inverse",
              help="Eventos de falsa alarma por unidad y año (alarmas consecutivas cuentan una vez).")
    if latencia_api:
        c4.metric("Latencia de la API", f"{latencia_api['p95_max_ms']['con_explicacion']:.0f} ms",
                  help="Diagnóstico con explicación: percentil 95 del activo más lento, por HTTP local. Sin explicación: "
                       f"{latencia_api['p95_max_ms']['sin_explicacion']:.0f} ms. Objetivo: 200 ms.")
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
