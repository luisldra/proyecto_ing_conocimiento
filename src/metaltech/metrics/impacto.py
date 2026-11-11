"""Impacto operativo simulado: fallas detectadas, eventos de falsa alarma y costo relativo
por unidad-año (Fase 7, D-060). Los costos son supuestos, en unidades relativas al costo de
una reparación planificada, y se reportan con análisis de sensibilidad.

Uso: ``python -m metaltech.metrics.impacto``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from metaltech.kb.base import RAIZ, cargar_base

SISTEMAS = ("M0", "M1", "M2", "M3")
HUECO_EVENTO = pd.Timedelta(hours=1)  # alarmas separadas por más de esto son eventos distintos


def episodios(pred: pd.DataFrame, sistema: str) -> pd.DataFrame:
    """Una fila por falla con ventanas visibles: ¿alguna ventana predijo el modo correcto?"""
    con_modo = pred[pred["modo"] != 0].copy()
    falla = pd.to_datetime(con_modo["ts"]) + pd.to_timedelta(con_modo["horas_a_falla"].astype(float), unit="h")
    con_modo["falla"] = falla.dt.round("10min")
    con_modo["acierto"] = con_modo[f"pred_{sistema}"] == con_modo["modo"]
    con_modo["horas_acierto"] = con_modo["horas_a_falla"].where(con_modo["acierto"])
    g = con_modo.groupby(["semilla", "activo", "unidad", "falla"])
    return pd.DataFrame({"detectada": g["acierto"].any(), "anticipacion_h": g["horas_acierto"].max()}).reset_index()


def eventos_falsa_alarma(pred: pd.DataFrame, sistema: str) -> pd.DataFrame:
    """Alarmas en equipo sano agrupadas en eventos: ventanas consecutivas cuentan una vez."""
    sanas = pred[(pred["modo"] == 0) & (pred["y"] == 0)]
    alarmas = sanas[sanas[f"pred_{sistema}"] != 0].sort_values(["semilla", "unidad", "ts"])
    if alarmas.empty:
        return pd.DataFrame({"semilla": [], "activo": [], "unidad": [], "eventos": []})
    ts = pd.to_datetime(alarmas["ts"])
    nuevo = (ts.diff() > HUECO_EVENTO) | (alarmas["unidad"] != alarmas["unidad"].shift()) \
        | (alarmas["semilla"] != alarmas["semilla"].shift())
    return (alarmas.assign(evento=nuevo.cumsum().to_numpy())
            .groupby(["semilla", "activo", "unidad"])["evento"].nunique().rename("eventos").reset_index())


def unidad_anios(pred: pd.DataFrame) -> pd.Series:
    """Años observados por semilla: suma sobre unidades y particiones del lapso que cubren sus ventanas."""
    lapso = pred.assign(ts=pd.to_datetime(pred["ts"])).groupby(["semilla", "particion", "unidad"])["ts"] \
        .agg(lambda s: (s.max() - s.min()).total_seconds() / 86400)
    return lapso.groupby(level="semilla").sum() / 365.25


def impacto(pred: pd.DataFrame, costos: dict[str, Any]) -> pd.DataFrame:
    anios = unidad_anios(pred)
    filas = []
    for s in SISTEMAS:
        ep = episodios(pred, s)
        fa = eventos_falsa_alarma(pred, s)
        for semilla, e in ep.groupby("semilla"):
            n_fa = int(fa.loc[fa["semilla"] == semilla, "eventos"].sum())
            detectadas, perdidas = int(e["detectada"].sum()), int((~e["detectada"]).sum())
            fila = {"sistema": s, "semilla": semilla, "fallas": len(e), "detectadas_pct": 100 * detectadas / len(e),
                    "anticipacion_mediana_h": float(e["anticipacion_h"].median()),
                    "eventos_falsa_alarma_por_unidad_anio": n_fa / anios[semilla]}
            base = costos["reparacion_planificada"]
            for r in costos["ratio_no_planificada"]:
                total = detectadas * base + perdidas * r * base + n_fa * costos["falsa_alarma"]
                fila[f"costo_unidad_anio_r{r}"] = total / anios[semilla]
            filas.append(fila)
    return pd.DataFrame(filas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Impacto operativo y costo relativo simulado.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--tablas", default=RAIZ / "reports" / "tables", type=Path)
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        costos = yaml.safe_load(f)["impacto"]
    pred = pd.concat([pd.read_parquet(args.datos / f"predicciones_{a}.parquet") for a in cargar_base().activos],
                     ignore_index=True)
    t = impacto(pred, costos)
    t.to_csv(args.tablas / "impacto_semillas.csv", index=False)
    medias = t.drop(columns="semilla").groupby("sistema").mean().round(3)
    medias.to_csv(args.tablas / "impacto_sistemas.csv")
    resumen: dict[str, Any] = {"supuestos": costos, "medias": medias.to_dict("index")}
    for r in costos["ratio_no_planificada"]:
        c = medias[f"costo_unidad_anio_r{r}"]
        resumen[f"ahorro_vs_M0_r{r}_pct"] = {s: round(float(100 * (1 - c[s] / c["M0"])), 2) for s in SISTEMAS}
        resumen[f"ahorro_vs_M1_r{r}_pct"] = {s: round(float(100 * (1 - c[s] / c["M1"])), 2) for s in SISTEMAS}
    (args.tablas / "impacto_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(medias.to_string())
    print(json.dumps({k: v for k, v in resumen.items() if k.startswith("ahorro")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
