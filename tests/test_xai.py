"""Pruebas de la Fase 6: atribuciones, métricas de explicabilidad y texto de la alerta."""

from __future__ import annotations

import numpy as np
import pytest
import torch
from torch import nn

from metaltech.data.features import variables_agregadas
from metaltech.kb.base import cargar_base
from metaltech.xai.explain import (
    acierto_en_top_k,
    estabilidad,
    explicar_alerta,
    fidelidad,
    importancia_por_variable,
    variables_de_firma,
)

BASE = cargar_base()
T, V = 36, 4


class SoloVariable(nn.Module):
    """Modelo de juguete: la clase 1 depende solo de la variable ``j`` (media en el tiempo)."""

    def __init__(self, j: int, mlp: bool = False) -> None:
        super().__init__()
        self.j, self.mlp = j, mlp

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = x[:, self.j] if self.mlp else x[:, :, self.j].mean(dim=1)  # en el MLP, la media es la columna j
        return torch.stack([torch.zeros_like(z), 3 * z], dim=1)


@pytest.fixture
def X():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 0.1, (20, T, V)).astype(np.float32)
    x[:, :, 2] += 2.0
    return x


@pytest.mark.parametrize("arq", ["cnn1d", "mlp"])
def test_importancia_se_concentra_en_la_variable_usada(X, arq):
    modelo = SoloVariable(2, mlp=arq == "mlp")
    imp = importancia_por_variable(modelo, arq, X, np.ones(len(X), dtype=np.int64))
    assert imp.shape == (len(X), V)
    assert np.allclose(imp.sum(axis=1), 1)
    assert (imp.argmax(axis=1) == 2).all()


def test_mlp_suma_las_siete_estadisticas_de_cada_variable(X):
    assert variables_agregadas(X).shape[1] == 7 * V


def test_fidelidad_anular_lo_importante_baja_mas_que_el_azar(X):
    modelo = SoloVariable(2)
    y = np.ones(len(X), dtype=np.int64)
    imp = importancia_por_variable(modelo, "cnn1d", X, y)
    f = fidelidad(modelo, "cnn1d", X, y, imp, 1.0, 1, np.random.default_rng(0))
    assert f["caida_top_k"] > f["caida_azar_k"] and f["top_supera_azar_pct"] > 50


def test_estabilidad_es_alta_con_un_modelo_suave(X):
    modelo = SoloVariable(2)
    y = np.ones(len(X), dtype=np.int64)
    imp = importancia_por_variable(modelo, "cnn1d", X, y)
    assert estabilidad(modelo, "cnn1d", X, y, imp, np.random.default_rng(0)) > 0.95


class NoLineal(nn.Module):
    """La clase 1 depende de relu(x0) + x2²: con mucho ruido cambia el reparto entre ambas."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = torch.relu(x[:, :, 0].mean(dim=1)) + x[:, :, 2].mean(dim=1) ** 2
        return torch.stack([torch.zeros_like(z), z], dim=1)


def test_estabilidad_baja_con_ruido_fuerte_en_un_modelo_no_lineal(X):
    modelo, y = NoLineal(), np.ones(len(X), dtype=np.int64)
    imp = importancia_por_variable(modelo, "cnn1d", X, y)
    leve = estabilidad(modelo, "cnn1d", X, y, imp, np.random.default_rng(0), ruido=0.05)
    fuerte = estabilidad(modelo, "cnn1d", X, y, imp, np.random.default_rng(0), ruido=20.0)
    assert leve > 0.99 and fuerte < leve


def test_acierto_en_top_k_ignora_ventanas_sin_referencia():
    imp = np.array([[0.5, 0.3, 0.2, 0.0], [0.1, 0.2, 0.3, 0.4]])
    assert acierto_en_top_k(imp, [{0, 3}, set()], 2) == 0.5


def test_firma_viene_del_simulador():
    variables = list(BASE.activos["bomba_centrifuga"]["variables"])
    firma = {variables[i] for i in variables_de_firma("cavitacion", variables, BASE)}
    assert "npsh_margen_ratio" in firma and "fuga_sello_ml_h" not in firma
    assert variables_de_firma("normal", variables, BASE) == set()


def test_texto_de_la_alerta_une_modelo_reglas_y_tecnico():
    diag = {
        "modo": "cavitacion", "nombre": "Cavitación por NPSH disponible insuficiente", "puntaje": 0.91,
        "reglas": [{"id": "R13", "premisas": [{"variable": "npsh_margen_ratio", "valor": 1.05, "operador": "<=", "umbral": 1.1}]}],
        "expresiones": ["la bomba está golpeando"], "acciones": ["Revisar NPSH disponible"],
    }
    r = explicar_alerta(diag, {"npsh_margen_ratio": 0.6, "vib_hf_rel": 0.3, "caudal_pct": 0.1})
    assert r["variables_influyentes"][0] == {"variable": "npsh_margen_ratio", "peso": 0.6, "en_reglas": True}
    assert r["concordancia_reglas"] == pytest.approx(1 / 3)
    for fragmento in ("R13", "npsh_margen_ratio", "la bomba está golpeando", "Revisar NPSH"):
        assert fragmento in r["texto"]


def test_texto_avisa_cuando_ninguna_regla_respalda():
    diag = {"modo": "cavitacion", "nombre": "Cavitación", "puntaje": 0.7, "reglas": [], "expresiones": [], "acciones": []}
    r = explicar_alerta(diag, {"a": 0.5, "b": 0.5})
    assert "solo del modelo" in r["texto"] and r["concordancia_reglas"] is None
