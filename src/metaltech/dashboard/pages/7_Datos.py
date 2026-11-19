"""Datos: explorador del dataset sintético, con episodios de falla y umbrales."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from metaltech.dashboard.comun import (
    DATOS,
    ESTADO,
    SERIES,
    base,
    estilo,
    falta,
    mostrar,
    nombre_activo,
    nombre_modo,
    pie,
)
from metaltech.kb.base import RAIZ

st.set_page_config(page_title="Datos · Metal Tech", page_icon="🗂️", layout="wide")
st.title("🗂️ Datos sintéticos")
st.markdown("36 meses de lecturas cada 10 minutos de 32 unidades, con fallas inyectadas, eventos que imitan fallas y "
            "observaciones de técnicos. **Son datos simulados**, no de una planta real.")
if falta(DATOS / "episodios.parquet", "python -m metaltech.data.generator"):
    st.stop()


@st.cache_data(show_spinner="Leyendo datos…")
def serie(activo: str, unidad: str, variable: str) -> pd.DataFrame:
    return pd.read_parquet(DATOS / f"{activo}.parquet", columns=["ts", "unidad", "estado", "confusor", "particion", variable],
                           filters=[("unidad", "==", unidad)])


@st.cache_data(show_spinner=False)
def episodios() -> pd.DataFrame:
    return pd.read_parquet(DATOS / "episodios.parquet")


b = base()
c1, c2, c3 = st.columns(3)
activo = c1.selectbox("Activo", list(b.activos), format_func=nombre_activo)
unidad = c2.selectbox("Unidad", [f"{activo}_{k:02d}" for k in range(1, b.activos[activo]["unidades"] + 1)])
variables = b.activos[activo]["variables"]
variable = c3.selectbox("Sensor", list(variables))
s = serie(activo, unidad, variable)
inicio = st.date_input("Desde", s["ts"].min().date() + pd.Timedelta(days=120), min_value=s["ts"].min().date(),
                       max_value=s["ts"].max().date())
dias = st.slider("Días a mostrar", 3, 90, 30)
tramo = s[(s["ts"] >= pd.Timestamp(inicio)) & (s["ts"] < pd.Timestamp(inicio) + pd.Timedelta(days=dias))]
ep = episodios()
ep = ep[(ep["unidad"] == unidad) & (ep["falla"] >= tramo["ts"].min()) & (ep["inicio"] <= tramo["ts"].max())]

fig = go.Figure(go.Scatter(x=tramo["ts"], y=tramo[variable], mode="lines", line_color=SERIES[0], name=variable,
                           hovertemplate="%{x|%Y-%m-%d %H:%M}: %{y:.3g}<extra></extra>"))
for _, e in ep.iterrows():
    fig.add_vrect(x0=e["inicio"], x1=e["falla"], fillcolor=ESTADO["alerta"], opacity=0.12, line_width=0,
                  annotation_text=nombre_modo(e["modo"])[:40], annotation_position="top left",
                  annotation_font_color="#52514e")
for nivel, color in (("alerta", ESTADO["alerta"]), ("critico", ESTADO["critico"])):
    fig.add_hline(y=variables[variable][nivel], line_dash="dash", line_color=color, line_width=1,
                  annotation_text=f"umbral de {nivel}", annotation_font_color="#52514e")
fig.update_layout(showlegend=False)
mostrar(estilo(fig, f"{variable} · {unidad} ({variables[variable]['unidad']})", alto=420), tramo, "serie")
st.caption("Bandas amarillas: degradación hasta la falla. Huecos: unidad en reparación (sin datos).")

izq, der = st.columns(2)
with izq:
    st.markdown("**Episodios de falla en el tramo**")
    st.dataframe(ep[["modo", "tarea", "inicio", "falla", "duracion_h", "particion"]], use_container_width=True, hide_index=True)
with der:
    st.markdown("**Eventos que imitan fallas en el tramo**")
    st.dataframe(tramo.loc[tramo["confusor"] != "ninguno", ["ts", "confusor"]].drop_duplicates("confusor").head(50),
                 use_container_width=True, hide_index=True)
with st.expander("Ficha de datos completa"):
    st.markdown((RAIZ / "data" / "README.md").read_text(encoding="utf-8"))
pie()
