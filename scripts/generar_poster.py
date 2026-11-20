"""Genera el póster (Fase 10): llena ``docs/poster/poster_plantilla.html`` con las cifras de ``reports/`` y lo
exporta a PDF A1 vertical con Playwright. Usa las mismas cifras y figuras que el documento APA.

Uso: ``python scripts/generar_poster.py`` (antes, ``python scripts/generar_documento.py --figuras``)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from generar_documento import sustituir, valores  # noqa: E402

CARPETA = RAIZ / "docs" / "poster"
PLANTILLA = CARPETA / "poster_plantilla.html"
HTML = CARPETA / "poster.html"
PDF = CARPETA / "poster.pdf"


def generar() -> None:
    texto = re.sub(r"<!--.*?-->", "", PLANTILLA.read_text(encoding="utf-8"), flags=re.S)
    HTML.write_text(sustituir(texto, valores()), encoding="utf-8")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2245, "height": 3179})  # A1 a 96 ppp
        pg.goto(HTML.as_uri())
        pg.wait_for_load_state("networkidle")
        desborde = pg.evaluate("Math.max(...[...document.querySelectorAll('main > div')].map(c => c.getBoundingClientRect().bottom))"
                               " > document.querySelector('footer').getBoundingClientRect().top")
        pg.screenshot(path=str(CARPETA / "poster_vista.png"))
        pg.pdf(path=str(PDF), width="594mm", height="841mm", print_background=True)
        b.close()
    print(f"{PDF.relative_to(RAIZ)}" + ("  Aviso: el contenido se monta sobre el pie de página" if desborde else ""))


if __name__ == "__main__":
    generar()
