from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CompareRequest(BaseModel):
    company_id: int = Field(..., ge=1)
    year: Optional[int] = None
    peer_scope: str = Field(default="sector", description="sector|industry|country|sector_country|industry_country")


class PeerStats(BaseModel):
    n: int = 0
    min: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    p25: Optional[float] = None
    p75: Optional[float] = None
    max: Optional[float] = None
    stdev: Optional[float] = None


class BenchmarkStatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    metric: str
    direction: str
    value: Optional[float] = None
    peer_stats: PeerStats
    percentile_rank: Optional[float] = None
    delta_vs_median: Optional[float] = None
    status: str


class PillarScores(BaseModel):
    environment: Optional[float] = None
    social: Optional[float] = None
    governance: Optional[float] = None


class CompareResponse(BaseModel):
    company_id: int
    year: Optional[int] = None
    peer_scope: str
    peer_count: int
    benchmarks: Dict[str, BenchmarkStatOut] = {}
    composite_score: Optional[float] = None
    composite_percentile_rank: Optional[float] = None
    pillar_scores: PillarScores = PillarScores()
    derived_composite: Optional[float] = None


class RoadmapRequest(BaseModel):
    company_id: int = Field(..., ge=1)
    year: Optional[int] = None
    horizon_months: int = Field(default=12, ge=1, le=36)
    peer_scope: str = "sector"
    include_benchmark: bool = True
    include_narrative: bool = True


class GapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    category: str
    metric: Optional[str] = None
    severity: str
    current: Optional[float] = None
    target: Optional[float] = None
    evidence: str
    citations: List[str] = []
    source: str


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    kind: str
    identifier: str
    severity: str
    weight: float
    description: str
    metric: Optional[str] = None
    current: Optional[float] = None
    target: Optional[float] = None
    citations: List[str] = []


class ExplanationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    drivers: List[DriverOut] = []
    priority_factors: Dict[str, Any] = {}
    horizon_rationale: str = ""
    methodology: str = ""
    narrative: Optional[str] = None


class RoadmapItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    description: str
    category: str
    severity: str
    priority: int
    horizon: str
    actions: List[str] = []
    kpis: List[str] = []
    evidence: str = ""
    citations: List[str] = []
    gap_ids: List[str] = []
    confidence: str = "medium"
    explanation: ExplanationOut = ExplanationOut()


class RoadmapResponse(BaseModel):
    company_id: int
    year: Optional[int] = None
    horizon_months: int
    gaps: List[GapOut] = []
    items: List[RoadmapItemOut] = []
    summary: Dict[str, int] = {}
