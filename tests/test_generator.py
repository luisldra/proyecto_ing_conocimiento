"""Pruebas del simulador de la Fase 3."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from metaltech.data.generator import (
    PASOS_POR_HORA,
    SIN_MODO,
    ConfigSimulador,
    particionar,
    perfil_degradacion,
    programar_episodios,
    simular,
    tarea_de,
)
from metaltech.kb.base import RAIZ, cargar_base, valor_final
from metaltech.kb.lexicon import Lexico

BASE = cargar_base()
CFG = ConfigSimulador.desde_yaml(RAIZ / "configs" / "train.yaml", meses=8)


@pytest.fixture(scope="module")
def sim():
    return simular(CFG, semilla=42)


# ----------------------------------------------------------------------------------------
# Formas
# ----------------------------------------------------------------------------------------
T = np.arange(1, 101) / 100


@pytest.mark.parametrize("forma", ["lineal", "exponencial", "sigmoide", "escalon"])
def test_perfil_llega_a_uno_y_no_decrece(forma):
    p = perfil_degradacion(forma, T)
    assert p[-1] == pytest.approx(1.0)
    assert np.all(np.diff(p) >= -1e-12)


def test_perfil_respeta_el_retardo():
    p = perfil_degradacion("exponencial", T, retardo=0.5)
    assert np.all(p[T <= 0.5] == 0) and p[-1] == pytest.approx(1.0)


def test_exponencial_es_tardia():
    assert perfil_degradacion("exponencial", np.array([0.5]))[0] < 0.2


def test_escalon_al_inicio_y_al_final():
    assert perfil_degradacion("escalon", T, escalon_en="inicio")[0] == 1.0
    final = perfil_degradacion("escalon", T, escalon_en="final")
    assert final[-1] == 1.0 and final[:-1].sum() == 0


# ----------------------------------------------------------------------------------------
# Especificación
# ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("modo", list(BASE.modos))
def test_tarea_coherente_con_la_duracion_y_la_forma(modo):
    deg = BASE.modos[modo]["degradacion"]
    esperada = "deteccion" if deg["forma"] == "escalon" or deg["duracion_h"][0] < CFG.horizonte_h else "prediccion"
    assert tarea_de(BASE.modos[modo]) == esperada
    assert deg["forma"] != "escalon" or deg["escalon_en"] in ("inicio", "final")


def test_todos_los_modos_aparecen_en_la_duracion_completa():
    completa = ConfigSimulador.desde_yaml(RAIZ / "configs" / "train.yaml")
    rng = np.random.default_rng(1)
    for activo, datos in BASE.activos.items():
        vistos = {
            ep.modo for k in range(datos["unidades"])
            for ep in programar_episodios(rng, BASE, completa, f"u{k}", activo)
        }
        assert vistos == {m for m, d in BASE.modos.items() if activo in d["activos"]}, activo


# ----------------------------------------------------------------------------------------
# Reproducibilidad
# ----------------------------------------------------------------------------------------
def test_misma_semilla_mismo_resultado(sim):
    otra = simular(CFG, semilla=42)
    for activo, df in sim.series.items():
        pd.testing.assert_frame_equal(df, otra.series[activo])
    pd.testing.assert_frame_equal(sim.observaciones, otra.observaciones)


def test_otra_semilla_cambia_el_resultado(sim):
    otra = simular(CFG, semilla=43)
    assert not sim.series["motor_electrico"]["vib_rms_mm_s"].equals(otra.series["motor_electrico"]["vib_rms_mm_s"])


# ----------------------------------------------------------------------------------------
# Episodios y etiquetas
# ----------------------------------------------------------------------------------------
def test_episodios_no_se_solapan(sim):
    for _, grupo in sim.episodios.sort_values("i0").groupby("unidad"):
        assert (grupo["i0"].to_numpy()[1:] > grupo["i1"].to_numpy()[:-1]).all()


def test_etiquetas_respetan_la_tarea(sim):
    for activo, df in sim.series.items():
        positivos = df[df["etiqueta"] != SIN_MODO]
        assert (positivos["etiqueta"].astype(str) == positivos["modo_activo"].astype(str)).all(), activo
        modos = positivos["etiqueta"].astype(str)
        por_modo = positivos[modos.map(lambda m: tarea_de(BASE.modos[m])) == "prediccion"]
        assert (por_modo["horas_a_falla"] <= CFG.horizonte_h).all(), activo


def test_la_falla_mueve_la_mayoria_de_su_firma(sim):
    """Hasta un 20 % de la firma puede omitirse, y la severidad varía (D-052)."""
    movidas, total = 0, 0
    for _, ep in sim.episodios.iterrows():
        df = sim.series[ep["activo"]]
        filas = df[df["unidad"] == ep["unidad"]].reset_index(drop=True)
        fila = filas.iloc[ep["i1"]]
        assert fila["estado"] == "falla" and fila["etiqueta"] == ep["modo"]
        if fila["confusor"] != "ninguno":
            continue
        sanos = filas[filas["estado"] == "sano"]
        for f in BASE.modos[ep["modo"]]["firma"]:
            v = f["variable"]
            if v not in filas or v == "desgaste_herramienta_min" or f["cambio"].get("valor") == 0:
                continue
            signo = 1 if f["direccion"] == "+" else -1
            if BASE.activos[ep["activo"]]["variables"][v]["nominal"] == [0, 0]:
                continue
            total += 1
            movidas += bool(signo * (fila[v] - sanos[v].median()) > 0)
    assert movidas / total >= 0.7, f"{movidas}/{total}"


def test_reparacion_sin_datos_de_sensores(sim):
    df = sim.series["motor_electrico"]
    assert df.loc[df["estado"] == "reparacion", "vib_rms_mm_s"].isna().all()


def test_operacion_sana_casi_siempre_cerca_del_rango_nominal(sim):
    """Sin recorte (D-052): la señal puede salirse del rango, pero solo en las colas."""
    for activo, df in sim.series.items():
        sanos = df[(df["estado"] == "sano") & (df["confusor"] == "ninguno")]
        for v, c in BASE.activos[activo]["variables"].items():
            lo, hi = c["nominal"]
            margen = 0.25 * max(hi - lo, 1e-3)
            dentro = sanos[v].between(lo - margen, hi + margen).mean()
            assert dentro >= 0.95, (activo, v, dentro)


def test_la_firma_de_vibracion_escala_con_la_alerta_del_activo():
    cambio = {"tipo": "frac_alerta", "valor": 1.43}
    assert valor_final(BASE.activos["bomba_centrifuga"]["variables"]["vib_rms_mm_s"], cambio) == pytest.approx(7.293)
    assert valor_final(BASE.activos["motor_electrico"]["variables"]["vib_rms_mm_s"], cambio) == pytest.approx(4.004)


def test_hay_confusores_y_datos_faltantes(sim):
    todos = pd.concat([df["confusor"].astype(str) for df in sim.series.values()])
    esperados = {"pico_espurio", "sensor_faltante", "pico_demanda_aire", "arranque_motor", "excursion_operativa"}
    assert esperados <= set(todos)


# ----------------------------------------------------------------------------------------
# Partición
# ----------------------------------------------------------------------------------------
def test_particion_temporal_con_purga():
    p = particionar(CFG, CFG.pasos)
    orden = ["train", "purga", "val", "purga", "test"]
    assert list(pd.Series(p).loc[lambda s: s != s.shift()]) == orden
    assert (p == "purga").sum() == 2 * (CFG.ventana_pasos + CFG.horizonte_h * PASOS_POR_HORA)


# ----------------------------------------------------------------------------------------
# Observaciones
# ----------------------------------------------------------------------------------------
def test_observaciones_las_reconoce_el_lexico(sim):
    lexico = Lexico(BASE)
    assert len(sim.observaciones) > 0
    for _, o in sim.observaciones.iterrows():
        assert o["id_expresion"] in {c.id for c in lexico.identificar(o["texto"], o["activo"])}


def test_observaciones_anonimizadas(sim):
    assert sim.observaciones["tecnico"].str.fullmatch(r"[TI]\d{2}").all()
