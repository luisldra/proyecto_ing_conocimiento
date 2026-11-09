"""Ontología OWL: generación desde los YAML, consultas, ida y vuelta a disco y HermiT."""

from __future__ import annotations

import pytest
from owlready2 import OwlReadyInconsistentOntologyError, Thing

from metaltech.kb.base import cargar_base
from metaltech.kb.ontology import (
    CLASES_SUPERIORES,
    RUTA_OWL,
    Ontologia,
    construir,
    generar,
    main,
)

BASE = cargar_base()


@pytest.fixture(scope="module")
def onto() -> Ontologia:
    return construir(BASE)


# ----------------------------------------------------------------------------------------
# Estructura
# ----------------------------------------------------------------------------------------
def test_esquema_tiene_las_clases_y_propiedades_del_plan(onto):
    clases = {c.name for c in onto.onto.classes()}
    assert set(CLASES_SUPERIORES) | {"SintomaMedido", "SintomaPercibido"} <= clases
    assert {"MotorElectrico", "BombaCentrifuga", "CompresorTornillo", "PrensaHidraulica",
            "BandaTransportadora", "CentroCnc"} <= clases
    props = {p.name for p in onto.onto.properties()}
    assert {"tieneComponente", "monitoreadoPor", "mide", "manifiesta", "causadoPor",
            "mitigadoPor", "refiereA", "sustentadaPor", "severidad", "umbral"} <= props


def test_clases_superiores_son_disjuntas(onto):
    pares = {frozenset(c.name for c in d.entities) for d in onto.onto.disjoint_classes()}
    todas = next(p for p in pares if "Activo" in p and "Regla" in p)
    assert set(CLASES_SUPERIORES) <= todas
    assert frozenset({"SintomaMedido", "SintomaPercibido"}) in pares


def test_validacion_estructural_sin_problemas(onto):
    assert onto.validar_estructura(BASE) == []


def test_conteos_coinciden_con_los_yaml(onto):
    c = onto.conteos()
    assert c["ModoFalla"] == len(BASE.modos) == 31
    assert c["Regla"] == len(BASE.reglas) == 55
    assert c["Sintoma"] == len(BASE.sintomas) == 68
    assert c["ExpresionColoquial"] == len(BASE.lexico) == 10
    assert c["FilaFMEA"] == sum(len(v) for v in BASE.fmea.values()) == 41
    assert c["Activo"] == sum(a["unidades"] for a in BASE.activos.values())
    assert c["Tecnico"] == 10 and c["Turno"] == 3
    assert c["Sensor"] == sum(a["unidades"] * len(a["variables"]) for a in BASE.activos.values())


def test_la_ontologia_refleja_cada_regla(onto):
    for r in BASE.reglas:
        x = onto._ix["Regla"][r["id"]]
        assert x.concluye.identificador == r["entonces"]
        assert [s.identificador for s in x.tienePremisa] == r["si"]
        assert x.fcRegla == pytest.approx(r["fc"])
        assert x.tipoActivo == [r["activo"]]


def test_la_ontologia_refleja_los_umbrales(onto):
    v = onto._ix["Variable"]["bomba_centrifuga__npsh_margen_ratio"]
    assert (v.umbralAlerta, v.umbralCritico) == (1.3, 1.1)
    assert v.direccion == "baja"
    assert v.umbralAlertaBaja is None
    c = onto._ix["Variable"]["motor_electrico__corriente_pct"]
    assert c.umbralAlertaBaja == 40.0


def test_cada_modo_manifiesta_sus_sintomas_de_la_fmea(onto):
    for tipo, filas in BASE.fmea.items():
        for f in filas:
            esperado = sorted(f["sintomas"])
            assert onto.sintomas_de_modo(f["modo_falla"], tipo) == esperado
            assert onto.causas_de_modo(f["modo_falla"], tipo) == sorted(f["causas"])
            assert onto.acciones_de_modo(f["modo_falla"], tipo) == sorted(f["acciones"])
            assert onto.componentes_de_modo(f["modo_falla"], tipo) == [f"{tipo}__{f['componente']}"]


# ----------------------------------------------------------------------------------------
# Consultas
# ----------------------------------------------------------------------------------------
def test_sintomas_de_un_modo_de_falla(onto):
    s = onto.sintomas_de_modo("cavitacion")
    assert {"margen_npsh_bajo", "vibracion_hf_alta", "caudal_inestable",
            "golpeteo_percibido"} <= set(s)


def test_acciones_para_una_falla(onto):
    assert "restablecer_npsha" in onto.acciones_de_modo("cavitacion")
    assert "limpiar_filtro_succion" in onto.acciones_de_modo("cavitacion", "bomba_centrifuga")


def test_la_misma_falla_tiene_distinto_detalle_por_activo(onto):
    motor = onto.sintomas_de_modo("desgaste_rodamiento", "motor_electrico")
    banda = onto.sintomas_de_modo("desgaste_rodamiento", "banda_transportadora")
    assert "vibracion_hf_critica" in motor and "vibracion_hf_critica" not in banda
    assert onto.componentes_de_modo("desgaste_rodamiento", "centro_cnc") == [
        "centro_cnc__rodamientos_husillo"]


def test_diagnostico_diferencial_por_sintoma(onto):
    modos = onto.modos_de_sintoma("vibracion_hf_alta")
    assert {"cavitacion", "desgaste_rodamiento", "falla_lubricacion_rodamiento"} <= set(modos)


