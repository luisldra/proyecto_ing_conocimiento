"""Simulador en vivo: se inyecta una falla, se escribe lo que diría un técnico y se ve el diagnóstico."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from metaltech.dashboard import cliente
from metaltech.dashboard.comun import (
    COLOR,
    ESTADO,
    NOMBRE_SISTEMA,
    SERIES,
    base,
    estilo,
    mostrar,
    nombre_activo,
    nombre_modo,
    pie,
)

st.set_page_config(page_title="Simulador · Metal Tech", page_icon="🧪", layout="wide")
st.title("🧪 Simulador en vivo")
st.markdown("Elija un activo y una falla, ajuste cuánto ha avanzado y, si quiere, escriba lo que reportaría un técnico. "
            "El sistema devuelve el diagnóstico de cada sistema y la explicación de la alerta.")

b = base()
c1, c2 = st.columns(2)
activo = c1.selectbox("Activo", list(b.activos), format_func=nombre_activo)
modos = ["normal", *sorted(m for m, d in b.modos.items() if activo in d["activos"])]
modo = c2.selectbox("Falla a simular", modos, format_func=nombre_modo, index=1)
c3, c4, c5 = st.columns(3)
avance = c3.slider("Avance de la degradación al final de la ventana", 0.0, 1.0, 1.0, 0.05,
                   help="0 = recién empieza, 1 = momento de la falla", disabled=modo == "normal")
severidad = c4.slider("Severidad", 0.5, 1.5, 1.0, 0.05)
semilla = c5.number_input("Semilla del ruido", 0, 999, 0)
expresiones = ["(ninguna)", *[e["expresion"] for e in b.lexico if activo in e["activos"]], "Escribir otra…"]
elegida = st.selectbox("Observación del técnico", expresiones)
texto = st.text_input("Texto libre del técnico") if elegida == "Escribir otra…" else (None if elegida == "(ninguna)" else elegida)

if st.button("Diagnosticar", type="primary"):
    with st.spinner("Diagnosticando…"):
        st.session_state["simulacion"] = cliente.enviar("/simulate", {
            "activo": activo, "modo": None if modo == "normal" else modo, "avance": avance,
            "severidad": severidad, "texto": texto, "semilla": int(semilla), "explicar": True})

r = st.session_state.get("simulacion")
if not r or r["activo"] != activo:
    st.stop()

d = r["diagnostico"]
st.divider()
cols = st.columns(3)
for col, (s, info) in zip(cols, r["sistemas"].items(), strict=True):
    valor = info.get("certeza", info.get("probabilidad", info.get("puntaje", 0.0)))
    icono = "✅" if info["modo"] == "normal" else "⚠️"
    col.metric(NOMBRE_SISTEMA[s], f"{icono} {nombre_modo(info['modo'])}", f"{valor:.0%}", delta_color="off")
    col.caption({"M0": "certeza de las reglas", "M1": "probabilidad del modelo", "M3": "puntaje fusionado"}[s])

simulado = r["modo_simulado"]
if d["modo"] == simulado:
    st.success(f"El sistema híbrido identificó la falla simulada: **{nombre_modo(simulado)}**.")
else:
    st.warning(f"Se simuló **{nombre_modo(simulado)}** y el sistema híbrido concluyó **{nombre_modo(d['modo'])}**.")
st.markdown(f"### Explicación\n{d['texto']}")

izq, der = st.columns(2)
with izq:
    imp = pd.Series(d.get("importancias", {})).sort_values()
    fig = go.Figure(go.Bar(x=imp.values, y=imp.index, orientation="h", marker_color=COLOR["M1"],
                           text=[f"{v:.0%}" for v in imp.values], textposition="outside",
                           hovertemplate="%{y}: %{x:.1%}<extra></extra>"))
    fig.update_xaxes(tickformat=".0%")
    mostrar(estilo(fig, "Peso de cada sensor en la predicción del modelo", alto=380),
            imp.rename("peso").reset_index().rename(columns={"index": "sensor"}), "importancias")
with der:
    st.markdown("**Reglas que respaldan la alerta**")
    if d["reglas"]:
        for regla in d["reglas"]:
            st.markdown(f"**{regla['id']}** · certeza {regla['fc']:.2f}")
            st.dataframe(pd.DataFrame(regla["premisas"]), use_container_width=True, hide_index=True)
    else:
        st.info("Ninguna regla respalda esta conclusión: es una alerta solo del modelo.")
    if r["reglas_parciales"]:
        with st.expander("Reglas que casi se cumplen"):
            st.dataframe(pd.DataFrame(r["reglas_parciales"]), use_container_width=True, hide_index=True)
    st.markdown("**Acciones sugeridas**")
    for a in d["acciones"][:4]:
        st.markdown(f"- {a}")
    if d["causas"]:
        st.markdown("**Causas posibles:** " + "; ".join(d["causas"]))

st.markdown("### Ventana de sensores simulada")
variables = b.activos[activo]["variables"]
firma = [f["variable"] for f in b.modos[simulado]["firma"] if f["variable"] in variables] if simulado != "normal" else []
elegidas = st.multiselect("Sensores", list(variables), default=(firma or list(variables))[:4])
if elegidas:
    fig = make_subplots(rows=len(elegidas), cols=1, shared_xaxes=True, subplot_titles=elegidas, vertical_spacing=0.08)
    minutos = [10 * k - 350 for k in range(36)]
    for i, v in enumerate(elegidas, 1):
        fig.add_trace(go.Scatter(x=minutos, y=r["ventana"][v], mode="lines", line_color=SERIES[0], name=v,
                                 hovertemplate=f"{v}: %{{y:.3g}}<extra></extra>"), row=i, col=1)
        for nivel, color in (("alerta", ESTADO["alerta"]), ("critico", ESTADO["critico"])):
            fig.add_hline(y=variables[v][nivel], line_dash="dash", line_color=color, line_width=1, row=i, col=1,
                          annotation_text=nivel, annotation_font_color="#52514e")
    fig.update_xaxes(title_text="minutos antes del diagnóstico", row=len(elegidas), col=1)
    fig.update_layout(showlegend=False)
    mostrar(estilo(fig, alto=180 * len(elegidas) + 60), pd.DataFrame({v: r["ventana"][v] for v in elegidas}), "ventana")
pie()
