from __future__ import annotations

import statistics
from typing import Dict, Iterable, List, Optional


def _clean(values: Iterable[Optional[float]]) -> List[float]:
    out: List[float] = []
    for v in values:
        if v is None:
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if f != f:  # NaN
            continue
        out.append(f)
    return out


def percentile_rank(value: Optional[float], series: Iterable[Optional[float]]) -> Optional[float]:
    if value is None:
        return None
    xs = _clean(series)
    if not xs:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    below = sum(1 for x in xs if x < v)
    equal = sum(1 for x in xs if x == v)
    return (below + 0.5 * equal) / len(xs) * 100.0


def summary_stats(series: Iterable[Optional[float]]) -> Dict[str, Optional[float]]:
    xs = _clean(series)
    if not xs:
        return {
            "n": 0, "min": None, "mean": None, "median": None,
            "p25": None, "p75": None, "max": None, "stdev": None,
        }
    xs_sorted = sorted(xs)
    n = len(xs_sorted)

    def q(p: float) -> float:
        if n == 1:
            return xs_sorted[0]
        i = (n - 1) * p
        lo = int(i)
        hi = min(lo + 1, n - 1)
        return xs_sorted[lo] + (xs_sorted[hi] - xs_sorted[lo]) * (i - lo)

    return {
        "n": n,
        "min": xs_sorted[0],
        "mean": statistics.fmean(xs),
        "median": statistics.median(xs),
        "p25": q(0.25),
        "p75": q(0.75),
        "max": xs_sorted[-1],
        "stdev": statistics.pstdev(xs) if n > 1 else 0.0,
    }
