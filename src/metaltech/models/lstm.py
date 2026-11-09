"""LSTM sobre la ventana de sensores [N, T, V]."""

from __future__ import annotations

import torch
from torch import nn


class LSTM(nn.Module):
    def __init__(self, variables: int, clases: int, ocultas: int, capas: int, dropout: float) -> None:
        super().__init__()
        self.lstm = nn.LSTM(variables, ocultas, capas, batch_first=True, dropout=dropout if capas > 1 else 0.0)
        self.salida = nn.Linear(ocultas, clases)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z, _ = self.lstm(x)
        return self.salida(z[:, -1])
