from typing import Optional

from pydantic import BaseModel, ConfigDict


class ESGMetricBase(BaseModel):
    year: int
    sector: Optional[str] = None
    country: Optional[str] = None
    scope_1_emissions_tco2e: Optional[float] = None
    scope_2_emissions_tco2e: Optional[float] = None
    scope_3_emissions_tco2e: Optional[float] = None
    energy_consumption_mwh: Optional[float] = None
    renewable_energy_percent: Optional[float] = None
    water_usage_m3: Optional[float] = None
    waste_generated_tons: Optional[float] = None
    waste_recycled_percent: Optional[float] = None
    employee_count: Optional[int] = None
    female_employee_ratio: Optional[float] = None
    board_independence_percent: Optional[float] = None
    incident_count: Optional[int] = None
    esg_score: Optional[float] = None


class ESGMetricCreate(ESGMetricBase):
    pass


class ESGMetricRead(ESGMetricBase):
    model_config = ConfigDict(from_attributes=True)
    company_id: int
