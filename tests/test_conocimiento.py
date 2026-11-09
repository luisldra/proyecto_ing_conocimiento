"""Coherencia de la base de conocimiento de la Fase 1 (rol QA).

Cruza configs/assets.yaml, configs/failure_modes.yaml, knowledge/acquisition/fmea.yaml,
knowledge/rules/rules.yaml, knowledge/lexicon/expresiones.yaml y decisiones.md.
Previene ERR-004 (IDs incoherentes entre YAML) y ERR-010 (firmas que no activan reglas).
"""

from __future__ import annotations

import re

import pytest
import yaml


def _yaml(raiz, ruta):
    return yaml.safe_load((raiz / ruta).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kb(raiz):
    assets = _yaml(raiz, "configs/assets.yaml")
    modos = _yaml(raiz, "configs/failure_modes.yaml")["modos_falla"]
    fmea = {k: v for k, v in _yaml(raiz, "knowledge/acquisition/fmea.yaml").items()
            if isinstance(v, list)}
    reglas = _yaml(raiz, "knowledge/rules/rules.yaml")
    lexico = _yaml(raiz, "knowledge/lexicon/expresiones.yaml")
    decisiones = re.findall(
        r"^## (D-\d{3})\b", (raiz / "knowledge/acquisition/decisiones.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    return {"activos": assets["activos"], "sintomas": assets["sintomas"], "modos": modos,
            "fmea": fmea, "reglas": reglas, "lexico": lexico, "decisiones": set(decisiones)}


def _componente(modo, activo):
    return modo.get("componentes_por_activo", {}).get(activo, modo["componente"])


def _valor_final(variable, cambio):
    """Valor de la variable al final de la degradación (ver encabezado de failure_modes.yaml)."""
    nominal = sum(variable["nominal"]) / 2
    return {"valor": cambio["valor"], "delta": nominal + cambio["valor"],
            "factor": nominal * cambio["valor"],
            "frac_alerta": variable["alerta"] * cambio["valor"]}[cambio["tipo"]]


def _se_activa(variable, nivel, valor):
    alta = variable["direccion"] == "alta"
    if nivel == "alerta":
        return valor >= variable["alerta"] if alta else valor <= variable["alerta"]
    if nivel == "critico":
        return valor >= variable["critico"] if alta else valor <= variable["critico"]
    if nivel == "alerta_baja":
        return valor <= variable["alerta_baja"]
    raise ValueError(nivel)


def _sintomas_con_umbral(kb, nombres):
    """Síntomas medidos cuyo nivel se puede comprobar con el valor final de una firma."""
    s = kb["sintomas"]
    return [n for n in nombres if s[n]["tipo"] == "medido" and s[n]["nivel"] in
            ("alerta", "critico", "alerta_baja")]


# ------------------------------- reglas -------------------------------------------------
def test_reglas_ids_unicos_y_fc_validos(kb):
    ids = [r["id"] for r in kb["reglas"]]
    assert len(ids) == len(set(ids))
    assert all(0 < r["fc"] <= 1 for r in kb["reglas"])


def test_reglas_referencias_validas(kb):
    for r in kb["reglas"]:
        assert r["entonces"] in kb["modos"], r["id"]
        assert r["activo"] in kb["modos"][r["entonces"]]["activos"], r["id"]
        for s in r["si"]:
            assert s in kb["sintomas"], (r["id"], s)


def test_reglas_variables_existen_en_el_activo(kb):
    for r in kb["reglas"]:
        variables = kb["activos"][r["activo"]]["variables"]
        for s in r["si"]:
            sd = kb["sintomas"][s]
            if sd["tipo"] == "medido":
                assert sd["variable"] in variables, (r["id"], s, sd["variable"])


def test_reglas_con_sintoma_percibido_no_superan_08(kb):
    for r in kb["reglas"]:
        if any(kb["sintomas"][s]["tipo"] == "percibido" for s in r["si"]):
            assert r["fc"] <= 0.8, r["id"]


def test_reglas_trazables_a_decisiones(kb):
    for r in kb["reglas"]:
        assert r["fuentes"], r["id"]
        assert set(r["fuentes"]) <= kb["decisiones"], (r["id"], r["fuentes"])


def test_decisiones_citadas_existen(kb, raiz):
    rutas = ["configs/assets.yaml", "configs/failure_modes.yaml", "knowledge/rules/rules.yaml",
             "knowledge/lexicon/expresiones.yaml", "knowledge/acquisition/fmea.yaml"]
    for ruta in rutas:
        citadas = set(re.findall(r"D-\d{3}", (raiz / ruta).read_text(encoding="utf-8")))
        assert citadas <= kb["decisiones"], (ruta, citadas - kb["decisiones"])


# --------------------------------- FMEA -------------------------------------------------
def test_fmea_coherente_con_modos_y_activos(kb):
    for activo, filas in kb["fmea"].items():
        for f in filas:
            modo = kb["modos"][f["modo_falla"]]
            assert activo in modo["activos"], (activo, f["modo_falla"])
            assert _componente(modo, activo) == f["componente"], (activo, f["modo_falla"])
            assert f["componente"] in kb["activos"][activo]["componentes"], (activo, f["componente"])
            assert all(s in kb["sintomas"] for s in f["sintomas"]), (activo, f["modo_falla"])
            assert f["severidad"] * f["ocurrencia"] * f["deteccion"] == f["npr"]


def test_cada_modo_activo_tiene_fila_fmea_y_regla(kb):
    con_regla = {(r["activo"], r["entonces"]) for r in kb["reglas"]}
    for nombre, modo in kb["modos"].items():
        for activo in modo["activos"]:
            assert nombre in [f["modo_falla"] for f in kb["fmea"][activo]], (activo, nombre)
            assert (activo, nombre) in con_regla, f"sin regla: {activo}/{nombre}"


def test_sintomas_de_la_fmea_miden_variables_del_activo(kb):
    for activo, filas in kb["fmea"].items():
        variables = kb["activos"][activo]["variables"]
        for f in filas:
            for s in f["sintomas"]:
                sd = kb["sintomas"][s]
                if sd["tipo"] == "medido":
                    assert sd["variable"] in variables, (activo, f["modo_falla"], s)


# ------------------------- firmas del simulador vs síntomas ------------------------------
def _problemas_firma(kb, activo, nombre_modo, sintomas, origen):
    firma = {f["variable"]: f for f in kb["modos"][nombre_modo]["firma"]}
    variables = kb["activos"][activo]["variables"]
    problemas = []
    for s in _sintomas_con_umbral(kb, sintomas):
        sd = kb["sintomas"][s]
        v = sd["variable"]
        if v not in firma:
            problemas.append(f"{origen}: {activo}/{nombre_modo} no modifica {v} (síntoma {s})")
            continue
        valor = _valor_final(variables[v], firma[v]["cambio"])
        if not _se_activa(variables[v], sd["nivel"], valor):
            problemas.append(
                f"{origen}: {activo}/{nombre_modo} termina en {valor:g} y no activa {s}")
    return problemas


def test_firma_activa_los_sintomas_medidos_de_la_fmea(kb):
    problemas = []
    for activo, filas in kb["fmea"].items():
        for f in filas:
            problemas += _problemas_firma(kb, activo, f["modo_falla"], f["sintomas"], "FMEA")
    assert not problemas, "\n".join(problemas)


def test_firma_activa_las_premisas_de_cada_regla(kb):
    problemas = []
    for r in kb["reglas"]:
        problemas += _problemas_firma(kb, r["activo"], r["entonces"], r["si"], r["id"])
    assert not problemas, "\n".join(problemas)


def test_toda_firma_tiene_variables_en_cada_activo(kb):
    for nombre, modo in kb["modos"].items():
        for activo in modo["activos"]:
            variables = kb["activos"][activo]["variables"]
            assert any(f["variable"] in variables for f in modo["firma"]), (nombre, activo)


# --------------------------------- léxico -----------------------------------------------
def test_lexico_referencias_validas(kb):
    for e in kb["lexico"]:
        assert e["sintoma_percibido"] in kb["sintomas"], e["id"]
        assert all(s in kb["sintomas"] for s in e["sintomas_formales"]), e["id"]
        for c in e["modos_falla_candidatos"]:
            assert c["id"] in kb["modos"], (e["id"], c["id"])
            assert c["fc_max"] <= 0.6, (e["id"], c["id"])
