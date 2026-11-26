"""Genera ``landing/data.js`` con las cifras de la landing, leídas de ``reports/`` y de la base de
conocimiento (Fase 8b). Así la página nunca muestra un número escrito a mano.

Se escribe como JavaScript (``window.DATOS = …``) y no como JSON para que ``index.html`` funcione
también abierto con doble clic, sin servidor (los navegadores bloquean ``fetch`` en file://).

Uso: ``python scripts/generar_datos_landing.py``
"""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd

from metaltech.kb.base import RAIZ, cargar_base

TABLAS = RAIZ / "reports" / "tables"
SALIDA = RAIZ / "landing" / "data.js"
SISTEMAS = ["M0", "M1", "M2", "M3"]
NORMAS = ["ISO 20816-3 (vibración)", "ISO 10816-7 vía Europump (bombas)", "ISO 17359 y 13374 (monitoreo de condición)",
          "IEC 60034-1 y NEMA MG-1 (motores)", "ANSI/HI 9.6.1 (NPSH, cavitación)", "IEEE 519 (armónicos)",
          "ISO 4406 (limpieza de aceite)"]
DATASETS = ["AI4I 2020", "CWRU Bearing", "NASA IMS", "NASA C-MAPSS", "MIMII", "SKAB", "UCI sistemas hidráulicos"]


def _json(nombre: str) -> Any:
    return json.loads((TABLAS / nombre).read_text(encoding="utf-8"))


def _redondear(x: float, d: int = 4) -> float:
    return round(float(x), d)


def conocimiento() -> dict[str, Any]:
    base = cargar_base()
    decisiones = (RAIZ / "knowledge" / "acquisition" / "decisiones.md").read_text(encoding="utf-8")
    referencias = decisiones[decisiones.index("## Referencias (APA 7)"):]
    regla = base.reglas_por_id["R13"]
    expresion = next(e for e in base.lexico if e["id"] == "EXP03")
    return {
        "reglas": len(base.reglas), "modos": len(base.modos), "sintomas": len(base.sintomas),
        "fmea": sum(len(v) for v in base.fmea.values()), "expresiones": len(base.lexico),
        "decisiones": len(re.findall(r"(?m)^\| D-\d{3} \|", decisiones)),
        "referencias": len(re.findall(r"(?m)^- ", referencias)),
        "activos": len(base.activos), "unidades": sum(d["unidades"] for d in base.activos.values()),
        "normas": NORMAS, "datasets": DATASETS,
        "regla_ejemplo": {"id": regla["id"], "si": regla["si"], "entonces": base.modos[regla["entonces"]]["nombre"],
                          "fc": regla["fc"], "accion": regla["accion"]},
        "expresion_ejemplo": {"texto": expresion["expresion"], "sintoma": expresion["sintoma_percibido"],
                              "candidatos": [base.modos[c["id"]]["nombre"] for c in expresion["modos_falla_candidatos"]
                                             if c["id"] in base.modos]},
    }


