"""Equidad: desempeño por turno, por observación del técnico, por máquina vista o no vista y por
activo (Fase 7, D-060).

M1 no usa las observaciones de los técnicos; M0 y M3 sí, a través del léxico. Comparar sus
brechas muestra si el sesgo del turno de noche (acierto 75 % frente a 84–86 % de día) pasa
de las personas al sistema.

Uso: ``python -m metaltech.metrics.equidad``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from metaltech.data.generator import _turnos
from metaltech.kb.base import RAIZ, cargar_base

SISTEMAS = ("M0", "M1", "M2", "M3")
MINIMO_GRUPO = 30  # ventanas mínimas por grupo para calcular una tasa
HORAS_OBSERVACION = 6.0


def observacion_por_ventana(pred: pd.DataFrame, obs: pd.DataFrame, horas: float = HORAS_OBSERVACION) -> np.ndarray:
    """``ninguna``, ``correcta`` o ``incorrecta`` (si alguna de las de la ventana lo es)."""
    resultado = np.full(len(pred), "ninguna", dtype=object)
    fin = pd.to_datetime(pred["ts"]).to_numpy()
    unidades = pred["unidad"].to_numpy()
    margen = np.timedelta64(int(horas * 60), "m")
    for u, g in obs.groupby("unidad"):
        idx = np.flatnonzero(unidades == u)
        if idx.size == 0:
            continue
        tiempos, correctas = g["ts"].to_numpy(), g["es_correcta"].to_numpy()
        for i in idx:
            m = (tiempos > fin[i] - margen) & (tiempos <= fin[i])
            if m.any():
                resultado[i] = "correcta" if correctas[m].all() else "incorrecta"
    return resultado


def tasas(pred: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Acierto en ventanas con falla y falsa alarma en ventanas sanas, por sistema, grupo y semilla."""
    limpias = pred[~pred["gris"]]
    filas = []
    for (semilla, valor), g in limpias.groupby(["semilla", grupo]):
        falla, sana = g[g["y"] != 0], g[g["y"] == 0]
        for s in SISTEMAS:
            filas.append({
                "grupo": grupo, "valor": valor, "semilla": semilla, "sistema": s,
                "ventanas_falla": len(falla), "ventanas_sanas": len(sana),
                "acierto_falla": float((falla[f"pred_{s}"] == falla["y"]).mean()) if len(falla) >= MINIMO_GRUPO else np.nan,
                "falsa_alarma": float((sana[f"pred_{s}"] != 0).mean()) if len(sana) >= MINIMO_GRUPO else np.nan,
            })
    return pd.DataFrame(filas)


def brechas(t: pd.DataFrame) -> pd.DataFrame:
    """Diferencia entre el mejor y el peor grupo (media entre semillas) y cuál es el peor."""
    medias = t.groupby(["grupo", "sistema", "valor"])[["acierto_falla", "falsa_alarma"]].mean().reset_index()
    filas = []
    for (grupo, sistema), g in medias.groupby(["grupo", "sistema"]):
        fila = {"grupo": grupo, "sistema": sistema}
        for m, peor in (("acierto_falla", "idxmin"), ("falsa_alarma", "idxmax")):
            v = g.dropna(subset=[m])
            if len(v) >= 2:
                fila[f"{m}_brecha"] = float(v[m].max() - v[m].min())
                fila[f"{m}_peor"] = str(v.loc[getattr(v[m], peor)(), "valor"])
        filas.append(fila)
    return pd.DataFrame(filas)


def preparar(datos: Path) -> pd.DataFrame:
    obs = pd.read_parquet(datos / "observaciones.parquet")
    partes = []
    for activo in cargar_base().activos:
        p = pd.read_parquet(datos / f"predicciones_{activo}.parquet")
        p["turno"] = _turnos(pd.DatetimeIndex(p["ts"]))
        p["observacion"] = observacion_por_ventana(p, obs[obs["activo"] == activo])
        p["maquina"] = np.where(p["particion"] == "test_unidad", "no_vista", "vista")
        partes.append(p)
    return pd.concat(partes, ignore_index=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Análisis de equidad por grupos.")
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--tablas", default=RAIZ / "reports" / "tables", type=Path)
    args = ap.parse_args(argv)
    pred = preparar(args.datos)
    t = pd.concat([tasas(pred, g) for g in ("turno", "observacion", "maquina", "activo")], ignore_index=True)
    b = brechas(t)
    t.to_csv(args.tablas / "equidad_grupos.csv", index=False)
    b.to_csv(args.tablas / "equidad_brechas.csv", index=False)
    medias = t.groupby(["grupo", "valor", "sistema"])[["acierto_falla", "falsa_alarma"]].mean().round(4)
    primera = pred[(pred["semilla"] == pred["semilla"].min()) & ~pred["gris"]]
    resumen = {"ventanas_por_observacion": {k: int(v) for k, v in primera.groupby("observacion").size().items()},
               "brechas": b.round(4).to_dict("records")}
    (args.tablas / "equidad_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(medias.unstack("sistema").to_string())
    print(b.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
