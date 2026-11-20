"""Fase 10: el documento APA se puede generar y sus citas, cifras, tablas y figuras están completas."""

import importlib.util
import re
import sys

import pytest

from metaltech.kb.base import RAIZ

CARPETA = RAIZ / "docs" / "documento_APA"
FUENTE = (CARPETA / "documento.md").read_text(encoding="utf-8")
TEXTO = re.sub(r"<!--.*?-->", "", FUENTE, flags=re.S)
REFS = [x[2:] for x in (CARPETA / "referencias.md").read_text(encoding="utf-8").splitlines() if x.startswith("- ")]

pytestmark = pytest.mark.skipif(not (RAIZ / "reports" / "tables" / "intervalos_sistemas.csv").exists(),
                                reason="faltan reports/tables")


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location("generar_documento", RAIZ / "scripts" / "generar_documento.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m  # las dataclasses lo necesitan
    spec.loader.exec_module(m)
    m.contar_pruebas = lambda: "600"  # evita recolectar pytest dentro de pytest
    return m


def test_cifras_tablas_y_figuras_existen(gen):
    v = gen.valores()
    assert set(re.findall(r"\{\{v:(\w+)\}\}", TEXTO)) <= set(v)
    assert set(re.findall(r"\{\{tabla:(\w+)\}\}", TEXTO)) <= set(gen.GENERADORES)
    assert set(re.findall(r"\{\{figura:(\w+)\}\}", TEXTO)) <= set(gen.FIGURAS_INFO)
    for nombre in gen.GENERADORES.values():
        t = nombre()
        assert t.filas and all(len(f) == len(t.encabezados) for f in t.filas), t.titulo


def test_resumen_entre_150_y_250_palabras():
    cuerpo = TEXTO[TEXTO.index("{{resumen}}") + 11:TEXTO.index("{{/resumen}}")]
    resumen = " ".join(x for x in cuerpo.splitlines() if x.strip() and not x.startswith("Palabras clave"))
    assert 150 <= len(re.sub(r"\{\{v:\w+\}\}", "X", resumen).split()) <= 250
    claves = next(x for x in cuerpo.splitlines() if x.startswith("Palabras clave")).split(":")[1].split(",")
    assert 3 <= len(claves) <= 5


def test_cada_cita_tiene_referencia():
    citas = re.findall(r"([A-ZÁÉÍÓÚ][a-záéíóúñ]+)(?: et al\.| y [A-Z][\w-]+)?,? \(?((?:19|20)\d\d)[a-z]?\b", TEXTO)
    no_autores = {"Desde", "En", "Para", "Entre", "Hasta"}
    faltan = {(n, a) for n, a in citas if n not in no_autores and not any(n in r and f"({a}" in r for r in REFS)}
    assert not faltan, faltan


def test_cada_referencia_se_cita():
    for r in REFS:
        autor = re.split(r"[,.(]", r)[0].split()[-1]
        assert autor in TEXTO, f"referencia sin cita: {r[:60]}"


def test_referencias_base_del_enunciado():
    for autor in ("Alimam", "Ciriello", "Ferrara", "Friston", "Kusiak"):
        assert any(r.startswith(autor) for r in REFS) and autor in TEXTO


def test_tablas_y_figuras_citadas_existen(gen):
    n_tablas = len(re.findall(r"\{\{tabla:\w+\}\}|^Tabla:", TEXTO, flags=re.M))
    n_figuras = len(re.findall(r"\{\{figura:\w+\}\}", TEXTO))
    assert max(map(int, re.findall(r"Tabla (\d+)", TEXTO))) <= n_tablas
    assert max(map(int, re.findall(r"Figura (\d+)", TEXTO))) <= n_figuras
    for f in re.findall(r"\{\{figura:(\w+)\}\}", TEXTO):
        assert (gen.FIGURAS / f"{f}.png").exists(), f
