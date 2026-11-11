"""Comparación M0 · M1 · M2 · M3 por tipo de activo (Fase 5).

M1 es el modelo elegido en la Fase 4; M2 reentrena esa misma arquitectura con el
conocimiento como entrada; M3 fusiona M1 con las reglas. Los parámetros de M3 se eligen
en validación y test no decide nada (D-056).

Uso: ``python -m metaltech.hybrid.comparar [--activos a b]``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from metaltech.data.features import PARTICIONES, cargar_activo
from metaltech.hybrid.conocimiento import cargar_o_calcular
from metaltech.hybrid.fusion import elegir_fusion, fusionar, proba_m0
from metaltech.kb.base import RAIZ, cargar_base
from metaltech.models.evaluate import aviso_temprano, falsas_alarmas, metricas, metricas_por_clase
from metaltech.models.train import (
    cargar_modelo,
    entradas,
    entrenar,
    guardar_modelo,
    predecir_logits,
    probabilidades,
)

SISTEMAS = ("M0", "M1", "M2", "M3")
EVALUADAS = ("val", "test", "test_unidad")


def _fila(activo: str, sistema: str, particion: str, v, proba: np.ndarray) -> dict[str, Any]:
    g = v.gris
    aviso = aviso_temprano(proba[g].argmax(1), v.modo[g], v.horas_a_falla[g], v.unidad[g], v.ts[g])
    return {"activo": activo, "sistema": sistema, "particion": particion,
            **metricas(v.y[~g], proba[~g]), **falsas_alarmas(v.y[~g], proba[~g], v.confusor[~g]), **aviso}


def comparar_activo(activo: str, cfg: dict[str, Any], datos_dir: Path, arquitectura: str, semilla: int, base) -> tuple:
    d = cfg["datos"]
    datos = cargar_activo(activo, datos_dir, d["ventana_pasos"], d["paso_ventana"], base)
    conocimiento = {
        p: cargar_o_calcular(activo, datos_dir, datos.particiones[p], datos.clases, datos.variables, base, d["ventana_pasos"], p)
        for p in PARTICIONES
    }
    modelos = RAIZ / cfg["rutas"]["checkpoints"]
    m1, ck = cargar_modelo(modelos / f"{activo}_{arquitectura}_s{semilla}.pt", d["ventana_pasos"], cfg)
    probas: dict[str, dict[str, np.ndarray]] = {s: {} for s in SISTEMAS}
    for p in EVALUADAS:
        v = datos.particiones[p]
        probas["M0"][p] = proba_m0(conocimiento[p].fc)
        probas["M1"][p] = probabilidades(predecir_logits(m1, entradas(arquitectura, v)), ck["temperatura"])

    for p in PARTICIONES:  # M2: misma arquitectura, con conocimiento como entrada
        datos.particiones[p].extra = conocimiento[p].vector
    r2 = entrenar(datos, arquitectura, semilla, cfg)
    guardar_modelo(modelos / f"{activo}_{arquitectura}_m2_s{semilla}.pt", datos, arquitectura, semilla, r2)
    for p in EVALUADAS:
        probas["M2"][p] = probabilidades(predecir_logits(r2.modelo, entradas(arquitectura, datos.particiones[p])), r2.temperatura)

    val = datos.particiones["val"]
    limpias = ~val.gris
    f = cfg["fusion"]
    parametros, rejilla = elegir_fusion(
        probas["M1"]["val"][limpias], conocimiento["val"].fc[limpias], val.y[limpias], f["alfa_grid"], f["veto_reglas_fc_min"]
    )
    for p in EVALUADAS:
        probas["M3"][p] = fusionar(probas["M1"][p], conocimiento[p].fc, parametros)

    filas, por_clase = [], []
    for s in SISTEMAS:
        for p in EVALUADAS:
            v = datos.particiones[p]
            filas.append(_fila(activo, s, p, v, probas[s][p]))
            por_clase += [{"activo": activo, "sistema": s, "particion": p, **c}
                          for c in metricas_por_clase(v.y[~v.gris], probas[s][p][~v.gris], datos.clases)]
    info = {"arquitectura": arquitectura, "alfa": parametros.alfa, "veto": parametros.veto,
            "fc_min": parametros.fc_min, "epocas_m2": r2.epocas, "rejilla_val": rejilla}
    return filas, por_clase, info


def resumir(tabla: pd.DataFrame) -> dict[str, Any]:
    columnas = ["f1_macro", "precision_macro", "recall_macro", "falsa_alarma_sin_confusor",
                "falsa_alarma_con_confusor", "aviso_episodios_pct", "anticipacion_mediana_h"]
    medias = tabla.groupby(["particion", "sistema"])[columnas].mean()
    resumen: dict[str, Any] = {"medias": {f"{p}|{s}": medias.loc[(p, s)].round(4).to_dict() for p, s in medias.index}}
    for p in ("test", "test_unidad"):
        fa = medias.loc[p, "falsa_alarma_con_confusor"]
        resumen[f"reduccion_falsa_alarma_confusor_{p}"] = {
            "M3_vs_M1": round(float(1 - fa["M3"] / fa["M1"]), 4) if fa["M1"] > 0 else None,
            "M3_vs_M0": round(float(1 - fa["M3"] / fa["M0"]), 4) if fa["M0"] > 0 else None,
            "M2_vs_M1": round(float(1 - fa["M2"] / fa["M1"]), 4) if fa["M1"] > 0 else None,
        }
    return resumen


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compara reglas, modelo, modelo con conocimiento y fusión.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--activos", nargs="*", default=None)
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    base = cargar_base()
    tablas = RAIZ / cfg["rutas"]["tablas"]
    seleccion = json.loads((tablas / "modelos_seleccion.json").read_text(encoding="utf-8"))
    filas, por_clase, parametros = [], [], {}
    for activo in args.activos or list(base.activos):
        a, b, info = comparar_activo(activo, cfg, args.datos, seleccion[activo], cfg["semilla_principal"], base)
        filas += a
        por_clase += b
        parametros[activo] = info
        print(f"[{activo}] alfa={info['alfa']} veto={info['veto']}", flush=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(tablas / "comparacion_sistemas.csv", index=False)
    pd.DataFrame(por_clase).to_csv(tablas / "comparacion_por_clase.csv", index=False)
    (tablas / "fusion_parametros.json").write_text(json.dumps(parametros, indent=2), encoding="utf-8")
    resumen = resumir(tabla)
    (tablas / "comparacion_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    columnas = ["activo", "sistema", "particion", "f1_macro", "falsa_alarma_sin_confusor", "falsa_alarma_con_confusor", "aviso_episodios_pct"]
    print(tabla[tabla["particion"] != "val"][columnas].round(3).to_string(index=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
