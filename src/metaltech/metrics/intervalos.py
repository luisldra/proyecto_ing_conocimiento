"""Intervalos de confianza entre semillas y diferencias pareadas entre sistemas (Fase 7, D-060).

La unidad de variación es la semilla: para cada semilla se promedian los 6 activos, y el
intervalo del 95 % usa la t de Student con n - 1 grados de libertad. Las diferencias entre
sistemas se miden pareadas por activo y semilla.

Uso: ``python -m metaltech.metrics.intervalos``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student
from scipy.stats import wilcoxon

from metaltech.kb.base import RAIZ

METRICAS = ["f1_macro", "precision_macro", "recall_macro", "falsa_alarma_sin_confusor",
            "falsa_alarma_con_confusor", "aviso_episodios_pct", "anticipacion_mediana_h"]
COMPARACIONES = [("M3", "M1"), ("M2", "M1"), ("M3", "M0"), ("M1", "M0"), ("M3", "M2")]


def intervalo(valores: np.ndarray, nivel: float = 0.95) -> tuple[float, float, float]:
    """Media e intervalo t de Student; con un solo valor el intervalo es degenerado."""
    valores = np.asarray(valores, dtype=float)
    valores = valores[~np.isnan(valores)]
    media = float(valores.mean())
    if len(valores) < 2:
        return media, media, media
    margen = float(student.ppf((1 + nivel) / 2, len(valores) - 1) * valores.std(ddof=1) / np.sqrt(len(valores)))
    return media, media - margen, media + margen


def por_sistema(tabla: pd.DataFrame) -> pd.DataFrame:
    """Media entre activos por semilla y, sobre eso, intervalo entre semillas."""
    por_semilla = tabla.groupby(["particion", "sistema", "semilla"])[METRICAS].mean().reset_index()
    filas = []
    for (particion, sistema), g in por_semilla.groupby(["particion", "sistema"]):
        for m in METRICAS:
            media, lo, hi = intervalo(g[m].to_numpy())
            filas.append({"particion": particion, "sistema": sistema, "metrica": m, "semillas": len(g),
                          "media": media, "ic95_inf": lo, "ic95_sup": hi, "desviacion": float(g[m].std(ddof=1))})
    return pd.DataFrame(filas)


def diferencias(tabla: pd.DataFrame, a: str, b: str, metrica: str, particion: str) -> dict[str, Any]:
    """``a - b`` pareado por activo y semilla: intervalo entre semillas, Wilcoxon y % de pares a favor."""
    t = tabla[tabla["particion"] == particion]
    pares = t.pivot_table(index=["activo", "semilla"], columns="sistema", values=metrica)[[a, b]].dropna()
    dif = pares[a] - pares[b]
    media, lo, hi = intervalo(dif.groupby(level="semilla").mean().to_numpy())
    no_nulas = dif[dif != 0]
    p = float(wilcoxon(no_nulas).pvalue) if len(no_nulas) >= 6 else float("nan")
    return {"particion": particion, "comparacion": f"{a}-{b}", "metrica": metrica, "pares": int(len(dif)),
            "diferencia_media": media, "ic95_inf": lo, "ic95_sup": hi,
            "a_mayor_pct": float(100 * (dif > 0).mean()), "p_wilcoxon": p}


def todas_las_diferencias(tabla: pd.DataFrame) -> pd.DataFrame:
    filas = [diferencias(tabla, a, b, m, p) for p in ("test", "test_unidad") for a, b in COMPARACIONES
             for m in ("f1_macro", "falsa_alarma_con_confusor", "falsa_alarma_sin_confusor", "aviso_episodios_pct")]
    return pd.DataFrame(filas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Intervalos de confianza entre semillas.")
    ap.add_argument("--tablas", default=RAIZ / "reports" / "tables", type=Path)
    args = ap.parse_args(argv)
    tabla = pd.read_csv(args.tablas / "comparacion_semillas.csv")
    sistemas, difs = por_sistema(tabla), todas_las_diferencias(tabla)
    sistemas.to_csv(args.tablas / "intervalos_sistemas.csv", index=False)
    difs.to_csv(args.tablas / "intervalos_diferencias.csv", index=False)
    clave = difs[difs["metrica"].isin(["f1_macro", "falsa_alarma_con_confusor"])]
    resumen = {"semillas": sorted(tabla["semilla"].unique().tolist()),
               "diferencias": clave.round(4).to_dict("records")}
    (args.tablas / "intervalos_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    f1 = sistemas[sistemas["metrica"] == "f1_macro"]
    print(f1.round(4).to_string(index=False))
    print(clave.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
