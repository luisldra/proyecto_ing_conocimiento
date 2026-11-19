"""Cada página de la web carga sin errores (modo en proceso, sin servidor)."""

from __future__ import annotations

import os

import pytest

from metaltech.kb.base import RAIZ

os.environ["METALTECH_API"] = "local"
CARPETA = RAIZ / "src" / "metaltech" / "dashboard"
PAGINAS = [CARPETA / "app.py", *sorted((CARPETA / "pages").glob("*.py"))]

pytestmark = pytest.mark.skipif(
    not (RAIZ / "checkpoints").exists() or not (RAIZ / "data" / "synthetic" / "episodios.parquet").exists(),
    reason="faltan modelos o datos generados",
)


@pytest.mark.parametrize("pagina", PAGINAS, ids=lambda p: p.stem)
def test_pagina_carga_sin_excepciones(pagina):
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(pagina), default_timeout=180).run()
    assert not app.exception, [e.value for e in app.exception]


def test_simulador_diagnostica_al_pulsar_el_boton():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(CARPETA / "pages" / "2_Simulador.py"), default_timeout=180).run()
    app.button[0].click().run()
    assert not app.exception, [e.value for e in app.exception]
    textos = " ".join(m.value for m in app.markdown)
    assert "Explicación" in textos and app.metric
