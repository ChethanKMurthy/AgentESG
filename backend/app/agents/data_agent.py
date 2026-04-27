from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, BaseAgent
from app.models.company import Company
from app.models.esg_metrics import ESGMetric


def _company_to_dict(c: Company) -> Dict[str, Any]:
    return {
        "company_id": c.company_id,
        "company_name": c.company_name,
        "country": c.country,
        "eu_member_state": c.eu_member_state,
        "region": c.region,
        "sector": c.sector,
        "subsector": c.subsector,
        "industry": c.industry,
        "revenue_usd": c.revenue_usd,
        "total_assets_usd": c.total_assets_usd,
        "employees": c.employees,
        "entity_type": c.entity_type,
        "listing_status": c.listing_status,
        "stock_symbol": c.stock_symbol,
        "fiscal_year": c.fiscal_year,
        "currency": c.currency,
        "company_size_band": c.company_size_band,
        "csrd_applicable": c.csrd_applicable,
    }


def _metric_to_dict(m: ESGMetric) -> Dict[str, Any]:
    return {
        "company_id": m.company_id,
        "year": m.year,
        "sector": m.sector,
        "country": m.country,
        "scope_1_emissions_tco2e": m.scope_1_emissions_tco2e,
        "scope_2_emissions_tco2e": m.scope_2_emissions_tco2e,
        "scope_3_emissions_tco2e": m.scope_3_emissions_tco2e,
        "energy_consumption_mwh": m.energy_consumption_mwh,
        "renewable_energy_percent": m.renewable_energy_percent,
        "water_usage_m3": m.water_usage_m3,
        "waste_generated_tons": m.waste_generated_tons,
        "waste_recycled_percent": m.waste_recycled_percent,
        "employee_count": m.employee_count,
        "female_employee_ratio": m.female_employee_ratio,
        "board_independence_percent": m.board_independence_percent,
        "incident_count": m.incident_count,
        "esg_score": m.esg_score,
    }


class DataAgent(BaseAgent):
    name = "data_agent"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        company = await self.db.get(Company, ctx.company_id)
        if not company:
            raise LookupError(f"company_id {ctx.company_id} not found")
        ctx.company = _company_to_dict(company)

        row = (
            await self.db.execute(
                select(ESGMetric)
                .where(ESGMetric.company_id == ctx.company_id)
                .order_by(ESGMetric.year.desc())
                .limit(1)
            )
        ).scalars().first()
        ctx.latest_metrics = _metric_to_dict(row) if row else None

        return {
            "company": ctx.company["company_name"],
            "has_metrics": ctx.latest_metrics is not None,
            "metrics_year": (ctx.latest_metrics or {}).get("year"),
        }
