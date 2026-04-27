from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.percentile import percentile_rank, summary_stats
from app.models.company import Company
from app.models.esg_metrics import ESGMetric

METRIC_DIRECTION: Dict[str, str] = {
    "scope_1_emissions_tco2e": "lower",
    "scope_2_emissions_tco2e": "lower",
    "scope_3_emissions_tco2e": "lower",
    "energy_consumption_mwh": "lower",
    "water_usage_m3": "lower",
    "waste_generated_tons": "lower",
    "incident_count": "lower",
    "renewable_energy_percent": "higher",
    "waste_recycled_percent": "higher",
    "female_employee_ratio": "higher",
    "board_independence_percent": "higher",
    "esg_score": "higher",
}


def _status(direction: str, pct_rank: Optional[float]) -> str:
    if pct_rank is None:
        return "unknown"
    if direction == "higher":
        if pct_rank >= 75:
            return "leader"
        if pct_rank <= 25:
            return "laggard"
        return "peer"
    if pct_rank <= 25:
        return "leader"
    if pct_rank >= 75:
        return "laggard"
    return "peer"


@dataclass
class BenchmarkStat:
    metric: str
    direction: str
    value: Optional[float]
    peer_stats: Dict[str, Optional[float]]
    percentile_rank: Optional[float]
    delta_vs_median: Optional[float]
    status: str


@dataclass
class BenchmarkResult:
    company_id: int
    year: Optional[int]
    peer_scope: str
    peer_count: int
    benchmarks: Dict[str, BenchmarkStat] = field(default_factory=dict)
    composite_score: Optional[float] = None
    composite_percentile_rank: Optional[float] = None


class BenchmarkService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _target(self, company_id: int, year: Optional[int]) -> Optional[ESGMetric]:
        stmt = select(ESGMetric).where(ESGMetric.company_id == company_id)
        if year is not None:
            stmt = stmt.where(ESGMetric.year == year)
        else:
            stmt = stmt.order_by(ESGMetric.year.desc()).limit(1)
        row = (await self.db.execute(stmt)).scalars().first()
        return row

    async def _peer_set(
        self,
        *,
        target_year: int,
        peer_scope: str,
        company: Company,
        exclude_id: int,
    ) -> List[ESGMetric]:
        stmt = select(ESGMetric).join(
            Company, Company.company_id == ESGMetric.company_id
        ).where(
            and_(ESGMetric.year == target_year, ESGMetric.company_id != exclude_id)
        )
        if peer_scope in ("sector", "sector_country") and company.sector:
            stmt = stmt.where(ESGMetric.sector == company.sector)
        if peer_scope in ("industry", "industry_country") and company.industry:
            stmt = stmt.where(Company.industry == company.industry)
        if peer_scope in ("country", "sector_country", "industry_country") and company.country:
            stmt = stmt.where(ESGMetric.country == company.country)
        return (await self.db.execute(stmt)).scalars().all()

    async def compare(
        self,
        company_id: int,
        year: Optional[int] = None,
        peer_scope: str = "sector",
    ) -> BenchmarkResult:
        target = await self._target(company_id, year)
        if target is None:
            return BenchmarkResult(
                company_id=company_id, year=year, peer_scope=peer_scope, peer_count=0
            )

        company = await self.db.get(Company, company_id)
        peers = await self._peer_set(
            target_year=target.year,
            peer_scope=peer_scope,
            company=company,
            exclude_id=company_id,
        )

        result = BenchmarkResult(
            company_id=company_id,
            year=target.year,
            peer_scope=peer_scope,
            peer_count=len(peers),
        )

        for metric_name, direction in METRIC_DIRECTION.items():
            value = getattr(target, metric_name, None)
            series = [getattr(p, metric_name, None) for p in peers]
            stats = summary_stats(series)
            pr = percentile_rank(value, series)
            delta = (
                float(value) - stats["median"]
                if value is not None and stats["median"] is not None
                else None
            )
            result.benchmarks[metric_name] = BenchmarkStat(
                metric=metric_name,
                direction=direction,
                value=float(value) if value is not None else None,
                peer_stats=stats,
                percentile_rank=pr,
                delta_vs_median=delta,
                status=_status(direction, pr),
            )

        esg = result.benchmarks.get("esg_score")
        if esg is not None:
            result.composite_score = esg.value
            result.composite_percentile_rank = esg.percentile_rank
        return result
