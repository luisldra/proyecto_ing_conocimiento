"""Sistemas M0 y M3 y el diagnóstico híbrido explicable (Fase 5).

M0: la certeza de las reglas como probabilidad por clase.
M3: ``s = alfa * p_DL + (1 - alfa) * certeza_reglas``, con veto opcional: una alerta del
modelo sin respaldo de reglas (certeza < ``fc_min``) vuelve a normal. ``alfa`` y el veto se
eligen en validación con un criterio fijado de antemano (D-056).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from metaltech.kb.base import BaseConocimiento
from metaltech.kb.rules_engine import Diagnostico
from metaltech.models.evaluate import metricas


@dataclass(frozen=True)
class ParametrosFusion:
    alfa: float
    veto: bool
    fc_min: float


def proba_m0(fc: np.ndarray) -> np.ndarray:
    """Certezas de las reglas normalizadas por fila (sin reglas disparadas = normal)."""
    return fc / np.maximum(fc.sum(axis=1, keepdims=True), 1e-9)


def fusionar(p_dl: np.ndarray, fc: np.ndarray, parametros: ParametrosFusion) -> np.ndarray:
    s = parametros.alfa * p_dl + (1 - parametros.alfa) * proba_m0(fc)
    if parametros.veto:
        pred = s.argmax(axis=1)
        sin_respaldo = (pred != 0) & (fc[np.arange(len(pred)), pred] < parametros.fc_min)
        s = s.copy()
        s[sin_respaldo, 0] = s[sin_respaldo].max(axis=1) + 1e-6
    return s


def elegir_fusion(
    p_dl: np.ndarray, fc: np.ndarray, y: np.ndarray, alfas: list[float], fc_min: float
) -> tuple[ParametrosFusion, list[dict[str, Any]]]:
    """Mayor F1 macro en validación; empate: menor falsa alarma y luego mayor alfa."""
    rejilla = []
    for alfa in alfas:
        for veto in (False, True):
            par = ParametrosFusion(alfa, veto, fc_min)
            m = metricas(y, fusionar(p_dl, fc, par))
            rejilla.append({"alfa": alfa, "veto": veto, "f1_macro": m["f1_macro"], "falsa_alarma": m["falsa_alarma"]})
    mejor = max(rejilla, key=lambda r: (round(r["f1_macro"], 6), -r["falsa_alarma"], r["alfa"]))
    return ParametrosFusion(mejor["alfa"], mejor["veto"], fc_min), rejilla


def diagnostico_hibrido(
    activo: str, clases: list[str], p_dl: np.ndarray, diag: Diagnostico,
    parametros: ParametrosFusion, base: BaseConocimiento,
) -> dict[str, Any]:
    """Diagnóstico de una ventana: falla, puntajes, reglas que lo sustentan, causas y acciones."""
    fc = np.zeros(len(clases), dtype=np.float32)
    for c in diag.conclusiones:
        fc[clases.index(c.modo)] = c.fc
    fc[0] = 1.0 - fc[1:].max(initial=0.0)
    s = fusionar(p_dl[None, :], fc[None, :], parametros)[0]
    k = int(s.argmax())
    modo = clases[k]
    reglas = [r for r in diag.reglas_disparadas if r.modo == modo]
    filas = [f for f in base.fmea.get(activo, []) if f.get("modo_falla") == modo]
    return {
        "activo": activo,
        "modo": modo,
        "nombre": base.modos[modo]["nombre"] if modo in base.modos else "Operación normal",
        "puntaje": float(s[k]),
        "probabilidad_modelo": float(p_dl[k]),
        "certeza_reglas": float(fc[k]) if k else 0.0,
        "respaldo_reglas": bool(reglas),
        "reglas": [
            {"id": r.id, "fc": r.fc_conclusion, "premisas": [
                {"sintoma": p.sintoma, "variable": p.variable, "valor": p.valor, "umbral": p.umbral, "operador": p.operador}
                for p in r.premisas
            ]} for r in reglas
        ],
        "causas": sorted({c for f in filas for c in f.get("causas", [])}),
        "acciones": list(dict.fromkeys([r.accion for r in reglas] + [a for f in filas for a in f.get("acciones", [])])),
        "expresiones": [e.expresion for e in diag.expresiones],
        "alternativas": [
            {"modo": clases[j], "puntaje": float(s[j])} for j in np.argsort(-s)[1:4] if s[j] > 0
        ],
    }
