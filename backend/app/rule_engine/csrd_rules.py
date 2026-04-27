from __future__ import annotations

from typing import Any, Dict, Optional

from app.rule_engine.types import Rule

LARGE_EMPLOYEES = 250
LARGE_REVENUE = 50_000_000
LARGE_ASSETS = 25_000_000
NON_EU_THRESHOLD = 150_000_000


def _is_eu(c: Dict[str, Any]) -> bool:
    return bool(c.get("eu_member_state")) or bool(c.get("region") and "europe" in str(c.get("region", "")).lower())


def _num(x) -> float:
    try:
        return float(x) if x is not None else 0.0
    except Exception:
        return 0.0


def _meets_large_thresholds(c: Dict[str, Any]) -> int:
    count = 0
    if _num(c.get("employees")) >= LARGE_EMPLOYEES:
        count += 1
    if _num(c.get("revenue_usd")) >= LARGE_REVENUE:
        count += 1
    if _num(c.get("total_assets_usd")) >= LARGE_ASSETS:
        count += 1
    return count


def _listed(c: Dict[str, Any]) -> bool:
    return str(c.get("listing_status", "")).lower().startswith("listed")


CSRD_RULES = [
    Rule(
        id="CSRD_APPLICABILITY_LARGE_EU",
        category="applicability",
        severity="info",
        description="EU large-undertaking thresholds: at least 2 of 3.",
        when=lambda c, m: _is_eu(c) and _meets_large_thresholds(c) >= 2,
        message=lambda c, m: (
            f"CSRD applies: EU entity meets {_meets_large_thresholds(c)} of 3 "
            "large-undertaking thresholds (employees>250, revenue>EUR50M, assets>EUR25M)."
        ),
        citations=["CSRD Art. 3; Directive (EU) 2022/2464"],
    ),
    Rule(
        id="CSRD_APPLICABILITY_LISTED",
        category="applicability",
        severity="info",
        description="Listed on an EU-regulated market (non-micro).",
        when=lambda c, m: _is_eu(c)
        and _listed(c)
        and str(c.get("company_size_band", "")).lower() != "micro",
        message=lambda c, m: "CSRD applies: company is listed on an EU-regulated market.",
        citations=["CSRD Art. 19a; Art. 29a"],
    ),
    Rule(
        id="CSRD_APPLICABILITY_NON_EU",
        category="applicability",
        severity="info",
        description="Non-EU entity with EU net turnover > EUR 150M.",
        when=lambda c, m: (not _is_eu(c)) and _num(c.get("revenue_usd")) > NON_EU_THRESHOLD,
        message=lambda c, m: (
            "CSRD may apply: non-EU entity with EU turnover above EUR 150M threshold; "
            "verify EU subsidiary/branch footprint."
        ),
        citations=["CSRD Art. 40a"],
    ),
    Rule(
        id="ESRS_E1_RENEWABLE_LOW",
        category="climate",
        severity="medium",
        description="Renewable energy share below 20%.",
        when=lambda c, m: bool(m) and _num(m.get("renewable_energy_percent")) < 20,
        message=lambda c, m: (
            f"Renewable energy share is {_num(m.get('renewable_energy_percent')):.1f}% "
            "(<20% minimum benchmark); expand ESRS E1 transition plan disclosure."
        ),
        citations=["ESRS E1 — Climate Change"],
    ),
    Rule(
        id="ESRS_E1_SCOPE3_DOMINANT",
        category="climate",
        severity="medium",
        description="Scope 3 emissions dominate Scopes 1+2 (>3x).",
        when=lambda c, m: bool(m)
        and _num(m.get("scope_3_emissions_tco2e"))
        > 3 * (_num(m.get("scope_1_emissions_tco2e")) + _num(m.get("scope_2_emissions_tco2e"))),
        message=lambda c, m: (
            "Scope 3 dominates Scopes 1+2; ESRS E1 requires a full 15-category Scope 3 breakdown "
            "and targets aligned with a 1.5C pathway."
        ),
        citations=["ESRS E1-6", "GHG Protocol Scope 3 Standard"],
    ),
    Rule(
        id="GOV_BOARD_INDEPENDENCE_LOW",
        category="governance",
        severity="high",
        description="Board independence below 50%.",
        when=lambda c, m: bool(m) and _num(m.get("board_independence_percent")) < 50,
        message=lambda c, m: (
            f"Board independence {_num(m.get('board_independence_percent')):.1f}% is below 50% "
            "best-practice threshold; remediate under ESRS G1."
        ),
        citations=["ESRS G1 — Business Conduct"],
    ),
    Rule(
        id="GOV_GENDER_DIVERSITY_LOW",
        category="governance",
        severity="medium",
        description="Female employee ratio below 30%.",
        when=lambda c, m: bool(m) and _num(m.get("female_employee_ratio")) < 0.30,
        message=lambda c, m: (
            f"Female employee ratio {_num(m.get('female_employee_ratio')):.2f} is below 0.30 benchmark; "
            "strengthen diversity disclosures."
        ),
        citations=["ESRS S1 — Own Workforce"],
    ),
    Rule(
        id="GOV_INCIDENTS_HIGH",
        category="governance",
        severity="high",
        description="More than 5 reportable incidents in the year.",
        when=lambda c, m: bool(m) and _num(m.get("incident_count")) > 5,
        message=lambda c, m: (
            f"{int(_num(m.get('incident_count')))} reportable incidents; enhanced ESRS G1 "
            "whistleblower and business-conduct disclosures are required."
        ),
        citations=["ESRS G1-5"],
    ),
    Rule(
        id="CIRCULAR_WASTE_RECYCLE_LOW",
        category="circular_economy",
        severity="low",
        description="Waste recycled below 50%.",
        when=lambda c, m: bool(m) and _num(m.get("waste_recycled_percent")) < 50,
        message=lambda c, m: (
            f"Waste recycled {_num(m.get('waste_recycled_percent')):.1f}%; ESRS E5 encourages "
            "targets and improvement plans."
        ),
        citations=["ESRS E5 — Resource Use and Circular Economy"],
    ),
    Rule(
        id="WATER_INTENSITY_HIGH",
        category="water",
        severity="low",
        description="Water usage per employee exceeds 5000 m3/FTE.",
        when=lambda c, m: bool(m)
        and _num(m.get("employee_count")) > 0
        and _num(m.get("water_usage_m3")) / _num(m.get("employee_count")) > 5000,
        message=lambda c, m: (
            "Water intensity per employee exceeds 5,000 m3/FTE; review ESRS E3 disclosures on "
            "water-stressed area operations."
        ),
        citations=["ESRS E3 — Water and Marine Resources"],
    ),
]
