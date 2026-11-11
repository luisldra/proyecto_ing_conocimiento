"""Evaluación humana de las explicaciones con escala Likert (Fase 6, D-058).

Cada evaluador califica, para la misma alerta, dos explicaciones sin saber cuál es cuál:
la del modelo solo (sensores con más peso) y la híbrida (sensores, reglas, técnico y
acción). Así se mide si el conocimiento experto hace la explicación más útil.

Uso:
    python -m metaltech.xai.evaluacion_humana preparar   # formulario, clave y plantilla
    python -m metaltech.xai.evaluacion_humana analizar   # resultados a partir de las respuestas
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from metaltech.kb.base import RAIZ

CARPETA = RAIZ / "docs" / "evaluacion_humana"
EJEMPLOS = RAIZ / "reports" / "tables" / "xai_ejemplos.json"
DIMENSIONES = {
    "comprensibilidad": "Entiendo por qué el sistema emitió esta alerta.",
    "utilidad": "La explicación me ayuda a decidir qué hacer con el equipo.",
    "confianza": "Confiaría en esta alerta para programar una intervención.",
}
ALERTAS_POR_ACTIVO = 2
COLUMNAS = ["evaluador", "perfil", "alerta", "explicacion", *DIMENSIONES, "preferida", "comentario"]


# ---------------------------------------------------------------------------------------
# Preparación
# ---------------------------------------------------------------------------------------
def texto_solo_modelo(ejemplo: dict[str, Any]) -> str:
    """Lo que diría M1 sin conocimiento experto: la falla, su puntaje y los sensores con más peso."""
    sensores = ", ".join(f"{v['variable']} ({v['peso']:.0%})" for v in ejemplo["variables_influyentes"])
    return (f"Alerta de {ejemplo['nombre'].lower()} (probabilidad del modelo {ejemplo['probabilidad_modelo']:.0%}). "
            f"Los sensores con más peso en la predicción fueron {sensores}.")


def seleccionar(ejemplos: dict[str, list[dict[str, Any]]], semilla: int = 42) -> list[dict[str, Any]]:
    """Por activo, una alerta con respaldo de reglas y una sin él cuando existen ambas."""
    rng = np.random.default_rng(semilla)
    elegidas = []
    for activo in sorted(ejemplos):
        con = [e for e in ejemplos[activo] if e["respaldo_reglas"]]
        sin = [e for e in ejemplos[activo] if not e["respaldo_reglas"]]
        grupo = [g for g in (con, sin) if g]
        tomadas: list[dict[str, Any]] = []
        for g in grupo:
            tomadas.append(g[int(rng.integers(len(g)))])
        resto = [e for e in ejemplos[activo] if e not in tomadas]
        while len(tomadas) < ALERTAS_POR_ACTIVO and resto:
            tomadas.append(resto.pop(int(rng.integers(len(resto)))))
        elegidas += [{"activo": activo, **e} for e in tomadas[:ALERTAS_POR_ACTIVO]]
    return elegidas


def preparar(carpeta: Path = CARPETA, semilla: int = 42) -> pd.DataFrame:
    """Escribe el formulario (orden contrabalanceado), la clave oculta y la plantilla de respuestas."""
    ejemplos = json.loads(EJEMPLOS.read_text(encoding="utf-8"))
    elegidas = seleccionar(ejemplos, semilla)
    carpeta.mkdir(parents=True, exist_ok=True)
    lineas = [
        "# Formulario de evaluación de explicaciones",
        "",
        "Para cada alerta lea las dos explicaciones y califique cada afirmación de 1 a 5",
        "(1 = totalmente en desacuerdo, 5 = totalmente de acuerdo). Después indique cuál prefiere.",
        "Las dos explicaciones corresponden a la misma alerta; no hay respuestas correctas.",
        "",
        "Afirmaciones:",
        *[f"- **{d.capitalize()}:** {t}" for d, t in DIMENSIONES.items()],
        "",
    ]
    clave = []
    for i, e in enumerate(elegidas, 1):
        textos = {"modelo": texto_solo_modelo(e), "hibrida": e["texto"]}
        orden = ["hibrida", "modelo"] if i % 2 else ["modelo", "hibrida"]
        lineas += [f"## Alerta A{i:02d} – {e['activo'].replace('_', ' ')}", "",
                   f"Unidad {e['unidad']}, {e['ts']}.", ""]
        for k, variante in enumerate(orden, 1):
            lineas += [f"**Explicación {k}.** {textos[variante]}", ""]
            clave.append({"alerta": f"A{i:02d}", "explicacion": k, "variante": variante,
                          "activo": e["activo"], "modo": e["modo"], "respaldo_reglas": e["respaldo_reglas"]})
        lineas += ["| | Comprensibilidad | Utilidad | Confianza |", "|---|---|---|---|",
                   "| Explicación 1 | | | |", "| Explicación 2 | | | |", "",
                   "Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual", "", "---", ""]
    (carpeta / "formulario.md").write_text("\n".join(lineas), encoding="utf-8")
    clave_df = pd.DataFrame(clave)
    clave_df.to_csv(carpeta / "clave.csv", index=False)
    plantilla = clave_df[["alerta", "explicacion"]].assign(evaluador="E01", perfil="", comprensibilidad="",
                                                         utilidad="", confianza="", preferida="", comentario="")
    plantilla[COLUMNAS].to_csv(carpeta / "respuestas_plantilla.csv", index=False)
    return clave_df


# ---------------------------------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------------------------------
def validar(respuestas: pd.DataFrame) -> pd.DataFrame:
    faltan = set(COLUMNAS) - set(respuestas.columns)
    if faltan:
        raise ValueError(f"faltan columnas: {sorted(faltan)}")
    r = respuestas.dropna(subset=list(DIMENSIONES)).copy()
    for d in DIMENSIONES:
        r[d] = pd.to_numeric(r[d], errors="raise")
        if not r[d].between(1, 5).all() or not (r[d] % 1 == 0).all():
            raise ValueError(f"{d}: solo se admiten enteros de 1 a 5")
    if r.duplicated(["evaluador", "alerta", "explicacion"]).any():
        raise ValueError("hay calificaciones repetidas de un mismo evaluador")
    return r


def analizar(respuestas: pd.DataFrame, clave: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Medias, medianas y % de acuerdo por variante; prueba de Wilcoxon pareada híbrida vs. modelo."""
    r = validar(respuestas).merge(clave, on=["alerta", "explicacion"], how="left")
    if r["variante"].isna().any():
        raise ValueError("hay alertas o explicaciones que no están en la clave")
    filas = []
    for d in DIMENSIONES:
        for variante, g in r.groupby("variante"):
            filas.append({"dimension": d, "variante": variante, "n": len(g), "media": g[d].mean(),
                          "mediana": g[d].median(), "acuerdo_pct": 100 * (g[d] >= 4).mean()})
    tabla = pd.DataFrame(filas)
    pares = r.pivot_table(index=["evaluador", "alerta"], columns="variante", values=list(DIMENSIONES))
    pruebas = {}
    for d in DIMENSIONES:
        dif = (pares[(d, "hibrida")] - pares[(d, "modelo")]).dropna()
        no_nulas = dif[dif != 0]
        p = float(wilcoxon(no_nulas).pvalue) if len(no_nulas) >= 6 else float("nan")
        pruebas[d] = {"pares": int(len(dif)), "diferencia_media": float(dif.mean()), "p_wilcoxon": p}
    pref = r[r["preferida"].notna() & (r["preferida"].astype(str) != "")].drop_duplicates(["evaluador", "alerta"])
    elegida = pref.apply(lambda f: _variante_preferida(f, clave), axis=1)
    resumen = {
        "evaluadores": int(r["evaluador"].nunique()), "alertas": int(r["alerta"].nunique()),
        "pruebas": pruebas, "preferencia": elegida.value_counts().to_dict(),
        "por_respaldo_reglas": r[r["variante"] == "hibrida"].groupby("respaldo_reglas")[list(DIMENSIONES)].mean().round(3).to_dict(),
    }
    return tabla, resumen


def _variante_preferida(fila: pd.Series, clave: pd.DataFrame) -> str:
    valor = str(fila["preferida"]).strip()
    if valor not in ("1", "2"):
        return "indiferente"
    k = clave[(clave["alerta"] == fila["alerta"]) & (clave["explicacion"] == int(valor))]
    return str(k["variante"].iloc[0])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluación humana de explicaciones (Likert).")
    ap.add_argument("accion", choices=["preparar", "analizar"])
    ap.add_argument("--respuestas", default=CARPETA / "respuestas.csv", type=Path)
    args = ap.parse_args(argv)
    if args.accion == "preparar":
        clave = preparar()
        print(f"{clave['alerta'].nunique()} alertas preparadas en {CARPETA}")
        return 0
    tabla, resumen = analizar(pd.read_csv(args.respuestas), pd.read_csv(CARPETA / "clave.csv"))
    salida = RAIZ / "reports" / "tables"
    tabla.to_csv(salida / "evaluacion_humana.csv", index=False)
    (salida / "evaluacion_humana_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(tabla.round(2).to_string(index=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
