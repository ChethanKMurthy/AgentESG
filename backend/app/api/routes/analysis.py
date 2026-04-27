from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.data_agent import _company_to_dict, _metric_to_dict
from app.agents.orchestrator import Orchestrator
from app.analytics.benchmark import BenchmarkService
from app.analytics.scoring import compute_composite
from app.api.deps import db_session
from app.models.company import Company
from app.models.esg_metrics import ESGMetric
from app.rule_engine import RuleEvaluator
from app.roadmap.explainer import narrate_items
from app.roadmap.gap_analysis import analyze_gaps
from app.roadmap.generator import generate_roadmap
from app.schemas.analysis import (
    AgentStepOut,
    AnalysisCitation,
    FullAnalysisRequest,
    FullAnalysisResponse,
    RuleResultOut,
)
from app.schemas.analytics import (
    BenchmarkStatOut,
    CompareRequest,
    CompareResponse,
    GapOut,
    PeerStats,
    PillarScores,
    RoadmapItemOut,
    RoadmapRequest,
    RoadmapResponse,
)

router = APIRouter()


def _snippet(text: str, n: int = 240) -> str:
    t = " ".join(text.split())
    return t if len(t) <= n else t[:n] + "…"


@router.post("/full", response_model=FullAnalysisResponse)
async def full_analysis(
    payload: FullAnalysisRequest,
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> FullAnalysisResponse:
    orchestrator = Orchestrator(db)
    ctx = await orchestrator.run(
        company_id=payload.company_id,
        query=payload.query,
        top_k=payload.top_k,
        include_rag=payload.include_rag,
        include_report=payload.include_report,
        request_id=getattr(request.state, "request_id", None),
    )

    if ctx.company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"company {payload.company_id} not found")

    citations = [
        AnalysisCitation(
            index=r["index"],
            chunk_id=r["chunk_id"],
            source=r["source"],
            score=r["score"],
            snippet=_snippet(r["text"]),
        )
        for r in ctx.retrieved
    ]

    return FullAnalysisResponse(
        company_id=ctx.company_id,
        company=ctx.company,
        metrics=ctx.latest_metrics,
        rule_results=[RuleResultOut(**r) for r in ctx.rule_results],
        rule_summary=ctx.rule_summary,
        citations=citations,
        report=ctx.report,
        trace=[AgentStepOut(**s) for s in ctx.trace],
        errors=ctx.errors,
        request_id=ctx.request_id,
    )


def _benchmark_to_out(stat) -> BenchmarkStatOut:
    return BenchmarkStatOut(
        metric=stat.metric,
        direction=stat.direction,
        value=stat.value,
        peer_stats=PeerStats(**stat.peer_stats),
        percentile_rank=stat.percentile_rank,
        delta_vs_median=stat.delta_vs_median,
        status=stat.status,
    )


@router.post("/compare", response_model=CompareResponse)
async def compare(
    payload: CompareRequest,
    db: AsyncSession = Depends(db_session),
) -> CompareResponse:
    company = await db.get(Company, payload.company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"company {payload.company_id} not found")

    service = BenchmarkService(db)
    result = await service.compare(
        company_id=payload.company_id,
        year=payload.year,
        peer_scope=payload.peer_scope,
    )
    scoring = compute_composite(result)

    return CompareResponse(
        company_id=result.company_id,
        year=result.year,
        peer_scope=result.peer_scope,
        peer_count=result.peer_count,
        benchmarks={k: _benchmark_to_out(v) for k, v in result.benchmarks.items()},
        composite_score=result.composite_score,
        composite_percentile_rank=result.composite_percentile_rank,
        pillar_scores=PillarScores(**{k: v for k, v in scoring["pillars"].items()}),
        derived_composite=scoring["composite"],
    )


@router.post("/roadmap", response_model=RoadmapResponse)
async def roadmap(
    payload: RoadmapRequest,
    db: AsyncSession = Depends(db_session),
) -> RoadmapResponse:
    company = await db.get(Company, payload.company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"company {payload.company_id} not found")

    stmt = select(ESGMetric).where(ESGMetric.company_id == payload.company_id)
    if payload.year is not None:
        stmt = stmt.where(ESGMetric.year == payload.year)
    else:
        stmt = stmt.order_by(ESGMetric.year.desc()).limit(1)
    metric_row = (await db.execute(stmt)).scalars().first()

    company_dict = _company_to_dict(company)
    metric_dict = _metric_to_dict(metric_row) if metric_row else None

    rules = RuleEvaluator().evaluate(company_dict, metric_dict)
    rule_dicts = [asdict(r) for r in rules]

    benchmark = None
    if payload.include_benchmark and metric_row is not None:
        benchmark = await BenchmarkService(db).compare(
            company_id=payload.company_id,
            year=metric_row.year,
            peer_scope=payload.peer_scope,
        )

    gaps = analyze_gaps(rule_dicts, metric_dict, benchmark)
    items = generate_roadmap(gaps, horizon_months=payload.horizon_months)

    if payload.include_narrative and items:
        await narrate_items(items, company=company_dict, metrics=metric_dict)

    summary = {
        "gaps": len(gaps),
        "items": len(items),
    }
    for g in gaps:
        summary[g.severity] = summary.get(g.severity, 0) + 1

    return RoadmapResponse(
        company_id=payload.company_id,
        year=metric_row.year if metric_row else None,
        horizon_months=payload.horizon_months,
        gaps=[GapOut(**asdict(g)) for g in gaps],
        items=[RoadmapItemOut(**asdict(i)) for i in items],
        summary=summary,
    )
