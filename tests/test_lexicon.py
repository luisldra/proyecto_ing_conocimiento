"""Léxico: expresiones coloquiales -> síntomas percibidos y modos candidatos."""

from __future__ import annotations

import pytest

from metaltech.kb.base import cargar_base
from metaltech.kb.lexicon import Lexico, normalizar

BASE = cargar_base()
FORMAS = [
    (e["id"], forma, activo)
    for e in BASE.lexico
    for forma in [e["expresion"], *e.get("variantes", [])]
    for activo in e["activos"][:1]
]


@pytest.fixture(scope="module")
def lexico():
    return Lexico(BASE)


def test_normalizar():
    assert normalizar("¡La BOMBA está golpeando!!") == "la bomba esta golpeando"
    assert normalizar("  huele   a quemado ") == "huele a quemado"


@pytest.mark.parametrize(("exp_id", "forma", "activo"), FORMAS)
def test_cada_expresion_y_variante_se_reconoce(lexico, exp_id, forma, activo):
    ids = [c.id for c in lexico.identificar(f"Hoy {forma} otra vez", activo)]
    assert exp_id in ids


@pytest.mark.parametrize("exp", BASE.lexico, ids=lambda e: e["id"])
def test_candidatos_respetan_fc_max_y_activo(lexico, exp):
    for activo in exp["activos"]:
        (c,) = [x for x in lexico.identificar(exp["expresion"], activo) if x.id == exp["id"]]
        assert c.sintoma_percibido == exp["sintoma_percibido"]
        for modo, fc in c.candidatos.items():
            assert fc <= 0.6
            assert activo in BASE.modos[modo]["activos"], (exp["id"], activo, modo)


def test_filtra_por_activo(lexico):
    assert lexico.identificar("la bomba está golpeando", "motor_electrico") == []
    assert lexico.sintomas_percibidos("la bomba está golpeando", "bomba_centrifuga") == [
        "golpeteo_percibido"
    ]


def test_candidatos_de_la_bomba_golpeando(lexico):
    c = lexico.candidatos("La bomba está golpeando", "bomba_centrifuga")
    assert c["cavitacion"] == 0.6
    assert list(c)[0] == "cavitacion"  # ordenados por fc_max


def test_varias_expresiones_en_un_texto(lexico):
    texto = "huele a quemado y el motor está cantando"
    ids = {c.id for c in lexico.identificar(texto, "motor_electrico")}
    assert ids == {"EXP01", "EXP02"}


def test_cascabeleo_incluye_holgura_en_el_motor(lexico):
    assert "holgura_mecanica" in lexico.candidatos("esto está cascabeleando", "motor_electrico")


def test_no_confunde_bomba_con_banda_por_defecto(lexico):
    # "la banda esta golpeando" no es una expresión del léxico para la banda
    assert lexico.identificar("la banda está golpeando") == []


def test_coincidencia_difusa_es_opcional(lexico):
    texto = "esto esta cascabeliando"
    assert lexico.identificar(texto, "motor_electrico") == []
    c = lexico.identificar(texto, "motor_electrico", umbral_difuso=0.85)
    assert [x.id for x in c] == ["EXP04"]
    assert 0.85 <= c[0].puntaje < 1.0


def test_texto_vacio_o_sin_expresiones(lexico):
    assert lexico.identificar("") == []
    assert lexico.identificar("todo funciona perfecto") == []


def test_expresiones_de_sintoma(lexico):
    assert "la bomba está golpeando" in lexico.expresiones_de_sintoma("golpeteo_percibido")
    assert "el motor está cantando" in lexico.expresiones_de_sintoma("vibracion_hf_alta")
