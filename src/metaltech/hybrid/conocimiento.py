"""Evaluación del sistema experto sobre cada ventana (Fase 5).

Para cada ventana se corre el motor de reglas con el último paso de los sensores, la
línea base de puesta en marcha de la unidad y la observación del técnico de las últimas
horas, si la hay. El resultado alimenta M0, M2 y M3. Decisiones en D-056.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from metaltech.data.features import Ventanas
from metaltech.data.generator import PASOS_POR_HORA
from metaltech.kb.base import RUTA_ASSETS, RUTA_LEXICO, RUTA_REGLAS, BaseConocimiento
from metaltech.kb.rules_engine import MotorReglas

DIAS_PUESTA_EN_MARCHA = 14


@dataclass
class Conocimiento:
    """``fc``: [N, C] certeza por clase (columna 0 = 1 - FC máximo). ``sintomas``: [N, S] grados."""

    fc: np.ndarray
    sintomas: np.ndarray
    nombres_sintomas: list[str]

    def subconjunto(self, mascara: np.ndarray) -> Conocimiento:
        return Conocimiento(self.fc[mascara], self.sintomas[mascara], self.nombres_sintomas)

    @property
    def vector(self) -> np.ndarray:
        """Entradas adicionales de M2: certezas de falla y grados de síntoma, en [0, 1]."""
        return np.concatenate([self.fc[:, 1:], self.sintomas], axis=1).astype(np.float32)


def sintomas_de(activo: str, base: BaseConocimiento) -> list[str]:
    """Síntomas medibles con las variables del activo y síntomas percibidos de su léxico."""
    variables = base.activos[activo]["variables"]
    percibidos = {e["sintoma_percibido"] for e in base.lexico if activo in e["activos"]}
    return [
        s for s, d in base.sintomas.items()
        if (d["tipo"] == "medido" and d["variable"] in variables) or s in percibidos
    ]


def lineas_base(df: pd.DataFrame, variables: list[str]) -> dict[str, dict[str, float]]:
    """Mediana de los primeros días de cada unidad, como se registraría al ponerla en marcha.

    Solo usa sensores (no etiquetas) y existe también para la unidad reservada.
    """
    lineas = {}
    for unidad, g in df.groupby("unidad", observed=True):
        inicio = g[g["ts"] < g["ts"].min() + pd.Timedelta(days=DIAS_PUESTA_EN_MARCHA)]
        lineas[str(unidad)] = {v: float(inicio[v].median()) for v in variables}
    return lineas


def textos_por_ventana(obs: pd.DataFrame, unidad: np.ndarray, ts: np.ndarray, horas: float) -> list[str | None]:
    """Expresiones de técnicos registradas en las ``horas`` previas al fin de cada ventana."""
    textos: list[str | None] = [None] * len(ts)
    fin = pd.to_datetime(ts)
    for u, g in obs.groupby("unidad"):
        idx = np.flatnonzero(unidad == u)
        if idx.size == 0:
            continue
        tiempos = g["ts"].to_numpy()
        for i in idx:
            mascara = (tiempos > fin[i] - pd.Timedelta(hours=horas)) & (tiempos <= fin[i])
            if mascara.any():
                textos[i] = " ".join(g["texto"].to_numpy()[mascara])
    return textos


def evaluar(
    ventanas: Ventanas, activo: str, clases: list[str], variables: list[str], base: BaseConocimiento,
    lineas: dict[str, dict[str, float]], textos: list[str | None], motor: MotorReglas | None = None,
) -> Conocimiento:
    motor = motor or MotorReglas(base)
    nombres = sintomas_de(activo, base)
    columna = {s: j for j, s in enumerate(nombres)}
    indice = {c: k for k, c in enumerate(clases)}
    fc = np.zeros((len(ventanas), len(clases)), dtype=np.float32)
    grados = np.zeros((len(ventanas), len(nombres)), dtype=np.float32)
    for i in range(len(ventanas)):
        valores = dict(zip(variables, ventanas.crudo[i].astype(float), strict=True))
        d = motor.diagnosticar(activo, valores, lineas[str(ventanas.unidad[i])], texto_tecnico=textos[i])
        for c in d.conclusiones:
            fc[i, indice[c.modo]] = c.fc
        for s, sa in d.sintomas.items():
            if s in columna:
                grados[i, columna[s]] = sa.grado
    fc[:, 0] = 1.0 - fc[:, 1:].max(axis=1, initial=0.0)
    return Conocimiento(fc, grados, nombres)


def _huella(ventanas: Ventanas) -> str:
    h = hashlib.sha256()
    for ruta in (RUTA_ASSETS, RUTA_REGLAS, RUTA_LEXICO):
        h.update(ruta.read_bytes())
    h.update(np.ascontiguousarray(ventanas.crudo).tobytes())
    h.update(ventanas.unidad.astype(str).tobytes())
    return h.hexdigest()


def cargar_o_calcular(
    activo: str, datos: Path, ventanas: Ventanas, clases: list[str], variables: list[str],
    base: BaseConocimiento, ventana_pasos: int, nombre: str,
) -> Conocimiento:
    """Evalúa el motor una vez y guarda el resultado; se recalcula si cambian reglas o datos."""
    cache = datos / f"conocimiento_{activo}_{nombre}.npz"
    huella = _huella(ventanas)
    if cache.exists():
        z = np.load(cache, allow_pickle=False)
        if str(z["huella"]) == huella:
            return Conocimiento(z["fc"], z["sintomas"], list(z["nombres"]))
    df = pd.read_parquet(datos / f"{activo}.parquet", columns=["ts", "unidad", *variables])
    obs = pd.read_parquet(datos / "observaciones.parquet")
    obs = obs[obs["activo"] == activo]
    textos = textos_por_ventana(obs, ventanas.unidad, ventanas.ts, ventana_pasos / PASOS_POR_HORA)
    k = evaluar(ventanas, activo, clases, variables, base, lineas_base(df, variables), textos)
    np.savez_compressed(cache, fc=k.fc, sintomas=k.sintomas, nombres=np.array(k.nombres_sintomas), huella=huella)
    return k
