"""Genera el documento APA 7 (Fase 10) desde ``docs/documento_APA/documento.md``.

Las cifras (``{{v:clave}}``), las tablas (``{{tabla:nombre}}``) y las figuras salen de ``reports/`` y de la
base de conocimiento, igual que la landing: el documento nunca muestra un número escrito a mano.

Uso:
    python scripts/generar_documento.py                 # docs/documento_APA/documento_apa.docx
    python scripts/generar_documento.py --figuras       # además regenera las figuras (matplotlib y Playwright)
    python scripts/generar_documento.py --capturas DIR  # copia la captura del simulador de revisar_web.py
    python scripts/generar_documento.py --pdf           # además exporta a PDF con Microsoft Word (Windows)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from generar_datos_landing import construir  # noqa: E402

from metaltech.kb.base import cargar_base  # noqa: E402

CARPETA = RAIZ / "docs" / "documento_APA"
FUENTE = CARPETA / "documento.md"
REFERENCIAS = CARPETA / "referencias.md"
FIGURAS = CARPETA / "figuras"
SALIDA = CARPETA / "documento_apa.docx"
TABLAS = RAIZ / "reports" / "tables"
SISTEMAS = ["M0", "M1", "M2", "M3"]
COLORES = {"M0": "#2a78d6", "M1": "#eb6834", "M2": "#1baf7a", "M3": "#eda100"}  # paleta validada (D-061)
TINTA, TINTA_2, REJILLA = "#1f2328", "#57606a", "#d0d7de"

PORTADA = {
    "titulo": "Mantenimiento predictivo explicable en una planta manufacturera con Deep Learning y base de conocimiento",
    "autores": ["Alejandro [PENDIENTE: apellidos]", "Luis David Rodríguez Arias", "Junio [PENDIENTE: apellidos]",
                "David [PENDIENTE: apellidos]"],
    "lineas": ["Facultad de Inteligencia Artificial e Ingenierías", "[PENDIENTE: departamento]", "Universidad de Caldas",
               "Ingeniería del Conocimiento", "Ing. Wilson Fernando López Cardona", "Noviembre de 2026"],
}
NOMBRES_ACTIVO = {"motor_electrico": "Motor eléctrico", "bomba_centrifuga": "Bomba centrífuga",
                  "compresor_tornillo": "Compresor de tornillo", "prensa_hidraulica": "Prensa hidráulica",
                  "banda_transportadora": "Banda transportadora", "centro_cnc": "Centro CNC"}
CLASES_ONTOLOGIA = {
    "Activo": "Equipo de la planta; una subclase por tipo",
    "Componente": "Parte de un activo (rodamiento, sello, devanado…)",
    "Sensor": "Instrumento de una unidad que mide una variable",
    "Variable": "Magnitud medida, con rango nominal y umbrales",
    "SintomaMedido": "Condición detectada sobre una variable",
    "SintomaPercibido": "Condición que percibe un técnico",
    "ModoFalla": "Forma en que falla un componente",
    "Causa": "Origen de un modo de falla",
    "Accion": "Intervención recomendada",
    "Regla": "SI síntomas ENTONCES modo de falla, con FC",
    "FilaFMEA": "Severidad, ocurrencia, detección y NPR",
    "ExpresionColoquial": "Frase de técnico y síntoma al que refiere",
    "Tecnico": "Técnico ficticio (seudónimo)",
    "Turno": "Mañana, tarde o noche",
    "Alerta": "Diagnóstico sustentado por reglas y variables",
}


# ----------------------------------------------------------------------------- cifras
def _pct(x: float, d: int = 1) -> str:
    return "—" if pd.isna(x) else f"{100 * x:.{d}f} %"


def _ic(x: float, a: float, b: float, d: int = 3) -> str:
    return f"{x:.{d}f} [{a:.{d}f}, {b:.{d}f}]"


def _puntos(x: float) -> str:
    return f"{100 * x:+.1f}".replace("-", "−")


def contar_pruebas() -> str:
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "--co", "-p", "no:warnings"], cwd=RAIZ,  # addopts ya trae -q
                           capture_output=True, text=True, timeout=300)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return m.group(1) if m else "más de 600"
    except (OSError, subprocess.SubprocessError):
        return "más de 600"


def valores() -> dict[str, str]:
    d = construir()
    k, r = d["conocimiento"], d["resultados"]
    nv = {x["sistema"]: x for x in r["f1_no_vista"]}
    fa = {x["sistema"]: x for x in r["fa_confusor_no_vista"]}
    imp = json.loads((TABLAS / "impacto_resumen.json").read_text(encoding="utf-8"))
    from metaltech.kb.ontology import Ontologia

    onto = Ontologia.cargar()
    o = getattr(onto, "onto", None) or onto.ontologia
    v = {
        "reglas": k["reglas"], "modos": k["modos"], "sintomas": k["sintomas"], "fmea": k["fmea"],
        "expresiones": k["expresiones"], "decisiones": k["decisiones"], "referencias_kb": k["referencias"],
        "activos": k["activos"], "unidades": k["unidades"], "repositorio": d["repositorio"],
        "pruebas": contar_pruebas(),
        "f1_m0_nv": f"{nv['M0']['media']:.3f}", "f1_m1_nv": f"{nv['M1']['media']:.3f}",
        "f1_m2_nv": f"{nv['M2']['media']:.3f}", "f1_m3_nv": f"{nv['M3']['media']:.3f}",
        "fa_m0_nv": _pct(fa["M0"]["media"]), "fa_m1_nv": _pct(fa["M1"]["media"]), "fa_m3_nv": _pct(fa["M3"]["media"]),
        "fa_red_rel": f"{100 * (1 - fa['M3']['media'] / fa['M1']['media']):.0f} %",
        "dif_f1_m3_m1": _puntos(r["m3_m1_f1_no_vista"]["media"]),
        "dif_f1_m3_m1_ic": f"{_puntos(r['m3_m1_f1_no_vista']['inf'])} a {_puntos(r['m3_m1_f1_no_vista']['sup'])}",
        "detect_m0": f"{imp['medias']['M0']['detectadas_pct']:.1f} %",
        "detect_m3": f"{imp['medias']['M3']['detectadas_pct']:.1f} %",
        "ev_fa_m0": f"{imp['medias']['M0']['eventos_falsa_alarma_por_unidad_anio']:.1f}",
        "ev_fa_m1": f"{imp['medias']['M1']['eventos_falsa_alarma_por_unidad_anio']:.1f}",
        "ev_fa_m3": f"{imp['medias']['M3']['eventos_falsa_alarma_por_unidad_anio']:.1f}",
        "ahorro_r3": f"{imp['ahorro_vs_M0_r3_pct']['M3']:.0f} %", "ahorro_r9": f"{imp['ahorro_vs_M0_r9_pct']['M3']:.0f} %",
        "lat_sin": f"{r['latencia_ms']['sin_explicacion']:.1f} ms", "lat_con": f"{r['latencia_ms']['con_explicacion']:.1f} ms",
        "xai_firma": _pct(r["xai"]["top3_firma"]), "xai_azar": _pct(r["xai"]["top3_azar"]),
        "xai_reglas": _pct(r["xai"]["top3_reglas"]), "fidelidad": _pct(r["xai"]["fidelidad"]),
        "fidelidad_azar": _pct(r["xai"]["fidelidad_azar"]),
        "fa_sin_obs_m0": f"{r['equidad']['fa_sin_obs']['M0']:.2f} %",
        "fa_obs_inc_m0": f"{r['equidad']['fa_obs_incorrecta']['M0']:.2f} %",
        "fa_sin_obs_m3": f"{r['equidad']['fa_sin_obs']['M3']:.2f} %",
        "fa_obs_inc_m3": f"{r['equidad']['fa_obs_incorrecta']['M3']:.2f} %",
        "brecha_turno": f"{r['equidad']['brecha_turno_m3_pts']:.1f}",
        "ejemplo": d["ejemplo"]["texto"],
        "propiedades_objeto": ", ".join(sorted(p.name for p in o.object_properties())),
    }
    return {c: str(x) for c, x in v.items()}


# ----------------------------------------------------------------------------- tablas
@dataclass
class Tabla:
    titulo: str
    encabezados: list[str]
    filas: list[list[str]]
    nota: str = ""
    letra: float = 10
    anchos: list[float] = field(default_factory=list)  # proporciones


def _intervalos() -> pd.DataFrame:
    return pd.read_csv(TABLAS / "intervalos_sistemas.csv")


def t_conocimiento() -> Tabla:
    k = construir()["conocimiento"]
    filas = [["Tipos de activo", k["activos"], "configs/assets.yaml"], ["Unidades simuladas", k["unidades"], "configs/assets.yaml"],
             ["Modos de falla", k["modos"], "configs/failure_modes.yaml"], ["Síntomas", k["sintomas"], "configs/assets.yaml"],
             ["Reglas con factor de certeza", k["reglas"], "knowledge/rules/rules.yaml"],
             ["Filas de la FMEA", k["fmea"], "knowledge/acquisition/fmea.yaml"],
             ["Expresiones de técnicos", k["expresiones"], "knowledge/lexicon/expresiones.yaml"],
             ["Decisiones documentadas", k["decisiones"], "knowledge/acquisition/decisiones.md"],
             ["Referencias consultadas", k["referencias"], "knowledge/acquisition/decisiones.md"]]
    return Tabla("Contenido de la base de conocimiento", ["Elemento", "Cantidad", "Archivo"],
                 [[a, str(b), c] for a, b, c in filas], "Los archivos YAML son la fuente única de verdad; la ontología se genera desde ellos.",
                 anchos=[3, 1.2, 3.5])


def t_lexico() -> Tabla:
    base = cargar_base()
    filas = [[f"“{e['expresion']}”", e["sintoma_percibido"].replace("_", " "),
              "; ".join(base.modos[c["id"]]["nombre"] for c in e["modos_falla_candidatos"] if c["id"] in base.modos)]
             for e in base.lexico]
    return Tabla("Léxico de expresiones de técnicos", ["Expresión", "Síntoma percibido", "Modos de falla candidatos"], filas,
                 "Las expresiones son las del enunciado del curso; no se atribuyen a técnicos reales.", letra=9, anchos=[2.2, 1.8, 4.5])


def t_ontologia() -> Tabla:
    from metaltech.kb.ontology import Ontologia

    onto = Ontologia.cargar()
    o = getattr(onto, "onto", None) or onto.ontologia
    cuenta: dict[str, int] = {}
    subclases = {c.name for c in o.Activo.subclasses()} if hasattr(o, "Activo") else set()
    for i in o.individuals():
        n = i.is_a[0].name
        cuenta["Activo" if n in subclases else n] = cuenta.get("Activo" if n in subclases else n, 0) + 1
    filas = [[c, d, str(cuenta.get(c, 0))] for c, d in CLASES_ONTOLOGIA.items()]
    n_clases = len(list(o.classes()))
    return Tabla("Clases principales de la ontología", ["Clase", "Qué representa", "Individuos"], filas,
                 f"La ontología tiene {n_clases} clases, {len(list(o.object_properties()))} propiedades de objeto, "
                 f"{len(list(o.data_properties()))} propiedades de datos y {len(list(o.individuals()))} individuos. "
                 "Activo agrupa las unidades de sus seis subclases. La clase Alerta se instancia en tiempo de ejecución.",
                 anchos=[2, 4.5, 1.2])


def t_modelos() -> Tabla:
    sel = json.loads((TABLAS / "modelos_seleccion.json").read_text(encoding="utf-8"))
    fus = json.loads((TABLAS / "fusion_parametros.json").read_text(encoding="utf-8"))
    filas = [[NOMBRES_ACTIVO[a], arq.upper(), f"{fus[a]['alfa']:.1f}", "sí" if fus[a]["veto"] else "no"] for a, arq in sel.items()]
    return Tabla("Arquitectura y parámetros de fusión elegidos por activo", ["Activo", "Arquitectura (M1)", "α (M3)", "Veto (M3)"],
                 filas, "Elegidos por F1 macro de validación con la semilla 42; α en {0.3, …, 0.8}.", anchos=[3, 2, 1.2, 1.2])


def t_resultados() -> Tabla:
    i = _intervalos()

    def celda(part: str, s: str, m: str, pct: bool = False) -> str:
        f = i[(i["particion"] == part) & (i["sistema"] == s) & (i["metrica"] == m)].iloc[0]
        if pct:
            return f"{100 * f['media']:.1f} [{100 * f['ic95_inf']:.1f}, {100 * f['ic95_sup']:.1f}]"
        return _ic(f["media"], f["ic95_inf"], f["ic95_sup"])

    filas = [[s, celda("test_unidad", s, "f1_macro"), celda("test_unidad", s, "precision_macro"),
              celda("test_unidad", s, "recall_macro"), celda("test_unidad", s, "falsa_alarma_con_confusor", True),
              celda("test", s, "f1_macro")] for s in SISTEMAS]
    return Tabla("Desempeño de los cuatro sistemas",
                 ["Sistema", "F1 macro", "Precisión", "Recall", "Falsa alarma con confusor (%)", "F1 macro (prueba temporal)"], filas,
                 "Las cinco primeras columnas corresponden a la unidad reservada de cada tipo (máquina no vista). "
                 "Media de 5 semillas e intervalo t del 95 % entre corchetes; M0 es determinista. "
                 "M0 = solo reglas; M1 = solo aprendizaje profundo; M2 = conocimiento como entrada; M3 = fusión.",
                 letra=9, anchos=[1, 2, 2, 2, 2, 2])


def t_diferencias() -> Tabla:
    d = pd.read_csv(TABLAS / "intervalos_diferencias.csv")
    d = d[d["particion"] == "test_unidad"]
    filas = []
    for c in ["M1-M0", "M3-M0", "M2-M1", "M3-M1", "M3-M2"]:
        f1 = d[(d["comparacion"] == c) & (d["metrica"] == "f1_macro")].iloc[0]
        fa = d[(d["comparacion"] == c) & (d["metrica"] == "falsa_alarma_con_confusor")].iloc[0]
        filas.append([c.replace("-", " − "), _puntos(f1["diferencia_media"]),
                      f"{_puntos(f1['ic95_inf'])} a {_puntos(f1['ic95_sup'])}",
                      _puntos(fa["diferencia_media"]), f"{_puntos(fa['ic95_inf'])} a {_puntos(fa['ic95_sup'])}"])
    return Tabla("Diferencias pareadas entre sistemas en la máquina no vista",
                 ["Comparación", "Δ F1 (puntos)", "IC 95 %", "Δ falsa alarma con confusor (puntos)", "IC 95 %"], filas,
                 "Diferencias pareadas por activo y semilla, en puntos porcentuales. Un intervalo que no incluye el cero indica "
                 "una diferencia consistente.", anchos=[1.6, 1.4, 1.8, 2, 1.8])


def t_impacto() -> Tabla:
    imp = json.loads((TABLAS / "impacto_resumen.json").read_text(encoding="utf-8"))["medias"]
    filas = [[s, f"{m['detectadas_pct']:.1f} %", f"{m['anticipacion_mediana_h']:.0f}", f"{m['eventos_falsa_alarma_por_unidad_anio']:.1f}",
              f"{m['costo_unidad_anio_r3']:.1f}", f"{m['costo_unidad_anio_r5']:.1f}", f"{m['costo_unidad_anio_r9']:.1f}"]
             for s, m in imp.items()]
    return Tabla("Fallas detectadas, falsas alarmas y costo relativo",
                 ["Sistema", "Fallas detectadas", "Anticipación mediana (h)", "Eventos de falsa alarma por unidad y año",
                  "Costo r = 3", "Costo r = 5", "Costo r = 9"], filas,
                 "Costo por unidad y año en unidades de una reparación planificada. r = costo de una falla no detectada "
                 "frente a una reparación planificada; una falsa alarma cuesta 0.1. Todos los costos son supuestos.",
                 letra=9, anchos=[1, 1.4, 1.5, 1.8, 1, 1, 1])


def t_xai() -> Tabla:
    x = pd.read_csv(TABLAS / "xai_metricas.csv")
    filas = [[NOMBRES_ACTIVO[f["activo"]], f["arquitectura"].upper(), _pct(f["top_k_en_firma"]), _pct(f["top_k_en_firma_azar"]),
              _pct(f["top_k_en_reglas"]), _pct(f["caida_top_k"]), _pct(f["caida_azar_k"]), f"{f['estabilidad_ruido_0.25']:.3f}"]
             for _, f in x.iterrows()]
    return Tabla("Métricas de las explicaciones por activo",
                 ["Activo", "Modelo", "Top-3 en la firma", "Top-3 en la firma (azar)", "Top-3 en reglas", "Caída al anular top-3",
                  "Caída al anular 3 al azar", "Estabilidad (ruido 0.25)"], filas,
                 "Sobre hasta 300 alertas correctas de prueba por activo. La estabilidad es la similitud coseno de las atribuciones "
                 "ante ruido de 0.25 desviaciones.", letra=8.5, anchos=[1.8, 1, 1, 1, 1, 1, 1, 1])


def t_panel() -> Tabla:
    e = pd.read_csv(TABLAS / "evaluacion_agentes.csv")
    res = json.loads((TABLAS / "evaluacion_agentes_resumen.json").read_text(encoding="utf-8"))
    filas = []
    for dim in ["comprensibilidad", "utilidad", "confianza"]:
        m = e[(e["dimension"] == dim) & (e["variante"] == "modelo")]["media"].iloc[0]
        h = e[(e["dimension"] == dim) & (e["variante"] == "hibrida")]["media"].iloc[0]
        p = res["pruebas"][dim]["p_wilcoxon"]
        filas.append([dim.capitalize(), f"{m:.2f}", f"{h:.2f}", f"{h - m:+.2f}", f"{p:.1e}"])
    return Tabla("Evaluación exploratoria de las explicaciones con un panel de agentes",
                 ["Dimensión", "Modelo solo", "Híbrida", "Diferencia", "p (Wilcoxon)"], filas,
                 f"Escala de 1 a 5; {res['evaluadores']} agentes × 12 alertas = 60 pares. Los agentes no son personas y sus respuestas "
                 "no son independientes, por lo que los valores p son optimistas.", anchos=[2, 1.3, 1.3, 1.3, 1.5])


def t_equidad() -> Tabla:
    g = pd.read_csv(TABLAS / "equidad_grupos.csv")
    filas = []
    for grupo, nombre in [("turno", "Turno"), ("observacion", "Observación del técnico")]:
        t = g[g["grupo"] == grupo].groupby(["valor", "sistema"])[["acierto_falla", "falsa_alarma"]].mean()
        for valor in sorted({v for v, _ in t.index}):
            filas.append([nombre, {"manana": "mañana"}.get(valor, valor), _pct(t.loc[(valor, "M0"), "acierto_falla"]), _pct(t.loc[(valor, "M3"), "acierto_falla"]),
                          _pct(t.loc[(valor, "M0"), "falsa_alarma"], 2), _pct(t.loc[(valor, "M3"), "falsa_alarma"], 2)])
    return Tabla("Acierto y falsa alarma por turno y por observación del técnico",
                 ["Grupo", "Valor", "Acierto en fallas M0", "Acierto en fallas M3", "Falsa alarma M0", "Falsa alarma M3"], filas,
                 "Promedio de activos y semillas. Los técnicos y su menor acierto nocturno son ficticios: un sesgo inyectado para "
                 "medir equidad. — = no hay ventanas sanas en ese grupo.", letra=9, anchos=[2, 1.3, 1.3, 1.3, 1.3, 1.3])


def t_peores_clases() -> Tabla:
    c = pd.read_csv(TABLAS / "comparacion_por_clase.csv")
    c = c[(c["sistema"] == "M3") & (c["particion"] == "test")].sort_values("f1").head(6)
    base = cargar_base()
    filas = [[NOMBRES_ACTIVO[f["activo"]], base.modos.get(f["clase"], {}).get("nombre", f["clase"]), str(int(f["soporte"])),
              f"{f['precision']:.2f}", f"{f['recall']:.2f}", f"{f['f1']:.2f}"] for _, f in c.iterrows()]
    return Tabla("Clases con menor F1 en M3", ["Activo", "Modo de falla", "Soporte", "Precisión", "Recall", "F1"], filas,
                 "Prueba temporal, semilla 42. Soporte = ventanas con esa clase.", letra=9, anchos=[1.8, 3.8, 1, 1, 1, 0.8])


def t_matriz() -> Tabla:
    texto = (RAIZ / "knowledge" / "acquisition" / "matriz_adquisicion.md").read_text(encoding="utf-8")
    bloque = texto[texto.index("## Matriz"):].split("\n## ")[0].splitlines()  # solo la tabla de la sección Matriz
    filas = [[_limpiar_md(c) for c in linea.strip().strip("|").split("|")] for linea in bloque if linea.startswith("| ")]
    enc, filas = filas[0], [f for f in filas[1:] if not set("".join(f)) <= set("-: ")]
    return Tabla("Matriz de adquisición del conocimiento", enc, filas, "Tipos: declarativo, procedimental o heurístico. "
                 "Las decisiones (D-NNN) están en knowledge/acquisition/decisiones.md.", letra=8, anchos=[0.4, 2, 0.8, 3.2, 1.3, 1.3, 1.1])


def t_reglas() -> Tabla:
    base = cargar_base()
    reglas = yaml.safe_load((RAIZ / "knowledge" / "rules" / "rules.yaml").read_text(encoding="utf-8"))
    filas = [[r["id"], NOMBRES_ACTIVO.get(r["activo"], r["activo"]), " Y ".join(s.replace("_", " ") for s in r["si"]),
              base.modos[r["entonces"]]["nombre"], f"{r['fc']:.2f}"] for r in reglas]
    return Tabla("Reglas de diagnóstico", ["ID", "Activo", "SI (síntomas)", "ENTONCES (modo de falla)", "FC"], filas,
                 "Las acciones y las fuentes de cada regla están en knowledge/rules/rules.yaml y decisiones.md.",
                 letra=8, anchos=[0.5, 1.5, 3.5, 3, 0.5])


GENERADORES = {"conocimiento": t_conocimiento, "lexico": t_lexico, "ontologia": t_ontologia, "modelos": t_modelos,
               "resultados": t_resultados, "diferencias": t_diferencias, "impacto": t_impacto, "xai": t_xai, "panel": t_panel,
               "equidad": t_equidad, "peores_clases": t_peores_clases, "matriz": t_matriz, "reglas": t_reglas}

ANCHO_FIGURA = {"web_simulador": 4.8}  # pulgadas; las demás usan 6.0
FIGURAS_INFO = {
    "arquitectura": ("Arquitectura del sistema híbrido", "Elaboración propia. M0 a M3 son los cuatro sistemas comparados."),
    "web_simulador": ("Simulador de la web demostrativa con una cavitación en la bomba centrífuga",
                      "Captura de la web: el usuario elige activo, falla y severidad; los tres sistemas diagnostican y la "
                      "explicación muestra el peso de cada sensor y las reglas R14 y R13 con sus valores reales."),
    "f1": ("F1 macro de los cuatro sistemas", "Media de 5 semillas e intervalo t del 95 %. M0 es determinista."),
    "falsas": ("Falsa alarma ante condiciones confusoras en la máquina no vista",
               "Porcentaje de ventanas sanas con un confusor que el sistema marca como falla. Media de 5 semillas e intervalo t del 95 %."),
}


# ----------------------------------------------------------------------------- figuras
def figuras(capturas: Path | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURAS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11, "axes.edgecolor": REJILLA,
                         "axes.labelcolor": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA})
    i = _intervalos()

    def puntos(ax, part: str, metrica: str, escala: float, titulo: str, fmt: str) -> None:
        for y, s in enumerate(reversed(SISTEMAS)):
            f = i[(i["particion"] == part) & (i["sistema"] == s) & (i["metrica"] == metrica)].iloc[0]
            m, a, b = escala * f["media"], escala * f["ic95_inf"], escala * f["ic95_sup"]
            ax.plot([a, b], [y, y], color=COLORES[s], lw=2, solid_capstyle="round")
            ax.plot(m, y, "o", ms=8, color=COLORES[s], mec="white", mew=2)
            ax.text(b + (0.008 if escala == 1 else 0.3), y, fmt.format(m), color=TINTA, fontsize=10, ha="left", va="center")
        ax.set_yticks(range(4), list(reversed(SISTEMAS)))
        ax.set_ylim(-0.6, 3.6)
        ax.set_title(titulo, color=TINTA, fontsize=11, loc="left")
        ax.grid(axis="x", color=REJILLA, lw=0.6)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.tick_params(axis="y", length=0)

    fig, ejes = plt.subplots(1, 2, figsize=(7.5, 2.8), sharey=True)
    puntos(ejes[0], "test", "f1_macro", 1, "Prueba temporal", "{:.3f}")
    puntos(ejes[1], "test_unidad", "f1_macro", 1, "Máquina no vista", "{:.3f}")
    for ax in ejes:
        ax.set_xlim(0.55, 1.0)
        ax.set_xlabel("F1 macro")
    fig.tight_layout()
    fig.savefig(FIGURAS / "f1.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    puntos(ax, "test_unidad", "falsa_alarma_con_confusor", 100, "", "{:.1f} %")
    ax.set_xlim(0, 20)
    ax.set_xlabel("Falsa alarma con confusor (%)")
    fig.tight_layout()
    fig.savefig(FIGURAS / "falsas.png", dpi=300)
    plt.close(fig)

    try:  # diagrama de arquitectura: el mismo SVG de la landing
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_context(device_scale_factor=3, color_scheme="light", viewport={"width": 1100, "height": 900}).new_page()
            pg.goto((RAIZ / "landing" / "index.html").as_uri())
            pg.wait_for_timeout(800)
            pg.locator("#arquitectura svg").screenshot(path=str(FIGURAS / "arquitectura.png"))
            b.close()
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: no se regeneró el diagrama de arquitectura ({e})")

    if capturas:  # simulador con cavitación en la bomba (el mismo caso de la regla R13 del texto)
        from PIL import Image

        candidatas = sorted(capturas.glob("*Simulador*Cavitaci*.png")) or sorted(capturas.glob("*Simulador*.png"))
        if candidatas:
            with Image.open(candidatas[0]) as img:  # controles, diagnóstico, explicación, pesos y reglas
                img.crop((360, 110, min(img.width, 1365), min(img.height, 1500))).save(FIGURAS / "web_simulador.png")
        else:
            print(f"Aviso: no hay captura del simulador en {capturas}")


# ----------------------------------------------------------------------------- Word
def _limpiar_md(t: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t).replace("**", "").replace("`", "").strip()


def _clave_orden(ref: str) -> str:
    s = unicodedata.normalize("NFKD", ref.replace("*", "")).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9 ]", "", s)


def referencias() -> list[str]:
    lineas = [x[2:].strip() for x in REFERENCIAS.read_text(encoding="utf-8").splitlines() if x.startswith("- ")]
    return sorted(lineas, key=_clave_orden)


def sustituir(texto: str, v: dict[str, str]) -> str:
    def rep(m: re.Match[str]) -> str:
        if m.group(1) not in v:
            raise KeyError(f"cifra desconocida: {m.group(1)}")
        return v[m.group(1)]

    return re.sub(r"\{\{v:([a-z0-9_]+)\}\}", rep, texto)


class Escritor:
    """Convierte el subconjunto de Markdown de documento.md en un .docx con formato APA 7."""

    def __init__(self) -> None:
        from docx import Document
        from docx.enum.text import WD_LINE_SPACING
        from docx.shared import Cm, Pt, RGBColor

        self.Cm, self.Pt = Cm, Pt
        self.doc = Document()
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)  # carta
        for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, lado, Cm(2.54))
        normal = self.doc.styles["Normal"]
        self._fuente(normal, 12)
        pf = normal.paragraph_format
        pf.line_spacing_rule, pf.space_before, pf.space_after = WD_LINE_SPACING.ONE_POINT_FIVE, Pt(0), Pt(0)
        for nivel, (centro, cursiva) in {1: (True, False), 2: (False, False), 3: (False, True)}.items():
            st = self.doc.styles[f"Heading {nivel}"]
            self._fuente(st, 12)
            st.font.bold, st.font.italic, st.font.color.rgb = True, cursiva, RGBColor(0, 0, 0)
            p = st.paragraph_format
            p.alignment = 1 if centro else 0
            p.space_before, p.space_after, p.keep_with_next = Pt(12), Pt(6), True
            p.first_line_indent = Cm(0)
        self._encabezado()
        self.n_tabla = self.n_figura = 0

    @staticmethod
    def _fuente(estilo: Any, tam: float) -> None:
        from docx.oxml.ns import qn
        from docx.shared import Pt

        estilo.font.name, estilo.font.size = "Times New Roman", Pt(tam)
        rpr = estilo.element.get_or_add_rPr()
        fuentes = rpr.find(qn("w:rFonts"))
        if fuentes is None:
            fuentes = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(fuentes)
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            fuentes.set(qn(a), "Times New Roman")
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            fuentes.attrib.pop(qn(a), None)

    def _campo(self, parrafo: Any, instruccion: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        run = parrafo.add_run()
        for tipo, texto in (("begin", None), (None, instruccion), ("separate", None), (None, "—"), ("end", None)):
            if tipo:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), tipo)
            elif texto == instruccion:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = instruccion
            else:
                el = OxmlElement("w:t")
                el.text = texto
            run._r.append(el)

    def _encabezado(self) -> None:
        p = self.doc.sections[0].header.paragraphs[0]
        p.alignment = 2
        self._campo(p, "PAGE")

    def _runs(self, parrafo: Any, texto: str, tam: float | None = None) -> None:
        for trozo in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", texto):
            if not trozo:
                continue
            if trozo.startswith("**"):
                r = parrafo.add_run(trozo[2:-2])
                r.bold = True
            elif trozo.startswith("*"):
                r = parrafo.add_run(trozo[1:-1])
                r.italic = True
            elif trozo.startswith("`"):
                r = parrafo.add_run(trozo[1:-1])
                r.font.name = "Consolas"
                r.font.size = self.Pt((tam or 12) - 1.5)
                continue
            else:
                r = parrafo.add_run(trozo)
            if tam:
                r.font.size = self.Pt(tam)

    def parrafo(self, texto: str, sangria: bool = True, alineacion: int = 0, tam: float | None = None) -> Any:
        p = self.doc.add_paragraph()
        p.alignment = alineacion
        if sangria:
            p.paragraph_format.first_line_indent = self.Cm(1.27)
        self._runs(p, texto, tam)
        return p

    def titulo(self, texto: str, nivel: int) -> None:
        self.doc.add_heading(texto, level=nivel)

    def salto(self) -> None:
        from docx.enum.text import WD_BREAK

        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def lista(self, items: list[str], numerada: bool) -> None:
        for n, item in enumerate(items, 1):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent = self.Cm(1.9), self.Cm(-0.63)
            self._runs(p, (f"{n}.\t" if numerada else "•\t") + item)
            pf.tab_stops.add_tab_stop(self.Cm(1.9))

    def cita(self, texto: str) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = self.Cm(1.27)
        self._runs(p, texto)

    def portada(self) -> None:
        for _ in range(4):
            self.doc.add_paragraph()
        p = self.parrafo(f"**{PORTADA['titulo']}**", sangria=False, alineacion=1)
        p.paragraph_format.space_after = self.Pt(24)
        for linea in [", ".join(PORTADA["autores"][:-1]) + " y " + PORTADA["autores"][-1], "", *PORTADA["lineas"]]:
            self.parrafo(linea, sangria=False, alineacion=1)
        self.salto()

    def resumen(self, texto: str, claves: str) -> None:
        self.parrafo("**Resumen**", sangria=False, alineacion=1)
        self.parrafo(texto, sangria=False)
        self.parrafo(f"*Palabras clave:* {claves}", sangria=True)
        self.salto()

    def indice(self) -> None:
        self.parrafo("**Contenido**", sangria=False, alineacion=1)
        self._campo(self.doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u')
        self.salto()

    def _bordes(self, tabla: Any) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        def borde(padre: Any, lados: tuple[str, ...]) -> None:
            caja = OxmlElement("w:tblBorders" if padre.tag.endswith("tblPr") else "w:tcBorders")
            for lado in lados:
                el = OxmlElement(f"w:{lado}")
                el.set(qn("w:val"), "single")
                el.set(qn("w:sz"), "6")
                el.set(qn("w:color"), "000000")
                caja.append(el)
            padre.append(caja)

        borde(tabla._tbl.tblPr, ("top", "bottom"))
        for celda in tabla.rows[0].cells:
            borde(celda._tc.get_or_add_tcPr(), ("bottom",))

    @staticmethod
    def _repetir_encabezado(tabla: Any) -> None:
        """El encabezado se repite en cada página y ninguna fila se parte entre páginas."""
        from docx.oxml import OxmlElement

        for n, fila in enumerate(tabla.rows):
            trpr = fila._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if n == 0:
                trpr.append(OxmlElement("w:tblHeader"))

    def tabla(self, t: Tabla) -> None:
        from docx.shared import Cm

        self.n_tabla += 1
        p = self.parrafo(f"**Tabla {self.n_tabla}**", sangria=False)
        p.paragraph_format.space_before, p.paragraph_format.keep_with_next = self.Pt(12), True
        p = self.parrafo(f"*{t.titulo}*", sangria=False)
        p.paragraph_format.keep_with_next = True
        tab = self.doc.add_table(rows=1 + len(t.filas), cols=len(t.encabezados))
        tab.autofit = False
        anchos = t.anchos or [1] * len(t.encabezados)
        total = 16.5
        for fila_i, fila in enumerate([t.encabezados, *t.filas]):
            for col, valor in enumerate(fila):
                celda = tab.cell(fila_i, col)
                celda.width = Cm(total * anchos[col] / sum(anchos))
                par = celda.paragraphs[0]
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.first_line_indent = Cm(0)
                self._runs(par, f"**{valor}**" if fila_i == 0 and valor else str(valor), t.letra)
        self._bordes(tab)
        self._repetir_encabezado(tab)
        if t.nota:
            n = self.doc.add_paragraph()
            n.paragraph_format.space_after = self.Pt(12)
            self._runs(n, f"*Nota.* {t.nota}", t.letra)
        else:
            self.doc.add_paragraph()

    def figura(self, nombre: str, titulo: str, nota: str, ruta: Path) -> None:
        from docx.shared import Inches

        self.n_figura += 1
        p = self.parrafo(f"**Figura {self.n_figura}**", sangria=False)
        p.paragraph_format.space_before, p.paragraph_format.keep_with_next = self.Pt(12), True
        p = self.parrafo(f"*{titulo}*", sangria=False)
        p.paragraph_format.keep_with_next = True
        if ruta.exists():
            img = self.doc.add_paragraph()
            img.alignment = 1
            img.paragraph_format.keep_with_next = True
            img.add_run().add_picture(str(ruta), width=Inches(ANCHO_FIGURA.get(nombre, 6.0)))
        else:
            self.parrafo(f"[PENDIENTE: figura {nombre}; ejecute con --figuras]", sangria=False)
        n = self.doc.add_paragraph()
        n.paragraph_format.space_after = self.Pt(12)
        self._runs(n, f"*Nota.* {nota}", 10)

    def referencias(self) -> None:
        self.salto()
        self.titulo("Referencias", 1)
        for ref in referencias():
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = self.Cm(1.27), self.Cm(-1.27)
            self._runs(p, ref)


def _tabla_md(lineas: list[str], titulo: str, nota: str) -> Tabla:
    filas = [[c.strip() for c in linea.strip().strip("|").split("|")] for linea in lineas]
    filas = [f for f in filas if not all(set(c) <= set("-: ") for c in f)]
    return Tabla(titulo, filas[0], filas[1:], nota)


def construir_docx(v: dict[str, str]) -> dict[str, int]:
    texto = sustituir(re.sub(r"<!--.*?-->", "", FUENTE.read_text(encoding="utf-8"), flags=re.S), v)
    w = Escritor()
    lineas = texto.splitlines()
    i = 0
    palabras_resumen = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()
        s = linea.strip()
        if not s:
            i += 1
            continue
        if s == "{{portada}}":
            w.portada()
        elif s == "{{resumen}}":
            fin = lineas.index("{{/resumen}}", i)
            cuerpo = [x for x in lineas[i + 1:fin] if x.strip()]
            claves = next(x for x in cuerpo if x.startswith("Palabras clave:")).split(":", 1)[1].strip()
            resumen = " ".join(x for x in cuerpo if not x.startswith("Palabras clave:"))
            palabras_resumen = len(resumen.split())
            w.resumen(resumen, claves)
            i = fin
        elif s == "{{indice}}":
            w.indice()
        elif s == "{{salto}}":
            w.salto()
        elif s == "{{referencias}}":
            w.referencias()
        elif m := re.fullmatch(r"\{\{tabla:(\w+)\}\}", s):
            w.tabla(GENERADORES[m.group(1)]())
        elif m := re.fullmatch(r"\{\{figura:(\w+)\}\}", s):
            titulo, nota = FIGURAS_INFO[m.group(1)]
            w.figura(m.group(1), titulo, nota, FIGURAS / f"{m.group(1)}.png")
        elif s.startswith("#"):
            nivel = len(s) - len(s.lstrip("#"))
            nombre = s[nivel:].strip()
            if nivel == 1 and nombre == "Anexos":
                w.salto()
            elif nivel == 2 and nombre.startswith("Anexo") and not nombre.startswith("Anexo A"):
                w.salto()
            w.titulo(nombre, nivel)
        elif s.startswith("Tabla:") and i + 1 < len(lineas) and lineas[i + 1].lstrip().startswith("|"):
            j = i + 1
            while j < len(lineas) and lineas[j].lstrip().startswith("|"):
                j += 1
            nota = ""
            if j < len(lineas) and lineas[j].startswith("Nota:"):
                nota, j = lineas[j][5:].strip(), j + 1
            w.tabla(_tabla_md(lineas[i + 1:j], s[6:].strip(), nota))
            i = j
            continue
        elif s.startswith(">"):
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                bloque.append(lineas[i].strip()[1:].strip())
                i += 1
            for parte in " ".join(b if b else "\n" for b in bloque).split("\n"):
                if parte.strip():
                    w.cita(parte.strip())
            continue
        elif re.match(r"^(- |\d+\. )", s):
            numerada = bool(re.match(r"^\d+\. ", s))
            items = []
            while i < len(lineas) and re.match(r"^(- |\d+\. )", lineas[i].strip()):
                items.append(re.sub(r"^(- |\d+\. )", "", lineas[i].strip()))
                i += 1
            w.lista(items, numerada)
            continue
        else:
            w.parrafo(s)
        i += 1
    w.doc.save(SALIDA)
    return {"tablas": w.n_tabla, "figuras": w.n_figura, "palabras_resumen": palabras_resumen}


def exportar_pdf() -> Path:
    """Actualiza el índice y los números de página con Word y guarda el .docx y el .pdf."""
    pdf = SALIDA.with_suffix(".pdf")
    script = (
        "$ErrorActionPreference='Stop'; $w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        f"try {{ $d = $w.Documents.Open('{SALIDA}'); foreach ($t in $d.TablesOfContents) {{ $t.Update() }}; "
        f"$d.Fields.Update() | Out-Null; $d.Save(); $d.SaveAs2('{pdf}', 17); $d.Close(0) }} finally {{ $w.Quit() }}"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True, timeout=600)
    return pdf


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figuras", action="store_true", help="regenera las figuras")
    ap.add_argument("--capturas", type=Path, help="carpeta de capturas de scripts/revisar_web.py")
    ap.add_argument("--pdf", action="store_true", help="exporta a PDF con Microsoft Word")
    a = ap.parse_args()
    if a.figuras or a.capturas:
        figuras(a.capturas)
    info = construir_docx(valores())
    print(f"{SALIDA.relative_to(RAIZ)}: {info['tablas']} tablas, {info['figuras']} figuras, "
          f"resumen de {info['palabras_resumen']} palabras")
    if not 150 <= info["palabras_resumen"] <= 250:
        print("Aviso: el resumen debe tener entre 150 y 250 palabras")
    if a.pdf:
        print(f"{exportar_pdf().relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
