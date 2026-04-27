from typing import List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    index: int
    chunk_id: str
    source: str
    score: float
    snippet: str


class CopilotQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    rerank: bool = True
    company_id: Optional[int] = None


class CopilotQueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    request_id: Optional[str] = None
    model: Optional[str] = None
    retrieved: int
    used_llm: bool
    company_id: Optional[int] = None


class BriefingFinding(BaseModel):
    severity: str
    text: str
    citation_indexes: List[int] = []


class CopilotBriefResponse(BaseModel):
    headline: str
    verdict: str
    summary: str
    findings: List[BriefingFinding] = []
    confidence: str = "medium"
    confidence_reason: Optional[str] = None
    citations: List[Citation] = []
    company_id: Optional[int] = None
    model: Optional[str] = None
    used_llm: bool = False


class IngestRequest(BaseModel):
    root: Optional[str] = Field(
        default=None,
        description="Absolute path; defaults to DOCUMENTS_PATH",
    )


class IngestResponse(BaseModel):
    documents: int
    chunks: int


class RAGStats(BaseModel):
    ready: bool = False
    documents: Optional[int] = None
    chunks: Optional[int] = None
    embedding_model: Optional[str] = None
    dim: Optional[int] = None
