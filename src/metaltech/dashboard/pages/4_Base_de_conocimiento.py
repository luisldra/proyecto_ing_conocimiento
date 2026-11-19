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
# Un selector y no pestañas: Streamlit dibuja las pestañas ocultas con ancho cero y el grafo de la
# ontología quedaba mal encuadrado al mostrarse (ERR-029). Así solo se dibuja la sección elegida.
seccion = st.radio("Sección", ["Reglas", "FMEA", "Léxico de técnicos", "Ontología", "Decisiones"], horizontal=True)

if seccion == "Reglas":
    r = pd.DataFrame(cliente.obtener("/kb/rules", activo=activo))
    modo = st.selectbox("Modo de falla", [None, *sorted(r["entonces"].unique())],
                        format_func=lambda m: "Todos" if m is None else nombre_modo(m))
    if modo:
        r = r[r["entonces"] == modo]
    r = r.assign(si=r["si"].map(" ∧ ".join), fuentes=r["fuentes"].map(", ".join))
    st.dataframe(r[["id", "activo", "si", "entonces", "fc", "accion", "fuentes"]], width="stretch", hide_index=True)

elif seccion == "FMEA":
    filas = [{"activo": a, **f} for a, lista in b.fmea.items() for f in lista if activo in (None, a)]
    f = pd.DataFrame(filas)
    for c in ("sintomas", "causas", "acciones", "fuentes"):
        f[c] = f[c].map(lambda x: ", ".join(x) if isinstance(x, list) else x)
    st.dataframe(f.sort_values("npr", ascending=False), width="stretch", hide_index=True)

elif seccion == "Léxico de técnicos":
    lx = pd.DataFrame(cliente.obtener("/kb/lexicon"))
    if activo:
        lx = lx[lx["activos"].map(lambda a: activo in a)]
    lx = lx.assign(candidatos=lx["modos_falla_candidatos"].map(lambda c: ", ".join(f"{x['id']} ({x['fc_max']})" for x in c)))
    st.dataframe(lx[["id", "expresion", "sintoma_percibido", "candidatos"]], width="stretch", hide_index=True)
    with st.expander("Física de cada expresión"):
        for _, e in lx.iterrows():
            st.markdown(f"**{e['expresion']}** — {e['fisica']}")

elif seccion == "Ontología":
    if activo is None:
        st.info("Elija un activo arriba para dibujar su parte de la ontología (el grafo completo es ilegible).")
    else:
        g = cliente.obtener("/kb/ontology/graph", activo=activo)
        tipos = ["ModoFalla", "Sintoma", "Regla", "Causa", "Accion", "ExpresionColoquial"]
        mostrar = st.multiselect("Tipos de nodo", tipos, default=["ModoFalla", "Sintoma", "Regla", "ExpresionColoquial"])
        # in_line incrusta vis.js: con rutas relativas el iframe pedía los scripts al servidor de
        # Streamlit, que devolvía su HTML y el navegador fallaba al ejecutarlo (ERR-029).
        red = Network(height="640px", width="100%", directed=True, bgcolor="#fcfcfb", font_color="#0b0b0b",
                      cdn_resources="in_line")
        visibles = {n["id"] for n in g["nodos"] if n["tipo"] in mostrar}
        for n in g["nodos"]:
            if n["id"] in visibles:
                red.add_node(n["id"], label=n["etiqueta"][:40], title=f"{n['tipo']}: {n['etiqueta']}",
                             color=SERIES[tipos.index(n["tipo"])], shape="dot", size=18 if n["tipo"] == "ModoFalla" else 10)
        for a in g["aristas"]:
            if a["origen"] in visibles and a["destino"] in visibles:
                red.add_edge(a["origen"], a["destino"], title=a["relacion"], color="#c3c2b7")
        # Se estabiliza antes de mostrarse y se ajusta al marco, para que ningún nodo quede cortado.
        red.set_options("""{"physics": {"solver": "forceAtlas2Based",
            "forceAtlas2Based": {"gravitationalConstant": -60, "springLength": 90, "centralGravity": 0.02},
            "stabilization": {"enabled": true, "iterations": 400, "fit": true}},
          "interaction": {"hover": true, "navigationButtons": true, "zoomView": true}}""")
        html = red.generate_html()
        creacion = "network = new vis.Network(container, data, options);"
        # pyvis no reencuadra tras estabilizar: sin esto quedaban nodos fuera del marco.
        html = html.replace(creacion, creacion + '\n network.once("stabilizationIterationsDone",'
                                                  ' function () { network.fit({animation: false}); });', 1)
        components.html(html, height=660)
        st.caption("Colores: " + " · ".join(f"{t} = {['azul', 'naranja', 'aqua', 'amarillo', 'rosa', 'verde'][i]}"
                                             for i, t in enumerate(tipos) if t in mostrar)
                   + ". Pase el cursor por un nodo para ver su tipo y nombre completo.")

else:
    st.markdown((RAIZ / "knowledge" / "acquisition" / "decisiones.md").read_text(encoding="utf-8"))
pie()
