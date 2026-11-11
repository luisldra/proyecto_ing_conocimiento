"""Pruebas de la Fase 7: intervalos, equidad e impacto (datos pequeños construidos a mano)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from metaltech.metrics.equidad import brechas, observacion_por_ventana, tasas
from metaltech.metrics.impacto import episodios, eventos_falsa_alarma, impacto
from metaltech.metrics.intervalos import diferencias, intervalo, por_sistema


# ----------------------------------------------------------------------------------------
# Intervalos
# ----------------------------------------------------------------------------------------
def test_intervalo_t_de_student():
    media, lo, hi = intervalo(np.array([1.0, 2.0, 3.0]))
    assert media == 2.0 and lo == pytest.approx(2 - 4.303 * 1 / np.sqrt(3), abs=1e-3) and hi > 3


def test_intervalo_con_un_solo_valor_es_degenerado():
    assert intervalo(np.array([0.5])) == (0.5, 0.5, 0.5)


def _tabla():
    filas = []
    for semilla in range(5):
        for activo in ("a", "b"):
            for sistema, f1 in (("M1", 0.90), ("M3", 0.92)):
                filas.append({"particion": "test", "semilla": semilla, "activo": activo, "sistema": sistema,
                              "f1_macro": f1 + 0.001 * semilla, **dict.fromkeys(
                                  ["precision_macro", "recall_macro", "falsa_alarma_sin_confusor",
                                   "falsa_alarma_con_confusor", "aviso_episodios_pct", "anticipacion_mediana_h"], 0.5)})
    return pd.DataFrame(filas)


def test_por_sistema_promedia_activos_y_da_intervalo_entre_semillas():
    t = por_sistema(_tabla())
    f1 = t[(t["sistema"] == "M3") & (t["metrica"] == "f1_macro")].iloc[0]
    assert f1["semillas"] == 5 and f1["ic95_inf"] < f1["media"] < f1["ic95_sup"]


def test_diferencias_pareadas():
    d = diferencias(_tabla(), "M3", "M1", "f1_macro", "test")
    assert d["pares"] == 10 and d["diferencia_media"] == pytest.approx(0.02) and d["a_mayor_pct"] == 100


# ----------------------------------------------------------------------------------------
# Equidad
# ----------------------------------------------------------------------------------------
def _pred(n_sanas=40, n_falla=40):
    rng = np.random.default_rng(0)
    filas = []
    for turno, error in (("manana", 0.0), ("noche", 0.5)):
        for k in range(n_sanas + n_falla):
            y = 1 if k >= n_sanas else 0
            mal = rng.random() < error
            pred = (1 - y) if mal else y
            filas.append({"semilla": 42, "turno": turno, "gris": False, "y": y,
                          **{f"pred_{s}": pred for s in ("M0", "M1", "M2", "M3")}})
    return pd.DataFrame(filas)


def test_brecha_detecta_el_grupo_peor():
    b = brechas(tasas(_pred(), "turno"))
    fila = b[b["sistema"] == "M3"].iloc[0]
    assert fila["acierto_falla_brecha"] > 0.3 and fila["acierto_falla_peor"] == "noche"


def test_grupos_pequenos_no_se_calculan():
    t = tasas(_pred(n_sanas=5, n_falla=5), "turno")
    assert t["acierto_falla"].isna().all()


def test_observacion_por_ventana():
    pred = pd.DataFrame({"unidad": ["u", "u", "u"],
                         "ts": pd.to_datetime(["2024-01-01 06:00", "2024-01-01 12:00", "2024-01-03 00:00"])})
    obs = pd.DataFrame({"unidad": ["u", "u"], "ts": pd.to_datetime(["2024-01-01 05:00", "2024-01-01 11:00"]),
                        "es_correcta": [True, False]})
    assert observacion_por_ventana(pred, obs).tolist() == ["correcta", "incorrecta", "ninguna"]


# ----------------------------------------------------------------------------------------
# Impacto
# ----------------------------------------------------------------------------------------
def _pred_impacto():
    ts = pd.date_range("2024-01-01", periods=10, freq="1h")
    base = {"semilla": 42, "activo": "a", "unidad": "u", "particion": "test"}
    filas = []
    for i, t in enumerate(ts):
        en_falla = i >= 6  # falla a las 09:00, ventanas 6–9 la anticipan
        filas.append({**base, "ts": t, "y": 1 if en_falla else 0, "modo": 1 if en_falla else 0,
                      "horas_a_falla": float(9 - i) if en_falla else np.nan,
                      "pred_M0": 0, "pred_M1": 1 if i in (1, 2, 4, 7) else 0, "pred_M2": 0, "pred_M3": 1 if i == 8 else 0})
    return pd.DataFrame(filas)


def test_episodio_detectado_y_anticipacion():
    e = episodios(_pred_impacto(), "M1")
    assert len(e) == 1 and bool(e["detectada"].iloc[0]) and e["anticipacion_h"].iloc[0] == 2.0
    assert not bool(episodios(_pred_impacto(), "M0")["detectada"].iloc[0])


def test_alarmas_consecutivas_son_un_solo_evento():
    assert int(eventos_falsa_alarma(_pred_impacto(), "M1")["eventos"].sum()) == 2  # (1,2) y (4)


def test_costo_premia_detectar_y_castiga_falsas_alarmas():
    costos = {"reparacion_planificada": 1.0, "ratio_no_planificada": [5], "falsa_alarma": 0.1}
    t = impacto(_pred_impacto(), costos).set_index("sistema")
    assert t.loc["M3", "costo_unidad_anio_r5"] < t.loc["M1", "costo_unidad_anio_r5"] < t.loc["M0", "costo_unidad_anio_r5"]
