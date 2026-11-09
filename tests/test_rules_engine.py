"""Motor de reglas: fusificación, encadenamiento, factores de certeza MYCIN y traza."""

from __future__ import annotations

import json
import math

import pytest

from metaltech.kb.base import cargar_base, valor_final, valor_nominal
from metaltech.kb.rules_engine import (
    FACTOR_TENDENCIA,
    MotorReglas,
    combinar_fc,
    combinar_fcs,
    main,
)

BASE = cargar_base()
MOTOR = MotorReglas(BASE)


# ----------------------------------------------------------------------------------------
# Construcción de casos
# ----------------------------------------------------------------------------------------
def nominales(activo: str) -> dict[str, float]:
    return {v: valor_nominal(c) for v, c in BASE.activos[activo]["variables"].items()}


def caso_positivo(regla: dict):
    """Valores, línea base y percibidos que activan exactamente las premisas de una regla."""
    cfg = BASE.activos[regla["activo"]]["variables"]
    valores = nominales(regla["activo"])
    linea_base = dict(valores)
    percibidos: list[str] = []
    fijadas: dict[str, float] = {}
    for s in regla["si"]:
        sd = BASE.sintomas[s]
        if sd["tipo"] == "percibido":
            percibidos.append(s)
            continue
        v, c, nivel = sd["variable"], cfg[sd["variable"]], sd["nivel"]
        if nivel in ("alerta", "critico"):
            nuevo = c[nivel]
        elif nivel == "alerta_baja":
            nuevo = c["alerta_baja"]
        elif nivel == "en_rango":
            nuevo = (c.get("alerta_baja", c["nominal"][0]) + c["alerta"]) / 2
        else:  # tendencia
            nuevo = valores[v] + 1.2 * FACTOR_TENDENCIA * c["alerta"]
        if v in fijadas:  # dos premisas sobre la misma variable: se toma la más extrema
            alta = c["direccion"] == "alta"
            nuevo = max(nuevo, fijadas[v]) if alta else min(nuevo, fijadas[v])
        fijadas[v] = valores[v] = nuevo
    return valores, linea_base, percibidos


REGLAS = BASE.reglas


# ----------------------------------------------------------------------------------------
# Factores de certeza
# ----------------------------------------------------------------------------------------
def test_combinar_fc_positivos():
    assert combinar_fc(0.75, 0.9) == pytest.approx(0.975)
    assert combinar_fc(0.0, 0.6) == pytest.approx(0.6)


def test_combinar_fc_es_conmutativo_y_asociativo():
    a, b, c = 0.6, 0.7, 0.85
    assert combinar_fc(a, b) == pytest.approx(combinar_fc(b, a))
    assert combinar_fcs([a, b, c]) == pytest.approx(combinar_fcs([c, a, b]))


def test_combinar_fc_signos_distintos_y_negativos():
    assert combinar_fc(0.8, -0.4) == pytest.approx(0.4 / 0.6)
    assert combinar_fc(-0.5, -0.5) == pytest.approx(-0.75)
    assert combinar_fc(1.0, -1.0) == 0.0  # evidencia totalmente contradictoria: indefinido -> 0


def test_el_fc_combinado_nunca_supera_uno():
    assert combinar_fcs([0.9, 0.9, 0.9, 0.9]) < 1.0


# ----------------------------------------------------------------------------------------
# Fusificación de síntomas
# ----------------------------------------------------------------------------------------
def test_umbral_inclusivo_y_direccion_alta():
    ev = lambda v: MOTOR.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": v})  # noqa: E731
    assert "vibracion_alerta" not in ev(2.79)
    assert ev(2.8)["vibracion_alerta"].grado == 1.0
    assert "vibracion_critica" not in ev(4.49)
    assert "vibracion_critica" in ev(4.5) and "vibracion_alerta" in ev(4.5)


def test_direccion_baja():
    ev = lambda v: MOTOR.evaluar_sintomas("bomba_centrifuga", {"npsh_margen_ratio": v})  # noqa: E731
    assert "margen_npsh_bajo" not in ev(1.31)
    assert "margen_npsh_bajo" in ev(1.3)
    assert "margen_npsh_insuficiente" in ev(1.1)


