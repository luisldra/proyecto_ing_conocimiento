"""API de diagnóstico explicable de Metal Tech (Fase 8).

Uso: ``uvicorn metaltech.api.main:app --reload`` y documentación en ``/docs``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException

from metaltech.api.esquemas import SolicitudDiagnostico, SolicitudPrediccion, SolicitudSimulacion
from metaltech.api.servicio import ErrorVentana, servicio
from metaltech.kb.base import RAIZ
from metaltech.kb.ontology import Ontologia

TABLAS = RAIZ / "reports" / "tables"
REPORTES = {  # nombre público -> archivo de reports/tables
    "comparacion": "comparacion_sistemas.csv", "semillas": "comparacion_semillas.csv",
    "intervalos": "intervalos_sistemas.csv", "diferencias": "intervalos_diferencias.csv",
    "equidad": "equidad_grupos.csv", "brechas": "equidad_brechas.csv", "impacto": "impacto_sistemas.csv",
    "latencia": "latencia.csv", "xai": "xai_metricas.csv", "calibracion": "calibracion_m0_por_modo.csv",
    "evaluacion_agentes": "evaluacion_agentes.csv",
}

app = FastAPI(
    title="Metal Tech – mantenimiento predictivo explicable",
    description="Deep Learning + base de conocimiento experto (ontología y reglas con factores de certeza). "
                "Datos sintéticos; proyecto académico de Ingeniería del Conocimiento.",
    version="1.0.0",
)


@lru_cache(maxsize=1)
def ontologia() -> Ontologia:
    return Ontologia.cargar()


def _error(e: Exception) -> HTTPException:
    return HTTPException(status_code=422 if isinstance(e, ErrorVentana) else 404, detail=str(e))


@app.get("/health")
def salud() -> dict[str, Any]:
    s = servicio()
    return {"estado": "ok", "modelos": sorted(s.modelos), "activos": len(s.base.activos)}


@app.get("/assets")
def activos() -> dict[str, Any]:
    return servicio().activos()


@app.get("/assets/{activo}")
def activo(activo: str) -> dict[str, Any]:
    datos = servicio().activos()
    if activo not in datos:
        raise HTTPException(404, f"activo desconocido: {activo}")
    return datos[activo]


@app.get("/kb/rules")
def reglas(activo: str | None = None, modo: str | None = None) -> list[dict[str, Any]]:
    return [r for r in servicio().base.reglas
            if (activo is None or r["activo"] == activo) and (modo is None or r["entonces"] == modo)]


@app.get("/kb/failure/{modo}")
def modo_falla(modo: str, activo: str | None = None) -> dict[str, Any]:
    try:
        return ontologia().detalle_modo(modo, activo)
    except (KeyError, ValueError) as e:
        raise HTTPException(404, f"modo de falla desconocido: {modo}") from e


@app.get("/kb/lexicon")
def lexico() -> list[dict[str, Any]]:
    return servicio().base.lexico


@app.get("/kb/ontology/graph")
def grafo(activo: str | None = None) -> dict[str, Any]:
    return ontologia().grafo(activo)


@app.post("/predict")
def predecir(s: SolicitudPrediccion) -> dict[str, Any]:
    try:
        srv = servicio()
        p = srv.predecir(s.activo, srv.matriz(s.activo, s.ventana))
        clases = srv.clases(s.activo)
        return {"activo": s.activo, "modo": clases[int(p.argmax())],
                "probabilidades": {c: float(x) for c, x in zip(clases, p, strict=True)}}
    except ErrorVentana as e:
        raise _error(e) from e


@app.post("/diagnose")
def diagnosticar(s: SolicitudDiagnostico) -> dict[str, Any]:
    try:
        return servicio().diagnosticar(s.activo, s.ventana, s.texto, s.unidad, s.explicar)
    except ErrorVentana as e:
        raise _error(e) from e


@app.post("/simulate")
def simular(s: SolicitudSimulacion) -> dict[str, Any]:
    try:
        return servicio().simular(s.activo, s.modo, s.avance, s.severidad, s.texto, s.semilla, s.explicar)
    except ErrorVentana as e:
        raise _error(e) from e


@app.get("/reports/{nombre}")
def reporte(nombre: str) -> list[dict[str, Any]]:
    if nombre not in REPORTES or not (TABLAS / REPORTES[nombre]).exists():
        raise HTTPException(404, f"reporte no disponible: {nombre}. Opciones: {sorted(REPORTES)}")
    return json.loads(pd.read_csv(TABLAS / REPORTES[nombre]).to_json(orient="records"))
