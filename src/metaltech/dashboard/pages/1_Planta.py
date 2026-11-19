"""Planta: estado de cada unidad en un instante del periodo de prueba, según M3."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from metaltech.dashboard.comun import DATOS, base, clases, falta, nombre_activo, nombre_modo, pie

st.set_page_config(page_title="Planta · Metal Tech", page_icon="🏭", layout="wide")
st.title("🏭 Planta")
st.markdown("Estado de cada unidad según el sistema híbrido (M3) en cualquier instante del periodo de prueba: las 26 "
            "unidades usadas en el entrenamiento o las 6 reservadas, que el modelo nunca vio. La columna **real** muestra "
            "lo que de verdad estaba pasando en la simulación.")


def resultado(pred_modo: str, real: str, etiqueta: str) -> str:
    """Compara la alerta con la verdad: la etiqueta solo marca las últimas 24 h antes de la falla."""
    if pred_modo == etiqueta:
        return "✔ Correcto"
    if pred_modo == real != "normal":
        return "⏳ Aviso temprano"  # degradación real a más de 24 h de la falla, modo correcto
    if pred_modo == "normal":
        return "✘ Falla no detectada"
    return "✘ Falsa alarma" if real == "normal" else "✘ Falla equivocada"


@st.cache_data(show_spinner="Cargando predicciones…")
def predicciones() -> pd.DataFrame:
    partes = []
    for activo in base().activos:
        p = pd.read_parquet(DATOS / f"predicciones_{activo}.parquet",
                            columns=["semilla", "activo", "particion", "unidad", "ts", "y", "modo", "horas_a_falla", "pred_M3"])
        partes.append(p[p["semilla"] == p["semilla"].min()])
    return pd.concat(partes, ignore_index=True)


if falta(DATOS / "predicciones_motor_electrico.parquet", "python -m metaltech.hybrid.comparar --todas"):
    st.stop()

pred = predicciones()
grupo = st.radio("Unidades", ["Vistas en entrenamiento (periodo de prueba)", "Reservadas (nunca vistas)"], horizontal=True)
p = pred[pred["particion"] == ("test" if grupo.startswith("Vistas") else "test_unidad")]
inicio, fin = p["ts"].min().to_pydatetime(), p["ts"].max().to_pydatetime()
instante = st.slider("Instante", min_value=inicio, max_value=fin, value=inicio + (fin - inicio) / 3,
                     step=pd.Timedelta(hours=1).to_pytimedelta(), format="YYYY-MM-DD HH:mm")

ultimo = p[p["ts"] <= pd.Timestamp(instante)].sort_values("ts").groupby("unidad").tail(1)
filas = []
for _, f in ultimo.iterrows():
    cl = clases(f["activo"])
    pred_modo, real = cl[int(f["pred_M3"])], cl[int(f["modo"])]
    filas.append({
        "Activo": nombre_activo(f["activo"]), "Unidad": f["unidad"],
        "Estado según M3": "✅ Normal" if pred_modo == "normal" else f"⚠️ {nombre_modo(pred_modo)}",
        "Resultado": resultado(pred_modo, real, cl[int(f["y"])]),
        "Real": "Sana" if real == "normal" else f"{nombre_modo(real)} · falla en {f['horas_a_falla']:.0f} h",
        "Última lectura": f["ts"],
    })
estado = pd.DataFrame(filas).sort_values(["Activo", "Unidad"])
c1, c2, c3, c4 = st.columns(4)
c1.metric("Unidades", len(estado))
c2.metric("⚠️ En alerta", int(estado["Estado según M3"].str.startswith("⚠️").sum()))
c3.metric("Degradándose de verdad", int((estado["Real"] != "Sana").sum()))
c4.metric("✘ Errores", int(estado["Resultado"].str.startswith("✘").sum()))
st.dataframe(estado, width="stretch", hide_index=True, height=35 * (len(estado) + 1) + 3,
             column_config={"Activo": st.column_config.TextColumn(width="medium"),
                            "Real": st.column_config.TextColumn("Real (simulación)", width="large")})
st.caption("Una máquina que se degrada pero a la que le faltan más de 24 h para fallar se espera en «Normal» "
           "(✔ Correcto); si el sistema ya avisa con el modo correcto, es un ⏳ aviso temprano.")
pie()
