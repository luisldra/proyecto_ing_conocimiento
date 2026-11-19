"""Datos, colores y estilo de gráficos compartidos por las páginas de la web."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from metaltech.data.features import clases_de
from metaltech.kb.base import RAIZ, cargar_base

TABLAS = RAIZ / "reports" / "tables"
DATOS = RAIZ / "data" / "synthetic"
SISTEMAS = ["M0", "M1", "M2", "M3"]
NOMBRE_SISTEMA = {"M0": "M0 · solo reglas", "M1": "M1 · solo modelo", "M2": "M2 · modelo + conocimiento",
                  "M3": "M3 · fusión"}
# Paleta categórica de referencia (validada: scripts/validate_palette.js), en orden fijo.
COLOR = {"M0": "#2a78d6", "M1": "#eb6834", "M2": "#1baf7a", "M3": "#eda100"}
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
ESTADO = {"normal": "#0ca30c", "alerta": "#fab219", "critico": "#d03b3b"}
TINTA, TINTA_2, MUTE = "#0b0b0b", "#52514e", "#898781"
SUPERFICIE, REJILLA, EJE = "#fcfcfb", "#e1e0d9", "#c3c2b7"


def estilo(fig: go.Figure, titulo: str | None = None, alto: int = 360) -> go.Figure:
    """Ejes y rejilla discretos, marcas finas, una sola escala por gráfico."""
    fig.update_layout(
        title=titulo, height=alto, plot_bgcolor=SUPERFICIE, paper_bgcolor=SUPERFICIE,
        font={"color": TINTA_2, "size": 13}, title_font={"color": TINTA, "size": 16},
        margin={"l": 10, "r": 10, "t": 50 if titulo else 20, "b": 10}, hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0, "title": None},
        bargap=0.25, bargroupgap=0.08,
    )
    fig.update_xaxes(showgrid=False, linecolor=EJE, tickfont={"color": MUTE})
    fig.update_yaxes(gridcolor=REJILLA, linecolor=EJE, zeroline=False, tickfont={"color": MUTE})
    fig.update_traces(selector={"type": "bar"}, marker_line_color=SUPERFICIE, marker_line_width=2)
    fig.update_traces(selector={"type": "scatter"}, line_width=2)
    return fig


def mostrar(fig: go.Figure, tabla: pd.DataFrame | None = None, clave: str | None = None) -> None:
    """Gráfico y, debajo, su tabla: los colores con poco contraste nunca son la única vía."""
    st.plotly_chart(fig, use_container_width=True, key=clave)
    if tabla is not None:
        with st.expander("Ver como tabla"):
            st.dataframe(tabla, use_container_width=True, hide_index=True)


@st.cache_data(show_spinner=False)
def tabla(nombre: str) -> pd.DataFrame | None:
    ruta = TABLAS / nombre
    if not ruta.exists():
        return None
    return pd.read_csv(ruta) if ruta.suffix == ".csv" else pd.DataFrame(json.loads(ruta.read_text(encoding="utf-8")))


@st.cache_data(show_spinner=False)
def json_reporte(nombre: str) -> Any:
    ruta = TABLAS / nombre
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


@st.cache_resource(show_spinner=False)
def base():
    return cargar_base()


def clases(activo: str) -> list[str]:
    return clases_de(activo, base())


def nombre_modo(modo: str) -> str:
    return "Operación normal" if modo == "normal" else base().modos[modo]["nombre"]


def nombre_activo(activo: str) -> str:
    return activo.replace("_", " ").capitalize()


def falta(ruta: Path, comando: str) -> bool:
    """Muestra cómo generar un archivo que no existe; devuelve True si falta."""
    if ruta.exists():
        return False
    st.warning(f"Falta `{ruta.relative_to(RAIZ)}`. Genérelo con `{comando}`.")
    return True


def pie() -> None:
    st.caption("Datos sintéticos generados por simulación. Proyecto académico de Ingeniería del Conocimiento, "
               "Universidad de Caldas, 2026-2.")
