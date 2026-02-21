from __future__ import annotations

import math

# ---- SI constants (rounded for teaching) ----
g = 9.80665  # m/s^2
e = 1.602176634e-19  # C
m_e = 9.1093837015e-31  # kg
h = 6.62607015e-34  # J*s
mu0 = 4e-7 * math.pi  # N/A^2


def deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0


def rad_to_deg(rad: float) -> float:
    return rad * 180.0 / math.pi


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

