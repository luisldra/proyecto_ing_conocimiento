"""Fase 9: las cifras del informe de sesgos salen de reports/tables y no quedan desactualizadas."""

import json

import pandas as pd
import pytest

from metaltech.kb.base import RAIZ

TABLAS = RAIZ / "reports" / "tables"
INFORME = RAIZ / "reports" / "sesgos_limitaciones.md"

pytestmark = pytest.mark.skipif(not (TABLAS / "equidad_grupos.csv").exists(), reason="faltan reports/tables")


@pytest.fixture(scope="module")
def texto() -> str:
    return INFORME.read_text(encoding="utf-8")


def _pct(x: float, d: int = 2) -> str:
    return f"{100 * x:.{d}f} %"


def test_falsa_alarma_por_observacion(texto):
    g = pd.read_csv(TABLAS / "equidad_grupos.csv")
    obs = g[g["grupo"] == "observacion"].groupby(["valor", "sistema"])["falsa_alarma"].mean()
    for valor, sistema in (("ninguna", "M0"), ("incorrecta", "M0"), ("ninguna", "M3"), ("incorrecta", "M3")):
        assert _pct(obs.loc[(valor, sistema)]) in texto, (valor, sistema)


def test_brechas_por_activo(texto):
    b = pd.read_csv(TABLAS / "equidad_brechas.csv").set_index(["grupo", "sistema"])
    for sistema in ("M0", "M3"):
        assert f"{100 * b.loc[('activo', sistema), 'acierto_falla_brecha']:.1f} puntos" in texto, sistema


def test_diferencias_en_maquina_no_vista(texto):
    d = pd.read_csv(TABLAS / "intervalos_diferencias.csv")
    f = d[(d["particion"] == "test_unidad") & (d["comparacion"] == "M3-M1")].set_index("metrica")
    assert f"+{100 * f.loc['f1_macro', 'diferencia_media']:.1f} puntos" in texto
    assert f"−{-100 * f.loc['falsa_alarma_con_confusor', 'diferencia_media']:.1f} puntos" in texto


def test_veto_hunde_el_f1(texto):
    p = json.loads((TABLAS / "fusion_parametros.json").read_text(encoding="utf-8"))
    assert not any(a["veto"] for a in p.values()), "el informe dice que ningún activo eligió veto"
    con_veto = [r["f1_macro"] for a in p.values() for r in a["rejilla_val"] if r["veto"] and r["alfa"] >= 0.6]
    assert max(con_veto) < 0.75


def test_concordancia_xai(texto):
    x = pd.read_csv(TABLAS / "xai_metricas.csv")
    assert _pct(x["top_k_en_firma"].mean(), 1) in texto
    assert _pct(x["top_k_en_firma_azar"].mean(), 1) in texto
