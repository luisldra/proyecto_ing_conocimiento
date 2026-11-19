"""Servicio de diagnóstico: carga una vez los modelos y la base de conocimiento (Fase 8).

Lo usan la API y, si la API no está levantada, la web demostrativa directamente. Recibe una
ventana de 6 h (36 lecturas por sensor) sin normalizar y devuelve M0, M1 y el diagnóstico
híbrido M3 con su explicación (D-061).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import yaml

from metaltech.data.features import RECORTE_Z
from metaltech.data.generator import VARIABLES_ENTERAS, perfil_degradacion
from metaltech.hybrid.conocimiento import lineas_base
from metaltech.hybrid.fusion import ParametrosFusion, diagnostico_hibrido, fusionar, proba_m0
from metaltech.kb.base import RAIZ, cargar_base, valor_final, valor_nominal
from metaltech.kb.rules_engine import MotorReglas
from metaltech.models.train import cargar_modelo, entradas_de, probabilidades
from metaltech.xai.explain import explicar_alerta, importancia_por_variable

RUTA_CONFIG = RAIZ / "configs" / "train.yaml"
HORAS_VENTANA = 6.0


class ErrorVentana(ValueError):
    """La ventana recibida no tiene los sensores o la longitud esperados."""


class Servicio:
    def __init__(self, datos: Path | None = None, ruta_config: Path = RUTA_CONFIG) -> None:
        with open(ruta_config, encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.datos = datos or RAIZ / self.cfg["rutas"]["datos"]
        self.base = cargar_base()
        self.motor = MotorReglas(self.base)
        self.pasos = self.cfg["datos"]["ventana_pasos"]
        tablas = RAIZ / self.cfg["rutas"]["tablas"]
        self.seleccion = json.loads((tablas / "modelos_seleccion.json").read_text(encoding="utf-8"))
        fusion = json.loads((tablas / "fusion_parametros.json").read_text(encoding="utf-8"))
        self.fusion = {a: ParametrosFusion(f["alfa"], f["veto"], f["fc_min"]) for a, f in fusion.items()}
        self.modelos: dict[str, tuple[torch.nn.Module, dict[str, Any]]] = {}
        semilla = self.cfg["semilla_principal"]
        for activo, arq in self.seleccion.items():
            ruta = RAIZ / self.cfg["rutas"]["checkpoints"] / f"{activo}_{arq}_s{semilla}.pt"
            if ruta.exists():
                modelo, ck = cargar_modelo(ruta, self.pasos, self.cfg)
                self.modelos[activo] = (modelo.eval(), ck)
        self._lineas: dict[str, dict[str, dict[str, float]]] = {}

    # --- consultas ---------------------------------------------------------------------
    def activos(self) -> dict[str, Any]:
        return {
            a: {"nombre": d["nombre"], "unidades": [f"{a}_{k:02d}" for k in range(1, d["unidades"] + 1)],
                "variables": d["variables"], "modos": self.clases(a)[1:], "modelo": self.seleccion.get(a),
                "disponible": a in self.modelos}
            for a, d in self.base.activos.items()
        }

    def clases(self, activo: str) -> list[str]:
        self._activo(activo)
        if activo in self.modelos:
            return self.modelos[activo][1]["clases"]
        return ["normal", *sorted(m for m, d in self.base.modos.items() if activo in d["activos"])]

    def linea_base(self, activo: str, unidad: str | None) -> dict[str, float]:
        """De la puesta en marcha de la unidad si hay datos; si no, el punto medio nominal."""
        variables = self.base.activos[activo]["variables"]
        if unidad:
            if activo not in self._lineas:
                ruta = self.datos / f"{activo}.parquet"
                self._lineas[activo] = (lineas_base(pd.read_parquet(ruta, columns=["ts", "unidad", *variables]), list(variables))
                                        if ruta.exists() else {})
            if unidad in self._lineas[activo]:
                return self._lineas[activo][unidad]
        return {v: valor_nominal(c) for v, c in variables.items()}

    # --- inferencia ----------------------------------------------------------------------
    def matriz(self, activo: str, ventana: dict[str, list[float | None]]) -> np.ndarray:
        """Ventana [T, V] cruda; los vacíos toman el último valor conocido o el nominal."""
        variables = self.base.activos[activo]["variables"]
        faltan = [v for v in variables if v not in ventana]
        if faltan:
            raise ErrorVentana(f"faltan sensores: {faltan}")
        sobran = [v for v in ventana if v not in variables]
        if sobran:
            raise ErrorVentana(f"sensores desconocidos para {activo}: {sobran}")
        largos = {v: len(ventana[v]) for v in variables if len(ventana[v]) != self.pasos}
        if largos:
            raise ErrorVentana(f"cada sensor necesita {self.pasos} lecturas (10 min, 6 h): {largos}")
        df = pd.DataFrame({v: pd.to_numeric(pd.Series(ventana[v], dtype=object), errors="coerce") for v in variables})
        return df.ffill().fillna({v: valor_nominal(c) for v, c in variables.items()}).to_numpy(dtype=np.float32)

    def _modelo(self, activo: str):
        self._activo(activo)
        if activo not in self.modelos:
            raise ErrorVentana(f"no hay modelo entrenado para {activo}: ejecute python -m metaltech.models.train")
        return self.modelos[activo]

    def predecir(self, activo: str, X: np.ndarray) -> np.ndarray:
        modelo, ck = self._modelo(activo)
        z = np.clip((X - ck["media"]) / ck["desviacion"], -RECORTE_Z, RECORTE_Z).astype(np.float32)[None]
        with torch.no_grad():
            return probabilidades(modelo(entradas_de(ck["arquitectura"], z)), ck["temperatura"])[0]

    def diagnosticar(
        self, activo: str, ventana: dict[str, list[float | None]], texto: str | None = None,
        unidad: str | None = None, explicar: bool = True,
    ) -> dict[str, Any]:
        X = self.matriz(activo, ventana)
        modelo, ck = self._modelo(activo)
        clases, variables = ck["clases"], ck["variables"]
        p = self.predecir(activo, X)
        diag = self.motor.diagnosticar(activo, dict(zip(variables, X[-1].astype(float), strict=True)),
                                       self.linea_base(activo, unidad), texto_tecnico=texto or None)
        fc = np.zeros(len(clases), dtype=np.float32)
        for c in diag.conclusiones:
            fc[clases.index(c.modo)] = c.fc
        fc[0] = 1 - fc[1:].max(initial=0.0)
        m0 = proba_m0(fc[None])[0]
        m3 = fusionar(p[None], fc[None], self.fusion[activo])[0]
        hibrido = diagnostico_hibrido(activo, clases, p, diag, self.fusion[activo], self.base)
        if explicar:
            z = np.clip((X - ck["media"]) / ck["desviacion"], -RECORTE_Z, RECORTE_Z).astype(np.float32)[None]
            objetivo = int(m3.argmax()) or int(p.argmax())
            imp = importancia_por_variable(modelo, ck["arquitectura"], z, np.array([objetivo]))[0]
            hibrido = explicar_alerta(hibrido, dict(zip(variables, imp.astype(float), strict=True)))
            hibrido["importancias"] = {v: float(w) for v, w in zip(variables, imp, strict=True)}
        return {
            "activo": activo,
            "sistemas": {
                "M0": {"modo": clases[int(m0.argmax())], "certeza": float(fc[int(m0.argmax())]) if m0.argmax() else 0.0},
                "M1": {"modo": clases[int(p.argmax())], "probabilidad": float(p.max())},
                "M3": {"modo": clases[int(m3.argmax())], "puntaje": float(m3.max())},
            },
            "probabilidades_modelo": {c: float(x) for c, x in zip(clases, p, strict=True)},
            "certezas_reglas": {c: float(x) for c, x in zip(clases[1:], fc[1:], strict=True) if x > 0},
            "reglas_parciales": [{"id": r.id, "modo": r.modo, "cumplidas": r.cumplidas, "faltantes": r.faltantes}
                                 for r in diag.reglas_parciales],
            "diagnostico": hibrido,
        }

    # --- simulación ----------------------------------------------------------------------
    def construir_ventana(
        self, activo: str, modo: str | None = None, avance: float = 1.0, severidad: float = 1.0, semilla: int = 0,
    ) -> dict[str, list[float]]:
        """Ventana de 6 h: operación sana con ruido y, si hay modo, el tramo de su degradación que
        termina en ``avance`` (0 = inicio, 1 = falla). Los pulsos intermitentes se aproximan por su envolvente."""
        self._activo(activo)
        variables = self.base.activos[activo]["variables"]
        rng = np.random.default_rng(semilla)
        ruido = self.cfg["datos"]["simulador"]["ruido_medicion_frac"]
        datos = {}
        for v, c in variables.items():
            lo, hi = c["nominal"]
            media_banda = (hi - lo) / 2
            datos[v] = valor_nominal(c) + rng.normal(0, max(ruido * media_banda, 1e-6) * 3, self.pasos)
        if modo and modo != "normal":
            if modo not in self.base.modos or activo not in self.base.modos[modo]["activos"]:
                raise ErrorVentana(f"el modo {modo} no aplica a {activo}")
            m = self.base.modos[modo]
            lo_h, hi_h = m["degradacion"]["duracion_h"]
            duracion = np.sqrt(lo_h * hi_h) if lo_h > 0 else max((lo_h + hi_h) / 2, HORAS_VENTANA)
            tramo = min(1.0, HORAS_VENTANA / max(duracion, 1e-6))
            t = np.clip(avance - tramo * (self.pasos - 1 - np.arange(self.pasos)) / (self.pasos - 1), 1e-6, 1.0)
            escalon_en = m["degradacion"].get("escalon_en", "inicio")
            for f in m["firma"]:
                v = f["variable"]
                if v not in variables:
                    continue
                forma = "lineal" if f["forma"] == "intermitente" else f["forma"]
                perfil = perfil_degradacion(forma, t, f.get("retardo_frac", 0.0), escalon_en)
                nominal = valor_nominal(variables[v])
                objetivo = nominal + severidad * (valor_final(variables[v], f["cambio"]) - nominal)
                datos[v] = datos[v] + perfil * (objetivo - datos[v])
        return {v: [float(round(x) if v in VARIABLES_ENTERAS else round(max(x, 0.0), 4)) for x in serie]
                for v, serie in datos.items()}

    def simular(
        self, activo: str, modo: str | None = None, avance: float = 1.0, severidad: float = 1.0,
        texto: str | None = None, semilla: int = 0, explicar: bool = True,
    ) -> dict[str, Any]:
        ventana = self.construir_ventana(activo, modo, avance, severidad, semilla)
        return {"ventana": ventana, "modo_simulado": modo or "normal", "avance": avance, "severidad": severidad,
                **self.diagnosticar(activo, ventana, texto, None, explicar)}

    def _activo(self, activo: str) -> None:
        if activo not in self.base.activos:
            raise ErrorVentana(f"activo desconocido: {activo}")


@lru_cache(maxsize=1)
def servicio() -> Servicio:
    """Instancia compartida (los modelos se cargan una sola vez)."""
    return Servicio()
