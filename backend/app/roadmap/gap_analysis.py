from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.analytics.benchmark import BenchmarkResult, METRIC_DIRECTION

SEVERITY_RANK = {"info": 1, "low": 2, "medium": 3, "high": 4, "critical": 5}


@dataclass
class Gap:
    id: str
    category: str
    metric: Optional[str]
    severity: str
    current: Optional[float]
    target: Optional[float]
    evidence: str
    citations: List[str] = field(default_factory=list)
    source: str = "rule"  # "rule" | "benchmark"


def _target_from_rule(rule_id: str, metric: Optional[str]) -> Optional[float]:
    defaults = {
        "ESRS_E1_RENEWABLE_LOW": 20.0,
        "GOV_BOARD_INDEPENDENCE_LOW": 50.0,
        "GOV_GENDER_DIVERSITY_LOW": 0.30,
        "GOV_INCIDENTS_HIGH": 5.0,
        "CIRCULAR_WASTE_RECYCLE_LOW": 50.0,
    }
    return defaults.get(rule_id)


def _metric_from_rule_id(rule_id: str) -> Optional[str]:
    mapping = {
        "ESRS_E1_RENEWABLE_LOW": "renewable_energy_percent",
        "GOV_BOARD_INDEPENDENCE_LOW": "board_independence_percent",
        "GOV_GENDER_DIVERSITY_LOW": "female_employee_ratio",
        "GOV_INCIDENTS_HIGH": "incident_count",
        "CIRCULAR_WASTE_RECYCLE_LOW": "waste_recycled_percent",
        "ESRS_E1_SCOPE3_DOMINANT": "scope_3_emissions_tco2e",
        "WATER_INTENSITY_HIGH": "water_usage_m3",
    }
    return mapping.get(rule_id)


def gaps_from_rules(rule_results: List[Dict[str, Any]], metrics: Optional[Dict[str, Any]]) -> List[Gap]:
    out: List[Gap] = []
    for rr in rule_results:
        if not rr.get("triggered"):
            continue
        if rr.get("severity") == "info":
            continue
        metric = _metric_from_rule_id(rr["rule_id"])
        current = None
        if metric and metrics:
            current = metrics.get(metric)
        out.append(
            Gap(
                id=f"gap:{rr['rule_id']}",
                category=rr.get("category", "other"),
                metric=metric,
                severity=rr.get("severity", "medium"),
                current=current,
                target=_target_from_rule(rr["rule_id"], metric),
                evidence=rr.get("message", ""),
                citations=list(rr.get("citations") or []),
                source="rule",
            )
        )
    return out


def gaps_from_benchmark(benchmark: Optional[BenchmarkResult]) -> List[Gap]:
    if benchmark is None or not benchmark.benchmarks:
        return []
    out: List[Gap] = []
    for metric_name, bs in benchmark.benchmarks.items():
        if bs.status != "laggard" or bs.percentile_rank is None or bs.value is None:
            continue
        direction = METRIC_DIRECTION.get(metric_name, "higher")
        target = bs.peer_stats.get("median")
        severity = "high" if (bs.percentile_rank <= 10 or bs.percentile_rank >= 90) else "medium"
        evidence = (
            f"{metric_name} at {bs.value:.2f} is in the "
            f"{'bottom' if direction == 'higher' else 'top'} "
            f"{bs.percentile_rank:.0f}th percentile vs peers "
            f"(median {target:.2f} n={bs.peer_stats.get('n')})."
            if target is not None
            else f"{metric_name} at {bs.value:.2f} is a peer laggard."
        )
        out.append(
            Gap(
                id=f"gap:bench:{metric_name}",
                category="benchmark",
                metric=metric_name,
                severity=severity,
                current=bs.value,
                target=target,
                evidence=evidence,
                source="benchmark",
            )
        )
    return out


def analyze_gaps(
    rule_results: List[Dict[str, Any]],
    metrics: Optional[Dict[str, Any]],
    benchmark: Optional[BenchmarkResult] = None,
) -> List[Gap]:
    merged: Dict[str, Gap] = {}
    for g in gaps_from_rules(rule_results, metrics):
        merged[g.id] = g
    for g in gaps_from_benchmark(benchmark):
        merged.setdefault(g.id, g)
    return sorted(
        merged.values(),
        key=lambda g: SEVERITY_RANK.get(g.severity, 0),
        reverse=True,
    )
