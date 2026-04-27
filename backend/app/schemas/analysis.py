from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RuleResultOut(BaseModel):
    rule_id: str
    category: str
    severity: str
    triggered: bool
    message: str
    citations: List[str] = []


class AgentStepOut(BaseModel):
    agent: str
    status: str
    duration_ms: float
    output_summary: Dict[str, Any] = {}
    error: Optional[str] = None


class AnalysisCitation(BaseModel):
    index: int
    chunk_id: str
    source: str
    score: float
    snippet: str


class FullAnalysisRequest(BaseModel):
    company_id: int = Field(..., ge=1)
    query: Optional[str] = Field(default=None, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    include_rag: bool = True
    include_report: bool = True


class FullAnalysisResponse(BaseModel):
    company_id: int
    company: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    rule_results: List[RuleResultOut] = []
    rule_summary: Dict[str, int] = {}
    citations: List[AnalysisCitation] = []
    report: Optional[str] = None
    trace: List[AgentStepOut] = []
    errors: List[str] = []
    request_id: Optional[str] = None
