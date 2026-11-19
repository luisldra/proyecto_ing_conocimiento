"""Bitácora y errores: el proceso del proyecto tal como quedó registrado por los agentes."""

from __future__ import annotations

import streamlit as st

from metaltech.dashboard.comun import pie
from metaltech.kb.base import RAIZ

st.set_page_config(page_title="Bitácora · Metal Tech", page_icon="📓", layout="wide")
st.title("📓 Bitácora y errores")
st.markdown("Cada tarea dejó una entrada en la bitácora y cada error, propio o del entorno, una ficha con su causa y su "
            "prevención. Así se ve el proceso completo, no solo el resultado.")
memoria, errores, plan = st.tabs(["Bitácora (MEMORIA)", "Errores (ERRORES)", "Plan"])
for pestana, ruta in ((memoria, "docs/agentes/MEMORIA.md"), (errores, "docs/agentes/ERRORES.md"), (plan, "docs/PLAN.md")):
    with pestana:
        st.markdown((RAIZ / ruta).read_text(encoding="utf-8"))
pie()