def test_corriente_en_rango_y_colas():
    ev = lambda v: MOTOR.evaluar_sintomas("motor_electrico", {"corriente_pct": v})  # noqa: E731
    assert "corriente_en_rango" in ev(80)
    assert "corriente_en_rango" not in ev(105) and "corriente_alta" in ev(105)
    assert "corriente_en_rango" not in ev(40) and "corriente_baja" in ev(40)
    assert "sobrecorriente" in ev(115) and "corriente_alta" in ev(115)


def test_tendencia_requiere_linea_base():
    sin = MOTOR.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 2.0})
    assert "vibracion_creciente" not in sin
    con = MOTOR.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 2.0}, {"vib_rms_mm_s": 1.0})
    assert con["vibracion_creciente"].valor == pytest.approx(1.0)  # cambio vs. línea base
    assert con["vibracion_creciente"].umbral == pytest.approx(0.7)  # 25 % de 2.8 (D-004)
    poco = MOTOR.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 1.5}, {"vib_rms_mm_s": 1.0})
    assert "vibracion_creciente" not in poco


def test_datos_faltantes_y_desconocidos():
    d = MOTOR.diagnosticar("motor_electrico", {"vib_rms_mm_s": math.nan, "temp_devanado_c": None,
                                               "no_existe": 3.0, "corriente_pct": 80})
    assert "vib_rms_mm_s" in d.datos_faltantes and "temp_devanado_c" in d.datos_faltantes
    assert "corriente_pct" not in d.datos_faltantes
    assert d.variables_desconocidas == ["no_existe"]
    assert "vibracion_alerta" not in d.sintomas


def test_variable_que_el_activo_no_tiene_se_ignora():
    s = MOTOR.evaluar_sintomas("motor_electrico", {"npsh_margen_ratio": 0.5})
    assert "margen_npsh_bajo" not in s


def test_percibidos_aceptan_lista_y_grados():
    s = MOTOR.evaluar_sintomas("bomba_centrifuga", {}, percibidos=["golpeteo_percibido"])
    assert s["golpeteo_percibido"].grado == 1.0 and s["golpeteo_percibido"].tipo == "percibido"
    s = MOTOR.evaluar_sintomas("bomba_centrifuga", {}, percibidos={"golpeteo_percibido": 0.5})
    assert s["golpeteo_percibido"].grado == 0.5


def test_margen_suave_crea_rampa_y_reduce_el_fc_de_la_premisa():
    suave = MotorReglas(BASE, margen_suave=0.5)
    # alerta 2.8; borde nominal 1.4; ancho = 0.5 * 1.4 = 0.7 -> rampa desde 2.1
    assert "vibracion_alerta" not in suave.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 2.1})
    g = suave.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 2.45})["vibracion_alerta"].grado
    assert g == pytest.approx(0.5)
    assert suave.evaluar_sintomas("motor_electrico", {"vib_rms_mm_s": 2.8})["vibracion_alerta"].grado == 1.0
    # el valor normal nunca activa nada, aunque haya rampa
    assert suave.diagnosticar("motor_electrico", nominales("motor_electrico")).reglas_disparadas == []


def test_margen_suave_invalido():
    with pytest.raises(ValueError):
        MotorReglas(BASE, margen_suave=1.5)


def test_fc_de_la_conclusion_usa_el_minimo_de_los_grados():
    suave = MotorReglas(BASE, margen_suave=0.5)
    vals = {"vib_rms_mm_s": 2.45, "vib_1x_frac": 0.9}  # R05: alerta (0.5) y 1X dominante (1.0)
    r = suave.diagnosticar("motor_electrico", vals).reglas_disparadas[0]
    assert r.id == "R05"
    assert r.fc_premisa == pytest.approx(0.5)
    assert r.fc_conclusion == pytest.approx(0.75 * 0.5)


