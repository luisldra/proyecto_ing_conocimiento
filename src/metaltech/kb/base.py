"""Carga de la base de conocimiento (fuente única de verdad: los YAML).

``cargar_base()`` lee ``configs/`` y ``knowledge/`` una sola vez y devuelve una
``BaseConocimiento`` con índices por id. Los módulos ``rules_engine``, ``lexicon`` y
``ontology`` trabajan sobre ella, de modo que ninguno repite datos del dominio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parents[3]
RUTA_ASSETS = RAIZ / "configs" / "assets.yaml"
RUTA_MODOS = RAIZ / "configs" / "failure_modes.yaml"
RUTA_FMEA = RAIZ / "knowledge" / "acquisition" / "fmea.yaml"
RUTA_REGLAS = RAIZ / "knowledge" / "rules" / "rules.yaml"
RUTA_LEXICO = RAIZ / "knowledge" / "lexicon" / "expresiones.yaml"


def _leer(ruta: Path) -> Any:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass(frozen=True)
class BaseConocimiento:
    """Contenido de los YAML de la Fase 1, indexado."""

    activos: dict[str, dict[str, Any]]
    sintomas: dict[str, dict[str, Any]]
    planta: dict[str, Any]
    modos: dict[str, dict[str, Any]]
    fmea: dict[str, list[dict[str, Any]]]
    reglas: list[dict[str, Any]]
    lexico: list[dict[str, Any]]
    muestreo_min: int = 10
    reglas_por_id: dict[str, dict[str, Any]] = field(default_factory=dict)

    def variable(self, activo: str, variable: str) -> dict[str, Any]:
        """Configuración de una variable de un tipo de activo."""
        return self.activos[activo]["variables"][variable]

    def componente_de_modo(self, modo: str, activo: str) -> str:
        """Componente afectado por un modo en un activo (con ``componentes_por_activo``)."""
        m = self.modos[modo]
        return m.get("componentes_por_activo", {}).get(activo, m["componente"])

    def reglas_de(self, activo: str) -> list[dict[str, Any]]:
        return [r for r in self.reglas if r["activo"] == activo]


@lru_cache(maxsize=1)
def cargar_base() -> BaseConocimiento:
    """Lee los YAML una vez (resultado en caché; tratarlo como solo lectura)."""
    assets = _leer(RUTA_ASSETS)
    fmea = {k: v for k, v in _leer(RUTA_FMEA).items() if isinstance(v, list)}
    reglas = _leer(RUTA_REGLAS)
    return BaseConocimiento(
        activos=assets["activos"],
        sintomas=assets["sintomas"],
        planta=assets.get("planta", {}),
        modos=_leer(RUTA_MODOS)["modos_falla"],
        fmea=fmea,
        reglas=reglas,
        lexico=_leer(RUTA_LEXICO),
        muestreo_min=assets.get("muestreo_min", 10),
        reglas_por_id={r["id"]: r for r in reglas},
    )


# ---------------------------------------------------------------------------------------
# Utilidades sobre variables y umbrales (las comparte el motor y, luego, el generador)
# ---------------------------------------------------------------------------------------
def valor_nominal(variable: dict[str, Any]) -> float:
    """Punto medio del rango nominal (operación sana)."""
    lo, hi = variable["nominal"]
    return (lo + hi) / 2


def valor_final(variable: dict[str, Any], cambio: dict[str, Any]) -> float:
    """Valor al final de la degradación según ``cambio`` de ``failure_modes.yaml``."""
    nominal = valor_nominal(variable)
    tipo, v = cambio["tipo"], cambio["valor"]
    if tipo == "valor":
        return float(v)
    if tipo == "delta":
        return nominal + v
    if tipo == "factor":
        return nominal * v
    if tipo == "frac_alerta":
        return variable["alerta"] * v
    raise ValueError(f"tipo de cambio desconocido: {tipo}")
