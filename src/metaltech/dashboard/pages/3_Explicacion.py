"""Explicación: métricas de explicabilidad, alertas reales explicadas y evaluación del panel."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from metaltech.dashboard.comun import (
    COLOR,
    MUTE,
    estilo,
    json_reporte,
    mostrar,
    nombre_activo,
    nombre_modo,
    pie,
    tabla,
)

st.set_page_config(page_title="Explicación · Metal Tech", page_icon="🔎", layout="wide")
st.title("🔎 Explicación de las alertas")

metricas = tabla("xai_metricas.csv")
if metricas is None:
    st.warning("Ejecute `python -m metaltech.xai.explain` para generar las métricas de explicabilidad.")
    st.stop()

st.markdown("**¿El modelo mira los sensores correctos?** Fracción de los 3 sensores con más peso que coinciden con "
            "los que la falla realmente mueve en el simulador, frente a lo que daría el azar.")
fig = go.Figure()
fig.add_bar(x=metricas["activo"].map(nombre_activo), y=metricas["top_k_en_firma"], name="Modelo", marker_color=COLOR["M1"],
            text=[f"{v:.0%}" for v in metricas["top_k_en_firma"]], textposition="outside")
fig.add_bar(x=metricas["activo"].map(nombre_activo), y=metricas["top_k_en_firma_azar"], name="Azar", marker_color=MUTE,
            text=[f"{v:.0%}" for v in metricas["top_k_en_firma_azar"]], textposition="outside")
fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
mostrar(estilo(fig, "Top-3 de sensores dentro de la firma real de la falla"),
        metricas[["activo", "top_k_en_firma", "top_k_en_firma_azar", "top_k_en_reglas", "caida_top_k", "caida_azar_k"]], "firma")

c1, c2, c3 = st.columns(3)
c1.metric("Fidelidad: caída al anular el top-3", f"{metricas['caida_top_k'].mean():.2f}",
          f"{metricas['caida_top_k'].mean() - metricas['caida_azar_k'].mean():+.2f} frente al azar",
          help=f"Al anular 3 sensores al azar la caída es {metricas['caida_azar_k'].mean():.2f}.")
c2.metric("Top-3 en reglas disparadas", f"{metricas['top_k_en_reglas'].mean():.0%}")
estab = [c for c in metricas if c.startswith("estabilidad")]
c3.metric("Estabilidad con ruido de 0.5 desviaciones", f"{metricas[estab[-1]].mean():.3f}" if estab else "–")

st.subheader("Alertas reales del periodo de prueba")
ejemplos = json_reporte("xai_ejemplos.json") or {}
activo = st.selectbox("Activo", list(ejemplos), format_func=nombre_activo)
opciones = ejemplos.get(activo, [])
if opciones:
    i = st.selectbox("Alerta", range(len(opciones)), format_func=lambda k: f"{nombre_modo(opciones[k]['modo'])} · {opciones[k]['unidad']} · {opciones[k]['ts']}")
    e = opciones[i]
    st.info(e["texto"])
    izq, der = st.columns(2)
    with izq:
        v = pd.DataFrame(e["variables_influyentes"])
        st.markdown("**Sensores con más peso**")
        st.dataframe(v.assign(peso=v["peso"].map("{:.0%}".format)), width="stretch", hide_index=True)
    with der:
        st.markdown("**Reglas**")
        if e["reglas"]:
            for r in e["reglas"]:
                st.markdown(f"**{r['id']}**")
                st.dataframe(pd.DataFrame(r["premisas"]), width="stretch", hide_index=True)
        else:
            st.write("Sin regla que la respalde (alerta solo del modelo).")

st.subheader("Evaluación de las explicaciones")
evaluacion = tabla("evaluacion_agentes.csv")
if evaluacion is not None:
    st.markdown("Panel de **5 agentes** con perfiles de la planta (no son personas; D-059): explicación del modelo solo "
                "frente a la híbrida, a ciegas, de 1 a 5.")
    datos = evaluacion[evaluacion["variante"].isin(["modelo", "hibrida"])]
    fig = go.Figure()
    for variante, nombre, color in (("modelo", "Modelo solo", COLOR["M1"]), ("hibrida", "Híbrida", COLOR["M3"])):
        g = datos[datos["variante"] == variante]
        fig.add_bar(x=g["dimension"], y=g["media"], name=nombre, marker_color=color,
                    text=[f"{m:.2f}" for m in g["media"]], textposition="outside")
    fig.update_yaxes(range=[0, 5.3], title="media (1–5)")
    mostrar(estilo(fig, "Calificación media por dimensión"), datos, "panel")
pie()