def test_activo_desconocido():
    with pytest.raises(KeyError, match="activo desconocido"):
        MOTOR.diagnosticar("grua", {})


# ----------------------------------------------------------------------------------------
# Cada regla: caso positivo, caso negativo y caso normal
# ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("regla", REGLAS, ids=lambda r: r["id"])
def test_regla_se_dispara_con_su_caso_positivo(regla):
    valores, base, percibidos = caso_positivo(regla)
    d = MOTOR.diagnosticar(regla["activo"], valores, base, percibidos)
    disparada = next((r for r in d.reglas_disparadas if r.id == regla["id"]), None)
    assert disparada is not None, f"{regla['id']} no se disparó; síntomas: {sorted(d.sintomas)}"
    assert disparada.fc_conclusion == pytest.approx(regla["fc"])
    assert disparada.modo == regla["entonces"]
    assert [p.sintoma for p in disparada.premisas] == regla["si"]
    assert d.fc_de(regla["entonces"]) >= regla["fc"] - 1e-9
    for p in disparada.premisas:
        assert p.grado == 1.0
        if p.tipo == "medido":
            assert p.valor is not None and p.umbral is not None


@pytest.mark.parametrize("regla", [r for r in REGLAS if len(r["si"]) > 1], ids=lambda r: r["id"])
def test_regla_no_se_dispara_si_falta_una_premisa(regla):
    for faltante in regla["si"]:
        parcial = {**regla, "si": [s for s in regla["si"] if s != faltante]}
        valores, base, percibidos = caso_positivo(parcial)
        if BASE.sintomas[faltante]["tipo"] == "medido":
            var = BASE.sintomas[faltante]["variable"]
            # si la premisa quitada comparte variable con otra, no se puede aislar
            if any(BASE.sintomas[s].get("variable") == var for s in parcial["si"]):
                continue
            if BASE.sintomas[faltante]["nivel"] == "en_rango":
                # síntoma de operación normal: hay que sacar la variable del rango activamente
                valores[var] = BASE.activos[regla["activo"]]["variables"][var]["alerta"]
        d = MOTOR.diagnosticar(regla["activo"], valores, base, percibidos)
        assert regla["id"] not in [r.id for r in d.reglas_disparadas], (regla["id"], faltante)
        assert any(p.id == regla["id"] and faltante in p.faltantes for p in d.reglas_parciales)


@pytest.mark.parametrize("activo", list(BASE.activos))
def test_operacion_normal_no_dispara_reglas(activo):
    cfg = BASE.activos[activo]["variables"]
    for nombre, valores in {
        "punto medio": nominales(activo),
        "borde inferior": {v: c["nominal"][0] for v, c in cfg.items()},
        "borde superior": {v: c["nominal"][1] for v, c in cfg.items()},
    }.items():
        d = MOTOR.diagnosticar(activo, valores, nominales(activo))
        assert d.reglas_disparadas == [], (activo, nombre, [r.id for r in d.reglas_disparadas])
        assert d.conclusiones == [] and d.principal is None


def test_reglas_de_otro_activo_no_se_disparan():
    regla = next(r for r in REGLAS if r["id"] == "R13")  # cavitación de bomba
    valores, base, percibidos = caso_positivo(regla)
    d = MOTOR.diagnosticar("motor_electrico", valores, base, percibidos)
    assert d.reglas_disparadas == []


# ----------------------------------------------------------------------------------------
# Integración con las firmas de la Fase 1
# ----------------------------------------------------------------------------------------
def _fin_de_degradacion(activo: str, modo: str):
    valores = nominales(activo)
    cfg = BASE.activos[activo]["variables"]
    for f in BASE.modos[modo]["firma"]:
        if f["variable"] in cfg:
            valores[f["variable"]] = valor_final(cfg[f["variable"]], f["cambio"])
    return valores


CASOS_FIN = [(a, m) for m, d in BASE.modos.items() for a in d["activos"]]


