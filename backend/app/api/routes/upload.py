from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.ingestion.extractor import extract_from_text
from app.ingestion.pdf import extract_pdf_text
from app.llm import get_llm_client
from app.models.audit import AuditLog
from app.models.company import Company
from app.models.esg_metrics import ESGMetric
from app.schemas.disclosure import DisclosureUploadResponse
from app.schemas.upload import KPIUploadRequest, KPIUploadResponse

router = APIRouter()

COMPANY_FIELDS = {
    "company_name",
    "country",
    "eu_member_state",
    "region",
    "sector",
    "subsector",
    "industry",
    "revenue_usd",
    "total_assets_usd",
    "employees",
    "entity_type",
    "listing_status",
    "stock_symbol",
    "fiscal_year",
    "currency",
    "company_size_band",
    "csrd_applicable",
}

METRIC_FIELDS = {
    "year",
    "sector",
    "country",
    "scope_1_emissions_tco2e",
    "scope_2_emissions_tco2e",
    "scope_3_emissions_tco2e",
    "energy_consumption_mwh",
    "renewable_energy_percent",
    "water_usage_m3",
    "waste_generated_tons",
    "waste_recycled_percent",
    "employee_count",
    "female_employee_ratio",
    "board_independence_percent",
    "incident_count",
    "esg_score",
}

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


