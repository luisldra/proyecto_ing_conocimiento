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
CONTROLES = 2
# Frase sin información para medir el sesgo por longitud en el panel de agentes (D-059).
RELLENO = ("Esta alerta fue generada automáticamente por el sistema de monitoreo de condición de la planta "
           "a partir del análisis de las señales registradas durante la ventana de observación más reciente.")
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


def preparar(carpeta: Path = CARPETA, semilla: int = 42, controles: bool = False) -> pd.DataFrame:
    """Escribe el formulario (orden contrabalanceado), la clave oculta y la plantilla de respuestas.

    Con ``controles`` se agregan alertas de control (mismo contenido, una con relleno) y los
    archivos llevan el sufijo ``_agentes``.
    """
    ejemplos = json.loads(EJEMPLOS.read_text(encoding="utf-8"))
    elegidas = [{**e, "tipo": "estudio"} for e in seleccionar(ejemplos, semilla)]
    if controles:
        usadas = {(e["activo"], e["modo"]) for e in elegidas}
        resto = [{"activo": a, **e} for a, lista in sorted(ejemplos.items()) for e in lista if (a, e["modo"]) not in usadas]
        rng = np.random.default_rng(semilla + 1)
        elegidas += [{**resto[i], "tipo": "control"} for i in rng.choice(len(resto), CONTROLES, replace=False)]
    sufijo = "_agentes" if controles else ""
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
        if e["tipo"] == "control":
            textos = {"control_relleno": f"{texto_solo_modelo(e)} {RELLENO}", "control_simple": texto_solo_modelo(e)}
        else:
            textos = {"modelo": texto_solo_modelo(e), "hibrida": e["texto"]}
        variantes = list(textos)
        orden = variantes[::-1] if i % 2 else variantes
        lineas += [f"## Alerta A{i:02d} – {e['activo'].replace('_', ' ')}", "",
                   f"Unidad {e['unidad']}, {e['ts']}.", ""]
        for k, variante in enumerate(orden, 1):
            lineas += [f"**Explicación {k}.** {textos[variante]}", ""]
            clave.append({"alerta": f"A{i:02d}", "explicacion": k, "variante": variante,
                          "activo": e["activo"], "modo": e["modo"], "respaldo_reglas": e["respaldo_reglas"]})
        lineas += ["| | Comprensibilidad | Utilidad | Confianza |", "|---|---|---|---|",
                   "| Explicación 1 | | | |", "| Explicación 2 | | | |", "",
                   "Prefiero: ☐ Explicación 1 ☐ Explicación 2 ☐ Me da igual", "", "---", ""]
    (carpeta / f"formulario{sufijo}.md").write_text("\n".join(lineas), encoding="utf-8")
    clave_df = pd.DataFrame(clave)
    clave_df.to_csv(carpeta / f"clave{sufijo}.csv", index=False)
    plantilla = clave_df[["alerta", "explicacion"]].assign(evaluador="E01", perfil="", comprensibilidad="",
                                                         utilidad="", confianza="", preferida="", comentario="")
    plantilla[COLUMNAS].to_csv(carpeta / f"respuestas_plantilla{sufijo}.csv", index=False)
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
    pruebas = {d: _comparar(pares, d, "hibrida", "modelo") for d in DIMENSIONES}
    pref = r[r["preferida"].notna() & (r["preferida"].astype(str) != "")].drop_duplicates(["evaluador", "alerta"])
    elegida = pref.apply(lambda f: _variante_preferida(f, clave), axis=1)
    resumen = {
        "evaluadores": int(r["evaluador"].nunique()), "alertas": int(r["alerta"].nunique()),
        "pruebas": pruebas, "preferencia": elegida.value_counts().to_dict(),
        "por_respaldo_reglas": r[r["variante"] == "hibrida"].groupby("respaldo_reglas")[list(DIMENSIONES)].mean().round(3).to_dict(),
    }
    if "control_relleno" in set(r["variante"]):  # sesgo por longitud: relleno sin información vs. simple
        resumen["control_longitud"] = {d: _comparar(pares, d, "control_relleno", "control_simple") for d in DIMENSIONES}
    return tabla, resumen


def _comparar(pares: pd.DataFrame, d: str, a: str, b: str) -> dict[str, float]:
    dif = (pares[(d, a)] - pares[(d, b)]).dropna()
    no_nulas = dif[dif != 0]
    p = float(wilcoxon(no_nulas).pvalue) if len(no_nulas) >= 6 else float("nan")
    return {"pares": int(len(dif)), "diferencia_media": float(dif.mean()) if len(dif) else float("nan"), "p_wilcoxon": p}


def _variante_preferida(fila: pd.Series, clave: pd.DataFrame) -> str:
    try:  # pandas puede leer la columna como texto o como número (1.0)
        valor = int(float(str(fila["preferida"]).strip()))
    except ValueError:
        return "indiferente"
    if valor not in (1, 2):
        return "indiferente"
    k = clave[(clave["alerta"] == fila["alerta"]) & (clave["explicacion"] == valor)]
    return str(k["variante"].iloc[0])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluación humana de explicaciones (Likert).")
    ap.add_argument("accion", choices=["preparar", "analizar"])
    ap.add_argument("--agentes", action="store_true", help="panel de agentes: formulario con controles (D-059)")
    args = ap.parse_args(argv)
    sufijo = "_agentes" if args.agentes else ""
    if args.accion == "preparar":
        clave = preparar(controles=args.agentes)
        print(f"{clave['alerta'].nunique()} alertas preparadas en {CARPETA}")
        return 0
    tabla, resumen = analizar(pd.read_csv(CARPETA / f"respuestas{sufijo}.csv"), pd.read_csv(CARPETA / f"clave{sufijo}.csv"))
    salida = RAIZ / "reports" / "tables"
    nombre = "evaluacion_agentes" if args.agentes else "evaluacion_humana"
    tabla.to_csv(salida / f"{nombre}.csv", index=False)
    (salida / f"{nombre}_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(tabla.round(2).to_string(index=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
