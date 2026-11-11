"""Explicabilidad del modelo y del sistema híbrido (Fase 6).

Gradientes integrados (Captum) sobre M1 dicen qué sensores pesaron en cada alerta; la
traza del motor de reglas dice qué reglas la respaldan. Las métricas de explicabilidad
son fidelidad, concordancia y estabilidad (D-057).

Uso: ``python -m metaltech.xai.explain [--activos a b] [--muestras 300]``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml
from captum.attr import IntegratedGradients
from torch import nn

from metaltech.data.features import NOMBRES_AGREGADOS, Ventanas, cargar_activo
from metaltech.data.generator import PASOS_POR_HORA
from metaltech.hybrid.conocimiento import lineas_base, textos_por_ventana
from metaltech.hybrid.fusion import ParametrosFusion, diagnostico_hibrido
from metaltech.kb.base import RAIZ, BaseConocimiento, cargar_base
from metaltech.kb.rules_engine import MotorReglas
from metaltech.models.train import cargar_modelo, entradas_de, probabilidades

PASOS_INTEGRACION = 32
TOP_K = 3
RUIDOS_ESTABILIDAD = (0.05, 0.25, 0.5)  # en desviaciones típicas de cada sensor; se reporta la curva
SORTEOS_ALEATORIOS = 5


# ---------------------------------------------------------------------------------------
# Atribuciones
# ---------------------------------------------------------------------------------------
def importancia_por_variable(
    modelo: nn.Module, arquitectura: str, X: np.ndarray, objetivo: np.ndarray
) -> np.ndarray:
    """Peso relativo de cada sensor [N, V] (suma 1 por ventana), respecto a la línea base cero.

    En variables normalizadas, cero es la media de entrenamiento. Para el MLP se suman las
    7 variables agregadas de cada sensor.
    """
    modelo.eval()
    x = entradas_de(arquitectura, X).requires_grad_(True)
    ig = IntegratedGradients(modelo)
    atrib = ig.attribute(x, baselines=torch.zeros_like(x), target=torch.from_numpy(objetivo),
                         n_steps=PASOS_INTEGRACION, internal_batch_size=4 * len(X)).detach().abs().numpy()
    if arquitectura == "mlp":
        por_variable = atrib.reshape(len(X), len(NOMBRES_AGREGADOS), X.shape[2]).sum(axis=1)
    else:
        por_variable = atrib.sum(axis=1)
    return por_variable / np.maximum(por_variable.sum(axis=1, keepdims=True), 1e-12)


def _proba(modelo: nn.Module, arquitectura: str, X: np.ndarray, temperatura: float) -> np.ndarray:
    with torch.no_grad():
        modelo.eval()
        return probabilidades(modelo(entradas_de(arquitectura, X)), temperatura)


def _anular(X: np.ndarray, variables: np.ndarray) -> np.ndarray:
    """Lleva las variables indicadas [N, k] a la media de entrenamiento en toda la ventana."""
    Xm = X.copy()
    filas = np.arange(len(X))[:, None]
    Xm[filas, :, variables] = 0.0
    return Xm


# ---------------------------------------------------------------------------------------
# Métricas de explicabilidad
# ---------------------------------------------------------------------------------------
def fidelidad(
    modelo: nn.Module, arquitectura: str, X: np.ndarray, objetivo: np.ndarray, importancia: np.ndarray,
    temperatura: float, k: int, rng: np.random.Generator,
) -> dict[str, float]:
    """Caída de la probabilidad predicha al anular las k variables más importantes vs. k al azar."""
    filas = np.arange(len(X))
    p0 = _proba(modelo, arquitectura, X, temperatura)[filas, objetivo]
    top = np.argsort(-importancia, axis=1)[:, :k]
    caida_top = p0 - _proba(modelo, arquitectura, _anular(X, top), temperatura)[filas, objetivo]
    caidas_azar = []
    for _ in range(SORTEOS_ALEATORIOS):
        azar = np.stack([rng.choice(X.shape[2], k, replace=False) for _ in filas])
        caidas_azar.append(p0 - _proba(modelo, arquitectura, _anular(X, azar), temperatura)[filas, objetivo])
    caida_azar = np.mean(caidas_azar, axis=0)
    return {
        "caida_top_k": float(caida_top.mean()),
        "caida_azar_k": float(caida_azar.mean()),
        "top_supera_azar_pct": float(100 * (caida_top > caida_azar).mean()),
    }


def estabilidad(
    modelo: nn.Module, arquitectura: str, X: np.ndarray, objetivo: np.ndarray, importancia: np.ndarray,
    rng: np.random.Generator, ruido: float = RUIDOS_ESTABILIDAD[0],
) -> float:
    """Similitud coseno media entre la explicación original y la de la ventana con ruido."""
    ruidosa = (X + rng.normal(0, ruido, X.shape)).astype(np.float32)
    otra = importancia_por_variable(modelo, arquitectura, ruidosa, objetivo)
    num = (importancia * otra).sum(axis=1)
    den = np.linalg.norm(importancia, axis=1) * np.linalg.norm(otra, axis=1)
    return float(np.mean(num / np.maximum(den, 1e-12)))


def acierto_en_top_k(importancia: np.ndarray, conjuntos: list[set[int]], k: int) -> float:
    """Fracción del top-k del modelo que cae en un conjunto de referencia (ventanas con conjunto no vacío)."""
    top = np.argsort(-importancia, axis=1)[:, :k]
    valores = [len(set(t) & c) / k for t, c in zip(top, conjuntos, strict=True) if c]
    return float(np.mean(valores)) if valores else float("nan")


def variables_de_firma(modo: str, variables: list[str], base: BaseConocimiento) -> set[int]:
    """Índices de los sensores que la falla mueve en el simulador (verdad de terreno)."""
    if modo not in base.modos:
        return set()
    return {variables.index(f["variable"]) for f in base.modos[modo]["firma"] if f["variable"] in variables}


# ---------------------------------------------------------------------------------------
# Explicación de una alerta
# ---------------------------------------------------------------------------------------
def explicar_alerta(diagnostico: dict[str, Any], importancias: dict[str, float], k: int = TOP_K) -> dict[str, Any]:
    """Agrega al diagnóstico híbrido los sensores con más peso y un texto en español."""
    top = sorted(importancias.items(), key=lambda kv: -kv[1])[:k]
    en_reglas = {p["variable"] for r in diagnostico["reglas"] for p in r["premisas"] if p["variable"]}
    if diagnostico["modo"] == "normal":
        texto = "Sin alerta: el sistema clasifica la operación como normal."
    else:
        partes = [f"Alerta de {diagnostico['nombre'].lower()} (puntaje {diagnostico['puntaje']:.0%})."]
        partes.append("El modelo se apoyó sobre todo en " + ", ".join(f"{v} ({w:.0%})" for v, w in top) + ".")
        if diagnostico["reglas"]:
            premisas = [f"{p['variable']} = {p['valor']:.2f} ({p['operador']} {p['umbral']:g})"
                        for r in diagnostico["reglas"][:1] for p in r["premisas"] if p["variable"] and p["valor"] is not None]
            partes.append(f"La respalda la regla {diagnostico['reglas'][0]['id']}: " + "; ".join(premisas) + ".")
        else:
            partes.append("Ninguna regla la respalda todavía: es una alerta solo del modelo.")
        if diagnostico["expresiones"]:
            partes.append("Un técnico reportó: \"" + diagnostico["expresiones"][0] + "\".")
        if diagnostico["acciones"]:
            partes.append(f"Acción sugerida: {diagnostico['acciones'][0]}")
        texto = " ".join(partes)
    return {
        **diagnostico,
        "variables_influyentes": [{"variable": v, "peso": float(w), "en_reglas": v in en_reglas} for v, w in top],
        "concordancia_reglas": len({v for v, _ in top} & en_reglas) / k if en_reglas else None,
        "texto": texto,
    }


# ---------------------------------------------------------------------------------------
# Evaluación por activo
# ---------------------------------------------------------------------------------------
def _diagnosticos(
    v: Ventanas, activo: str, variables: list[str], datos_dir: Path, base: BaseConocimiento, horas: float
):
    df = pd.read_parquet(datos_dir / f"{activo}.parquet", columns=["ts", "unidad", *variables])
    obs = pd.read_parquet(datos_dir / "observaciones.parquet")
    lineas = lineas_base(df, variables)
    textos = textos_por_ventana(obs[obs["activo"] == activo], v.unidad, v.ts, horas)
    motor = MotorReglas(base)
    return [
        motor.diagnosticar(activo, dict(zip(variables, v.crudo[i].astype(float), strict=True)),
                           lineas[str(v.unidad[i])], texto_tecnico=textos[i])
        for i in range(len(v))
    ]


def evaluar_activo(
    activo: str, cfg: dict[str, Any], datos_dir: Path, arquitectura: str, fusion: dict[str, Any],
    muestras: int, base: BaseConocimiento,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    d = cfg["datos"]
    datos = cargar_activo(activo, datos_dir, d["ventana_pasos"], d["paso_ventana"], base)
    modelo, ck = cargar_modelo(RAIZ / cfg["rutas"]["checkpoints"] / f"{activo}_{arquitectura}_s{cfg['semilla_principal']}.pt",
                               d["ventana_pasos"], cfg)
    rng = np.random.default_rng(cfg["semilla_principal"])
    v = datos.particiones["test"].sin_grises()
    pred = _proba(modelo, arquitectura, v.X, ck["temperatura"]).argmax(1)
    aciertos = np.flatnonzero((v.y != 0) & (pred == v.y))
    elegidas = np.sort(rng.choice(aciertos, min(muestras, aciertos.size), replace=False))
    m = v.subconjunto(elegidas)
    objetivo = m.y

    importancia = importancia_por_variable(modelo, arquitectura, m.X, objetivo)
    diags = _diagnosticos(m, activo, datos.variables, datos_dir, base, d["ventana_pasos"] / PASOS_POR_HORA)
    reglas = [
        {datos.variables.index(p.variable) for r in dg.reglas_disparadas if r.modo == datos.clases[c]
         for p in r.premisas if p.variable in datos.variables}
        for dg, c in zip(diags, objetivo, strict=True)
    ]
    firma = [variables_de_firma(datos.clases[c], datos.variables, base) for c in objetivo]
    azar_firma = float(np.mean([len(f) / len(datos.variables) for f in firma]))
    resumen = {
        "activo": activo, "arquitectura": arquitectura, "alertas_explicadas": int(len(m)),
        **fidelidad(modelo, arquitectura, m.X, objetivo, importancia, ck["temperatura"], TOP_K, rng),
        **{f"estabilidad_ruido_{r:g}": estabilidad(modelo, arquitectura, m.X, objetivo, importancia, rng, r)
           for r in RUIDOS_ESTABILIDAD},
        "top_k_en_firma": acierto_en_top_k(importancia, firma, TOP_K),
        "top_k_en_firma_azar": azar_firma,
        "top_k_en_reglas": acierto_en_top_k(importancia, reglas, TOP_K),
        "alertas_con_reglas_pct": float(100 * np.mean([bool(r) for r in reglas])),
    }

    par = ParametrosFusion(fusion["alfa"], fusion["veto"], fusion["fc_min"])
    proba = _proba(modelo, arquitectura, m.X, ck["temperatura"])
    ejemplos, vistos = [], set()
    for i in range(len(m)):  # un ejemplo por modo, priorizando los que tienen reglas y observación
        modo = datos.clases[objetivo[i]]
        if modo in vistos:
            continue
        diag = diagnostico_hibrido(activo, datos.clases, proba[i], diags[i], par, base)
        imp = dict(zip(datos.variables, importancia[i].astype(float), strict=True))
        ejemplos.append({"unidad": str(m.unidad[i]), "ts": str(pd.Timestamp(m.ts[i])), **explicar_alerta(diag, imp)})
        vistos.add(modo)
    return resumen, ejemplos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Explicabilidad: gradientes integrados y traza de reglas.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--activos", nargs="*", default=None)
    ap.add_argument("--muestras", default=300, type=int)
    args = ap.parse_args(argv)
    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    base = cargar_base()
    tablas = RAIZ / cfg["rutas"]["tablas"]
    seleccion = json.loads((tablas / "modelos_seleccion.json").read_text(encoding="utf-8"))
    fusion = json.loads((tablas / "fusion_parametros.json").read_text(encoding="utf-8"))
    filas, ejemplos = [], {}
    for activo in args.activos or list(base.activos):
        resumen, ej = evaluar_activo(activo, cfg, args.datos, seleccion[activo], fusion[activo], args.muestras, base)
        filas.append(resumen)
        ejemplos[activo] = ej
        print(f"[{activo}] " + json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in resumen.items()}), flush=True)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(tablas / "xai_metricas.csv", index=False)
    (tablas / "xai_ejemplos.json").write_text(json.dumps(ejemplos, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(tabla.drop(columns=["activo", "arquitectura"]).mean(numeric_only=True).round(3).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
