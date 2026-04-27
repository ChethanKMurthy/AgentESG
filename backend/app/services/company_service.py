from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        country: Optional[str] = None,
        sector: Optional[str] = None,
        csrd_applicable: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[int, Sequence[Company]]:
        base = select(Company)
        if country:
            base = base.where(Company.country == country)
        if sector:
            base = base.where(Company.sector == sector)
        if csrd_applicable is not None:
            base = base.where(Company.csrd_applicable == csrd_applicable)
        if search:
            base = base.where(Company.company_name.ilike(f"%{search}%"))

        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        rows = (
            await self.db.execute(
                base.order_by(Company.company_id).limit(limit).offset(offset)
            )
        ).scalars().all()
        return total, rows

    async def get(self, company_id: int) -> Optional[Company]:
        return await self.db.get(Company, company_id)

    async def create(self, payload: CompanyCreate) -> Company:
        company = Company(**payload.model_dump(exclude_none=True))
        self.db.add(company)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise ValueError("Company with this id already exists") from exc
        await self.db.refresh(company)
        return company

    async def update(self, company_id: int, payload: CompanyUpdate) -> Optional[Company]:
        company = await self.get(company_id)
        if not company:
            return None
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(company, k, v)
        await self.db.commit()
        await self.db.refresh(company)
        return company

    async def delete(self, company_id: int) -> bool:
        company = await self.get(company_id)
        if not company:
            return False
        await self.db.delete(company)
        await self.db.commit()
        return True
