"""Base de conocimiento: reglas, FMEA, léxico, grafo de la ontología y decisiones."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from metaltech.dashboard import cliente
from metaltech.dashboard.comun import SERIES, base, nombre_activo, nombre_modo, pie
from metaltech.kb.base import RAIZ

st.set_page_config(page_title="Base de conocimiento · Metal Tech", page_icon="📚", layout="wide")
st.title("📚 Base de conocimiento")
b = base()
st.markdown(f"{len(b.reglas)} reglas · {len(b.modos)} modos de falla · {len(b.sintomas)} síntomas · "
            f"{sum(len(v) for v in b.fmea.values())} filas FMEA · {len(b.lexico)} expresiones de técnicos. "
            "Todo proviene de revisión documental con sus fuentes en el registro de decisiones.")

activo = st.selectbox("Activo", [None, *b.activos], format_func=lambda a: "Todos" if a is None else nombre_activo(a))
reglas, fmea, lexico, grafo, decisiones = st.tabs(["Reglas", "FMEA", "Léxico de técnicos", "Ontología", "Decisiones"])

with reglas:
    r = pd.DataFrame(cliente.obtener("/kb/rules", activo=activo))
    modo = st.selectbox("Modo de falla", [None, *sorted(r["entonces"].unique())],
                        format_func=lambda m: "Todos" if m is None else nombre_modo(m))
    if modo:
        r = r[r["entonces"] == modo]
    r = r.assign(si=r["si"].map(" ∧ ".join), fuentes=r["fuentes"].map(", ".join))
    st.dataframe(r[["id", "activo", "si", "entonces", "fc", "accion", "fuentes"]], use_container_width=True, hide_index=True)

with fmea:
    filas = [{"activo": a, **f} for a, lista in b.fmea.items() for f in lista if activo in (None, a)]
    f = pd.DataFrame(filas)
    for c in ("sintomas", "causas", "acciones", "fuentes"):
        f[c] = f[c].map(lambda x: ", ".join(x) if isinstance(x, list) else x)
    st.dataframe(f.sort_values("npr", ascending=False), use_container_width=True, hide_index=True)

with lexico:
    lx = pd.DataFrame(cliente.obtener("/kb/lexicon"))
    if activo:
        lx = lx[lx["activos"].map(lambda a: activo in a)]
    lx = lx.assign(candidatos=lx["modos_falla_candidatos"].map(lambda c: ", ".join(f"{x['id']} ({x['fc_max']})" for x in c)))
    st.dataframe(lx[["id", "expresion", "sintoma_percibido", "candidatos"]], use_container_width=True, hide_index=True)
    with st.expander("Física de cada expresión"):
        for _, e in lx.iterrows():
            st.markdown(f"**{e['expresion']}** — {e['fisica']}")

with grafo:
    if activo is None:
        st.info("Elija un activo arriba para dibujar su parte de la ontología (el grafo completo es ilegible).")
    else:
        g = cliente.obtener("/kb/ontology/graph", activo=activo)
        tipos = ["ModoFalla", "Sintoma", "Regla", "Causa", "Accion", "ExpresionColoquial"]
        mostrar = st.multiselect("Tipos de nodo", tipos, default=["ModoFalla", "Sintoma", "Regla", "ExpresionColoquial"])
        red = Network(height="640px", width="100%", directed=True, bgcolor="#fcfcfb", font_color="#0b0b0b")
        visibles = {n["id"] for n in g["nodos"] if n["tipo"] in mostrar}
        for n in g["nodos"]:
            if n["id"] in visibles:
                red.add_node(n["id"], label=n["etiqueta"][:40], title=f"{n['tipo']}: {n['etiqueta']}",
                             color=SERIES[tipos.index(n["tipo"])], shape="dot", size=18 if n["tipo"] == "ModoFalla" else 10)
        for a in g["aristas"]:
            if a["origen"] in visibles and a["destino"] in visibles:
                red.add_edge(a["origen"], a["destino"], title=a["relacion"], color="#c3c2b7")
        red.toggle_physics(True)
        components.html(red.generate_html(), height=660)
        st.caption("Colores: " + " · ".join(f"{t} = {['azul', 'naranja', 'aqua', 'amarillo', 'rosa', 'verde'][i]}"
                                             for i, t in enumerate(tipos) if t in mostrar)
                   + ". Pase el cursor por un nodo para ver su tipo y nombre completo.")

with decisiones:
    st.markdown((RAIZ / "knowledge" / "acquisition" / "decisiones.md").read_text(encoding="utf-8"))
pie()
