"""Equidad e impacto: brechas entre grupos y costo relativo simulado."""

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

st.set_page_config(page_title="Equidad e impacto · Metal Tech", page_icon="⚖️", layout="wide")
st.title("⚖️ Equidad e impacto")

grupos, brechas = tabla("equidad_grupos.csv"), tabla("equidad_brechas.csv")
if grupos is None:
    st.warning("Ejecute `python -m metaltech.metrics.equidad` y `python -m metaltech.metrics.impacto`.")
    st.stop()

st.subheader("Equidad")
st.markdown("¿El sistema funciona igual en todos los turnos, con o sin observación del técnico, en máquinas vistas y no vistas? "
            "M1 no usa las observaciones de los técnicos; M0 y M3 sí. De noche los técnicos aciertan menos (75 % frente a 84–86 %).")
GRUPOS = {"turno": "Turno", "observacion": "Observación del técnico", "maquina": "Máquina", "activo": "Activo"}
MEDIDAS = {"falsa_alarma": "Falsa alarma en equipo sano", "acierto_falla": "Acierto en ventanas con falla"}
c1, c2 = st.columns(2)
grupo = c1.selectbox("Agrupar por", list(GRUPOS), format_func=GRUPOS.get)
medida = c2.selectbox("Medida", list(MEDIDAS), format_func=MEDIDAS.get)
g = grupos[grupos["grupo"] == grupo].groupby(["valor", "sistema"])[medida].mean().reset_index().dropna()
fig = go.Figure()
for s in SISTEMAS:
    d = g[g["sistema"] == s]
    etiquetas = d["valor"].map(nombre_activo) if grupo == "activo" else d["valor"]
    fig.add_bar(x=etiquetas, y=d[medida], name=NOMBRE_SISTEMA[s], marker_color=COLOR[s],
                hovertemplate=f"{NOMBRE_SISTEMA[s]} · %{{x}}: %{{y:.2%}}<extra></extra>")
fig.update_yaxes(tickformat=".1%")
mostrar(estilo(fig, f"{MEDIDAS[medida]} por {GRUPOS[grupo].lower()}", alto=380),
        g.pivot(index="valor", columns="sistema", values=medida).round(4).reset_index(), "equidad")
st.markdown("**Brecha entre el mejor y el peor grupo**")
b = brechas[brechas["grupo"] == grupo]
legible = (lambda v: nombre_activo(v)) if grupo == "activo" else (lambda v: v)
st.dataframe(pd.DataFrame({
    "Sistema": b["sistema"].map(NOMBRE_SISTEMA),
    "Brecha en acierto (puntos)": (100 * b["acierto_falla_brecha"]).round(1),
    "Grupo con menor acierto": b["acierto_falla_peor"].map(legible),
    "Brecha en falsa alarma (puntos)": (100 * b["falsa_alarma_brecha"]).round(2),
    "Grupo con más falsas alarmas": b["falsa_alarma_peor"].map(legible),
}), width="stretch", hide_index=True)

st.subheader("Impacto operativo simulado")
impacto = tabla("impacto_sistemas.csv")
resumen = json_reporte("impacto_resumen.json")
if impacto is not None and resumen is not None:
    st.markdown("Costos en **unidades relativas** a una reparación planificada. Una falsa alarma cuesta 0.1 y una falla no "
                "detectada cuesta *r* veces más que una planificada. Son supuestos, por eso se muestran tres escenarios.")
    r = st.radio("Costo de una falla no detectada (r)", resumen["supuestos"]["ratio_no_planificada"], index=1, horizontal=True)
    i = impacto.set_index("sistema").loc[SISTEMAS]
    columna = f"costo_unidad_anio_r{r}"
    fig = go.Figure(go.Bar(x=[NOMBRE_SISTEMA[s] for s in SISTEMAS], y=i[columna], marker_color=[COLOR[s] for s in SISTEMAS],
                           text=[f"{v:.1f}" for v in i[columna]], textposition="outside",
                           hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_yaxes(title="costo relativo por unidad-año")
    mostrar(estilo(fig, f"Costo por unidad y año (r = {r})", alto=360), i.reset_index().round(3), "impacto")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fallas detectadas por M3", f"{i.loc['M3', 'detectadas_pct']:.1f} %", f"{i.loc['M3', 'detectadas_pct'] - i.loc['M1', 'detectadas_pct']:+.1f} frente a M1",
              delta_color="off")
    c2.metric("Eventos de falsa alarma por unidad-año (M3)", f"{i.loc['M3', 'eventos_falsa_alarma_por_unidad_anio']:.1f}",
              f"{i.loc['M3', 'eventos_falsa_alarma_por_unidad_anio'] - i.loc['M1', 'eventos_falsa_alarma_por_unidad_anio']:+.1f} frente a M1",
              delta_color="inverse")
    c3.metric(f"Ahorro de M3 frente a M0 (r = {r})", f"{resumen[f'ahorro_vs_M0_r{r}_pct']['M3']:.0f} %")
pie()
