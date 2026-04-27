from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ESGMetric(Base):
    __tablename__ = "esg_metrics"

    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.company_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    sector: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    country: Mapped[Optional[str]] = mapped_column(String(128), index=True)

    scope_1_emissions_tco2e: Mapped[Optional[float]] = mapped_column(Float)
    scope_2_emissions_tco2e: Mapped[Optional[float]] = mapped_column(Float)
    scope_3_emissions_tco2e: Mapped[Optional[float]] = mapped_column(Float)
    energy_consumption_mwh: Mapped[Optional[float]] = mapped_column(Float)
    renewable_energy_percent: Mapped[Optional[float]] = mapped_column(Float)
    water_usage_m3: Mapped[Optional[float]] = mapped_column(Float)
    waste_generated_tons: Mapped[Optional[float]] = mapped_column(Float)
    waste_recycled_percent: Mapped[Optional[float]] = mapped_column(Float)
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    female_employee_ratio: Mapped[Optional[float]] = mapped_column(Float)
    board_independence_percent: Mapped[Optional[float]] = mapped_column(Float)
    incident_count: Mapped[Optional[int]] = mapped_column(Integer)
    esg_score: Mapped[Optional[float]] = mapped_column(Float, index=True)

    company: Mapped["Company"] = relationship("Company", back_populates="metrics")
