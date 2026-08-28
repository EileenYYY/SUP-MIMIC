from __future__ import annotations

from math import sqrt
from statistics import mean, pstdev
from typing import Iterable


def standardized_mean_difference(a: Iterable[float], b: Iterable[float]) -> float | None:
    x = [float(v) for v in a]
    y = [float(v) for v in b]
    if not x or not y:
        return None
    sx = pstdev(x) if len(x) > 1 else 0.0
    sy = pstdev(y) if len(y) > 1 else 0.0
    denom = sqrt((sx * sx + sy * sy) / 2.0)
    if denom == 0:
        return 0.0
    return (mean(x) - mean(y)) / denom

