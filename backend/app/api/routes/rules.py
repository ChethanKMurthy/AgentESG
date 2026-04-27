from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.rule_engine import RuleEvaluator

router = APIRouter()


class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    company_id: Optional[int] = None
    company_name: Optional[str] = None
    country: Optional[str] = None
    eu_member_state: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    revenue_usd: Optional[float] = Field(default=None, validation_alias="revenue")
    total_assets_usd: Optional[float] = Field(default=None, validation_alias="total_assets")
    employees: Optional[int] = None
    entity_type: Optional[str] = None
    listing_status: Optional[str] = None
    company_size_band: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class RuleResultOut(BaseModel):
    rule_id: str
    category: str
    severity: str
    triggered: bool
    message: str
    citations: List[str] = []


class EvaluateResponse(BaseModel):
    csrd_applicable: bool
    decision: str
    reasoning: List[str]
    sources: List[str]
    rule_results: List[RuleResultOut]
    summary: Dict[str, int]


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    data = payload.model_dump()
    metrics = data.pop("metrics", None)
    for alt_key in ("revenue", "total_assets"):
        data.pop(alt_key, None)

    _infer_eu(data)

    evaluator = RuleEvaluator()
    results = evaluator.evaluate(data, metrics)

    csrd_rules_triggered = [r for r in results if r.category == "applicability" and r.triggered]
    csrd_applicable = bool(csrd_rules_triggered)

    reasoning = [r.message for r in csrd_rules_triggered] or [
        "No CSRD applicability pathway matched given inputs."
    ]
    sources: List[str] = []
    for r in csrd_rules_triggered:
        sources.extend(r.citations)

    decision = (
        "CSRD APPLIES based on current thresholds."
        if csrd_applicable
        else "CSRD does NOT apply based on current inputs."
    )

    return EvaluateResponse(
        csrd_applicable=csrd_applicable,
        decision=decision,
        reasoning=reasoning,
        sources=sources,
        rule_results=[RuleResultOut(**asdict(r)) for r in results],
        summary=RuleEvaluator.summarize(results),
    )


_EU_COUNTRIES = {
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czech republic", "czechia",
    "denmark", "estonia", "finland", "france", "germany", "greece", "hungary", "ireland",
    "italy", "latvia", "lithuania", "luxembourg", "malta", "netherlands", "poland",
    "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
}


def _infer_eu(data: Dict[str, Any]) -> None:
    if data.get("eu_member_state"):
        return
    country = (data.get("country") or "").strip().lower()
    if country in _EU_COUNTRIES:
        data["eu_member_state"] = data.get("country")
