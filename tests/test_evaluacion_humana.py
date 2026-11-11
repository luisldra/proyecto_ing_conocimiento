"""Pruebas del instrumento de evaluación humana. Las respuestas aquí son ficticias y solo
comprueban el cálculo; no son resultados del proyecto."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from metaltech.xai.evaluacion_humana import (
    COLUMNAS,
    DIMENSIONES,
    analizar,
    preparar,
    seleccionar,
    texto_solo_modelo,
    validar,
)

EJEMPLO = {
    "modo": "cavitacion", "nombre": "Cavitación", "probabilidad_modelo": 0.9, "respaldo_reglas": True,
    "texto": "Alerta de cavitación… La respalda la regla R13…",
    "variables_influyentes": [{"variable": "npsh_margen_ratio", "peso": 0.6, "en_reglas": True}],
}


def test_explicacion_solo_modelo_no_menciona_reglas_ni_acciones():
    t = texto_solo_modelo(EJEMPLO)
    assert "npsh_margen_ratio (60%)" in t and "regla" not in t.lower() and "acción" not in t.lower()


def test_seleccion_mezcla_alertas_con_y_sin_reglas():
    ejemplos = {"a": [EJEMPLO, {**EJEMPLO, "modo": "x", "respaldo_reglas": False}, {**EJEMPLO, "modo": "y"}]}
    elegidas = seleccionar(ejemplos)
    assert len(elegidas) == 2 and {e["respaldo_reglas"] for e in elegidas} == {True, False}


def test_preparar_contrabalancea_y_oculta_la_variante(tmp_path):
    clave = preparar(tmp_path)
    assert (clave.groupby("alerta")["variante"].nunique() == 2).all()
    primeras = clave[clave["explicacion"] == 1]["variante"]
    assert set(primeras) == {"hibrida", "modelo"}  # el orden alterna entre alertas
    formulario = (tmp_path / "formulario.md").read_text(encoding="utf-8")
    assert "hibrida" not in formulario and "modelo solo" not in formulario
    plantilla = pd.read_csv(tmp_path / "respuestas_plantilla.csv")
    assert list(plantilla.columns) == COLUMNAS


def _respuestas(clave: pd.DataFrame, evaluadores: int, mejora: int) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    filas = []
    for e in range(1, evaluadores + 1):
        for _, k in clave.iterrows():
            base = int(rng.integers(2, 4))
            valor = min(5, base + mejora) if k["variante"] == "hibrida" else base
            filas.append({"evaluador": f"E{e:02d}", "perfil": "estudiante", "alerta": k["alerta"],
                          "explicacion": k["explicacion"], **dict.fromkeys(DIMENSIONES, valor),
                          "preferida": k["explicacion"] if k["variante"] == "hibrida" else "", "comentario": ""})
    return pd.DataFrame(filas)


def test_analisis_detecta_una_mejora_clara(tmp_path):
    clave = preparar(tmp_path)
    tabla, resumen = analizar(_respuestas(clave, 4, 2), clave)
    medias = tabla.pivot(index="dimension", columns="variante", values="media")
    assert (medias["hibrida"] > medias["modelo"]).all()
    assert resumen["pruebas"]["utilidad"]["p_wilcoxon"] < 0.05
    assert resumen["preferencia"] == {"hibrida": 4 * clave["alerta"].nunique()}


def test_preferencia_leida_desde_csv_como_numero(tmp_path):
    clave = preparar(tmp_path)
    ruta = tmp_path / "r.csv"
    _respuestas(clave, 2, 1).to_csv(ruta, index=False)
    _, resumen = analizar(pd.read_csv(ruta), clave)  # 'preferida' llega como 1.0 / 2.0
    assert resumen["preferencia"] == {"hibrida": 2 * clave["alerta"].nunique()}


def test_controles_de_longitud_para_el_panel_de_agentes(tmp_path):
    clave = preparar(tmp_path, controles=True)
    controles = clave[clave["variante"].str.startswith("control")]
    assert controles["alerta"].nunique() == 2 and (tmp_path / "formulario_agentes.md").exists()
    filas = _respuestas(clave[~clave["variante"].str.startswith("control")], 3, 1)
    for e in range(1, 4):  # un panel sin sesgo califica igual el relleno y el texto simple
        filas = pd.concat([filas, pd.DataFrame([
            {"evaluador": f"E{e:02d}", "perfil": "agente", "alerta": k["alerta"], "explicacion": k["explicacion"],
             **dict.fromkeys(DIMENSIONES, 3), "preferida": "", "comentario": ""} for _, k in controles.iterrows()])])
    _, resumen = analizar(filas, clave)
    assert resumen["control_longitud"]["utilidad"]["diferencia_media"] == 0


def test_validar_rechaza_valores_fuera_de_escala():
    r = pd.DataFrame([{c: 1 for c in COLUMNAS} | {"utilidad": 7}])
    with pytest.raises(ValueError, match="utilidad"):
        validar(r)
