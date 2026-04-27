from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.roadmap.gap_analysis import Gap, SEVERITY_RANK

HORIZON_BY_SEVERITY = {
    "critical": "0-3m",
    "high": "0-3m",
    "medium": "3-6m",
    "low": "6-12m",
    "info": "12m+",
}

ACTIONS_BY_CATEGORY: Dict[str, List[str]] = {
    "climate": [
        "Establish Scope 1/2/3 inventory per GHG Protocol with third-party validation",
        "Set science-based targets (SBTi) aligned with 1.5C pathway and disclose under ESRS E1",
        "Increase renewable energy procurement via PPAs and on-site generation",
        "Publish transition plan covering mitigation, adaptation, and capex allocation",
    ],
    "governance": [
        "Recruit independent directors to reach >=50% board independence",
        "Formalize whistleblower, anti-corruption, and business-conduct policies",
        "Adopt diversity targets (>=30%) and publish progress annually",
        "Disclose G1 policies, incidents, and remediation in CSRD report",
    ],
    "circular_economy": [
        "Establish waste hierarchy and set >=50% recycling target",
        "Launch supplier engagement program for packaging reduction",
        "Track and report circular material use rate under ESRS E5",
    ],
    "water": [
        "Perform water-stressed location screening (WRI Aqueduct)",
        "Set absolute and intensity reduction targets under ESRS E3",
        "Install metering and reuse systems at high-intensity sites",
    ],
    "benchmark": [
        "Investigate peer-leader practices for this metric",
        "Set a median-closing target for next reporting cycle",
        "Assign metric ownership and monthly review cadence",
    ],
    "other": [
        "Commission materiality assessment and align disclosures to ESRS",
    ],
}

KPIS_BY_METRIC: Dict[str, List[str]] = {
    "renewable_energy_percent": ["Renewable share (%)", "PPA MWh signed", "On-site generation MWh"],
    "board_independence_percent": ["Independent directors (%)", "Board tenure distribution"],
    "female_employee_ratio": ["Female workforce share", "Female leadership share", "Pay-gap ratio"],
    "incident_count": ["Open incidents", "Time-to-remediate (days)", "Near-miss ratio"],
    "waste_recycled_percent": ["Recycled share (%)", "Landfill diversion rate", "Waste per unit output"],
    "scope_3_emissions_tco2e": ["Scope 3 covered categories", "Supplier engagement (%)"],
    "water_usage_m3": ["m3 per employee", "Reused volume (m3)"],
}


@dataclass
class Driver:
    kind: str
    identifier: str
    severity: str
    weight: float
    description: str
    metric: Optional[str] = None
    current: Optional[float] = None
    target: Optional[float] = None
    citations: List[str] = field(default_factory=list)


@dataclass
class Explanation:
    drivers: List[Driver] = field(default_factory=list)
    priority_factors: Dict[str, Any] = field(default_factory=dict)
    horizon_rationale: str = ""
    methodology: str = ""
    narrative: Optional[str] = None


@dataclass
class RoadmapItem:
    id: str
    title: str
    description: str
    category: str
    severity: str
    priority: int
    horizon: str
    actions: List[str] = field(default_factory=list)
    kpis: List[str] = field(default_factory=list)
    evidence: str = ""
    citations: List[str] = field(default_factory=list)
    gap_ids: List[str] = field(default_factory=list)
    confidence: str = "medium"
    explanation: Explanation = field(default_factory=Explanation)


METHODOLOGY_TEXT = (
    "Items are ranked by the highest severity among contributing gaps "
    "(critical=5, high=4, medium=3, low=2, info=1). "
    "Horizon maps deterministically from severity: critical/high -> 0-3m, "
    "medium -> 3-6m, low -> 6-12m, info -> 12m+. "
    "Targets come from the regulation for rule-driven gaps, or from the peer median "
    "for benchmark-driven gaps. Actions are drawn from a category playbook."
)


