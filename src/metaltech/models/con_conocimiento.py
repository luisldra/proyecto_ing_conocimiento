"""M2: cualquier arquitectura de la Fase 4 con el conocimiento experto como entrada adicional."""

from __future__ import annotations

import torch
from torch import nn


class ConConocimiento(nn.Module):
    """Combina la salida de la red de sensores con una rama para certezas y síntomas de reglas."""

    def __init__(self, red: nn.Module, clases: int, extra: int, ocultas: int = 32) -> None:
        super().__init__()
        self.red = red
        self.rama = nn.Sequential(nn.Linear(extra, ocultas), nn.ReLU())
        self.salida = nn.Linear(clases + ocultas, clases)

    def forward(self, x: torch.Tensor, conocimiento: torch.Tensor) -> torch.Tensor:
        return self.salida(torch.cat([self.red(x), self.rama(conocimiento)], dim=1))