@pytest.mark.parametrize(("activo", "modo"), CASOS_FIN, ids=[f"{a}-{m}" for a, m in CASOS_FIN])
def test_el_final_de_cada_falla_concluye_ese_modo(activo, modo):
    d = MOTOR.diagnosticar(activo, _fin_de_degradacion(activo, modo), nominales(activo))
    assert modo in [c.modo for c in d.conclusiones], (
        f"{activo}/{modo}: concluyó {[(c.modo, round(c.fc, 2)) for c in d.conclusiones]}"
    )


def test_precision_top1_de_las_reglas_sobre_las_firmas():
    """Referencia para M0 (solo reglas): el modo correcto debe ser el de mayor FC en >= 60 %."""
    aciertos = 0
    for activo, modo in CASOS_FIN:
        d = MOTOR.diagnosticar(activo, _fin_de_degradacion(activo, modo), nominales(activo))
        aciertos += bool(d.principal and d.principal.modo == modo)
    assert aciertos / len(CASOS_FIN) >= 0.6, f"top-1 = {aciertos}/{len(CASOS_FIN)}"


@pytest.mark.parametrize(("activo", "modo"), CASOS_FIN, ids=[f"{a}-{m}" for a, m in CASOS_FIN])
def test_el_final_de_cada_falla_tiene_ese_modo_como_principal(activo, modo):
    """D-045: las premisas ``en_rango`` separan los modos que antes empataban o se cruzaban."""
    d = MOTOR.diagnosticar(activo, _fin_de_degradacion(activo, modo), nominales(activo))
    assert d.principal is not None and d.principal.modo == modo, (
        f"{activo}/{modo}: concluyó {[(c.modo, round(c.fc, 2)) for c in d.conclusiones]}"
    )


@pytest.mark.parametrize(("activo", "modo"), CASOS_FIN, ids=[f"{a}-{m}" for a, m in CASOS_FIN])
@pytest.mark.parametrize("t", [0.85, 0.90, 0.95])
def test_la_trayectoria_final_no_cruza_a_otro_modo(activo, modo, t):
    """Tramo final (interpolación lineal): D-045 solo admite cruces antes de 0.83.

    Sin conclusión no hay cruce: varias reglas se disparan recién al llegar a su umbral.
    """
    base = nominales(activo)
    fin = _fin_de_degradacion(activo, modo)
    valores = {v: base[v] + t * (fin[v] - base[v]) for v in base}
    d = MOTOR.diagnosticar(activo, valores, base)
    assert d.principal is None or d.principal.modo == modo, (
        f"{activo}/{modo} en t={t}: concluyó {[(c.modo, round(c.fc, 2)) for c in d.conclusiones]}"
    )


@pytest.mark.parametrize(
    "regla", [r for r in REGLAS if any(BASE.sintomas[s].get("nivel") == "en_rango" for s in r["si"])],
    ids=lambda r: r["id"],
)
def test_la_premisa_en_rango_bloquea_la_regla_fuera_de_rango(regla):
    """Una premisa ``en_rango`` deja de cumplirse cuando su variable alcanza la alerta."""
    valores, base, percibidos = caso_positivo(regla)
    cfg = BASE.activos[regla["activo"]]["variables"]
    for s in (s for s in regla["si"] if BASE.sintomas[s].get("nivel") == "en_rango"):
        variable = BASE.sintomas[s]["variable"]
        d = MOTOR.diagnosticar(
            regla["activo"], {**valores, variable: cfg[variable]["alerta"]}, base, percibidos
        )
        assert regla["id"] not in [r.id for r in d.reglas_disparadas]


# ----------------------------------------------------------------------------------------
# Escenarios del plan
# ----------------------------------------------------------------------------------------
BOMBA_CAVITANDO = {"npsh_margen_ratio": 1.0, "vib_hf_rel": 4.2, "caudal_cv_pct": 8,
                   "presion_descarga_pct": 88, "vib_rms_mm_s": 3.4, "corriente_pct": 88}