def _title(category: str, metric: Optional[str]) -> str:
    m = metric or category
    nice = m.replace("_", " ").replace("percent", "%").title()
    return f"Close gap on {nice}"


def _confidence_of(drivers: List[Driver]) -> str:
    has_rule = any(d.kind == "rule" for d in drivers)
    has_bench = any(d.kind == "benchmark" for d in drivers)
    if has_rule and has_bench:
        return "high"
    if has_rule:
        return "medium"
    return "low"


def _build_explanation(group: List[Gap], severity: str, horizon: str) -> Explanation:
    drivers: List[Driver] = []
    for g in group:
        w = float(SEVERITY_RANK.get(g.severity, 1))
        drivers.append(
            Driver(
                kind=g.source,
                identifier=g.id.replace("gap:", "").replace("bench:", "benchmark:"),
                severity=g.severity,
                weight=w,
                description=g.evidence,
                metric=g.metric,
                current=g.current,
                target=g.target,
                citations=list(g.citations),
            )
        )
    factors = {
        "severity_rank": SEVERITY_RANK.get(severity, 0),
        "gap_count": len(group),
        "rule_drivers": sum(1 for d in drivers if d.kind == "rule"),
        "benchmark_drivers": sum(1 for d in drivers if d.kind == "benchmark"),
        "weight_sum": round(sum(d.weight for d in drivers), 2),
    }
    horizon_rationale = (
        f"Horizon {horizon} assigned because the highest-severity driver is '{severity}'. "
        "Critical and high-severity items receive a 0-3 month window."
    )
    return Explanation(
        drivers=drivers,
        priority_factors=factors,
        horizon_rationale=horizon_rationale,
        methodology=METHODOLOGY_TEXT,
    )


def generate_roadmap(gaps: List[Gap], horizon_months: int = 12) -> List[RoadmapItem]:
    by_key: Dict[str, List[Gap]] = {}
    for g in gaps:
        key = g.metric or g.category
        by_key.setdefault(key, []).append(g)

    items: List[RoadmapItem] = []
    priority_counter = 1

    def _severity_of(group: List[Gap]) -> str:
        return max(group, key=lambda x: SEVERITY_RANK.get(x.severity, 0)).severity

    ordered_keys = sorted(
        by_key.keys(),
        key=lambda k: SEVERITY_RANK.get(_severity_of(by_key[k]), 0),
        reverse=True,
    )

    for key in ordered_keys:
        group = by_key[key]
        first = group[0]
        sev = _severity_of(group)
        horizon = HORIZON_BY_SEVERITY.get(sev, "12m+")
        category = first.category if first.source == "rule" else "benchmark"
        actions = ACTIONS_BY_CATEGORY.get(category, ACTIONS_BY_CATEGORY["other"])
        kpis = KPIS_BY_METRIC.get(first.metric, []) if first.metric else []
        evidence = " | ".join(g.evidence for g in group if g.evidence)
        citations: List[str] = []
        for g in group:
            citations.extend(g.citations)

        explanation = _build_explanation(group, sev, horizon)
        confidence = _confidence_of(explanation.drivers)

        item = RoadmapItem(
            id=f"item:{priority_counter}",
            title=_title(category, first.metric),
            description=(
                f"Severity: {sev}. "
                f"{len(group)} gap(s) aggregated for {first.metric or category}."
            ),
            category=category,
            severity=sev,
            priority=priority_counter,
            horizon=horizon,
            actions=list(actions),
            kpis=kpis,
            evidence=evidence,
            citations=sorted(set(citations)),
            gap_ids=[g.id for g in group],
            confidence=confidence,
            explanation=explanation,
        )
        items.append(item)
        priority_counter += 1

    if horizon_months < 12:
        allowed = (
            {"0-3m"}
            if horizon_months <= 3
            else {"0-3m", "3-6m"}
            if horizon_months <= 6
            else {"0-3m", "3-6m", "6-12m"}
        )
        items = [i for i in items if i.horizon in allowed]
    return items
