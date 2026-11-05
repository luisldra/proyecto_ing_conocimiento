"""Configuración compartida de pytest."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def raiz() -> Path:
    """Raíz del repositorio."""
    return RAIZ


def java_disponible() -> bool:
    """HermiT (owlready2) necesita un JDK; ver ERRORES.md (ERR-008)."""
    return shutil.which("java") is not None


def pytest_collection_modifyitems(config, items):
    """Las pruebas marcadas @pytest.mark.java se omiten si no hay Java."""
    if java_disponible():
        return
    omitir = pytest.mark.skip(reason="Java no está instalado (ver ERR-008)")
    for item in items:
        if "java" in item.keywords:
            item.add_marker(omitir)
