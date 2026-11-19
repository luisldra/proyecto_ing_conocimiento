"""Modelos y comparación: M0 · M1 · M2 · M3 con intervalos de confianza entre semillas."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from metaltech.dashboard.comun import (
    COLOR,
    NOMBRE_SISTEMA,
    SISTEMAS,
    estilo,
    json_reporte,
    mostrar,
    nombre_activo,
    pie,
    tabla,
)

st.set_page_config(page_title="Modelos y comparación · Metal Tech", page_icon="📊", layout="wide")
st.title("📊 Modelos y comparación")
st.markdown("La comparación que pide el enunciado: **modelo solo frente a modelo + conocimiento experto**. "
            "Medias de los 6 tipos de activo con intervalo del 95 % entre 5 semillas.")

intervalos, difs = tabla("intervalos_sistemas.csv"), tabla("intervalos_diferencias.csv")
if intervalos is None:
    st.warning("Ejecute `python -m metaltech.hybrid.comparar --todas` y `python -m metaltech.metrics.intervalos`.")
    st.stop()

PARTICIONES = {"test": "Periodo de prueba", "test_unidad": "Máquinas nunca vistas"}
METRICAS = {"f1_macro": "F1 macro", "falsa_alarma_con_confusor": "Falsa alarma con confusores",
            "falsa_alarma_sin_confusor": "Falsa alarma sin confusores", "recall_macro": "Recall macro",
            "precision_macro": "Precisión macro", "aviso_episodios_pct": "Episodios con aviso temprano (%)"}
metrica = st.selectbox("Métrica", list(METRICAS), format_func=METRICAS.get)
cols = st.columns(2)
for col, (particion, titulo) in zip(cols, PARTICIONES.items(), strict=True):
    d = intervalos[(intervalos["particion"] == particion) & (intervalos["metrica"] == metrica)].set_index("sistema").loc[SISTEMAS]
    fig = go.Figure()
    for s in SISTEMAS:
        fila = d.loc[s]
        fig.add_scatter(x=[NOMBRE_SISTEMA[s]], y=[fila["media"]], mode="markers", marker={"size": 12, "color": COLOR[s]},
                        name=NOMBRE_SISTEMA[s], error_y={"type": "data", "symmetric": False, "color": COLOR[s], "thickness": 2,
                                                         "array": [fila["ic95_sup"] - fila["media"]],
                                                         "arrayminus": [fila["media"] - fila["ic95_inf"]]},
                        hovertemplate=f"{NOMBRE_SISTEMA[s]}: %{{y:.4f}} [{fila['ic95_inf']:.4f}, {fila['ic95_sup']:.4f}]<extra></extra>")
    fig.update_layout(showlegend=False)
    with col:
        mostrar(estilo(fig, titulo, alto=340), d.reset_index()[["sistema", "media", "ic95_inf", "ic95_sup", "desviacion"]], particion)

st.subheader("¿Cuánto aporta el conocimiento?")
st.markdown("Diferencias pareadas por activo y semilla. Si el intervalo no incluye el cero, la diferencia es consistente.")
vista = difs[difs["comparacion"].isin(["M3-M1", "M2-M1", "M3-M0"])].copy()
vista["particion"] = vista["particion"].map(PARTICIONES)
vista["metrica"] = vista["metrica"].map(lambda m: METRICAS.get(m, m))
vista["consistente"] = (vista["ic95_inf"] > 0) | (vista["ic95_sup"] < 0)
st.dataframe(pd.DataFrame({
    "Conjunto": vista["particion"], "Comparación": vista["comparacion"].str.replace("-", " − "), "Métrica": vista["metrica"],
    "Diferencia media": vista["diferencia_media"].round(4), "IC 95 % inferior": vista["ic95_inf"].round(4),
    "IC 95 % superior": vista["ic95_sup"].round(4), "Pares donde el primero es mayor (%)": vista["a_mayor_pct"].round(0),
    "Consistente": vista["consistente"].map({True: "✔ sí", False: "no"}),
}), width="stretch", hide_index=True)
st.caption("En falsa alarma, una diferencia negativa es buena (M3 tiene menos). Los valores p de Wilcoxon están en el archivo "
           "completo; son optimistas porque los pares comparten datos (D-060).")

st.subheader("Por activo (semilla 42)")
comp = tabla("comparacion_sistemas.csv")
part = st.radio("Partición", list(PARTICIONES), format_func=PARTICIONES.get, horizontal=True)
c = comp[comp["particion"] == part]
fig = go.Figure()
for s in SISTEMAS:
    g = c[c["sistema"] == s]
    fig.add_bar(x=g["activo"].map(nombre_activo), y=g["f1_macro"], name=NOMBRE_SISTEMA[s], marker_color=COLOR[s],
                hovertemplate=f"{NOMBRE_SISTEMA[s]} · %{{x}}: %{{y:.3f}}<extra></extra>")
fig.update_yaxes(range=[0, 1], title="F1 macro")
mostrar(estilo(fig, "F1 macro por activo y sistema", alto=380),
        c.pivot(index="activo", columns="sistema", values="f1_macro").round(3).reset_index(), "por_activo")

seleccion = json_reporte("modelos_seleccion.json") or {}
latencia = tabla("latencia.csv")
izq, der = st.columns(2)
with izq:
    st.markdown("**Arquitectura elegida por validación**")
    st.dataframe(pd.DataFrame({"activo": map(nombre_activo, seleccion), "modelo": seleccion.values()}),
                 width="stretch", hide_index=True)
with der:
    st.markdown("**Latencia por solicitud (ms, CPU)**")
    if latencia is not None:
        lat = latencia.pivot(index="activo", columns="sistema", values="p95_ms").round(2).reset_index()
        lat["activo"] = lat["activo"].map(nombre_activo)
        st.dataframe(lat.rename(columns={"activo": "Activo", "M3+XAI": "M3 + explicación"}), width="stretch", hide_index=True)
        st.caption("Percentil 95 por solicitud, sin red ni servidor. Objetivo: 200 ms. Vía API con explicación: ver la portada.")
pie()
