from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Bracket:
    i0: int
    i1: int
    t: float  # in [0,1]


def find_bracket(values: Sequence[float], x: float) -> Bracket:
    n = len(values)
    if n < 2:
        return Bracket(0, 0, 0.0)
    if x <= values[0]:
        return Bracket(0, 1, 0.0)
    if x >= values[-1]:
        return Bracket(n - 2, n - 1, 1.0)
    lo, hi = 0, n - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if values[mid] <= x:
            lo = mid
        else:
            hi = mid
    a, b = values[lo], values[hi]
    t = (x - a) / (b - a)
    return Bracket(lo, hi, float(t))


def lerp(a: float, b: float, t: float) -> float:
    return a * (1 - t) + b * t

