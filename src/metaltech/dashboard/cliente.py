"""Acceso de la web a la API. Si la API no responde, usa la misma API dentro del proceso.

``METALTECH_API`` fija la URL (por defecto http://127.0.0.1:8000); ``local`` fuerza el modo
en proceso, útil para pruebas y para una demo sin servidor.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st

URL = os.environ.get("METALTECH_API", "http://127.0.0.1:8000")


@st.cache_resource(show_spinner="Cargando modelos y base de conocimiento…")
def _local():
    from fastapi.testclient import TestClient

    from metaltech.api.main import app

    return TestClient(app)


@st.cache_data(ttl=30, show_spinner=False)
def modo_conexion() -> str:
    if URL == "local":
        return "local"
    try:
        httpx.get(f"{URL}/health", timeout=1.5).raise_for_status()
        return "api"
    except httpx.HTTPError:
        return "local"


def _pedir(metodo: str, ruta: str, **kwargs: Any) -> Any:
    if modo_conexion() == "api":
        r = httpx.request(metodo, f"{URL}{ruta}", timeout=60, **kwargs)
    else:
        r = _local().request(metodo, ruta, **kwargs)
    if r.status_code >= 400:
        raise RuntimeError(r.json().get("detail", r.text))
    return r.json()


@st.cache_data(show_spinner=False)
def obtener(ruta: str, **params: Any) -> Any:
    """GET con caché (consultas de la base de conocimiento y reportes)."""
    return _pedir("GET", ruta, params={k: v for k, v in params.items() if v is not None})


def enviar(ruta: str, cuerpo: dict[str, Any]) -> Any:
    """POST sin caché (diagnóstico y simulación)."""
    return _pedir("POST", ruta, json=cuerpo)


def estado() -> str:
    return f"API en {URL}" if modo_conexion() == "api" else "API en proceso (sin servidor)"
