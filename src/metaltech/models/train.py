"""Entrenamiento de MLP, CNN1D y LSTM por tipo de activo (Fase 4).

La arquitectura de cada activo se elige solo con validación; test se reporta y no decide
nada. Decisiones en D-053.

Uso: ``python -m metaltech.models.train [--activos a b] [--arquitecturas mlp cnn1d lstm]``
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml
from torch import nn
from torch.nn import functional as F

from metaltech.data.features import (
    DatosActivo,
    balancear_entrenamiento,
    cargar_activo,
    variables_agregadas,
)
from metaltech.kb.base import RAIZ, cargar_base
from metaltech.models.cnn1d import CNN1D
from metaltech.models.evaluate import aviso_temprano, matriz_confusion, metricas, metricas_por_clase
from metaltech.models.lstm import LSTM
from metaltech.models.mlp import MLP

ARQUITECTURAS = ("mlp", "cnn1d", "lstm")
LOTE_INFERENCIA = 4096


def crear_modelo(arquitectura: str, variables: int, pasos: int, clases: int, cfg: dict[str, Any]) -> nn.Module:
    c = cfg["modelos"][arquitectura]
    if arquitectura == "mlp":
        entradas = variables_agregadas(np.zeros((1, pasos, variables), dtype=np.float32)).shape[1]
        return MLP(entradas, clases, c["ocultas"], c["dropout"])
    if arquitectura == "cnn1d":
        return CNN1D(variables, clases, c["canales"], c["kernel"], c["dropout"])
    if arquitectura == "lstm":
        return LSTM(variables, clases, c["ocultas"], c["capas"], c["dropout"])
    raise ValueError(f"arquitectura desconocida: {arquitectura}")


def entradas_de(arquitectura: str, X: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(variables_agregadas(X) if arquitectura == "mlp" else X)


def perdida_focal(logits: torch.Tensor, y: torch.Tensor, pesos: torch.Tensor, gamma: float) -> torch.Tensor:
    ce = F.cross_entropy(logits, y, reduction="none")
    return (pesos[y] * (1 - torch.exp(-ce)) ** gamma * ce).mean()


def pesos_de_clase(y: np.ndarray, clases: int) -> torch.Tensor:
    """Inverso de la raíz de la frecuencia, con media 1 entre las clases observadas."""
    conteo = np.bincount(y, minlength=clases).astype(np.float32)
    pesos = np.where(conteo > 0, 1 / np.sqrt(np.maximum(conteo, 1)), 0.0)
    return torch.from_numpy((pesos / pesos[conteo > 0].mean()).astype(np.float32))


@torch.no_grad()
def predecir_logits(modelo: nn.Module, x: torch.Tensor) -> torch.Tensor:
    modelo.eval()
    return torch.cat([modelo(x[i : i + LOTE_INFERENCIA]) for i in range(0, len(x), LOTE_INFERENCIA)])


def ajustar_temperatura(logits: torch.Tensor, y: torch.Tensor) -> float:
    """Calibración en validación: no cambia la clase predicha, solo la confianza."""
    log_t = torch.zeros(1, requires_grad=True)
    optimizador = torch.optim.LBFGS([log_t], lr=0.1, max_iter=50)

    def paso() -> torch.Tensor:
        optimizador.zero_grad()
        perdida = F.cross_entropy(logits / log_t.exp(), y)
        perdida.backward()
        return perdida

    optimizador.step(paso)
    return float(log_t.detach().exp())


def probabilidades(logits: torch.Tensor, temperatura: float) -> np.ndarray:
    return F.softmax(logits / temperatura, dim=1).numpy()


@dataclass
class Entrenado:
    modelo: nn.Module
    temperatura: float
    epocas: int
    segundos: float
    f1_val: float


def entrenar(datos: DatosActivo, arquitectura: str, semilla: int, cfg: dict[str, Any]) -> Entrenado:
    """Ajuste con detención temprana sobre el F1 macro de validación."""
    torch.manual_seed(semilla)
    rng = np.random.default_rng(semilla)
    e = cfg["entrenamiento"]
    train = balancear_entrenamiento(datos.particiones["train"].sin_grises(), e["negativos_por_positivo"], rng)
    val = datos.particiones["val"].sin_grises()
    x_train, y_train = entradas_de(arquitectura, train.X), torch.from_numpy(train.y)
    x_val, y_val = entradas_de(arquitectura, val.X), torch.from_numpy(val.y)
    modelo = crear_modelo(arquitectura, train.X.shape[2], train.X.shape[1], len(datos.clases), cfg)
    optimizador = torch.optim.Adam(modelo.parameters(), lr=e["lr"], weight_decay=e["weight_decay"])
    pesos = pesos_de_clase(train.y, len(datos.clases))

    inicio = time.perf_counter()
    mejor_f1, mejor_estado, sin_mejora, epocas_usadas = -1.0, None, 0, 0
    for epoca in range(1, e["epocas"] + 1):
        epocas_usadas = epoca
        modelo.train()
        orden = torch.randperm(len(x_train))
        for i in range(0, len(orden), e["batch"]):
            lote = orden[i : i + e["batch"]]
            optimizador.zero_grad()
            perdida = perdida_focal(modelo(x_train[lote]), y_train[lote], pesos, e["focal_gamma"])
            perdida.backward()
            optimizador.step()
        f1 = metricas(val.y, F.softmax(predecir_logits(modelo, x_val), dim=1).numpy())["f1_macro"]
        if f1 > mejor_f1:
            mejor_f1, mejor_estado, sin_mejora = f1, copy.deepcopy(modelo.state_dict()), 0
        else:
            sin_mejora += 1
            if sin_mejora >= e["early_stopping_paciencia"]:
                break
    modelo.load_state_dict(mejor_estado)
    temperatura = ajustar_temperatura(predecir_logits(modelo, x_val), y_val)
    return Entrenado(modelo, temperatura, epocas_usadas, time.perf_counter() - inicio, mejor_f1)


def guardar_modelo(ruta: Path, datos: DatosActivo, arquitectura: str, semilla: int, r: Entrenado) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "estado": r.modelo.state_dict(), "arquitectura": arquitectura, "semilla": semilla,
        "activo": datos.activo, "variables": datos.variables, "clases": datos.clases,
        "media": datos.media, "desviacion": datos.desviacion, "temperatura": r.temperatura,
    }, ruta)


def ejecutar(args: argparse.Namespace) -> pd.DataFrame:
    with open(args.config, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if args.epocas is not None:
        cfg["entrenamiento"]["epocas"] = args.epocas
    base = cargar_base()
    semilla = args.semilla if args.semilla is not None else cfg["semilla_principal"]
    tablas, modelos = RAIZ / cfg["rutas"]["tablas"], RAIZ / cfg["rutas"]["checkpoints"]
    tablas.mkdir(parents=True, exist_ok=True)
    filas, por_clase, seleccion = [], [], {}
    for activo in args.activos or list(base.activos):
        datos = cargar_activo(activo, args.datos, cfg["datos"]["ventana_pasos"], cfg["datos"]["paso_ventana"], base)
        print(f"[{activo}] " + str({p: len(v) for p, v in datos.particiones.items()}), flush=True)
        resultados = {}
        for arquitectura in args.arquitecturas:
            r = entrenar(datos, arquitectura, semilla, cfg)
            guardar_modelo(modelos / f"{activo}_{arquitectura}_s{semilla}.pt", datos, arquitectura, semilla, r)
            resultados[arquitectura] = r
            for particion in ("val", "test", "test_unidad"):
                todas = datos.particiones[particion]
                proba_todas = probabilidades(predecir_logits(r.modelo, entradas_de(arquitectura, todas.X)), r.temperatura)
                g = todas.gris
                aviso = aviso_temprano(proba_todas[g].argmax(1), todas.modo[g], todas.horas_a_falla[g], todas.unidad[g], todas.ts[g])
                v, proba = todas.sin_grises(), proba_todas[~g]
                filas.append({"activo": activo, "arquitectura": arquitectura, "semilla": semilla, "particion": particion,
                              **metricas(v.y, proba), **aviso, "epocas": r.epocas, "segundos": round(r.segundos, 1),
                              "temperatura": round(r.temperatura, 3)})
                por_clase += [{"activo": activo, "arquitectura": arquitectura, "particion": particion, **c}
                              for c in metricas_por_clase(v.y, proba, datos.clases)]
            print(f"  {arquitectura}: f1_val={r.f1_val:.3f} epocas={r.epocas} {r.segundos:.0f}s", flush=True)
        mejor = max(resultados, key=lambda a: resultados[a].f1_val)
        seleccion[activo] = mejor
        v = datos.particiones["test"].sin_grises()
        proba = probabilidades(predecir_logits(resultados[mejor].modelo, entradas_de(mejor, v.X)), resultados[mejor].temperatura)
        pd.DataFrame(matriz_confusion(v.y, proba, datos.clases), index=datos.clases, columns=datos.clases).to_csv(
            tablas / f"modelos_confusion_{activo}.csv"
        )
    resultado = pd.DataFrame(filas)
    resultado.to_csv(tablas / "modelos_resultados.csv", index=False)
    pd.DataFrame(por_clase).to_csv(tablas / "modelos_por_clase.csv", index=False)
    (tablas / "modelos_seleccion.json").write_text(json.dumps(seleccion, indent=2), encoding="utf-8")
    return resultado


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Entrena los modelos de Deep Learning por activo.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--datos", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--activos", nargs="*", default=None)
    ap.add_argument("--arquitecturas", nargs="*", default=list(ARQUITECTURAS), choices=ARQUITECTURAS)
    ap.add_argument("--semilla", default=None, type=int)
    ap.add_argument("--epocas", default=None, type=int)
    resultado = ejecutar(ap.parse_args(argv))
    columnas = ["activo", "arquitectura", "particion", "f1_macro", "precision_macro", "recall_macro", "falsa_alarma", "epocas"]
    print(resultado[columnas].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
