from pydantic import BaseModel, Field

from app.schemas.company import CompanyCreate
from app.schemas.esg_metrics import ESGMetricCreate


class KPIUploadRequest(BaseModel):
    company: CompanyCreate
    metrics: ESGMetricCreate = Field(..., description="Metrics row keyed by year")


class KPIUploadResponse(BaseModel):
    company_id: int
    created: bool
    metrics_year: int