def test_reglas_y_expresiones_de_un_modo(onto):
    assert onto.reglas_de_modo("cavitacion") == ["R13", "R14", "R15"]
    assert onto.reglas_de_modo("holgura_mecanica", "bomba_centrifuga") == ["R47"]
    assert "la bomba está golpeando" in onto.expresiones_de_modo("cavitacion")
    assert "la bomba está golpeando" in onto.expresiones_de_sintoma("golpeteo_percibido")


def test_modos_por_activo(onto):
    assert "cavitacion" in onto.modos("bomba_centrifuga")
    assert "cavitacion" not in onto.modos("motor_electrico")
    assert len(onto.modos()) == 31


def test_activos_componentes_y_sensores(onto):
    assert onto.unidades("bomba_centrifuga") == [f"bomba_centrifuga_{k}" for k in (1, 2, 3)]
    assert "impulsor" in onto.componentes_de_activo("bomba_centrifuga")
    sensores = onto.sensores_de_unidad("bomba_centrifuga_1")
    assert sensores["bomba_centrifuga_1__npsh_margen_ratio"] == "npsh_margen_ratio"
    assert len(sensores) == len(BASE.activos["bomba_centrifuga"]["variables"])


def test_detalle_de_modo(onto):
    d = onto.detalle_modo("cavitacion", "bomba_centrifuga")
    assert d["nombre"].startswith("Cavitación") and d["severidad"] == 8
    assert d["fmea"] == [{"activo": "bomba_centrifuga", "severidad": 8, "ocurrencia": 5,
                          "deteccion": 4, "npr": 160}]
    assert d["reglas"] == ["R13", "R14", "R15"] and d["activos"] == ["bomba_centrifuga"]


def test_consultas_con_ids_desconocidos(onto):
    with pytest.raises(KeyError, match="modo de falla desconocido"):
        onto.sintomas_de_modo("no_existe")


def test_grafo(onto):
    g = onto.grafo()
    ids = {n["id"] for n in g["nodos"]}
    assert all(a["origen"] in ids and a["destino"] in ids for a in g["aristas"])
    assert {n["tipo"] for n in g["nodos"]} >= {"ModoFalla", "Sintoma", "Regla", "Causa", "Accion",
                                              "ExpresionColoquial"}
    gb = onto.grafo("bomba_centrifuga")
    assert 0 < len(gb["nodos"]) < len(g["nodos"])
    assert "ModoFalla:cavitacion" in {n["id"] for n in gb["nodos"]}
    assert "ModoFalla:falla_contactor" not in {n["id"] for n in gb["nodos"]}


# ----------------------------------------------------------------------------------------
# Persistencia
# ----------------------------------------------------------------------------------------
def test_guardar_y_cargar_conserva_todo(onto, tmp_path):
    ruta = onto.guardar(tmp_path / "metaltech.owl")
    otra = Ontologia.cargar(ruta)
    assert otra.conteos() == onto.conteos()
    assert otra.validar_estructura(BASE) == []
    for modo in onto.modos():
        assert otra.detalle_modo(modo) == onto.detalle_modo(modo)
    assert otra.grafo()["aristas"].__len__() == onto.grafo()["aristas"].__len__()


def test_el_owl_versionado_esta_al_dia(onto):
    """knowledge/ontology/metaltech.owl debe ser lo que generan hoy los YAML."""
    assert RUTA_OWL.exists(), "ejecute: python -m metaltech.kb.ontology"
    guardada = Ontologia.cargar(RUTA_OWL)
    assert guardada.conteos() == onto.conteos()
    for modo in onto.modos():
        assert guardada.detalle_modo(modo) == onto.detalle_modo(modo), modo
    for r in BASE.reglas:
        assert guardada.reglas_de_modo(r["entonces"], r["activo"]) == onto.reglas_de_modo(
            r["entonces"], r["activo"])


def test_cli_genera_el_owl(tmp_path, capsys):
    salida = tmp_path / "x.owl"
    assert main(["--salida", str(salida), "--modo", "cavitacion", "--activo", "bomba_centrifuga"]) == 0
    assert salida.exists()
    texto = capsys.readouterr().out
    assert "Validación estructural: OK" in texto and "Cavitación" in texto


def test_generar_escribe_el_archivo(tmp_path):
    assert generar(tmp_path / "g.owl").conteos()["Regla"] == 55


# ----------------------------------------------------------------------------------------
# Consistencia lógica con HermiT (requiere Java; ver ERR-008)
# ----------------------------------------------------------------------------------------
@pytest.mark.java
def test_hermit_ontologia_consistente():
    construir(BASE).validar_con_hermit()


@pytest.mark.java
def test_hermit_detecta_individuo_en_clases_disjuntas():
    o = construir(BASE)
    with o.onto:
        mal = Thing("individuo_incoherente")
        mal.is_a.extend([o.onto["Activo"], o.onto["Componente"]])
    with pytest.raises(OwlReadyInconsistentOntologyError):
        o.validar_con_hermit()


@pytest.mark.java
def test_hermit_detecta_propiedad_funcional_con_dos_valores():
    o = construir(BASE)
    with o.onto:
        regla = o._ix["Regla"]["R01"]
        regla.concluye = o._ix["ModoFalla"]["cavitacion"]
        # `concluye` es funcional: un segundo valor distinto debe ser inconsistente
        o.onto["concluye"][regla].append(o._ix["ModoFalla"]["falla_variador"])
    with pytest.raises(OwlReadyInconsistentOntologyError):
        o.validar_con_hermit()
