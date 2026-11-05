"""Configuración compartida de pytest."""

from __future__ import annotations

from pathlib import Path

import pytest

from metaltech.kb.ontology import buscar_java

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def raiz() -> Path:
    """Raíz del repositorio."""
    return RAIZ


def java_disponible() -> bool:
    """HermiT (owlready2) necesita un JDK (PATH o .tools/jdk17); ver ERRORES.md (ERR-008)."""
    return buscar_java() is not None


def pytest_collection_modifyitems(config, items):
    """Las pruebas marcadas @pytest.mark.java se omiten si no hay Java."""
    if java_disponible():
        return
    omitir = pytest.mark.skip(reason="Java no está disponible; ejecute scripts/instalar_jdk.py (ERR-008)")
    for item in items:
        if "java" in item.keywords:
            item.add_marker(omitir)
