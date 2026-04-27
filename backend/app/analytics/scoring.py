from __future__ import annotations

from typing import Any, Dict, Optional

from app.analytics.benchmark import BenchmarkResult

PILLAR_WEIGHTS = {"environment": 0.4, "social": 0.3, "governance": 0.3}

PILLAR_METRICS = {
    "environment": [
        "scope_1_emissions_tco2e",
        "scope_2_emissions_tco2e",
        "scope_3_emissions_tco2e",
        "energy_consumption_mwh",
        "water_usage_m3",
        "waste_generated_tons",
        "renewable_energy_percent",
        "waste_recycled_percent",
    ],
    "social": [
        "female_employee_ratio",
    ],
    "governance": [
        "board_independence_percent",
        "incident_count",
    ],
}


def _norm(percentile_rank: Optional[float], direction: str) -> Optional[float]:
    if percentile_rank is None:
        return None
    if direction == "higher":
        return percentile_rank
    return 100.0 - percentile_rank


def compute_pillar_scores(benchmark: BenchmarkResult) -> Dict[str, Optional[float]]:
    out: Dict[str, Optional[float]] = {}
    for pillar, metrics in PILLAR_METRICS.items():
        parts = []
        for m in metrics:
            bs = benchmark.benchmarks.get(m)
            if bs is None:
                continue
            n = _norm(bs.percentile_rank, bs.direction)
            if n is not None:
                parts.append(n)
        out[pillar] = sum(parts) / len(parts) if parts else None
    return out


def compute_composite(benchmark: BenchmarkResult) -> Dict[str, Any]:
    pillars = compute_pillar_scores(benchmark)
    weighted = 0.0
    weight_sum = 0.0
    for pillar, score in pillars.items():
        if score is None:
            continue
        w = PILLAR_WEIGHTS[pillar]
        weighted += score * w
        weight_sum += w
    composite = weighted / weight_sum if weight_sum > 0 else None
    return {"pillars": pillars, "composite": composite}
