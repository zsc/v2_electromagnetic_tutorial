from __future__ import annotations

import math
from dataclasses import dataclass

from emlab.common.units import e, h, m_e


def electron_speed_from_vacc(v_acc: float) -> float:
    """Non-relativistic electron speed from accelerating voltage (V)."""
    return math.sqrt(max(0.0, 2.0 * e * v_acc / m_e))


def de_broglie_wavelength_electron(v_acc: float) -> float:
    """Non-relativistic de Broglie wavelength (m) for an electron accelerated by v_acc (V)."""
    p = math.sqrt(max(0.0, 2.0 * m_e * e * v_acc))
    return h / p if p > 0 else float("inf")


@dataclass(frozen=True)
class SeriesRLC:
    R: float
    L: float
    C: float

    def omega0(self) -> float:
        return 1.0 / math.sqrt(self.L * self.C)

    def alpha(self) -> float:
        return self.R / (2.0 * self.L)

    def regime(self) -> str:
        a = self.alpha()
        w0 = self.omega0()
        if abs(a - w0) / w0 < 1e-3:
            return "critical"
        return "over" if a > w0 else "under"