@router.post("/kpi", response_model=KPIUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_kpi(
    payload: KPIUploadRequest,
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> KPIUploadResponse:
    company_data = payload.company.model_dump(exclude_none=True)
    metrics_data = payload.metrics.model_dump(exclude_none=True)

    if not company_data.get("company_name"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "company.company_name is required")
    if metrics_data.get("year") is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "metrics.year is required")

    company_id = company_data.get("company_id")
    if company_id is None:
        company_id = (
            await db.execute(select(func.coalesce(func.max(Company.company_id), 0)))
        ).scalar_one() + 1
        company_data["company_id"] = company_id

    existing = await db.get(Company, company_id)
    created = existing is None
    if existing is None:
        db.add(Company(**company_data))
    else:
        for k, v in company_data.items():
            if k == "company_id":
                continue
            setattr(existing, k, v)

    await db.flush()

    metrics_data["company_id"] = company_id
    for k in ("sector", "country"):
        if not metrics_data.get(k):
            metrics_data[k] = company_data.get(k)

    existing_metric = await db.get(ESGMetric, (company_id, metrics_data["year"]))
    if existing_metric is None:
        db.add(ESGMetric(**metrics_data))
    else:
        for k, v in metrics_data.items():
            if k in ("company_id", "year"):
                continue
            setattr(existing_metric, k, v)

    db.add(
        AuditLog(
            request_id=getattr(request.state, "request_id", "") or "",
            method=request.method,
            path=request.url.path,
            status_code=201,
            event_type="kpi_upload",
            user_id=request.headers.get("x-user-id"),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            payload={
                "company_id": company_id,
                "year": metrics_data["year"],
                "created": created,
            },
        )
    )

    await db.commit()
    return KPIUploadResponse(
        company_id=company_id,
        created=created,
        metrics_year=metrics_data["year"],
    )


def _coerce_bool(v):
    if isinstance(v, bool) or v is None:
        return v
    s = str(v).strip().lower()
    if s in {"true", "yes", "1"}:
        return True
    if s in {"false", "no", "0"}:
        return False
    return None


def _coerce_int(v):
    if v is None:
        return None
    try:
        return int(float(v))
    except Exception:
        return None


def _coerce_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _sanitize_company(raw: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in (raw or {}).items():
        if k not in COMPANY_FIELDS or v is None:
            continue
        if k in ("employees", "fiscal_year"):
            v = _coerce_int(v)
        elif k in ("revenue_usd", "total_assets_usd"):
            v = _coerce_float(v)
        elif k == "csrd_applicable":
            v = _coerce_bool(v)
        if v is not None and v != "":
            out[k] = v
    return out


def _sanitize_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
    int_fields = {"year", "employee_count", "incident_count"}
    out: Dict[str, Any] = {}
    for k, v in (raw or {}).items():
        if k not in METRIC_FIELDS or v is None:
            continue
        if k in int_fields:
            v = _coerce_int(v)
        elif k in ("sector", "country"):
            v = str(v) if v else None
        else:
            v = _coerce_float(v)
        if v is not None and v != "":
            out[k] = v
    return out


@router.post(
    "/disclosure",
    response_model=DisclosureUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_disclosure(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(db_session),
) -> DisclosureUploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "PDF file required")

    raw = await file.read()
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"PDF exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit",
        )

    try:
        text, page_count = extract_pdf_text(raw)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"PDF parse failed: {exc}") from exc

    if len(text.strip()) < 200:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Could not extract enough text from the PDF (scanned image? try an OCR-ready version).",
        )

    llm = get_llm_client()
    if not llm.enabled:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "LLM disabled — set ANTHROPIC_API_KEY to enable disclosure extraction.",
        )

    extracted = await extract_from_text(text)
    company_raw = extracted.get("company") or {}
    metrics_raw = extracted.get("metrics") or {}

    company_data = _sanitize_company(company_raw)
    metrics_data = _sanitize_metrics(metrics_raw)

    # Fallbacks
    if not company_data.get("company_name"):
        stem = (file.filename or "Unknown Entity").rsplit(".", 1)[0]
        company_data["company_name"] = stem[:255]

    year = metrics_data.get("year") or company_data.get("fiscal_year")
    if not year:
        year = datetime.utcnow().year - 1
    metrics_data["year"] = int(year)

    # Upsert company by case-insensitive name match
    lookup = (
        await db.execute(
            select(Company).where(
                func.lower(Company.company_name) == company_data["company_name"].lower()
            )
        )
    ).scalars().first()

    created = lookup is None
    if lookup is None:
        next_id = (
            await db.execute(select(func.coalesce(func.max(Company.company_id), 0)))
        ).scalar_one() + 1
        company_data["company_id"] = next_id
        db.add(Company(**company_data))
        company_id = next_id
    else:
        company_id = lookup.company_id
        for k, v in company_data.items():
            if k == "company_id" or v is None:
                continue
            setattr(lookup, k, v)

    await db.flush()

    metrics_data["company_id"] = company_id
    if not metrics_data.get("sector"):
        metrics_data["sector"] = company_data.get("sector")
    if not metrics_data.get("country"):
        metrics_data["country"] = company_data.get("country")

    existing_metric = await db.get(ESGMetric, (company_id, metrics_data["year"]))
    if existing_metric is None:
        db.add(ESGMetric(**metrics_data))
    else:
        for k, v in metrics_data.items():
            if k in ("company_id", "year") or v is None:
                continue
            setattr(existing_metric, k, v)

    missing = sorted(
        [
            k
            for k in METRIC_FIELDS
            if k not in ("year", "sector", "country") and metrics_data.get(k) is None
        ]
    )

    db.add(
        AuditLog(
            request_id=getattr(request.state, "request_id", "") or "",
            method=request.method,
            path=request.url.path,
            status_code=201,
            event_type="disclosure_upload",
            user_id=request.headers.get("x-user-id"),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            payload={
                "company_id": company_id,
                "year": metrics_data["year"],
                "filename": file.filename,
                "page_count": page_count,
                "created": created,
                "missing_metrics": missing,
                "extraction_notes": extracted.get("extraction_notes"),
                "model": llm.model,
            },
        )
    )

    await db.commit()

    return DisclosureUploadResponse(
        company_id=company_id,
        company_name=company_data["company_name"],
        year=metrics_data["year"],
        filename=file.filename or "",
        page_count=page_count,
        text_chars=len(text),
        created=created,
        extracted_company=company_data,
        extracted_metrics=metrics_data,
        missing_metrics=missing,
        extraction_notes=extracted.get("extraction_notes"),
        used_llm=True,
        model=llm.model,
    )
