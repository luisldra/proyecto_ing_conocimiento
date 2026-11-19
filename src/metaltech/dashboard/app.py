"""Web demostrativa de Metal Tech (Streamlit). Uso: ``streamlit run src/metaltech/dashboard/app.py``.

Define el menú con títulos legibles; cada página vive en ``pages/`` y la portada en ``inicio.py``.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

CARPETA = Path(__file__).parent
st.set_page_config(page_title="Metal Tech · Mantenimiento predictivo explicable", page_icon="🛠️", layout="wide")

PAGINAS = [
    ("inicio.py", "Inicio", "🏠"),
    ("pages/1_Planta.py", "Planta", "🏭"),
    ("pages/2_Simulador.py", "Simulador", "🧪"),
    ("pages/3_Explicacion.py", "Explicación", "🔎"),
    ("pages/4_Base_de_conocimiento.py", "Base de conocimiento", "📚"),
    ("pages/5_Modelos_y_comparacion.py", "Modelos y comparación", "📊"),
    ("pages/6_Equidad_e_impacto.py", "Equidad e impacto", "⚖️"),
    ("pages/7_Datos.py", "Datos", "🗂️"),
    ("pages/8_Bitacora_y_errores.py", "Bitácora y errores", "📓"),
]
st.navigation([st.Page(CARPETA / ruta, title=titulo, icon=icono, default=i == 0)
               for i, (ruta, titulo, icono) in enumerate(PAGINAS)]).run()
