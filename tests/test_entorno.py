"""Pruebas de humo de la Fase 0: entorno, estructura y configuración."""

from __future__ import annotations

import importlib

import pytest
import yaml

MODULOS = ["numpy", "pandas", "sklearn", "torch", "owlready2", "fastapi", "streamlit", "yaml"]
SUBPAQUETES = ["data", "kb", "models", "hybrid", "xai", "metrics", "api", "dashboard"]


@pytest.mark.parametrize("modulo", MODULOS)
def test_dependencia_importable(modulo):
    importlib.import_module(modulo)


def test_paquete_metaltech():
    import metaltech

    assert metaltech.__version__


@pytest.mark.parametrize("sub", SUBPAQUETES)
def test_subpaquete_existe(sub):
    importlib.import_module(f"metaltech.{sub}")


@pytest.mark.parametrize(
    "ruta",
    ["configs/assets.yaml", "configs/failure_modes.yaml", "configs/train.yaml",
     "knowledge/rules/rules.yaml", "knowledge/lexicon/expresiones.yaml",
     "knowledge/acquisition/fmea.yaml"],
)
def test_yaml_se_carga(raiz, ruta):
    with open(raiz / ruta, encoding="utf-8") as f:
        assert yaml.safe_load(f) is not None


def test_train_yaml_coherente(raiz):
    cfg = yaml.safe_load((raiz / "configs/train.yaml").read_text(encoding="utf-8"))
    assert sum(cfg["datos"]["particion"].values()) == pytest.approx(1.0)
    assert cfg["semilla_principal"] in cfg["semillas"]
    assets = yaml.safe_load((raiz / "configs/assets.yaml").read_text(encoding="utf-8"))
    assert cfg["datos"]["muestreo_min"] == assets["muestreo_min"]
