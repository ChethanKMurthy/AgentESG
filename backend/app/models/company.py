from typing import List, Optional

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    company_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    eu_member_state: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    region: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    sector: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    subsector: Mapped[Optional[str]] = mapped_column(String(128))
    industry: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    revenue_usd: Mapped[Optional[float]] = mapped_column(Float)
    total_assets_usd: Mapped[Optional[float]] = mapped_column(Float)
    employees: Mapped[Optional[int]] = mapped_column(Integer)
    entity_type: Mapped[Optional[str]] = mapped_column(String(64))
    listing_status: Mapped[Optional[str]] = mapped_column(String(64))
    stock_symbol: Mapped[Optional[str]] = mapped_column(String(32))
    fiscal_year: Mapped[Optional[int]] = mapped_column(Integer)
    currency: Mapped[Optional[str]] = mapped_column(String(16))
    company_size_band: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    csrd_applicable: Mapped[Optional[bool]] = mapped_column(Boolean, index=True)

    metrics: Mapped[List["ESGMetric"]] = relationship(
        "ESGMetric",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
