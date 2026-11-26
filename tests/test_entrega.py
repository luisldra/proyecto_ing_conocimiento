"""Entrega final: la carpeta entrega/ está completa y al día, y el guion respeta el reparto del equipo."""

import hashlib
import importlib.util
import re
from collections import Counter

import pytest

from metaltech.kb.base import RAIZ

ENTREGA = RAIZ / "entrega"
_spec = importlib.util.spec_from_file_location("preparar_entrega", RAIZ / "scripts" / "preparar_entrega.py")
preparar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(preparar)


def _sha(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def test_indice_y_archivos_coinciden():
    indice = (ENTREGA / "README.md").read_text(encoding="utf-8")
    citados = set(re.findall(r"\]\((\d\d_[^)]+)\)", indice))
    esperados = set(preparar.COPIAS) | set(preparar.CONVERSIONES)
    assert citados == esperados
    for nombre in esperados:
        assert (ENTREGA / nombre).exists(), f"falta entrega/{nombre}: ejecute python scripts/preparar_entrega.py"


@pytest.mark.parametrize("nombre", sorted(preparar.COPIAS))
def test_copias_al_dia(nombre):
    fuente = RAIZ / preparar.COPIAS[nombre]
    assert _sha(ENTREGA / nombre) == _sha(fuente), (
        f"entrega/{nombre} no coincide con {preparar.COPIAS[nombre]}: ejecute python scripts/preparar_entrega.py")


def test_guion_maximo_dos_intervenciones_por_persona():
    guion = (RAIZ / "docs" / "demo_guion.md").read_text(encoding="utf-8")
    reparto = guion[guion.index("## Reparto"):guion.index("## Antes de empezar")]
    filas = re.findall(r"^\| (\d+) \| [^|]+ \| ([^|]+) \|", reparto, flags=re.M)
    personas = Counter(p.strip() for _, p in filas)
    assert len(personas) == 4, personas
    assert max(personas.values()) <= 2, personas
    minutos = sum(int(m) * 60 + int(s) for m, s in re.findall(r"^\| \d+ \|[^|]+\|[^|]+\| (\d+):(\d\d) \|", reparto, flags=re.M))
    assert 10 * 60 <= minutos <= 15 * 60
