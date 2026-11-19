"""La landing muestra las cifras vigentes de los reportes (Fase 8b)."""

from __future__ import annotations

import importlib.util
import re

import pytest

from metaltech.kb.base import RAIZ

LANDING = RAIZ / "landing"
_spec = importlib.util.spec_from_file_location("generar_datos_landing", RAIZ / "scripts" / "generar_datos_landing.py")
generador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generador)

pytestmark = pytest.mark.skipif(not (RAIZ / "reports" / "tables" / "intervalos_sistemas.csv").exists(),
                                reason="faltan los reportes de la Fase 7")


def test_data_js_coincide_con_los_reportes():
    assert generador.leer_actual() == generador.construir(), (
        "landing/data.js está desactualizado: ejecute python scripts/generar_datos_landing.py")


def test_la_pagina_carga_sus_recursos_locales():
    html = (LANDING / "index.html").read_text(encoding="utf-8")
    for recurso in re.findall(r'(?:src|href)="([^"#:]+\.(?:js|css))"', html):
        assert (LANDING / recurso).exists(), recurso


def test_cifras_de_resultados_no_estan_escritas_a_mano_en_el_html():
    html = (LANDING / "index.html").read_text(encoding="utf-8")
    datos = generador.leer_actual()["resultados"]
    f1 = next(x["media"] for x in datos["f1_no_vista"] if x["sistema"] == "M3")
    assert f"{f1:.3f}".replace(".", ",") not in html and f"{f1:.3f}" not in html


def test_ejemplo_tiene_regla_que_lo_respalda():
    assert generador.leer_actual()["ejemplo"]["reglas"]
