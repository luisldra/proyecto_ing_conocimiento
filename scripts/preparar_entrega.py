"""Prepara la carpeta ``entrega/`` con los entregables del curso.

Copia el documento APA (PDF y Word) y el póster, y convierte a PDF los documentos en Markdown (guion, informe de
sesgos, acta ética y manuales) con Chromium (Playwright), para que la carpeta se pueda subir tal cual a la
plataforma del curso. Los archivos de ``entrega/`` no se editan: se edita la fuente y se vuelve a ejecutar.

Uso: ``python scripts/preparar_entrega.py`` (antes: ``generar_documento.py --pdf`` y ``generar_poster.py``).
Requiere conexión a internet para cargar el conversor de Markdown (marked) desde jsDelivr.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTREGA = RAIZ / "entrega"

COPIAS = {
    "01_Documento_APA.pdf": "docs/documento_APA/documento_apa.pdf",
    "01_Documento_APA.docx": "docs/documento_APA/documento_apa.docx",
    "02_Poster_A1.pdf": "docs/poster/poster.pdf",
}
CONVERSIONES = {
    "03_Guion_presentacion.pdf": "docs/demo_guion.md",
    "04_Informe_sesgos_y_limitaciones.pdf": "reports/sesgos_limitaciones.md",
    "05_Acta_etica.pdf": "docs/etica/acta_etica.md",
    "06_Puesta_en_marcha.pdf": "docs/manuales/puesta_en_marcha.md",
    "07_Manual_usuario_web.pdf": "docs/manuales/manual_usuario_web.md",
    "08_Manual_API.pdf": "docs/manuales/manual_api.md",
}

ESTILO = """
body { font: 10.5pt/1.45 "Segoe UI", Arial, sans-serif; color: #111; margin: 0; }
h1 { font-size: 19pt; color: #1c5cab; margin: 0 0 10px; } h2 { font-size: 14pt; color: #1c5cab; margin: 18px 0 6px; }
h3 { font-size: 12pt; margin: 14px 0 4px; } p, li { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #d6d5cd; padding: 4px 6px; text-align: left; vertical-align: top; } th { background: #f1f0ec; }
tr { page-break-inside: avoid; } code { font: 9pt Consolas, monospace; background: #f1f0ec; padding: 0 3px; }
pre { background: #f6f6f4; padding: 8px; font-size: 8.5pt; white-space: pre-wrap; } blockquote { border-left: 4px solid #d6d5cd; margin: 8px 0; padding: 2px 12px; color: #444; }
img { max-width: 100%; border: 1px solid #e1e0d9; } a { color: #1c5cab; text-decoration: none; }
"""


def convertir(pagina, fuente: Path, destino: Path) -> None:
    """Markdown → PDF. La página temporal va junto a la fuente para que las imágenes relativas carguen."""
    temporal = fuente.with_name(f".__entrega_{fuente.stem}.html")
    temporal.write_text(
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<style>{ESTILO}</style>"
        "<script src='https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js'></script></head>"
        "<body><main id='c'></main><script>"
        f"document.getElementById('c').innerHTML = marked.parse({json.dumps(fuente.read_text(encoding='utf-8'))});"
        "</script></body></html>", encoding="utf-8")
    try:
        pagina.goto(temporal.as_uri())
        pagina.wait_for_load_state("networkidle")
        if not pagina.evaluate("document.getElementById('c').textContent.trim().length > 0"):
            raise RuntimeError(f"no se pudo convertir {fuente.name} (¿sin conexión para cargar marked?)")
        pagina.pdf(path=str(destino), format="Letter", print_background=True,
                   margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
                   display_header_footer=True, header_template="<span></span>",
                   footer_template="<div style='font-size:8px;width:100%;text-align:center;color:#666'>"
                                   "Metal Tech · Proyecto 3 · <span class='pageNumber'></span>/<span class='totalPages'></span></div>")
    finally:
        temporal.unlink(missing_ok=True)


def preparar() -> list[str]:
    ENTREGA.mkdir(exist_ok=True)
    for nombre, fuente in COPIAS.items():
        shutil.copyfile(RAIZ / fuente, ENTREGA / nombre)
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        pagina = b.new_page()
        for nombre, fuente in CONVERSIONES.items():
            convertir(pagina, RAIZ / fuente, ENTREGA / nombre)
        b.close()
    return sorted([*COPIAS, *CONVERSIONES])


if __name__ == "__main__":
    for archivo in preparar():
        print(f"entrega/{archivo}  ({(ENTREGA / archivo).stat().st_size // 1024} KB)")
