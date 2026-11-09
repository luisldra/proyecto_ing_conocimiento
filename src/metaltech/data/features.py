"""Ventanas temporales y variables agregadas para los modelos (Fase 4).

Solo los sensores entran al modelo: ``estado``, ``modo_activo``, ``t_degradacion``,
``horas_a_falla`` y ``confusor`` son verdad de terreno. Decisiones en D-053.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from metaltech.data.generator import SIN_MODO
from metaltech.kb.base import BaseConocimiento, cargar_base, valor_nominal

PARTICIONES = ("train", "val", "test", "test_unidad")
RECORTE_Z = 10.0
NOMBRES_AGREGADOS = ("media", "rms", "curtosis", "pendiente", "maximo", "minimo", "ultimo")


@dataclass
class Ventanas:
    """Ventanas de una o varias unidades: ``X`` tiene forma [N, T, V]."""

    X: np.ndarray
    y: np.ndarray
    unidad: np.ndarray
    ts: np.ndarray
    particion: np.ndarray
    gris: np.ndarray | None = None  # degradación en curso a más de H de la falla (D-054)
    modo: np.ndarray | None = None  # índice del modo que se está degradando (0 si no hay)
    horas_a_falla: np.ndarray | None = None

    def __post_init__(self) -> None:
        n = len(self.y)
        self.gris = np.zeros(n, dtype=bool) if self.gris is None else self.gris
        self.modo = np.zeros(n, dtype=np.int64) if self.modo is None else self.modo
        self.horas_a_falla = np.full(n, np.nan) if self.horas_a_falla is None else self.horas_a_falla

    def __len__(self) -> int:
        return len(self.y)

    def subconjunto(self, mascara: np.ndarray) -> Ventanas:
        return Ventanas(*(getattr(self, f.name)[mascara] for f in fields(self)))

    def sin_grises(self) -> Ventanas:
        """Ventanas con etiqueta inequívoca: las que se entrenan y puntúan."""
        return self.subconjunto(~self.gris)


@dataclass
class DatosActivo:
    """Ventanas normalizadas por partición, con los estadísticos del conjunto de entrenamiento."""

    activo: str
    variables: list[str]
    clases: list[str]
    media: np.ndarray
    desviacion: np.ndarray
    particiones: dict[str, Ventanas]


def clases_de(activo: str, base: BaseConocimiento) -> list[str]:
    return [SIN_MODO, *sorted(m for m, d in base.modos.items() if activo in d["activos"])]


def imputar(df: pd.DataFrame, variables: list[str], nominales: dict[str, float]) -> np.ndarray:
    """Último valor conocido de la unidad; si no existe, el nominal. No mira el futuro."""
    return df[variables].ffill().fillna(nominales).to_numpy(dtype=np.float32)


def _ventanas_unidad(
    df: pd.DataFrame, variables: list[str], nominales: dict[str, float], indices: dict[str, int],
    ventana: int, paso: int,
) -> Ventanas | None:
    n = len(df)
    if n < ventana:
        return None
    # Una falla de un solo paso caería entre dos ventanas: se agrega el instante de la falla.
    fallas = np.flatnonzero(df["estado"].to_numpy(dtype=object) == "falla")
    fines = np.union1d(np.arange(ventana - 1, n, paso), fallas[fallas >= ventana - 1])
    particion = df["particion"].astype(str).to_numpy()
    codigo = pd.Categorical(particion, categories=[*PARTICIONES, "purga"]).codes
    en_reparacion = (df["estado"].astype(str).to_numpy() == "reparacion").astype(np.int8)
    vista_c = sliding_window_view(codigo, ventana)[fines - ventana + 1]
    vista_r = sliding_window_view(en_reparacion, ventana)[fines - ventana + 1]
    validos = (vista_c.min(1) == vista_c.max(1)) & (vista_c[:, 0] < len(PARTICIONES)) & (vista_r.max(1) == 0)
    fines = fines[validos]
    if fines.size == 0:
        return None
    x = imputar(df, variables, nominales)
    etiqueta = df["etiqueta"].astype(str).to_numpy()
    y = np.empty(fines.size, dtype=np.int64)
    for k, fin in enumerate(fines):  # la etiqueta más reciente desde la ventana anterior
        recientes = etiqueta[max(fin - paso + 1, 0) : fin + 1]
        positivas = recientes[recientes != SIN_MODO]
        y[k] = indices[positivas[-1] if positivas.size else SIN_MODO]
    estado = df["estado"].astype(str).to_numpy()[fines]
    modo_activo = df["modo_activo"].astype(str).to_numpy()[fines]
    return Ventanas(
        np.stack([x[f - ventana + 1 : f + 1] for f in fines]), y,
        df["unidad"].astype(str).to_numpy()[fines], df["ts"].to_numpy()[fines], particion[fines],
        (estado == "degradacion") & (y == 0),
        np.array([indices[m] for m in modo_activo], dtype=np.int64),
        df["horas_a_falla"].to_numpy(dtype=np.float32)[fines],
    )


def construir_ventanas(
    df: pd.DataFrame, activo: str, base: BaseConocimiento, ventana: int, paso: int
) -> tuple[Ventanas, list[str], list[str]]:
    """Ventanas sin normalizar de todas las unidades del activo."""
    variables = list(base.activos[activo]["variables"])
    nominales = {v: valor_nominal(c) for v, c in base.activos[activo]["variables"].items()}
    clases = clases_de(activo, base)
    indices = {c: i for i, c in enumerate(clases)}
    partes = [
        v for _, g in df.groupby("unidad", observed=True, sort=True)
        if (v := _ventanas_unidad(g.reset_index(drop=True), variables, nominales, indices, ventana, paso)) is not None
    ]
    union = Ventanas(*(np.concatenate([getattr(p, f.name) for p in partes]) for f in fields(Ventanas)))
    return union, variables, clases


def normalizar(ventanas: Ventanas) -> tuple[np.ndarray, np.ndarray]:
    """Media y desviación de cada variable, solo con ventanas de entrenamiento."""
    x = ventanas.X[(ventanas.particion == "train") & ~ventanas.gris]
    media = x.mean(axis=(0, 1))
    desviacion = x.std(axis=(0, 1))
    return media, np.where(desviacion < 1e-6, 1.0, desviacion)


def aplicar_normalizacion(X: np.ndarray, media: np.ndarray, desviacion: np.ndarray) -> np.ndarray:
    return np.clip((X - media) / desviacion, -RECORTE_Z, RECORTE_Z).astype(np.float32)


def cargar_activo(
    activo: str, datos: Path, ventana: int, paso: int, base: BaseConocimiento | None = None
) -> DatosActivo:
    base = base or cargar_base()
    union, variables, clases = construir_ventanas(pd.read_parquet(datos / f"{activo}.parquet"), activo, base, ventana, paso)
    return preparar(activo, union, variables, clases)


def preparar(activo: str, union: Ventanas, variables: list[str], clases: list[str]) -> DatosActivo:
    media, desviacion = normalizar(union)
    union.X = aplicar_normalizacion(union.X, media, desviacion)
    particiones = {p: union.subconjunto(union.particion == p) for p in PARTICIONES}
    return DatosActivo(activo, variables, clases, media, desviacion, particiones)


def balancear_entrenamiento(
    ventanas: Ventanas, negativos_por_positivo: float, rng: np.random.Generator
) -> Ventanas:
    """Conserva todas las ventanas con falla y una muestra de las normales (clase 0)."""
    positivas = np.flatnonzero(ventanas.y != 0)
    normales = np.flatnonzero(ventanas.y == 0)
    n = min(normales.size, int(negativos_por_positivo * max(positivas.size, 1)))
    elegidas = rng.choice(normales, n, replace=False)
    return ventanas.subconjunto(np.sort(np.concatenate([positivas, elegidas])))


def variables_agregadas(X: np.ndarray) -> np.ndarray:
    """Por variable: media, RMS, curtosis, pendiente, máximo, mínimo y último valor."""
    media = X.mean(axis=1)
    centrado = X - media[:, None, :]
    varianza = np.maximum((centrado**2).mean(axis=1), 1e-6)
    curtosis = (centrado**4).mean(axis=1) / varianza**2
    t = np.arange(X.shape[1], dtype=np.float32) - (X.shape[1] - 1) / 2
    pendiente = (centrado * t[None, :, None]).sum(axis=1) / (t**2).sum()
    agregados = [media, np.sqrt((X**2).mean(axis=1)), curtosis, pendiente, X.max(axis=1), X.min(axis=1), X[:, -1, :]]
    return np.concatenate(agregados, axis=1).astype(np.float32)
