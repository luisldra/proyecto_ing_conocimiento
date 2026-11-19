"""Cada página de la web carga sin errores (modo en proceso, sin servidor)."""

from __future__ import annotations

import os

import pytest

from metaltech.kb.base import RAIZ

os.environ["METALTECH_API"] = "local"
CARPETA = RAIZ / "src" / "metaltech" / "dashboard"
PAGINAS = [CARPETA / "app.py", CARPETA / "inicio.py", *sorted((CARPETA / "pages").glob("*.py"))]

pytestmark = pytest.mark.skipif(
    not (RAIZ / "checkpoints").exists() or not (RAIZ / "data" / "synthetic" / "episodios.parquet").exists(),
    reason="faltan modelos o datos generados",
)


@pytest.mark.parametrize("pagina", PAGINAS, ids=lambda p: p.stem)
def test_pagina_carga_sin_excepciones(pagina):
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(pagina), default_timeout=180).run()
    assert not app.exception, [e.value for e in app.exception]


def test_portada_lee_las_cifras_de_los_reportes():
    import pandas as pd
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(CARPETA / "inicio.py"), default_timeout=180).run()
    t = pd.read_csv(RAIZ / "reports" / "tables" / "intervalos_sistemas.csv")
    m3 = t[(t["particion"] == "test_unidad") & (t["metrica"] == "f1_macro") & (t["sistema"] == "M3")]["media"].iloc[0]
    assert app.metric[0].value == f"{m3:.3f}"


def test_menu_tiene_titulos_con_tildes():
    texto = (CARPETA / "app.py").read_text(encoding="utf-8")
    assert all(t in texto for t in ("Explicación", "Modelos y comparación", "Bitácora y errores"))


def test_simulador_diagnostica_al_pulsar_el_boton():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(CARPETA / "pages" / "2_Simulador.py"), default_timeout=180).run()
    app.button[0].click().run()
    assert not app.exception, [e.value for e in app.exception]
    textos = " ".join(m.value for m in app.markdown)
    assert "Explicación" in textos and app.metric
