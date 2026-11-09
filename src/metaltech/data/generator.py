"""Simulador de sensores de Metal Tech con fallas inyectadas (Fase 3).

Genera series cada 10 min por unidad a partir de ``configs/assets.yaml`` y las firmas de
``configs/failure_modes.yaml``: señal sana con ciclo de turno, episodios de degradación
sin solaparse, eventos confusores, datos faltantes y observaciones de técnicos con sesgo.
Todo depende de la semilla. Supuestos y etiquetas: D-049, D-050 y ``data/README.md``.

Uso: ``python -m metaltech.data.generator [--config configs/train.yaml] [--meses N]``
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from scipy.signal import lfilter

from metaltech.kb.base import RAIZ, BaseConocimiento, cargar_base, valor_final, valor_nominal

K_EXPONENCIAL = 4.0  # D-037
K_SIGMOIDE = 10.0  # D-050: D-037 no fija la pendiente
UMBRAL_OBSERVABLE = 0.10  # fracción de la firma desde la que una falla es detectable
AMPLITUD_INICIAL_PULSO = 0.6
PASOS_POR_HORA = 6
DIAS_ENTRE_CALIBRACIONES = 180.0
VARIACION_FIRMA = 0.10  # dispersión de cada variable alrededor de la severidad del episodio
SIN_MODO = "normal"
VARIABLES_ENTERAS = ("disparos_variador_24h", "iso4406_14um_codigo")
TURNOS_TECNICOS = {
    "manana": ["T01", "T02", "T03", "I01"],
    "tarde": ["T04", "T05", "T06", "I02"],
    "noche": ["T07", "T08"],
}


@dataclass(frozen=True)
class ConfigSimulador:
    """Parámetros de ``configs/train.yaml`` (sección ``datos``)."""

    meses: int
    muestreo_min: int
    ventana_pasos: int
    horizonte_h: int
    particion: dict[str, float]
    sensor_faltante_prob: float
    pico_espurio_prob: float
    inicio: str
    hueco_sano_h: tuple[float, float]
    reparacion_h: tuple[float, float]
    severidad: tuple[float, float]
    prob_firma_omitida: float
    excursiones_por_semana: float
    deriva_sensor_frac: float
    ruido_medicion_frac: float
    observaciones_por_episodio: float
    observaciones_falsas_mes: float
    penalizacion_noche: float

    @classmethod
    def desde_yaml(cls, ruta: Path | str, meses: int | None = None) -> ConfigSimulador:
        with open(ruta, encoding="utf-8") as f:
            d = yaml.safe_load(f)["datos"]
        s = d["simulador"]
        return cls(
            meses=meses if meses is not None else d["meses"],
            muestreo_min=d["muestreo_min"],
            ventana_pasos=d["ventana_pasos"],
            horizonte_h=d["horizonte_h"],
            particion=d["particion"],
            sensor_faltante_prob=d["ruido"]["sensor_faltante_prob"],
            pico_espurio_prob=d["ruido"]["pico_espurio_prob"],
            inicio=s["inicio"],
            hueco_sano_h=tuple(s["hueco_sano_h"]),
            reparacion_h=tuple(s["reparacion_h"]),
            severidad=tuple(s["severidad"]),
            prob_firma_omitida=s["prob_firma_omitida"],
            excursiones_por_semana=s["excursiones_por_semana"],
            deriva_sensor_frac=s["deriva_sensor_frac"],
            ruido_medicion_frac=s["ruido_medicion_frac"],
            observaciones_por_episodio=s["observaciones_por_episodio"],
            observaciones_falsas_mes=s["observaciones_falsas_mes"],
            penalizacion_noche=s["penalizacion_noche"],
        )

    @property
    def pasos(self) -> int:
        return int(self.meses * 30.4375 * 24 * 60 / self.muestreo_min)


@dataclass(frozen=True)
class Episodio:
    """Una falla programada; ``i1`` es el paso de la falla (incluido)."""

    unidad: str
    activo: str
    modo: str
    i0: int
    i1: int
    fin_servicio: int  # primer paso de vuelta en servicio


@dataclass
class Simulacion:
    series: dict[str, pd.DataFrame] = field(default_factory=dict)  # por tipo de activo
    episodios: pd.DataFrame = field(default_factory=pd.DataFrame)
    observaciones: pd.DataFrame = field(default_factory=pd.DataFrame)


# ---------------------------------------------------------------------------------------
# Formas de degradación
# ---------------------------------------------------------------------------------------
def perfil_degradacion(
    forma: str, t: np.ndarray, retardo: float = 0.0, escalon_en: str = "inicio"
) -> np.ndarray:
    """Fracción de la firma alcanzada en ``t`` ∈ (0, 1]; vale 1 en ``t = 1``."""
    if forma == "escalon" and escalon_en == "final":
        return (t >= 1.0).astype(float)
    u = np.clip((t - retardo) / max(1.0 - retardo, 1e-9), 0.0, 1.0)
    activo = t > retardo
    if forma == "lineal":
        p = u
    elif forma == "exponencial":
        p = (np.exp(K_EXPONENCIAL * u) - 1) / (np.exp(K_EXPONENCIAL) - 1)
    elif forma == "sigmoide":
        f = lambda x: 1 / (1 + np.exp(-K_SIGMOIDE * (x - 0.5)))  # noqa: E731
        p = (f(u) - f(0.0)) / (f(1.0) - f(0.0))
    elif forma == "escalon":
        p = np.ones_like(u)
    elif forma == "intermitente":
        p = AMPLITUD_INICIAL_PULSO + (1 - AMPLITUD_INICIAL_PULSO) * u  # envolvente de los pulsos
    else:
        raise ValueError(f"forma desconocida: {forma}")
    return np.where(activo, p, 0.0)


def _pulsos(rng: np.random.Generator, t: np.ndarray) -> np.ndarray:
    """Eventos de 1 a 3 pasos con tasa creciente; el último paso siempre está activo."""
    pulso = np.zeros(t.size, dtype=bool)
    for i in np.flatnonzero(rng.random(t.size) < 0.03 + 0.5 * t**2):
        pulso[i : i + int(rng.integers(1, 4))] = True
    pulso[-1] = True
    return pulso


def tarea_de(modo: dict[str, Any]) -> str:
    return modo["degradacion"].get("tarea", "prediccion")


def paso_observable(modo: dict[str, Any], t: np.ndarray) -> int:
    """Primer paso en que la forma principal del modo ya es perceptible en sus firmas."""
    deg = modo["degradacion"]
    perfiles = [
        perfil_degradacion(f["forma"], t, f.get("retardo_frac", 0.0), deg.get("escalon_en", "inicio"))
        for f in modo["firma"]
        if f["forma"] == deg["forma"]
    ]
    if not perfiles:
        return 0
    return int(np.argmax(np.max(perfiles, axis=0) >= UMBRAL_OBSERVABLE))


# ---------------------------------------------------------------------------------------
# Señal sana
# ---------------------------------------------------------------------------------------
def _turnos(indice: pd.DatetimeIndex) -> np.ndarray:
    h = indice.hour.to_numpy()
    return np.select([(h >= 6) & (h < 14), (h >= 14) & (h < 22)], ["manana", "tarde"], "noche")


def _ar1(rng: np.random.Generator, n: int, phi: float = 0.9) -> np.ndarray:
    e = rng.standard_normal(n) * np.sqrt(1 - phi**2)
    return lfilter([1.0], [1.0, -phi], e)


def _carga(rng: np.random.Generator, indice: pd.DatetimeIndex, turnos: np.ndarray) -> np.ndarray:
    """Régimen de carga en [-1, 1]: menor de noche y los domingos."""
    nivel = np.select([turnos == "manana", turnos == "tarde"], [0.6, 0.2], -0.6)
    nivel = np.where(indice.day_of_week.to_numpy() == 6, -0.8, nivel)
    return np.clip(nivel + 0.25 * _ar1(rng, len(indice), 0.95), -1, 1)


def _acople(variable: str) -> float:
    """Sensibilidad de la variable a la carga."""
    if variable.startswith(("corriente", "carga_pct")):
        return 1.0
    if variable.startswith("temp_"):
        return 0.7
    return 0.3 if variable == "vib_rms_mm_s" else 0.0


def _deriva(rng: np.random.Generator, dias: np.ndarray, amplitud: float) -> np.ndarray:
    """Deriva lineal del sensor que se reinicia en cada calibración (cada 180 días)."""
    return rng.uniform(-amplitud, amplitud) * np.mod(dias, DIAS_ENTRE_CALIBRACIONES) / DIAS_ENTRE_CALIBRACIONES


def _senal_sana(
    rng: np.random.Generator, variables: dict[str, Any], indice: pd.DatetimeIndex, carga: np.ndarray,
    cfg: ConfigSimulador,
) -> dict[str, np.ndarray]:
    n = len(indice)
    dias = (indice - indice[0]).total_seconds().to_numpy() / 86400
    termica = lfilter([0.1], [1.0, -0.9], carga, zi=[0.9 * carga[0]])[0]
    estacion = np.sin(2 * np.pi * dias / 365.25 + rng.uniform(0, 2 * np.pi))
    datos: dict[str, np.ndarray] = {}
    for v, c in variables.items():
        lo, hi = c["nominal"]
        centro, media_banda = lo + (hi - lo) * rng.uniform(0.3, 0.7), (hi - lo) / 2
        if v == "desgaste_herramienta_min":  # diente de sierra: cambio preventivo de herramienta
            datos[v] = np.mod(np.cumsum(np.full(n, 7.0)), rng.uniform(0.85, 1.0) * hi)
            continue
        base = carga if not v.startswith("temp_") else termica
        x = _acople(v) * 0.45 * base + 0.2 * _ar1(rng, n)
        if v.startswith("temp_"):
            x = x + 0.1 * estacion
        datos[v] = centro + media_banda * x + _deriva(rng, dias, cfg.deriva_sensor_frac * media_banda)
    return datos


# ---------------------------------------------------------------------------------------
# Programación e inyección de episodios
# ---------------------------------------------------------------------------------------
def _duracion_pasos(rng: np.random.Generator, modo: dict[str, Any]) -> int:
    lo, hi = modo["degradacion"]["duracion_h"]
    horas = np.exp(rng.uniform(np.log(lo), np.log(hi))) if lo > 0 and hi > lo else rng.uniform(lo, hi)
    return max(1, round(horas * PASOS_POR_HORA))


def programar_episodios(
    rng: np.random.Generator, base: BaseConocimiento, cfg: ConfigSimulador, unidad: str, activo: str
) -> list[Episodio]:
    """Rondas barajadas de los modos del activo; así todos aparecen un número similar de veces."""
    modos = sorted(m for m, d in base.modos.items() if activo in d["activos"])
    minimo, media = cfg.hueco_sano_h
    episodios: list[Episodio] = []
    i, colocado = 0, True
    while colocado:
        colocado = False
        for modo in rng.permutation(modos):
            hueco = minimo + rng.exponential(max(media - minimo, 1.0))
            n = _duracion_pasos(rng, base.modos[modo])
            i0 = i + round(hueco * PASOS_POR_HORA)
            i1 = i0 + n - 1
            if i1 >= cfg.pasos:
                continue
            fin = i1 + 1 + round(rng.uniform(*cfg.reparacion_h) * PASOS_POR_HORA)
            episodios.append(Episodio(unidad, activo, str(modo), i0, i1, min(fin, cfg.pasos)))
            i, colocado = fin, True
    return episodios


def _inyectar(
    rng: np.random.Generator,
    datos: dict[str, np.ndarray],
    variables: dict[str, Any],
    modo: dict[str, Any],
    ep: Episodio,
    cfg: ConfigSimulador,
) -> None:
    n = ep.i1 - ep.i0 + 1
    t = np.arange(1, n + 1) / n
    severidad, pulso = rng.uniform(*modo["degradacion"].get("severidad", cfg.severidad)), _pulsos(rng, t)
    escalon_en = modo["degradacion"].get("escalon_en", "inicio")
    propias = [f for f in modo["firma"] if f["variable"] in variables]
    for k, f in enumerate(propias):
        if k > 0 and rng.random() < cfg.prob_firma_omitida:  # no toda falla muestra todos sus síntomas
            continue
        v = f["variable"]
        p = perfil_degradacion(f["forma"], t, f.get("retardo_frac", 0.0), escalon_en)
        if f["forma"] == "intermitente":
            p = p * pulso
        nominal = valor_nominal(variables[v])
        factor = severidad * rng.uniform(1 - VARIACION_FIRMA, 1 + VARIACION_FIRMA)
        objetivo = nominal + factor * (valor_final(variables[v], f["cambio"]) - nominal)
        tramo = datos[v][ep.i0 : ep.i1 + 1]
        datos[v][ep.i0 : ep.i1 + 1] = tramo + p * (objetivo - tramo)


# ---------------------------------------------------------------------------------------
# Confusores y defectos de medición (D-037)
# ---------------------------------------------------------------------------------------
def _marcar(confusor: np.ndarray, datos: dict[str, np.ndarray], nombre: str, i: int, pasos: int, **valores: float) -> None:
    fin = min(i + pasos, confusor.size)
    confusor[i:fin] = nombre
    for v, x in valores.items():
        datos[v][i:fin] = x


def _eventos_por_semana(rng: np.random.Generator, n: int, por_semana: float) -> np.ndarray:
    return np.flatnonzero(rng.random(n) < por_semana / (7 * 24 * PASOS_POR_HORA))


def _confusores_multivariable(
    rng: np.random.Generator, activo: str, datos: dict[str, np.ndarray], confusor: np.ndarray,
    definiciones: dict[str, dict[str, Any]],
) -> None:
    """Condiciones de operación que mueven varias variables con subida y bajada graduales."""
    n = confusor.size
    for nombre, c in sorted(definiciones.items()):
        if activo not in c["activos"]:
            continue
        for i in _eventos_por_semana(rng, n, c["por_semana"]):
            pasos = min(max(1, round(rng.uniform(*c["duracion_h"]) * PASOS_POR_HORA)), n - int(i))
            confusor[i : i + pasos] = nombre
            peso = np.minimum(1.0, np.minimum(np.arange(1, pasos + 1), np.arange(pasos, 0, -1)) / 3)
            for v, efecto in c["efectos"].items():
                tramo = datos[v][i : i + pasos]
                objetivo = rng.uniform(*efecto["valor"]) if "valor" in efecto else tramo + rng.uniform(*efecto["delta"])
                datos[v][i : i + pasos] = tramo + peso * (objetivo - tramo)


def _confusores(
    rng: np.random.Generator,
    activo: str,
    datos: dict[str, np.ndarray],
    variables: dict[str, Any],
    indice: pd.DatetimeIndex,
    cfg: ConfigSimulador,
    definiciones: dict[str, dict[str, Any]],
) -> np.ndarray:
    n = len(indice)
    confusor = np.full(n, "ninguno", dtype=object)
    _confusores_multivariable(rng, activo, datos, confusor, definiciones)
    inicio_manana = np.flatnonzero((indice.hour == 6) & (indice.minute == 0))
    if activo == "prensa_hidraulica":
        for i in inicio_manana[rng.random(inicio_manana.size) < 0.15]:
            _marcar(confusor, datos, "arranque_en_frio_prensa", int(i), PASOS_POR_HORA,
                    temp_aceite_c=rng.uniform(18, 20), tiempo_ciclo_pct=rng.uniform(108, 112))
    elif activo == "compresor_tornillo":
        for i in _eventos_por_semana(rng, n, 2):
            _marcar(confusor, datos, "pico_demanda_aire", int(i), int(rng.integers(6, 13)),
                    carga_pct=rng.uniform(88, 92), presion_descarga_pct=rng.uniform(93, 95))
    elif activo == "centro_cnc":
        for i in _eventos_por_semana(rng, n, 1):
            _marcar(confusor, datos, "cambio_de_lote_cnc", int(i), int(rng.integers(12, 49)),
                    carga_husillo_rel=rng.uniform(1.2, 1.3))
    elif activo == "bomba_centrifuga":
        for i in _eventos_por_semana(rng, n, 0.5):
            _marcar(confusor, datos, "golpe_de_ariete_valvula", int(i), 2, caudal_cv_pct=rng.uniform(5.5, 6.5))
    if activo in ("motor_electrico", "banda_transportadora"):  # el pico de segundos se promedia en 10 min
        for i in inicio_manana[rng.random(inicio_manana.size) < 0.3]:
            _marcar(confusor, datos, "arranque_motor", int(i), 1,
                    corriente_pct=float(datos["corriente_pct"][i] + rng.uniform(3, 8)))

    nombres = list(variables)
    excursionables = [v for v in nombres if v not in VARIABLES_ENTERAS and v != "desgaste_herramienta_min"]
    for i in _eventos_por_semana(rng, n, cfg.excursiones_por_semana):
        v, c, u = excursionables[int(rng.integers(len(excursionables)))], None, rng.uniform(0.3, 1.1)
        c = variables[v]
        lo, hi = c["nominal"]
        valor = hi + u * (c["alerta"] - hi) if c["direccion"] == "alta" else lo - u * (lo - c["alerta"])
        _marcar(confusor, datos, "excursion_operativa", int(i), int(rng.integers(12, 73)), **{v: valor})
    for i in np.flatnonzero(rng.random(n) < cfg.pico_espurio_prob):
        v = nombres[int(rng.integers(len(nombres)))]
        factor = 1.05 if variables[v]["direccion"] == "alta" else 0.95
        _marcar(confusor, datos, "pico_espurio", int(i), 1, **{v: variables[v]["critico"] * factor})
    for i in np.flatnonzero(rng.random(n) < cfg.sensor_faltante_prob):
        v = nombres[int(rng.integers(len(nombres)))]
        _marcar(confusor, datos, "sensor_faltante", int(i), int(rng.integers(6, 37)), **{v: np.nan})
    return confusor


# ---------------------------------------------------------------------------------------
# Serie de una unidad
# ---------------------------------------------------------------------------------------
def _simular_unidad(
    base: BaseConocimiento, cfg: ConfigSimulador, semilla: int, numero: int, unidad: str, activo: str,
    indice: pd.DatetimeIndex, turnos: np.ndarray,
) -> tuple[pd.DataFrame, list[Episodio]]:
    rng = np.random.default_rng(np.random.SeedSequence([semilla, numero]))
    variables = base.activos[activo]["variables"]
    n = len(indice)
    datos = _senal_sana(rng, variables, indice, _carga(rng, indice, turnos), cfg)
    episodios = programar_episodios(rng, base, cfg, unidad, activo)

    estado = np.full(n, "sano", dtype=object)
    modo_activo = np.full(n, SIN_MODO, dtype=object)
    etiqueta = np.full(n, SIN_MODO, dtype=object)
    t_degradacion = np.full(n, np.nan)
    horas_a_falla = np.full(n, np.nan)
    previo = 0
    for ep in episodios:
        modo = base.modos[ep.modo]
        _inyectar(rng, datos, variables, modo, ep, cfg)
        pasos = ep.i1 - ep.i0 + 1
        t = np.arange(1, pasos + 1) / pasos
        estado[ep.i0 : ep.i1 + 1], estado[ep.i1] = "degradacion", "falla"
        estado[ep.i1 + 1 : ep.fin_servicio] = "reparacion"
        modo_activo[ep.i0 : ep.i1 + 1] = ep.modo
        t_degradacion[ep.i0 : ep.i1 + 1] = t
        horas_a_falla[previo : ep.i1 + 1] = (ep.i1 - np.arange(previo, ep.i1 + 1)) / PASOS_POR_HORA
        previo = ep.fin_servicio
        if tarea_de(modo) == "prediccion":
            desde = max(ep.i0, ep.i1 - cfg.horizonte_h * PASOS_POR_HORA)
        else:
            desde = ep.i0 + paso_observable(modo, t)
        etiqueta[desde : ep.i1 + 1] = ep.modo

    confusor = _confusores(rng, activo, datos, variables, indice, cfg, base.confusores)
    for v, c in variables.items():
        ruido = cfg.ruido_medicion_frac * (c["nominal"][1] - c["nominal"][0]) / 2
        x = np.maximum(datos[v] + rng.normal(0, ruido, n), 0.0)
        datos[v] = np.round(x) if v in VARIABLES_ENTERAS else x
        datos[v][estado == "reparacion"] = np.nan

    df = pd.DataFrame({
        "ts": indice, "unidad": unidad, "activo": activo, "turno": turnos, "estado": estado,
        "modo_activo": modo_activo, "etiqueta": etiqueta, "t_degradacion": t_degradacion,
        "horas_a_falla": horas_a_falla, "confusor": confusor,
    })
    for v in variables:
        df[v] = datos[v].astype("float32")
    return df, episodios


def particionar(cfg: ConfigSimulador, n: int) -> np.ndarray:
    """Partición temporal común con purga de ventana + horizonte antes de cada corte (sin fuga)."""
    corte_a = int(n * cfg.particion["train"])
    corte_b = int(n * (cfg.particion["train"] + cfg.particion["val"]))
    purga = cfg.ventana_pasos + cfg.horizonte_h * PASOS_POR_HORA
    p = np.full(n, "test", dtype=object)
    p[:corte_b] = "val"
    p[:corte_a] = "train"
    p[max(corte_a - purga, 0):corte_a] = "purga"
    p[max(corte_b - purga, 0):corte_b] = "purga"
    return p


# ---------------------------------------------------------------------------------------
# Observaciones de técnicos
# ---------------------------------------------------------------------------------------
def _cuadrilla(turno: str, indice: pd.DatetimeIndex, i: int) -> list[str]:
    """Los grupos rotan de turno cada semana: así se separa el efecto de la persona y del turno."""
    turnos, semana = list(TURNOS_TECNICOS), (indice[i] - indice[0]).days // 7
    return TURNOS_TECNICOS[turnos[(turnos.index(turno) + semana) % len(turnos)]]


def _tecnico_y_acierto(
    rng: np.random.Generator, turno: str, acierto: dict[str, float], cfg: ConfigSimulador,
    indice: pd.DatetimeIndex, i: int,
) -> tuple[str, float]:
    tecnico = str(rng.choice(_cuadrilla(turno, indice, i)))
    return tecnico, acierto[tecnico] * (cfg.penalizacion_noche if turno == "noche" else 1.0)


def _texto(rng: np.random.Generator, exp: dict[str, Any]) -> str:
    return str(rng.choice([exp["expresion"], *exp.get("variantes", [])]))


def _observaciones(
    base: BaseConocimiento, cfg: ConfigSimulador, semilla: int, episodios: list[Episodio],
    indice: pd.DatetimeIndex, turnos: np.ndarray, unidades: dict[str, str],
) -> pd.DataFrame:
    """Expresiones del léxico; el acierto depende del técnico y del turno (fuente de sesgo)."""
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 999_983]))
    todos = [t for lista in TURNOS_TECNICOS.values() for t in lista]
    acierto = {t: float(rng.uniform(0.55, 0.9)) for t in sorted(todos)}
    filas: list[dict[str, Any]] = []

    def registrar(unidad: str, activo: str, i: int, modo: str, exp: dict[str, Any], tecnico: str) -> None:
        candidatos = {c["id"] for c in exp["modos_falla_candidatos"]}
        filas.append({
            "ts": indice[i], "unidad": unidad, "activo": activo, "turno": turnos[i], "tecnico": tecnico,
            "id_expresion": exp["id"], "texto": _texto(rng, exp), "modo_real": modo,
            "es_correcta": modo in candidatos,
        })

    for ep in episodios:
        propias = [e for e in base.lexico if ep.activo in e["activos"]]
        correctas = [e for e in propias if ep.modo in {c["id"] for c in e["modos_falla_candidatos"]}]
        if not correctas:
            continue
        for _ in range(rng.poisson(cfg.observaciones_por_episodio)):
            i = ep.i0 + int(rng.beta(4, 1.5) * (ep.i1 - ep.i0))  # se nota más cerca de la falla
            tecnico, p = _tecnico_y_acierto(rng, str(turnos[i]), acierto, cfg, indice, i)
            lista = correctas if rng.random() < p else propias
            registrar(ep.unidad, ep.activo, i, ep.modo, lista[int(rng.integers(len(lista)))], tecnico)

    ocupados: dict[str, np.ndarray] = {}
    for u in unidades:
        ocupados[u] = np.zeros(len(indice), dtype=bool)
    for ep in episodios:
        ocupados[ep.unidad][ep.i0 : ep.fin_servicio] = True
    for unidad, activo in unidades.items():
        propias = [e for e in base.lexico if activo in e["activos"]]
        libres = np.flatnonzero(~ocupados[unidad])
        if not propias or libres.size == 0:
            continue
        for _ in range(rng.poisson(cfg.observaciones_falsas_mes * cfg.meses)):
            i = int(rng.choice(libres))
            tecnico = str(rng.choice(_cuadrilla(str(turnos[i]), indice, i)))
            registrar(unidad, activo, i, SIN_MODO, propias[int(rng.integers(len(propias)))], tecnico)
    columnas = ["ts", "unidad", "activo", "turno", "tecnico", "id_expresion", "texto", "modo_real", "es_correcta"]
    return pd.DataFrame(filas, columns=columnas).sort_values(["ts", "unidad"]).reset_index(drop=True)


# ---------------------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------------------
def simular(cfg: ConfigSimulador, semilla: int = 42, base: BaseConocimiento | None = None) -> Simulacion:
    """Simula la planta completa; misma semilla y configuración, mismo resultado."""
    base = base or cargar_base()
    indice = pd.date_range(cfg.inicio, periods=cfg.pasos, freq=f"{cfg.muestreo_min}min")
    turnos = _turnos(indice)
    particion = particionar(cfg, cfg.pasos)
    sim, episodios, unidades, numero, particion_de = Simulacion(), [], {}, 0, {}
    for activo, datos in base.activos.items():
        marcos = []
        for k in range(1, datos["unidades"] + 1):
            unidad = f"{activo}_{k:02d}"
            unidades[unidad] = activo
            df, eps = _simular_unidad(base, cfg, semilla, numero, unidad, activo, indice, turnos)
            numero += 1
            # La última unidad de cada tipo nunca se entrena: mide la generalización (D-055).
            particion_de[unidad] = np.full(cfg.pasos, "test_unidad", dtype=object) if k == datos["unidades"] else particion
            df["particion"] = particion_de[unidad]
            marcos.append(df)
            episodios.extend(eps)
        marco = pd.concat(marcos, ignore_index=True)
        for c in ("unidad", "activo", "turno", "estado", "modo_activo", "etiqueta", "confusor", "particion"):
            marco[c] = marco[c].astype("category")
        sim.series[activo] = marco
    sim.episodios = pd.DataFrame(
        [{
            "unidad": e.unidad, "activo": e.activo, "modo": e.modo,
            "tarea": tarea_de(base.modos[e.modo]), "inicio": indice[e.i0], "falla": indice[e.i1],
            "i0": e.i0, "i1": e.i1, "duracion_h": (e.i1 - e.i0 + 1) / PASOS_POR_HORA,
            "particion": particion_de[e.unidad][e.i1],
        } for e in episodios]
    )
    sim.observaciones = _observaciones(base, cfg, semilla, episodios, indice, turnos, unidades)
    return sim


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def guardar(sim: Simulacion, salida: Path, cfg: ConfigSimulador, semilla: int) -> dict[str, Any]:
    """Escribe parquet y ``manifest.json`` con conteos y huellas de cada archivo."""
    salida.mkdir(parents=True, exist_ok=True)
    archivos = {f"{a}.parquet": df for a, df in sim.series.items()}
    archivos |= {"episodios.parquet": sim.episodios, "observaciones.parquet": sim.observaciones}
    for nombre, df in archivos.items():
        df.to_parquet(salida / nombre, index=False)
    manifiesto = {
        "semilla": semilla, "meses": cfg.meses, "pasos_por_unidad": cfg.pasos,
        "filas": {n: len(df) for n, df in archivos.items()},
        "episodios_por_tarea": sim.episodios["tarea"].value_counts().to_dict(),
        "sha256": {n: _sha256(salida / n) for n in archivos},
    }
    (salida / "manifest.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifiesto


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Genera el dataset sintético de Metal Tech.")
    ap.add_argument("--config", default=RAIZ / "configs" / "train.yaml", type=Path)
    ap.add_argument("--salida", default=RAIZ / "data" / "synthetic", type=Path)
    ap.add_argument("--semilla", default=42, type=int)
    ap.add_argument("--meses", default=None, type=int, help="reemplaza datos.meses del YAML")
    args = ap.parse_args(argv)
    cfg = ConfigSimulador.desde_yaml(args.config, args.meses)
    print(json.dumps(guardar(simular(cfg, args.semilla), args.salida, cfg, args.semilla), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
