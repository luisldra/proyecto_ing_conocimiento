"""Latencia por solicitud de una sola ventana, en CPU (Fase 7, D-060).

Mide lo que tardaría el sistema en responder una consulta: M0 (reglas), M1 (modelo),
M3 (modelo + reglas + fusión + diagnóstico explicado) y M3 con gradientes integrados. No
incluye la red ni el servidor web, que se miden con la API en la Fase 8.

Uso: ``python -m metaltech.metrics.latencia [--solicitudes 1000]``
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from metaltech.data.features import cargar_activo
from metaltech.hybrid.conocimiento import lineas_base
from metaltech.hybrid.fusion import ParametrosFusion, diagnostico_hibrido
from metaltech.kb.base import RAIZ, cargar_base
from metaltech.kb.rules_engine import MotorReglas
from metaltech.models.train import cargar_modelo, entradas_de, probabilidades
from metaltech.xai.explain import explicar_alerta, importancia_por_variable

SOLICITUDES_XAI = 100  # los gradientes integrados son más lentos: se miden menos solicitudes


def percentiles(tiempos_s: list[float]) -> dict[str, float]:
    ms = np.asarray(tiempos_s) * 1000
    return {"p50_ms": float(np.percentile(ms, 50)), "p95_ms": float(np.percentile(ms, 95)), "max_ms": float(ms.max())}


def medir_activo(activo: str, cfg: dict, datos_dir: Path, arquitectura: str, fusion: dict, n: int, base) -> list[dict]:
    d = cfg["datos"]
    datos = cargar_activo(activo, datos_dir, d["ventana_pasos"], d["paso_ventana"], base)
    v = datos.particiones["test"]
    rng = np.random.default_rng(cfg["semilla_principal"])
    elegidas = rng.choice(len(v), min(n, len(v)), replace=False)
    modelo, ck = cargar_modelo(RAIZ / cfg["rutas"]["checkpoints"] / f"{activo}_{arquitectura}_s{cfg['semilla_principal']}.pt",
                               d["ventana_pasos"], cfg)
    modelo.eval()
    motor = MotorReglas(base)
    df = pd.read_parquet(datos_dir / f"{activo}.parquet", columns=["ts", "unidad", *datos.variables])
    lineas = lineas_base(df, datos.variables)
    par = ParametrosFusion(fusion["alfa"], fusion["veto"], fusion["fc_min"])
    tiempos: dict[str, list[float]] = {"M0": [], "M1": [], "M3": [], "M3+XAI": []}

    def m0(i: int):
        return motor.diagnosticar(activo, dict(zip(datos.variables, v.crudo[i].astype(float), strict=True)), lineas[str(v.unidad[i])])

    def m1(i: int) -> np.ndarray:
        with torch.no_grad():
            return probabilidades(modelo(entradas_de(arquitectura, v.X[i : i + 1])), ck["temperatura"])[0]

    for k, i in enumerate(elegidas):
        for nombre, funcion in (("M0", lambda i=i: m0(i)), ("M1", lambda i=i: m1(i)),
                                ("M3", lambda i=i: diagnostico_hibrido(activo, datos.clases, m1(i), m0(i), par, base))):
            t0 = time.perf_counter()
            funcion()
            tiempos[nombre].append(time.perf_counter() - t0)
        if k < SOLICITUDES_XAI:
            t0 = time.perf_counter()
            p, diag = m1(i), m0(i)
            dh = diagnostico_hibrido(activo, datos.clases, p, diag, par, base)
            imp = importancia_por_variable(modelo, arquitectura, v.X[i : i + 1], np.array([int(p.argmax())]))[0]
            explicar_alerta(dh, dict(zip(datos.variables, imp.astype(float), strict=True)))
            tiempos["M3+XAI"].append(time.perf_counter() - t0)
    return [{"activo": activo, "arquitectura": arquitectura, "sistema": s, "solicitudes": len(t), **percentiles(t)}
            for s, t in tiempos.items()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Latencia por solicitud en CPU.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--solicitudes", default=None, type=int)
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    n = args.solicitudes or cfg["evaluacion"]["latencia_solicitudes"]
    tablas = RAIZ / cfg["rutas"]["tablas"]
    seleccion = json.loads((tablas / "modelos_seleccion.json").read_text(encoding="utf-8"))
    fusion = json.loads((tablas / "fusion_parametros.json").read_text(encoding="utf-8"))
    base = cargar_base()
    torch.set_num_threads(1)  # una solicitud a la vez, como en un servidor sencillo
    filas = []
    for activo in base.activos:
        filas += medir_activo(activo, cfg, args.datos, seleccion[activo], fusion[activo], n, base)
        print(f"[{activo}] listo", flush=True)
    t = pd.DataFrame(filas)
    t.to_csv(tablas / "latencia.csv", index=False)
    objetivo = cfg["evaluacion"]["latencia_objetivo_p95_ms"]
    resumen = {"objetivo_p95_ms": objetivo, "por_sistema_p95_max_ms": t.groupby("sistema")["p95_ms"].max().round(2).to_dict(),
               "cumple_objetivo": {s: bool(g["p95_ms"].max() <= objetivo) for s, g in t.groupby("sistema")}}
    (tablas / "latencia_resumen.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    print(t.round(2).to_string(index=False))
    print(json.dumps(resumen, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
