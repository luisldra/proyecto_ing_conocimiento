"""Pruebas de ventanas y modelos de la Fase 4."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch
import yaml

from metaltech.data.features import (
    Ventanas,
    balancear_entrenamiento,
    clases_de,
    construir_ventanas,
    imputar,
    normalizar,
    preparar,
    variables_agregadas,
)
from metaltech.data.generator import ConfigSimulador, simular
from metaltech.kb.base import RAIZ, cargar_base
from metaltech.models.evaluate import metricas
from metaltech.models.train import (
    ARQUITECTURAS,
    ajustar_temperatura,
    crear_modelo,
    entradas_de,
    entrenar,
    perdida_focal,
    pesos_de_clase,
)

BASE = cargar_base()
RUTA = RAIZ / "configs" / "train.yaml"
with open(RUTA, encoding="utf-8") as f:
    CFG = yaml.safe_load(f)
VENTANA, PASO = CFG["datos"]["ventana_pasos"], CFG["datos"]["paso_ventana"]


@pytest.fixture(scope="module")
def serie():
    return simular(ConfigSimulador.desde_yaml(RUTA, meses=8), semilla=42).series["centro_cnc"]


@pytest.fixture(scope="module")
def ventanas(serie):
    return construir_ventanas(serie, "centro_cnc", BASE, VENTANA, PASO)


# ----------------------------------------------------------------------------------------
# Sin fuga de información
# ----------------------------------------------------------------------------------------
def test_solo_los_sensores_entran_al_modelo(ventanas):
    _, variables, _ = ventanas
    assert variables == list(BASE.activos["centro_cnc"]["variables"])
    assert not {"estado", "modo_activo", "t_degradacion", "horas_a_falla", "confusor", "etiqueta"} & set(variables)


def test_imputar_no_mira_el_futuro():
    df = pd.DataFrame({"a": [np.nan, 1.0, np.nan, 3.0]})
    assert imputar(df, ["a"], {"a": 9.0}).ravel().tolist() == [9.0, 1.0, 1.0, 3.0]


def test_cada_ventana_cae_en_una_sola_particion(ventanas, serie):
    v, _, _ = ventanas
    assert set(np.unique(v.particion)) == {"train", "val", "test"}
    for unidad in np.unique(v.unidad):
        filas = serie[serie["unidad"] == unidad].set_index("ts")
        mascara = v.unidad == unidad
        for ts, p in zip(v.ts[mascara][::50], v.particion[mascara][::50], strict=True):
            tramo = filas.loc[:ts].tail(VENTANA)
            assert set(tramo["particion"].astype(str)) == {p}


def test_las_particiones_no_se_solapan_en_el_tiempo(ventanas):
    v, _, _ = ventanas
    assert v.ts[v.particion == "train"].max() < v.ts[v.particion == "val"].min()
    assert v.ts[v.particion == "val"].max() < v.ts[v.particion == "test"].min()


def test_ninguna_ventana_incluye_reparacion(ventanas, serie):
    v, _, _ = ventanas
    assert np.isfinite(v.X).all()
    assert len(v) < len(serie) / PASO


def test_los_fallos_de_un_solo_paso_quedan_representados(ventanas, serie):
    v, _, clases = ventanas
    colisiones = int(((serie["estado"] == "falla") & (serie["modo_activo"] == "colision_husillo")).sum())
    assert colisiones > 0
    assert (v.y == clases.index("colision_husillo")).sum() >= 0.8 * colisiones


def test_normalizacion_usa_solo_entrenamiento():
    X = np.ones((4, 2, 1), dtype=np.float32)
    X[2:] = 100.0
    v = Ventanas(X, np.zeros(4, dtype=np.int64), np.array(["u"] * 4), np.arange(4), np.array(["train", "train", "test", "test"]))
    media, _ = normalizar(v)
    assert media[0] == pytest.approx(1.0)


def test_balanceo_conserva_todas_las_fallas_y_no_toca_otra_cosa():
    y = np.array([0] * 100 + [1] * 3)
    v = Ventanas(np.zeros((103, 2, 1), dtype=np.float32), y, np.array(["u"] * 103), np.arange(103), np.array(["train"] * 103))
    b = balancear_entrenamiento(v, 2, np.random.default_rng(0))
    assert (b.y == 1).sum() == 3 and (b.y == 0).sum() == 6


# ----------------------------------------------------------------------------------------
# Variables agregadas y modelos
# ----------------------------------------------------------------------------------------
def test_variables_agregadas_recuperan_tendencia_y_ultimo_valor():
    X = np.arange(10, dtype=np.float32)[None, :, None]
    a = variables_agregadas(X)[0]
    assert a[0] == pytest.approx(4.5) and a[3] == pytest.approx(1.0) and a[4] == 9 and a[5] == 0 and a[6] == 9


@pytest.mark.parametrize("arq", ARQUITECTURAS)
def test_salida_tiene_una_columna_por_clase(arq):
    modelo = crear_modelo(arq, 5, VENTANA, 4, CFG)
    x = entradas_de(arq, np.zeros((3, VENTANA, 5), dtype=np.float32))
    assert modelo(x).shape == (3, 4)


def test_clases_empiezan_por_normal_y_son_las_del_activo():
    clases = clases_de("centro_cnc", BASE)
    assert clases[0] == "normal"
    assert set(clases[1:]) == {m for m, d in BASE.modos.items() if "centro_cnc" in d["activos"]}


def test_perdida_focal_atenua_los_ejemplos_faciles():
    y, pesos = torch.tensor([0]), torch.ones(2)
    assert perdida_focal(torch.tensor([[5.0, 0.0]]), y, pesos, 2.0) < perdida_focal(torch.tensor([[0.5, 0.0]]), y, pesos, 2.0)


def test_pesos_favorecen_la_clase_rara():
    p = pesos_de_clase(np.array([0] * 100 + [1] * 4), 3)
    assert p[1] > p[0] and p[2] == 0


def test_temperatura_no_cambia_la_prediccion():
    torch.manual_seed(0)
    logits = torch.randn(200, 3) * 8
    y = torch.randint(0, 3, (200,))
    t = ajustar_temperatura(logits, y)
    assert t > 1  # logits sobreconfiados sobre etiquetas aleatorias
    assert torch.equal((logits / t).argmax(1), logits.argmax(1))


def test_metricas_macro_y_falsa_alarma():
    y = np.array([0, 0, 1, 1])
    proba = np.array([[0.9, 0.1], [0.1, 0.9], [0.1, 0.9], [0.1, 0.9]])
    m = metricas(y, proba)
    assert m["falsa_alarma"] == 0.5 and m["alerta_correcta_binaria"] == 1.0


@pytest.mark.lento
@pytest.mark.parametrize("arq", ARQUITECTURAS)
def test_aprende_un_problema_separable(arq):
    rng = np.random.default_rng(0)
    n = 900
    y = np.array([0, 1, 2] * (n // 3))
    X = rng.normal(0, 0.3, (n, VENTANA, 3)).astype(np.float32)
    for c in (1, 2):
        X[y == c, :, c] += 2.5
    particion = np.array(["train", "train", "val"] * (n // 3))
    # 'val' debe tener de todas las clases: se baraja el reparto entre las filas.
    particion = rng.permutation(particion)
    v = Ventanas(X, y, np.array(["u"] * n), np.arange(n), particion)
    datos = preparar("sintetico", v, ["a", "b", "c"], ["normal", "x", "z"])
    cfg = {**CFG, "entrenamiento": {**CFG["entrenamiento"], "epocas": 15, "batch": 64}}
    assert entrenar(datos, arq, 42, cfg).f1_val > 0.9
