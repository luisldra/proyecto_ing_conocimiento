"""Pruebas de la API y del servicio de diagnóstico (Fase 8). Requieren los modelos entrenados."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from metaltech.api.main import app
from metaltech.api.servicio import servicio
from metaltech.hybrid.fusion import humanizar
from metaltech.kb.base import RAIZ

pytestmark = pytest.mark.skipif(
    not (RAIZ / "checkpoints").exists(), reason="faltan los modelos: ejecute python -m metaltech.models.train"
)
CLIENTE = TestClient(app)


def test_salud_y_activos():
    r = CLIENTE.get("/health").json()
    assert r["estado"] == "ok" and len(r["modelos"]) == 6
    a = CLIENTE.get("/assets").json()
    assert a["bomba_centrifuga"]["modos"] and a["bomba_centrifuga"]["disponible"]
    assert CLIENTE.get("/assets/no_existe").status_code == 404


def test_base_de_conocimiento():
    reglas = CLIENTE.get("/kb/rules", params={"activo": "bomba_centrifuga", "modo": "cavitacion"}).json()
    assert reglas and all(r["entonces"] == "cavitacion" for r in reglas)
    ficha = CLIENTE.get("/kb/failure/cavitacion").json()
    assert ficha["reglas"] and ficha["sintomas"]
    assert CLIENTE.get("/kb/failure/no_existe").status_code == 404
    grafo = CLIENTE.get("/kb/ontology/graph", params={"activo": "bomba_centrifuga"}).json()
    assert grafo["nodos"] and grafo["aristas"]
    assert len(CLIENTE.get("/kb/lexicon").json()) == 10


def test_simular_falla_da_diagnostico_explicado():
    r = CLIENTE.post("/simulate", json={"activo": "bomba_centrifuga", "modo": "cavitacion",
                                        "texto": "la bomba está golpeando"}).json()
    d = r["diagnostico"]
    assert r["sistemas"]["M3"]["modo"] == d["modo"]
    assert d["modo"] == "cavitacion" and d["respaldo_reglas"] and d["reglas"][0]["premisas"]
    assert d["variables_influyentes"] and "R1" in d["texto"] and d["expresiones"]
    assert len(r["ventana"]["npsh_margen_ratio"]) == 36


def test_simular_operacion_normal():
    r = CLIENTE.post("/simulate", json={"activo": "motor_electrico", "explicar": False}).json()
    assert r["sistemas"]["M3"]["modo"] == "normal" and r["sistemas"]["M0"]["modo"] == "normal"


def test_diagnosticar_y_predecir_con_ventana_propia():
    ventana = servicio().construir_ventana("prensa_hidraulica", "sobrecalentamiento_aceite_hidraulico")
    ventana["temp_aceite_c"][5] = None  # dato faltante
    r = CLIENTE.post("/diagnose", json={"activo": "prensa_hidraulica", "ventana": ventana, "explicar": False})
    assert r.status_code == 200 and r.json()["diagnostico"]["modo"] != ""
    p = CLIENTE.post("/predict", json={"activo": "prensa_hidraulica", "ventana": ventana}).json()
    assert abs(sum(p["probabilidades"].values()) - 1) < 1e-4


@pytest.mark.parametrize("cambio, mensaje", [
    (lambda v: v.pop("temp_aceite_c"), "faltan sensores"),
    (lambda v: v.update(otro=[0.0] * 36), "desconocidos"),
    (lambda v: v.update(temp_aceite_c=[50.0] * 10), "36 lecturas"),
])
def test_ventanas_invalidas_dan_422(cambio, mensaje):
    ventana = servicio().construir_ventana("prensa_hidraulica")
    cambio(ventana)
    r = CLIENTE.post("/diagnose", json={"activo": "prensa_hidraulica", "ventana": ventana})
    assert r.status_code == 422 and mensaje in r.json()["detail"]


def test_modo_que_no_aplica_al_activo():
    r = CLIENTE.post("/simulate", json={"activo": "motor_electrico", "modo": "cavitacion"})
    assert r.status_code == 422


def test_reportes():
    assert CLIENTE.get("/reports/comparacion").json()
    assert CLIENTE.get("/reports/no_existe").status_code == 404


def test_acciones_legibles_aunque_no_haya_regla_disparada():
    assert humanizar("analisis_envolvente") == "Analisis envolvente"
    r = servicio().simular("bomba_centrifuga", "desgaste_rodamiento", avance=0.6, explicar=False)
    d = r["diagnostico"]
    if d["modo"] == "desgaste_rodamiento" and not d["respaldo_reglas"]:
        assert d["origen_accion"] == "reglas del modo" and "_" not in d["acciones"][0]
    assert all("_" not in a for a in d["acciones"])
