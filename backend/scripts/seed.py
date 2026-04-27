from __future__ import annotations

import asyncio
import csv
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import delete

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.company import Company  # noqa: E402
from app.models.esg_metrics import ESGMetric  # noqa: E402

COMPANY_COLS = {
    "company_id": int,
    "company_name": str,
    "country": str,
    "eu_member_state": str,
    "region": str,
    "sector": str,
    "subsector": str,
    "industry": str,
    "revenue_usd": float,
    "total_assets_usd": float,
    "employees": int,
    "entity_type": str,
    "listing_status": str,
    "stock_symbol": str,
    "fiscal_year": int,
    "currency": str,
    "company_size_band": str,
    "csrd_applicable": lambda v: str(v).strip().lower() in {"yes", "true", "1"},
}

METRIC_COLS = {
    "company_id": int,
    "year": int,
    "sector": str,
    "country": str,
    "scope_1_emissions_tco2e": float,
    "scope_2_emissions_tco2e": float,
    "scope_3_emissions_tco2e": float,
    "energy_consumption_mwh": float,
    "renewable_energy_percent": float,
    "water_usage_m3": float,
    "waste_generated_tons": float,
    "waste_recycled_percent": float,
    "employee_count": int,
    "female_employee_ratio": float,
    "board_independence_percent": float,
    "incident_count": int,
    "esg_score": float,
}


def _cast(val: str, caster):
    if val is None or val == "":
        return None
    try:
        return caster(val)
    except Exception:
        return None


def _read_csv(path: Path, cols: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row: Dict[str, Any] = {}
            for name, caster in cols.items():
                row[name] = _cast(raw.get(name), caster)
            rows.append(row)
    return rows


async def seed(companies_csv: str, metrics_csv: str, replace: bool = True) -> Dict[str, int]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    companies = _read_csv(Path(companies_csv), COMPANY_COLS)
    metrics = _read_csv(Path(metrics_csv), METRIC_COLS)

    async with SessionLocal() as session:
        if replace:
            await session.execute(delete(ESGMetric))
            await session.execute(delete(Company))
            await session.commit()

        session.add_all([Company(**row) for row in companies if row.get("company_id") is not None])
        await session.flush()

        session.add_all(
            [
                ESGMetric(**row)
                for row in metrics
                if row.get("company_id") is not None and row.get("year") is not None
            ]
        )
        await session.commit()

    await engine.dispose()
    return {"companies": len(companies), "metrics": len(metrics)}


def main() -> None:
    companies_csv = os.environ.get("SEED_COMPANIES_CSV", "/app/data/seed/company_master.csv")
    metrics_csv = os.environ.get("SEED_METRICS_CSV", "/app/data/seed/esg_metrics.csv")
    result = asyncio.run(seed(companies_csv, metrics_csv))
    print(result)


if __name__ == "__main__":
    main()
