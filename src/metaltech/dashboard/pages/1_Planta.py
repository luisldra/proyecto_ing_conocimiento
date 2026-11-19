"""Planta: estado de cada unidad en un instante del periodo de prueba, según M3."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from metaltech.dashboard.comun import DATOS, base, clases, falta, nombre_activo, nombre_modo, pie

st.set_page_config(page_title="Planta · Metal Tech", page_icon="🏭", layout="wide")
st.title("🏭 Planta")
st.markdown("Estado de las 32 unidades según el sistema híbrido (M3), en cualquier instante del periodo de prueba. "
            "La columna **real** muestra lo que de verdad estaba pasando en la simulación.")


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
        "Real": "Sana" if real == "normal" else f"{nombre_modo(real)} (falla en {f['horas_a_falla']:.0f} h)",
        "Acierto": "✔" if pred_modo == cl[int(f["y"])] or (pred_modo == real != "normal") else "✘",
        "Última lectura": f["ts"],
    })
estado = pd.DataFrame(filas).sort_values(["Activo", "Unidad"])
alertas = int(estado["Estado según M3"].str.startswith("⚠️").sum())
c1, c2, c3 = st.columns(3)
c1.metric("Unidades", len(estado))
c2.metric("⚠️ En alerta", alertas)
c3.metric("✔ Coincide con la realidad", f"{(estado['Acierto'] == '✔').mean():.0%}")
st.dataframe(estado, use_container_width=True, hide_index=True)
st.caption("Una alerta puede llegar antes de las 24 h previas a la falla (aviso temprano): en ese caso aparece como acierto "
           "si el modo coincide con la degradación real.")
pie()
