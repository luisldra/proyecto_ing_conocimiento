"""Verificación del proceso: MEMORIA.md y ERRORES.md enlazados (rol QA)."""

from __future__ import annotations

from metaltech.proceso import verificar


def test_memoria_y_errores_consistentes():
    assert verificar() == []


def test_detecta_error_citado_inexistente(tmp_path):
    memoria = tmp_path / "MEMORIA.md"
    errores = tmp_path / "ERRORES.md"
    memoria.write_text(
        "## Estado actual\n## [2026-01-01] Tarea\n- Errores: ERR-999\n", encoding="utf-8"
    )
    errores.write_text(
        "## Índice por origen\n| x | ERR-001 |\n## Lecciones aprendidas\n### ERR-001 – a\n",
        encoding="utf-8",
    )
    problemas = verificar(memoria, errores)
    assert any("ERR-999" in p for p in problemas)
