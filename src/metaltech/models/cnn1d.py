"""Red convolucional 1D sobre la ventana de sensores [N, T, V]."""

from __future__ import annotations

import torch
from torch import nn


class CNN1D(nn.Module):
    def __init__(self, variables: int, clases: int, canales: list[int], kernel: int, dropout: float) -> None:
        super().__init__()
        capas: list[nn.Module] = []
        previa = variables
        for n in canales:
            capas += [nn.Conv1d(previa, n, kernel, padding=kernel // 2), nn.BatchNorm1d(n), nn.ReLU()]
            previa = n
        self.convoluciones = nn.Sequential(*capas)
        self.salida = nn.Sequential(nn.Dropout(dropout), nn.Linear(2 * previa, clases))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.convoluciones(x.transpose(1, 2))
        # La media resume la tendencia y el máximo conserva eventos de un solo paso.
        return self.salida(torch.cat([z.mean(dim=2), z.max(dim=2).values], dim=1))