def test_cavitacion_combina_r13_y_r14_con_mycin():
    d = MOTOR.diagnosticar("bomba_centrifuga", {**nominales("bomba_centrifuga"), **BOMBA_CAVITANDO})
    assert d.principal.modo == "cavitacion"
    assert d.principal.reglas == ["R14", "R13"]
    assert d.fc_de("cavitacion") == pytest.approx(combinar_fcs([0.9, 0.85]))
    assert d.fc_de("cavitacion") == pytest.approx(0.985)


def test_la_expresion_del_tecnico_agrega_la_regla_percibida():
    vals = {**nominales("bomba_centrifuga"), **BOMBA_CAVITANDO}
    d = MOTOR.diagnosticar("bomba_centrifuga", vals, texto_tecnico="La bomba está golpeando")
    assert "R15" in d.principal.reglas
    assert d.fc_de("cavitacion") == pytest.approx(combinar_fcs([0.9, 0.85, 0.75]))
    assert [c.id for c in d.expresiones] == ["EXP03"]
    assert d.candidatos_lexico["cavitacion"] == 0.6
    assert "observación del técnico" in d.a_texto()


def test_la_expresion_sola_no_basta_para_diagnosticar():
    d = MOTOR.diagnosticar("bomba_centrifuga", nominales("bomba_centrifuga"),
                           texto_tecnico="la bomba está golpeando")
    assert d.conclusiones == []  # D-038: sin síntomas medidos no hay diagnóstico
    assert d.candidatos_lexico and "golpeteo_percibido" in d.sintomas


def test_rodamiento_del_motor_r03_y_r04_no_se_combinan():
    """D-045: R03 exige temperatura en rango; con el rodamiento caliente solo queda R04."""
    vals = {**nominales("motor_electrico"), "vib_curtosis": 8.0, "vib_hf_rel": 6.0,
            "temp_rodamiento_c": 95}
    d = MOTOR.diagnosticar("motor_electrico", vals)
    assert d.principal.modo == "desgaste_rodamiento"
    assert d.principal.reglas == ["R04"]
    assert d.fc_de("desgaste_rodamiento") == pytest.approx(0.85)


def test_prensa_dura_con_presion_alta():
    vals = {**nominales("prensa_hidraulica"), "presion_sistema_pct": 115}
    d = MOTOR.diagnosticar("prensa_hidraulica", vals, texto_tecnico="la prensa está dura")
    assert [r.id for r in d.reglas_disparadas] == ["R29"]
    assert d.principal.modo == "valvula_hidraulica_pegada"


# ----------------------------------------------------------------------------------------
# Salida: texto, JSON y línea de comandos
# ----------------------------------------------------------------------------------------
def test_a_texto_muestra_reglas_valores_y_accion():
    d = MOTOR.diagnosticar("bomba_centrifuga", {**nominales("bomba_centrifuga"), **BOMBA_CAVITANDO})
    texto = d.a_texto()
    for fragmento in ("Cavitación", "R14", "R13", "npsh_margen_ratio = 1 (<= 1.1)", "Acción:"):
        assert fragmento in texto


def test_a_texto_sin_diagnostico():
    d = MOTOR.diagnosticar("motor_electrico", {"corriente_pct": 80})
    assert "ninguna regla se disparó" in d.a_texto()


def test_a_dict_es_serializable():
    d = MOTOR.diagnosticar("bomba_centrifuga", {**nominales("bomba_centrifuga"), **BOMBA_CAVITANDO},
                           texto_tecnico="la bomba está golpeando")
    datos = json.loads(json.dumps(d.a_dict()))
    assert datos["conclusiones"][0]["modo"] == "cavitacion"
    assert datos["reglas_disparadas"][0]["premisas"]


def test_cli(capsys):
    argumentos = ["--activo", "bomba_centrifuga", "--valores", json.dumps(BOMBA_CAVITANDO),
                  "--texto", "la bomba está golpeando"]
    assert main(argumentos) == 0
    salida = capsys.readouterr().out
    assert "cavitacion" in salida and "Expresiones reconocidas" in salida
    assert main([*argumentos, "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["activo"] == "bomba_centrifuga"
