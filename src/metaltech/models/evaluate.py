"""Métricas de clasificación por ventana (Fase 4)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def metricas(y: np.ndarray, proba: np.ndarray) -> dict[str, float]:
    """Macro sobre las clases presentes en ``y``; la clase 0 es la operación normal."""
    pred = proba.argmax(axis=1)
    presentes = np.unique(y)
    p, r, f, _ = precision_recall_fscore_support(y, pred, labels=presentes, average=None, zero_division=0)
    pr_auc = [average_precision_score(y == c, proba[:, c]) for c in presentes]
    fallas = presentes != 0
    normales, con_falla = y == 0, y != 0
    return {
        "f1_macro": float(f.mean()),
        "f1_macro_fallas": float(f[fallas].mean()) if fallas.any() else float("nan"),
        "precision_macro": float(p.mean()),
        "recall_macro": float(r.mean()),
        "pr_auc_macro": float(np.mean(pr_auc)),
        "falsa_alarma": float((pred[normales] != 0).mean()) if normales.any() else float("nan"),
        "alerta_correcta_binaria": float((pred[con_falla] != 0).mean()) if con_falla.any() else float("nan"),
        "ventanas": int(y.size),
        "ventanas_falla": int(con_falla.sum()),
    }


def aviso_temprano(
    pred: np.ndarray, modo: np.ndarray, horas_a_falla: np.ndarray, unidad: np.ndarray, ts: np.ndarray
) -> dict[str, float]:
    """Sobre ventanas grises (degradación a más de H): ¿se avisó y con qué anticipación? (D-054)."""
    if pred.size == 0:
        return {"aviso_ventanas_pct": float("nan"), "aviso_episodios_pct": float("nan"), "anticipacion_mediana_h": float("nan")}
    falla = pd.to_datetime(ts) + pd.to_timedelta(horas_a_falla.astype(float), unit="h")
    df = pd.DataFrame({"unidad": unidad, "falla": falla.round("10min"), "acierto": pred == modo, "horas": horas_a_falla})
    por_episodio = df.groupby(["unidad", "falla"])
    con_aviso = df[df["acierto"]].groupby(["unidad", "falla"])["horas"].max()
    return {
        "aviso_ventanas_pct": float(100 * df["acierto"].mean()),
        "aviso_episodios_pct": float(100 * len(con_aviso) / por_episodio.ngroups),
        "anticipacion_mediana_h": float(con_aviso.median()) if len(con_aviso) else float("nan"),
    }


def metricas_por_clase(y: np.ndarray, proba: np.ndarray, clases: list[str]) -> list[dict[str, Any]]:
    pred = proba.argmax(axis=1)
    presentes = np.unique(y)
    p, r, f, n = precision_recall_fscore_support(y, pred, labels=presentes, average=None, zero_division=0)
    return [
        {"clase": clases[c], "soporte": int(s), "precision": float(a), "recall": float(b), "f1": float(d)}
        for c, a, b, d, s in zip(presentes, p, r, f, n, strict=True)
    ]


def matriz_confusion(y: np.ndarray, proba: np.ndarray, clases: list[str]) -> np.ndarray:
    return confusion_matrix(y, proba.argmax(axis=1), labels=list(range(len(clases))))
