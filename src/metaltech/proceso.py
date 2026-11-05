"""Verificación del proceso: enlaces MEMORIA <-> ERRORES (rol QA).

Uso:  python -m metaltech.proceso
Reglas:
  - todo ERR-NNN citado en MEMORIA.md existe en ERRORES.md;
  - los ERR-NNN de ERRORES.md son únicos y están en el índice por origen;
  - MEMORIA.md tiene el bloque "Estado actual" y al menos una entrada de bitácora.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MEMORIA = RAIZ / "docs" / "agentes" / "MEMORIA.md"
ERRORES = RAIZ / "docs" / "agentes" / "ERRORES.md"

_ERR = re.compile(r"ERR-\d{3}")


def _ids_definidos(texto: str) -> list[str]:
    return re.findall(r"^### (ERR-\d{3})\b", texto, flags=re.M)


def verificar(memoria: Path = MEMORIA, errores: Path = ERRORES) -> list[str]:
    """Devuelve la lista de problemas encontrados (vacía si todo está bien)."""
    problemas: list[str] = []
    txt_mem = memoria.read_text(encoding="utf-8")
    # La plantilla de ERRORES.md va en un comentario HTML y no cuenta como entrada.
    txt_err = re.sub(r"<!--.*?-->", "", errores.read_text(encoding="utf-8"), flags=re.S)

    definidos = _ids_definidos(txt_err)
    repetidos = {i for i in definidos if definidos.count(i) > 1}
    if repetidos:
        problemas.append(f"ERR duplicados en ERRORES.md: {sorted(repetidos)}")

    for err in sorted(set(_ERR.findall(txt_mem)) - set(definidos)):
        problemas.append(f"{err} se cita en MEMORIA.md pero no existe en ERRORES.md")

    # Índice por origen: la sección entre "## Índice" y "## Lecciones".
    m = re.search(r"## Índice por origen(.*?)## Lecciones", txt_err, flags=re.S)
    indice = set(_ERR.findall(m.group(1))) if m else set()
    for err in sorted(set(definidos) - indice):
        problemas.append(f"{err} no aparece en el índice por origen de ERRORES.md")

    if "## Estado actual" not in txt_mem:
        problemas.append("MEMORIA.md no tiene el bloque 'Estado actual'")
    if not re.search(r"^## \[\d{4}-\d{2}-\d{2}\]", txt_mem, flags=re.M):
        problemas.append("MEMORIA.md no tiene entradas de bitácora con fecha AAAA-MM-DD")
    return problemas


def main() -> int:
    problemas = verificar()
    for p in problemas:
        print(f"[FALLA] {p}")
    if not problemas:
        print("Proceso OK: MEMORIA y ERRORES son consistentes.")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
