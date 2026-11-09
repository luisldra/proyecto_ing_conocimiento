"""Perceptrón multicapa sobre variables agregadas por ventana (línea base)."""

from __future__ import annotations

import torch
from torch import nn


class MLP(nn.Module):
    def __init__(self, entradas: int, clases: int, ocultas: list[int], dropout: float) -> None:
        super().__init__()
        capas: list[nn.Module] = []
        previa = entradas
        for n in ocultas:
            capas += [nn.Linear(previa, n), nn.ReLU(), nn.Dropout(dropout)]
            previa = n
        self.red = nn.Sequential(*capas, nn.Linear(previa, clases))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.red(x)
