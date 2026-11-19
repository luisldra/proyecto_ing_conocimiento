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
for _, e in ep.iterrows():  # sin rótulos sobre el gráfico: se encimaban; el nombre va en el marcador
    fig.add_vrect(x0=e["inicio"], x1=e["falla"], fillcolor=ESTADO["alerta"], opacity=0.12, line_width=0)
fig.add_trace(go.Scatter(
    x=ep["falla"], y=[variables[variable]["critico"]] * len(ep), mode="markers",
    marker={"symbol": "x", "size": 11, "color": ESTADO["critico"], "line": {"width": 2, "color": ESTADO["critico"]}},
    text=[nombre_modo(m) for m in ep["modo"]], hovertemplate="Falla: %{text}<br>%{x|%Y-%m-%d %H:%M}<extra></extra>",
))
for nivel, color, texto in (("alerta", ESTADO["alerta"], "umbral de alerta"), ("critico", ESTADO["critico"], "umbral crítico")):
    fig.add_hline(y=variables[variable][nivel], line_dash="dash", line_color=color, line_width=1,
                  annotation_text=texto, annotation_position="bottom right", annotation_font_color="#52514e")
fig.update_layout(showlegend=False)
mostrar(estilo(fig, f"{variable} · {unidad} ({variables[variable]['unidad']})", alto=420), tramo, "serie")
st.caption("Bandas amarillas: degradación hasta la falla. ✕ rojas: instante de cada falla (pase el cursor para ver cuál). "
           "Huecos: unidad en reparación (sin datos).")

TAREAS = {"prediccion": "Predicción (24 h antes)", "deteccion": "Detección"}
izq, der = st.columns(2)
with izq:
    st.markdown("**Fallas en el tramo**")
    st.dataframe(pd.DataFrame({"Falla": ep["modo"].map(nombre_modo), "Tarea": ep["tarea"].map(TAREAS),
                               "Inicio": ep["inicio"], "Falla en": ep["falla"], "Duración (h)": ep["duracion_h"].round(1)}),
                 width="stretch", hide_index=True)
with der:
    st.markdown("**Eventos que imitan fallas en el tramo**")
    eventos = tramo.loc[tramo["confusor"] != "ninguno", ["ts", "confusor"]].drop_duplicates("confusor").head(50)
    st.dataframe(pd.DataFrame({"Inicio": eventos["ts"], "Evento": eventos["confusor"].astype(str).str.replace("_", " ").str.capitalize()}),
                 width="stretch", hide_index=True)
with st.expander("Ficha de datos completa"):
    st.markdown((RAIZ / "data" / "README.md").read_text(encoding="utf-8"))
pie()
