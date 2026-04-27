from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    company_name: str = Field(..., max_length=255)
    country: Optional[str] = None
    eu_member_state: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    industry: Optional[str] = None
    revenue_usd: Optional[float] = None
    total_assets_usd: Optional[float] = None
    employees: Optional[int] = None
    entity_type: Optional[str] = None
    listing_status: Optional[str] = None
    stock_symbol: Optional[str] = None
    fiscal_year: Optional[int] = None
    currency: Optional[str] = None
    company_size_band: Optional[str] = None
    csrd_applicable: Optional[bool] = None


class CompanyCreate(CompanyBase):
    company_id: Optional[int] = None


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    country: Optional[str] = None
    eu_member_state: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    industry: Optional[str] = None
    revenue_usd: Optional[float] = None
    total_assets_usd: Optional[float] = None
    employees: Optional[int] = None
    entity_type: Optional[str] = None
    listing_status: Optional[str] = None
    stock_symbol: Optional[str] = None
    fiscal_year: Optional[int] = None
    currency: Optional[str] = None
    company_size_band: Optional[str] = None
    csrd_applicable: Optional[bool] = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    company_id: int


class CompanyListResponse(BaseModel):
    total: int
    items: List[CompanyRead]
    limit: int
    offset: int
