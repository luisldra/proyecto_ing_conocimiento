"""Léxico: de las expresiones coloquiales de los técnicos a síntomas formales.

Ejemplo: ``"la bomba está golpeando"`` -> síntoma percibido ``golpeteo_percibido`` y modos
candidatos ``cavitacion`` (fc_max 0.6), ``obstruccion_bomba`` (0.4)...

Criterios (D-038): la expresión es ambigua, así que solo aporta un síntoma percibido y una
lista de candidatos con ``fc_max`` <= 0.6; la desambiguación la hacen las reglas con
síntomas medidos. La coincidencia es exacta sobre el texto normalizado (minúsculas, sin
tildes ni puntuación). La coincidencia difusa es opcional (``umbral_difuso``) porque con
frases cortas confunde p. ej. "bomba" con "banda".
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from metaltech.kb.base import BaseConocimiento, cargar_base


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes ni signos; espacios colapsados."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return re.sub(r"[^a-z0-9]+", " ", sin_tildes.lower()).strip()


@dataclass(frozen=True)
class Coincidencia:
    """Una expresión del léxico encontrada en el texto de un técnico."""

    id: str
    expresion: str
    forma: str  # variante o expresión canónica que coincidió
    puntaje: float  # 1.0 = coincidencia exacta
    sintoma_percibido: str
    sintomas_formales: tuple[str, ...]
    candidatos: dict[str, float] = field(default_factory=dict)  # modo -> fc_max
    fisica: str = ""


class Lexico:
    """Índice de expresiones coloquiales (``knowledge/lexicon/expresiones.yaml``)."""

    def __init__(self, base: BaseConocimiento | None = None) -> None:
        self.base = base or cargar_base()
        self._formas: list[tuple[str, str, dict[str, Any]]] = []  # (normalizada, original, exp)
        for exp in self.base.lexico:
            for forma in [exp["expresion"], *exp.get("variantes", [])]:
                self._formas.append((normalizar(forma), forma, exp))

    # ------------------------------------------------------------------------------
    def identificar(
        self, texto: str, activo: str | None = None, umbral_difuso: float | None = None
    ) -> list[Coincidencia]:
        """Expresiones encontradas en ``texto``, de mayor a menor puntaje.

        ``activo`` filtra las expresiones que aplican a ese tipo de activo y deja solo los
        modos candidatos que existen en él. ``umbral_difuso`` (p. ej. 0.9) activa la
        tolerancia a errores de digitación.
        """
        norm = normalizar(texto)
        if not norm:
            return []
        mejores: dict[str, Coincidencia] = {}
        for forma_norm, forma, exp in self._formas:
            if activo is not None and activo not in exp["activos"]:
                continue
            puntaje = self._puntaje(norm, forma_norm, umbral_difuso)
            if puntaje is None:
                continue
            previa = mejores.get(exp["id"])
            if previa is None or puntaje > previa.puntaje:
                mejores[exp["id"]] = self._coincidencia(exp, forma, puntaje, activo)
        return sorted(mejores.values(), key=lambda c: (-c.puntaje, c.id))

    def sintomas_percibidos(
        self, texto: str, activo: str | None = None, umbral_difuso: float | None = None
    ) -> list[str]:
        """Síntomas percibidos (sin repetir) que activa el texto."""
        vistos: list[str] = []
        for c in self.identificar(texto, activo, umbral_difuso):
            if c.sintoma_percibido not in vistos:
                vistos.append(c.sintoma_percibido)
        return vistos

    def candidatos(
        self, texto: str, activo: str | None = None, umbral_difuso: float | None = None
    ) -> dict[str, float]:
        """Modos de falla candidatos con su ``fc_max`` (el máximo entre expresiones)."""
        resultado: dict[str, float] = {}
        for c in self.identificar(texto, activo, umbral_difuso):
            for modo, fc in c.candidatos.items():
                resultado[modo] = max(resultado.get(modo, 0.0), fc)
        return dict(sorted(resultado.items(), key=lambda kv: -kv[1]))

    def expresiones_de_sintoma(self, sintoma: str) -> list[str]:
        """Expresiones canónicas que producen o se refieren a un síntoma."""
        return [
            e["expresion"]
            for e in self.base.lexico
            if sintoma == e["sintoma_percibido"] or sintoma in e["sintomas_formales"]
        ]

    # ------------------------------------------------------------------------------
    @staticmethod
    def _puntaje(texto: str, forma: str, umbral_difuso: float | None) -> float | None:
        if not forma:
            return None
        if f" {forma} " in f" {texto} ":
            return 1.0
        if umbral_difuso is None:
            return None
        palabras_t, n = texto.split(), len(forma.split())
        mejor = 0.0
        for i in range(max(1, len(palabras_t) - n + 1)):
            ventana = " ".join(palabras_t[i : i + n])
            mejor = max(mejor, SequenceMatcher(None, ventana, forma).ratio())
        return mejor if mejor >= umbral_difuso else None

    def _coincidencia(
        self, exp: dict[str, Any], forma: str, puntaje: float, activo: str | None
    ) -> Coincidencia:
        candidatos = {
            c["id"]: c["fc_max"]
            for c in exp["modos_falla_candidatos"]
            if activo is None or activo in self.base.modos[c["id"]]["activos"]
        }
        return Coincidencia(
            id=exp["id"],
            expresion=exp["expresion"],
            forma=forma,
            puntaje=round(puntaje, 3),
            sintoma_percibido=exp["sintoma_percibido"],
            sintomas_formales=tuple(exp["sintomas_formales"]),
            candidatos=candidatos,
            fisica=" ".join(str(exp.get("fisica", "")).split()),
        )
