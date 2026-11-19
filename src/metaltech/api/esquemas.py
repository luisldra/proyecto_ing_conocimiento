"""Esquemas de entrada de la API (Pydantic)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SolicitudPrediccion(BaseModel):
    activo: str = Field(examples=["bomba_centrifuga"])
    ventana: dict[str, list[float | None]] = Field(
        description="Lecturas crudas por sensor: 36 valores cada 10 min (6 h). Un vacío toma el último valor conocido."
    )


class SolicitudDiagnostico(SolicitudPrediccion):
    texto: str | None = Field(None, description="Observación del técnico, p. ej. 'la bomba está golpeando'")
    unidad: str | None = Field(None, description="Unidad, para usar su línea base de puesta en marcha")
    explicar: bool = Field(True, description="Calcula la importancia de cada sensor (gradientes integrados)")


class SolicitudSimulacion(BaseModel):
    activo: str = Field(examples=["bomba_centrifuga"])
    modo: str | None = Field(None, examples=["cavitacion"], description="Modo de falla; vacío = operación normal")
    avance: float = Field(1.0, ge=0.0, le=1.0, description="Punto de la degradación al final de la ventana (1 = falla)")
    severidad: float = Field(1.0, ge=0.5, le=1.5, description="Multiplica el cambio de la firma")
    texto: str | None = None
    semilla: int = 0
    explicar: bool = True