def resultados() -> dict[str, Any]:
    intervalos = pd.read_csv(TABLAS / "intervalos_sistemas.csv")
    difs = pd.read_csv(TABLAS / "intervalos_diferencias.csv")

    def serie(particion: str, metrica: str) -> list[dict[str, Any]]:
        t = intervalos[(intervalos["particion"] == particion) & (intervalos["metrica"] == metrica)].set_index("sistema")
        return [{"sistema": s, "media": _redondear(t.loc[s, "media"]), "inf": _redondear(t.loc[s, "ic95_inf"]),
                 "sup": _redondear(t.loc[s, "ic95_sup"])} for s in SISTEMAS]

    def diferencia(particion: str, comparacion: str, metrica: str) -> dict[str, float]:
        f = difs[(difs["particion"] == particion) & (difs["comparacion"] == comparacion) & (difs["metrica"] == metrica)].iloc[0]
        return {"media": _redondear(f["diferencia_media"]), "inf": _redondear(f["ic95_inf"]), "sup": _redondear(f["ic95_sup"]),
                "a_mayor_pct": _redondear(f["a_mayor_pct"], 1)}

    impacto = _json("impacto_resumen.json")
    xai = pd.read_csv(TABLAS / "xai_metricas.csv")
    panel = pd.read_csv(TABLAS / "evaluacion_agentes.csv")
    panel = panel[panel["variante"].isin(["modelo", "hibrida"])]
    brechas = pd.read_csv(TABLAS / "equidad_brechas.csv").set_index(["grupo", "sistema"])
    grupos = pd.read_csv(TABLAS / "equidad_grupos.csv")
    obs = grupos[(grupos["grupo"] == "observacion")].groupby(["valor", "sistema"])["falsa_alarma"].mean()
    latencia = _json("latencia_api_resumen.json")
    panel_res = _json("evaluacion_agentes_resumen.json")
    return {
        "semillas": int(intervalos["semillas"].max()),
        "f1_test": serie("test", "f1_macro"), "f1_no_vista": serie("test_unidad", "f1_macro"),
        "fa_confusor_no_vista": serie("test_unidad", "falsa_alarma_con_confusor"),
        "m3_m1_f1_no_vista": diferencia("test_unidad", "M3-M1", "f1_macro"),
        "m3_m1_fa_no_vista": diferencia("test_unidad", "M3-M1", "falsa_alarma_con_confusor"),
        "m2_m1_f1_no_vista": diferencia("test_unidad", "M2-M1", "f1_macro"),
        "impacto": {s: {"detectadas_pct": _redondear(impacto["medias"][s]["detectadas_pct"], 1),
                        "eventos_fa": _redondear(impacto["medias"][s]["eventos_falsa_alarma_por_unidad_anio"], 2),
                        "costo_r5": _redondear(impacto["medias"][s]["costo_unidad_anio_r5"], 2)} for s in SISTEMAS},
        "ahorro_m3_vs_m0_pct": {str(r): impacto[f"ahorro_vs_M0_r{r}_pct"]["M3"] for r in (3, 5, 9)},
        "xai": {"top3_firma": _redondear(xai["top_k_en_firma"].mean(), 3), "top3_azar": _redondear(xai["top_k_en_firma_azar"].mean(), 3),
                "top3_reglas": _redondear(xai["top_k_en_reglas"].mean(), 3), "fidelidad": _redondear(xai["caida_top_k"].mean(), 3),
                "fidelidad_azar": _redondear(xai["caida_azar_k"].mean(), 3)},
        "panel": {d: {v: _redondear(g.loc[g["variante"] == v, "media"].iloc[0], 2) for v in ("modelo", "hibrida")}
                  for d, g in panel.groupby("dimension")},
        "panel_preferencia": {"hibrida": int(panel_res["preferencia"]["hibrida"]),
                              "pares": int(panel_res["pruebas"]["utilidad"]["pares"])},
        "equidad": {"brecha_turno_m3_pts": _redondear(100 * brechas.loc[("turno", "M3"), "acierto_falla_brecha"], 1),
                    "fa_obs_incorrecta": {s: _redondear(100 * obs.loc[("incorrecta", s)], 2) for s in ("M0", "M3")},
                    "fa_sin_obs": {s: _redondear(100 * obs.loc[("ninguna", s)], 2) for s in ("M0", "M3")}},
        "latencia_ms": {"sin_explicacion": latencia["p95_max_ms"]["sin_explicacion"],
                        "con_explicacion": latencia["p95_max_ms"]["con_explicacion"]},
    }


def ejemplo() -> dict[str, Any]:
    """Una alerta real explicada: con regla que la respalda y, si hay, observación del técnico."""
    ejemplos = [e for lista in _json("xai_ejemplos.json").values() for e in lista]
    sugiere = {e["expresion"]: {c["id"] for c in e["modos_falla_candidatos"]} for e in cargar_base().lexico}

    def coherente(x: dict[str, Any]) -> bool:  # la expresión del técnico sugiere el modo concluido
        return any(x["modo"] in sugiere.get(t, set()) for t in x["expresiones"])

    # Con regla que la respalde; mejor sin observación que con una que no corresponde a la falla.
    e = max(ejemplos, key=lambda x: (x["respaldo_reglas"], coherente(x), not x["expresiones"], x["modo"] == "cavitacion"))
    return {"texto": e["texto"], "variables": e["variables_influyentes"], "unidad": e["unidad"],
            "reglas": [r["id"] for r in e["reglas"]]}


def datos_y_prototipo() -> dict[str, Any]:
    """Tamaño del dataset (desde el manifiesto) y piezas del prototipo (contadas en el código)."""
    manifiesto = RAIZ / "data" / "synthetic" / "manifest.json"
    datos = None
    if manifiesto.exists():
        m = json.loads(manifiesto.read_text(encoding="utf-8"))
        filas = m["filas"]
        datos = {"meses": m["meses"], "filas": sum(n for f, n in filas.items() if f not in ("episodios.parquet", "observaciones.parquet")),
                 "episodios": filas["episodios.parquet"], "observaciones": filas["observaciones.parquet"]}
    api = (RAIZ / "src" / "metaltech" / "api" / "main.py").read_text(encoding="utf-8")
    paginas = sorted((RAIZ / "src" / "metaltech" / "dashboard" / "pages").glob("[0-9]_*.py"))
    return {"datos": datos, "prototipo": {"endpoints": len(re.findall(r"@app\.(?:get|post)\(", api)), "paginas": len(paginas)}}


def construir() -> dict[str, Any]:
    return {"conocimiento": conocimiento(), "resultados": resultados(), "ejemplo": ejemplo(), **datos_y_prototipo(),
            "repositorio": "https://github.com/luisldra/proyecto_ing_conocimiento"}


def leer_actual() -> dict[str, Any]:
    """Lo que hoy contiene ``landing/data.js``."""
    texto = SALIDA.read_text(encoding="utf-8")
    return json.loads(texto[texto.index("{"): texto.rindex("}") + 1])


def generar() -> dict[str, Any]:
    datos = construir()
    SALIDA.write_text("// Generado por scripts/generar_datos_landing.py; no editar a mano.\nwindow.DATOS = "
                      + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    return datos


if __name__ == "__main__":
    d = generar()
    print(f"{SALIDA.relative_to(RAIZ)}: {len(json.dumps(d))} caracteres")
