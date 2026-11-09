"""Reporte de calibración del simulador (Fase 3).

Mide sobre el dataset generado lo que hace el sistema experto (M0) y deja las tablas en
``reports/tables``. Solo usa M0: las firmas no se ajustan mirando el resultado de M3 (D-050).

Uso: ``python -m metaltech.data.calibracion [--datos data/synthetic]``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from metaltech.data.generator import PASOS_POR_HORA
from metaltech.kb.base import RAIZ, BaseConocimiento, cargar_base
from metaltech.kb.rules_engine import MotorReglas

HORAS_EVALUADAS = 96  # tramo final de cada episodio, una evaluación por hora
MUESTRA_SANOS = 1500


def _linea_base(filas: pd.DataFrame, variables: list[str]) -> dict[str, float]:
    sanos = filas.loc[(filas["estado"] == "sano") & (filas["confusor"] == "ninguno"), variables]
    return {v: float(sanos[v].median()) for v in variables}


def anticipacion_por_episodio(
    episodios: pd.DataFrame, series: dict[str, pd.DataFrame], base: BaseConocimiento
) -> pd.DataFrame:
    """Primera hora en que M0 concluye el modo correcto, dentro del tramo final del episodio."""
    motor = MotorReglas(base)
    resultados = []
    for (unidad, activo), grupo in episodios.groupby(["unidad", "activo"], observed=True):
        variables = list(base.activos[activo]["variables"])
        filas = series[activo][series[activo]["unidad"] == unidad].reset_index(drop=True)
        linea = _linea_base(filas, variables)
        valores = filas[variables].to_numpy(dtype=float)
        for ep in grupo.itertuples():
            desde = max(ep.i0, ep.i1 - HORAS_EVALUADAS * PASOS_POR_HORA)
            anticipacion, cruzo = None, False
            for i in sorted({*range(ep.i1, desde - 1, -PASOS_POR_HORA), ep.i1}):
                vals = {v: float(x) for v, x in zip(variables, valores[i], strict=True) if not np.isnan(x)}
                principal = motor.diagnosticar(activo, vals, linea).principal
                if principal is None:
                    continue
                if principal.modo == ep.modo:
                    anticipacion = anticipacion if anticipacion is not None else (ep.i1 - i) / PASOS_POR_HORA
                else:
                    cruzo = True
            resultados.append({
                "activo": activo, "modo": ep.modo, "tarea": ep.tarea, "duracion_h": ep.duracion_h,
                "detectado": anticipacion is not None,
                "anticipacion_h": np.nan if anticipacion is None else anticipacion, "cruce": cruzo,
            })
    return pd.DataFrame(resultados)


def falsas_alarmas(series: dict[str, pd.DataFrame], base: BaseConocimiento, semilla: int) -> pd.DataFrame:
    """% de muestras sanas con alguna conclusión de M0, con y sin confusores."""
    motor = MotorReglas(base)
    rng = np.random.default_rng(semilla)
    filas = []
    for activo, df in series.items():
        variables = list(base.activos[activo]["variables"])
        sanos = df[(df["estado"] == "sano") & (df["etiqueta"] == "normal")]
        for nombre, parte in (
            ("sin_confusor", sanos[sanos["confusor"] == "ninguno"]),
            ("con_confusor", sanos[~sanos["confusor"].isin(["ninguno", "sensor_faltante"])]),
        ):
            if parte.empty:
                continue
            elegidas = rng.choice(len(parte), min(MUESTRA_SANOS, len(parte)), replace=False)
            muestra = parte.iloc[np.sort(elegidas)]
            lineas = {
                u: _linea_base(g, variables) for u, g in sanos.groupby("unidad", observed=True) if len(g)
            }
            alarmas = 0
            for fila, unidad in zip(muestra[variables].to_numpy(dtype=float), muestra["unidad"].astype(str), strict=True):
                vals = {v: float(x) for v, x in zip(variables, fila, strict=True) if not np.isnan(x)}
                alarmas += bool(motor.diagnosticar(activo, vals, lineas[unidad]).conclusiones)
            filas.append({"activo": activo, "grupo": nombre, "muestras": len(muestra),
                          "alarma_pct": round(100 * alarmas / len(muestra), 2)})
    return pd.DataFrame(filas)


def reportar(datos: Path, salida: Path, semilla: int = 42) -> dict:
    base = cargar_base()
    series = {a: pd.read_parquet(datos / f"{a}.parquet") for a in base.activos}
    episodios = pd.read_parquet(datos / "episodios.parquet")
    obs = pd.read_parquet(datos / "observaciones.parquet")
    salida.mkdir(parents=True, exist_ok=True)

    ant = anticipacion_por_episodio(episodios, series, base)
    tabla = ant.groupby(["activo", "modo", "tarea"], as_index=False).agg(
        episodios=("detectado", "size"), duracion_mediana_h=("duracion_h", "median"),
        detectado_pct=("detectado", lambda s: round(100 * s.mean(), 1)),
        anticipacion_mediana_h=("anticipacion_h", "median"), cruces=("cruce", "sum"),
    )
    alarmas = falsas_alarmas(series, base, semilla)
    con_falla = obs[obs["modo_real"] != "normal"]
    acierto = con_falla.groupby(["turno", "tecnico"], as_index=False, observed=True).agg(
        observaciones=("es_correcta", "size"), acierto_pct=("es_correcta", lambda s: round(100 * s.mean(), 1))
    )
    tabla.to_csv(salida / "calibracion_m0_por_modo.csv", index=False)
    alarmas.to_csv(salida / "calibracion_falsas_alarmas.csv", index=False)
    acierto.to_csv(salida / "calibracion_observaciones.csv", index=False)

    filas_totales = sum(len(df) for df in series.values())
    positivas = sum(int((df["etiqueta"] != "normal").sum()) for df in series.values())
    resumen = {
        "filas": filas_totales, "positivas_pct": round(100 * positivas / filas_totales, 2),
        "episodios": len(episodios), "episodios_por_particion": episodios["particion"].value_counts().to_dict(),
        "min_episodios_por_modo_activo": int(tabla["episodios"].min()),
        "m0_detectado_pct_por_tarea": ant.groupby("tarea")["detectado"].mean().mul(100).round(1).to_dict(),
        "m0_anticipacion_mediana_h": ant.groupby("tarea")["anticipacion_h"].median().round(1).to_dict(),
        "episodios_con_cruce_pct": round(100 * ant["cruce"].mean(), 1),
        "falsas_alarmas_pct_medio": alarmas.groupby("grupo")["alarma_pct"].mean().round(2).to_dict(),
        "acierto_tecnicos_pct_por_turno": con_falla.groupby("turno", observed=True)["es_correcta"].mean().mul(100).round(1).to_dict(),
    }
    (salida / "calibracion_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    return resumen


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Calibración del simulador con el sistema experto.")
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--salida", default=RAIZ / "reports" / "tables", type=Path)
    args = ap.parse_args(argv)
    print(json.dumps(reportar(args.datos, args.salida), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
