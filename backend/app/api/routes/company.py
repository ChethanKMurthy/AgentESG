from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyRead,
    CompanyUpdate,
)
from app.services.company_service import CompanyService

router = APIRouter()


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    country: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    csrd_applicable: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Name contains"),
    db: AsyncSession = Depends(db_session),
) -> CompanyListResponse:
    service = CompanyService(db)
    total, items = await service.list(
        limit=limit,
        offset=offset,
        country=country,
        sector=sector,
        csrd_applicable=csrd_applicable,
        search=search,
    )
    return CompanyListResponse(
        total=total,
        items=[CompanyRead.model_validate(c) for c in items],
        limit=limit,
        offset=offset,
    )


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(db_session),
) -> CompanyRead:
    service = CompanyService(db)
    company = await service.get(company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return CompanyRead.model_validate(company)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreate,
    db: AsyncSession = Depends(db_session),
) -> CompanyRead:
    service = CompanyService(db)
    try:
        company = await service.create(payload)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    return CompanyRead.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int,
    payload: CompanyUpdate,
    db: AsyncSession = Depends(db_session),
) -> CompanyRead:
    service = CompanyService(db)
    company = await service.update(company_id, payload)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return CompanyRead.model_validate(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(db_session),
) -> None:
    service = CompanyService(db)
    deleted = await service.delete(company_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
