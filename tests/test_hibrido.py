"""Pruebas de la Fase 5: conocimiento por ventana, M2 y fusión M3."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch
import yaml

from metaltech.data.features import Ventanas, construir_ventanas
from metaltech.data.generator import ConfigSimulador, simular
from metaltech.hybrid.conocimiento import evaluar, lineas_base, sintomas_de, textos_por_ventana
from metaltech.hybrid.fusion import (
    ParametrosFusion,
    diagnostico_hibrido,
    elegir_fusion,
    fusionar,
    proba_m0,
)
from metaltech.kb.base import RAIZ, cargar_base, valor_nominal
from metaltech.kb.rules_engine import MotorReglas
from metaltech.models.evaluate import falsas_alarmas
from metaltech.models.train import crear_modelo, entradas

BASE = cargar_base()
MOTOR = MotorReglas(BASE)
RUTA = RAIZ / "configs" / "train.yaml"
with open(RUTA, encoding="utf-8") as f:
    CFG = yaml.safe_load(f)


@pytest.fixture(scope="module")
def sim():
    return simular(ConfigSimulador.desde_yaml(RUTA, meses=8), semilla=42)


@pytest.fixture(scope="module")
def ventanas_cnc(sim):
    return construir_ventanas(sim.series["centro_cnc"], "centro_cnc", BASE, CFG["datos"]["ventana_pasos"], CFG["datos"]["paso_ventana"])


# ----------------------------------------------------------------------------------------
# Conocimiento por ventana
# ----------------------------------------------------------------------------------------
def test_las_reglas_ven_sensores_sin_normalizar(ventanas_cnc, sim):
    v, variables, _ = ventanas_cnc
    df = sim.series["centro_cnc"].set_index(["unidad", "ts"])
    for i in range(0, len(v), 997):
        fila = df.loc[(v.unidad[i], v.ts[i]), variables].to_numpy(dtype=float)
        conocidos = ~np.isnan(fila)
        assert np.allclose(v.crudo[i][conocidos], fila[conocidos], atol=1e-4)


def test_linea_base_solo_usa_los_primeros_dias(sim):
    df = sim.series["centro_cnc"]
    variables = list(BASE.activos["centro_cnc"]["variables"])
    lineas = lineas_base(df, variables)
    assert set(lineas) == set(df["unidad"].astype(str).unique())
    u = next(iter(lineas))
    primeros = df[(df["unidad"] == u) & (df["ts"] < df["ts"].min() + pd.Timedelta(days=14))]
    assert lineas[u]["temp_husillo_c"] == pytest.approx(primeros["temp_husillo_c"].median())


def test_textos_solo_de_la_unidad_y_las_horas_previas():
    obs = pd.DataFrame({"unidad": ["a", "a", "b"], "ts": pd.to_datetime(["2024-01-01 05:00", "2024-01-02 00:00", "2024-01-01 05:00"]),
                        "texto": ["la bomba está golpeando", "otra", "de otra unidad"]})
    ts = np.array(pd.to_datetime(["2024-01-01 06:00", "2024-01-01 12:00"]), dtype="datetime64[ns]")
    assert textos_por_ventana(obs, np.array(["a", "a"]), ts, 6) == ["la bomba está golpeando", None]


def test_evaluar_coincide_con_el_motor(ventanas_cnc, sim):
    v, variables, clases = ventanas_cnc
    muestra = v.subconjunto(np.arange(len(v)) % 300 == 0)
    lineas = lineas_base(sim.series["centro_cnc"], variables)
    k = evaluar(muestra, "centro_cnc", clases, variables, BASE, lineas, [None] * len(muestra), MOTOR)
    for i in range(len(muestra)):
        d = MOTOR.diagnosticar("centro_cnc", dict(zip(variables, muestra.crudo[i].astype(float), strict=True)), lineas[muestra.unidad[i]])
        esperado = {c.modo: c.fc for c in d.conclusiones}
        for j, c in enumerate(clases[1:], 1):
            assert k.fc[i, j] == pytest.approx(esperado.get(c, 0.0))
    assert np.allclose(k.fc[:, 0], 1 - k.fc[:, 1:].max(axis=1))
    assert k.vector.shape == (len(muestra), len(clases) - 1 + len(sintomas_de("centro_cnc", BASE)))


def test_sintomas_del_activo_incluyen_percibidos_de_su_lexico():
    s = sintomas_de("bomba_centrifuga", BASE)
    assert "margen_npsh_bajo" in s
    assert any(BASE.sintomas[x]["tipo"] == "percibido" for x in s)
    assert all(BASE.sintomas[x]["tipo"] == "percibido" or BASE.sintomas[x]["variable"] in BASE.activos["bomba_centrifuga"]["variables"] for x in s)


# ----------------------------------------------------------------------------------------
# M0 y M3
# ----------------------------------------------------------------------------------------
FC = np.array([[1.0, 0.0, 0.0], [0.2, 0.8, 0.0], [0.6, 0.0, 0.4]], dtype=np.float32)


def test_m0_sin_reglas_es_normal_y_con_reglas_es_la_falla():
    assert proba_m0(FC).argmax(1).tolist() == [0, 1, 0]


def test_fusion_con_alfa_extremos_reproduce_m0_y_m1():
    p = np.array([[0.1, 0.1, 0.8], [0.7, 0.2, 0.1], [0.2, 0.3, 0.5]])
    assert np.allclose(fusionar(p, FC, ParametrosFusion(1.0, False, 0.3)), p)
    assert np.allclose(fusionar(p, FC, ParametrosFusion(0.0, False, 0.3)), proba_m0(FC))


def test_veto_quita_alertas_sin_respaldo_de_reglas():
    p = np.array([[0.1, 0.1, 0.8], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]])
    pred = fusionar(p, FC, ParametrosFusion(0.9, True, 0.3)).argmax(1)
    assert pred.tolist() == [0, 1, 2]  # la fila 0 no tiene reglas; la 2 tiene FC 0.4 >= 0.3


def test_elegir_fusion_usa_validacion_y_devuelve_la_rejilla():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 3, 300)
    p = np.eye(3)[y] * 0.6 + 0.4 / 3
    par, rejilla = elegir_fusion(p, np.tile(FC[0], (300, 1)), y, [0.3, 0.7], 0.3)
    assert len(rejilla) == 4 and par.alfa in (0.3, 0.7)


def test_falsas_alarmas_separa_confusores():
    y = np.array([0, 0, 0, 0])
    proba = np.array([[0, 1], [1, 0], [0, 1], [0, 1]], dtype=float)
    fa = falsas_alarmas(y, proba, np.array([False, False, True, True]))
    assert fa["falsa_alarma_sin_confusor"] == 0.5 and fa["falsa_alarma_con_confusor"] == 1.0


def test_diagnostico_hibrido_explica_con_reglas_causas_y_acciones():
    activo = "bomba_centrifuga"
    clases = ["normal", *sorted(m for m, d in BASE.modos.items() if activo in d["activos"])]
    vals = {v: valor_nominal(c) for v, c in BASE.activos[activo]["variables"].items()}
    vals.update(npsh_margen_ratio=1.0, vib_hf_rel=4.2, caudal_cv_pct=8, presion_descarga_pct=88)
    d = MOTOR.diagnosticar(activo, vals, texto_tecnico="la bomba está golpeando")
    p = np.full(len(clases), 0.02)
    p[clases.index("cavitacion")] = 1 - 0.02 * (len(clases) - 1)
    r = diagnostico_hibrido(activo, clases, p, d, ParametrosFusion(0.5, True, 0.3), BASE)
    assert r["modo"] == "cavitacion" and r["respaldo_reglas"]
    assert r["reglas"] and r["reglas"][0]["premisas"] and r["causas"] and r["acciones"]
    assert r["expresiones"] == ["la bomba está golpeando"]


# ----------------------------------------------------------------------------------------
# M2
# ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("arq", ["mlp", "cnn1d", "lstm"])
def test_m2_recibe_sensores_y_conocimiento(arq):
    v = Ventanas(np.zeros((4, 36, 5), dtype=np.float32), np.zeros(4, dtype=np.int64), np.array(["u"] * 4),
                 np.arange(4), np.array(["train"] * 4), extra=np.ones((4, 7), dtype=np.float32))
    modelo = crear_modelo(arq, 5, 36, 3, CFG, extra=7)
    x = entradas(arq, v)
    assert len(x) == 2 and modelo(*x).shape == (4, 3)


def test_subconjunto_conserva_el_conocimiento():
    v = Ventanas(np.zeros((3, 2, 1), dtype=np.float32), np.arange(3), np.array(["u"] * 3), np.arange(3),
                 np.array(["train"] * 3), extra=np.arange(6, dtype=np.float32).reshape(3, 2))
    assert v.subconjunto(np.array([False, True, True])).extra.tolist() == [[2, 3], [4, 5]]
    assert torch.is_tensor(entradas("mlp", v)[1])
