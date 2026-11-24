"""Fase 11: los manuales no tienen enlaces rotos y sus comandos y endpoints existen."""

import importlib.util
import re
import unicodedata

import pytest

from metaltech.kb.base import RAIZ

CARPETA = RAIZ / "docs" / "manuales"
MANUALES = sorted(CARPETA.glob("*.md"))
ESPERADOS = {"README.md", "puesta_en_marcha.md", "guia_comandos.md", "guia_documentos.md", "diagramas_flujo.md",
             "manual_usuario_web.md", "manual_api.md", "manual_tecnico.md", "glosario.md"}


def _ancla(titulo: str) -> str:
    """Ancla de un título como la genera GitHub."""
    t = unicodedata.normalize("NFC", titulo.strip().lower())
    t = re.sub(r"[^\w\s-]", "", t)
    return t.replace(" ", "-")


def _anclas(ruta) -> set[str]:
    return {_ancla(m) for m in re.findall(r"^#{1,6}\s+(.+)$", ruta.read_text(encoding="utf-8"), flags=re.M)}


def test_estan_todos_los_manuales():
    assert ESPERADOS <= {m.name for m in MANUALES}


@pytest.mark.parametrize("manual", MANUALES, ids=lambda m: m.name)
def test_enlaces_internos_e_imagenes(manual):
    texto = re.sub(r"```.*?```", "", manual.read_text(encoding="utf-8"), flags=re.S)
    for destino in re.findall(r"\]\(([^)\s]+)\)", texto):
        if destino.startswith(("http://", "https://", "mailto:")):
            continue
        ruta, _, ancla = destino.partition("#")
        archivo = (manual.parent / ruta).resolve() if ruta else manual
        assert archivo.exists(), f"{manual.name}: enlace roto {destino}"
        if ancla and archivo.suffix == ".md":
            assert ancla in _anclas(archivo), f"{manual.name}: ancla inexistente {destino}"


def test_comandos_de_la_guia_existen():
    texto = (CARPETA / "guia_comandos.md").read_text(encoding="utf-8")
    modulos = set(re.findall(r"python -m (metaltech[\w.]*)", texto))
    scripts = set(re.findall(r"python (scripts/\w+\.py)", texto))
    assert modulos and scripts
    for m in modulos:
        assert importlib.util.find_spec(m) is not None, f"módulo inexistente: {m}"
    for s in scripts:
        assert (RAIZ / s).exists(), f"script inexistente: {s}"
    for t in set(re.findall(r"pytest (tests/\w+\.py)", texto)):
        assert (RAIZ / t).exists(), t


def test_endpoints_del_manual_coinciden_con_la_api():
    main = (RAIZ / "src" / "metaltech" / "api" / "main.py").read_text(encoding="utf-8")
    rutas_api = set(re.findall(r'@app\.(?:get|post)\("([^"]+)"\)', main))
    manual = (CARPETA / "manual_api.md").read_text(encoding="utf-8")
    rutas_manual = {r.split("?")[0] for r in re.findall(r"^\| (?:GET|POST) \| `([^`]+)`", manual, flags=re.M)}
    assert rutas_manual == rutas_api


def test_diagramas_mermaid():
    texto = (CARPETA / "diagramas_flujo.md").read_text(encoding="utf-8")
    bloques = re.findall(r"```mermaid\n(.*?)```", texto, flags=re.S)
    assert len(bloques) >= 6
    assert all(b.lstrip().startswith("flowchart") for b in bloques)
