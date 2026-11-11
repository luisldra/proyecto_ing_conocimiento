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


def _modelo(ruta: Path, datos, arquitectura: str, semilla: int, cfg: dict[str, Any]):
    """Carga el modelo si ya existe (resultados idénticos al reejecutar); si no, lo entrena."""
    if ruta.exists():
        modelo, ck = cargar_modelo(ruta, cfg["datos"]["ventana_pasos"], cfg)
        return modelo, ck["temperatura"], None
    r = entrenar(datos, arquitectura, semilla, cfg)
    guardar_modelo(ruta, datos, arquitectura, semilla, r)
    return r.modelo, r.temperatura, r.epocas


def comparar_activo(
    activo: str, cfg: dict[str, Any], datos_dir: Path, arquitectura: str, semillas: list[int], base
) -> tuple[list, list, dict, pd.DataFrame]:
    """M0–M3 para cada semilla; los datos y el conocimiento se cargan una sola vez."""
    d = cfg["datos"]
    datos = cargar_activo(activo, datos_dir, d["ventana_pasos"], d["paso_ventana"], base)
    conocimiento = {
        p: cargar_o_calcular(activo, datos_dir, datos.particiones[p], datos.clases, datos.variables, base, d["ventana_pasos"], p)
        for p in PARTICIONES
    }
    modelos = RAIZ / cfg["rutas"]["checkpoints"]
    filas, por_clase, infos, predicciones = [], [], {}, []
    for semilla in semillas:
        for p in PARTICIONES:  # M1 se entrena solo con sensores
            datos.particiones[p].extra = np.zeros((len(datos.particiones[p]), 0), dtype=np.float32)
        m1, t1, _ = _modelo(modelos / f"{activo}_{arquitectura}_s{semilla}.pt", datos, arquitectura, semilla, cfg)
        probas: dict[str, dict[str, np.ndarray]] = {s: {} for s in SISTEMAS}
        for p in EVALUADAS:
            probas["M0"][p] = proba_m0(conocimiento[p].fc)
            probas["M1"][p] = probabilidades(predecir_logits(m1, entradas(arquitectura, datos.particiones[p])), t1)

        for p in PARTICIONES:  # M2: misma arquitectura, con conocimiento como entrada
            datos.particiones[p].extra = conocimiento[p].vector
        m2, t2, epocas_m2 = _modelo(modelos / f"{activo}_{arquitectura}_m2_s{semilla}.pt", datos, arquitectura, semilla, cfg)
        for p in EVALUADAS:
            probas["M2"][p] = probabilidades(predecir_logits(m2, entradas(arquitectura, datos.particiones[p])), t2)

        val = datos.particiones["val"]
        limpias = ~val.gris
        f = cfg["fusion"]
        parametros, rejilla = elegir_fusion(
            probas["M1"]["val"][limpias], conocimiento["val"].fc[limpias], val.y[limpias], f["alfa_grid"], f["veto_reglas_fc_min"]
        )
        for p in EVALUADAS:
            probas["M3"][p] = fusionar(probas["M1"][p], conocimiento[p].fc, parametros)

        for s in SISTEMAS:
            for p in EVALUADAS:
                v = datos.particiones[p]
                filas.append({"semilla": semilla, **_fila(activo, s, p, v, probas[s][p])})
                por_clase += [{"semilla": semilla, "activo": activo, "sistema": s, "particion": p, **c}
                              for c in metricas_por_clase(v.y[~v.gris], probas[s][p][~v.gris], datos.clases)]
        for p in ("test", "test_unidad"):
            v = datos.particiones[p]
            predicciones.append(pd.DataFrame({
                "semilla": semilla, "activo": activo, "particion": p, "unidad": v.unidad, "ts": v.ts, "y": v.y,
                "gris": v.gris, "modo": v.modo, "horas_a_falla": v.horas_a_falla, "confusor": v.confusor,
                **{f"pred_{s}": probas[s][p].argmax(1) for s in SISTEMAS},
            }))
        infos[semilla] = {"arquitectura": arquitectura, "alfa": parametros.alfa, "veto": parametros.veto,
                          "fc_min": parametros.fc_min, "epocas_m2": epocas_m2, "rejilla_val": rejilla}
        print(f"[{activo}] semilla={semilla} alfa={parametros.alfa} veto={parametros.veto}", flush=True)
    return filas, por_clase, infos, pd.concat(predicciones, ignore_index=True)


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
    ap.add_argument("--semillas", nargs="*", type=int, default=None,
                    help="por defecto solo la semilla principal; 'todas' las de configs/train.yaml con --todas")
    ap.add_argument("--todas", action="store_true", help="usa todas las semillas de configs/train.yaml (Fase 7)")
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    principal = cfg["semilla_principal"]
    semillas = cfg["semillas"] if args.todas else (args.semillas or [principal])
    base = cargar_base()
    tablas = RAIZ / cfg["rutas"]["tablas"]
    seleccion = json.loads((tablas / "modelos_seleccion.json").read_text(encoding="utf-8"))
    filas, por_clase, parametros = [], [], {}
    for activo in args.activos or list(base.activos):
        a, b, infos, pred = comparar_activo(activo, cfg, args.datos, seleccion[activo], semillas, base)
        filas += a
        por_clase += b
        parametros[activo] = infos
        pred.to_parquet(args.datos / f"predicciones_{activo}.parquet", index=False)
    todas = pd.DataFrame(filas)
    todas.to_csv(tablas / "comparacion_semillas.csv", index=False)
    (tablas / "fusion_parametros_semillas.json").write_text(json.dumps(parametros, indent=2), encoding="utf-8")
    if principal not in semillas:
        return 0
    tabla = todas[todas["semilla"] == principal].drop(columns="semilla")
    tabla.to_csv(tablas / "comparacion_sistemas.csv", index=False)
    pd.DataFrame(por_clase).query("semilla == @principal").drop(columns="semilla").to_csv(
        tablas / "comparacion_por_clase.csv", index=False)
    (tablas / "fusion_parametros.json").write_text(
        json.dumps({a: info[principal] for a, info in parametros.items()}, indent=2), encoding="utf-8")
    resumen = resumir(tabla)
    (tablas / "comparacion_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    columnas = ["activo", "sistema", "particion", "f1_macro", "falsa_alarma_sin_confusor", "falsa_alarma_con_confusor", "aviso_episodios_pct"]
    print(tabla[tabla["particion"] != "val"][columnas].round(3).to_string(index=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
