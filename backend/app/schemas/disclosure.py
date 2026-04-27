from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DisclosureUploadResponse(BaseModel):
    company_id: int
    company_name: str
    year: int
    filename: str
    page_count: int
    text_chars: int
    created: bool
    extracted_company: Dict[str, Any]
    extracted_metrics: Dict[str, Any]
    missing_metrics: List[str]
    extraction_notes: Optional[str] = None
    used_llm: bool
    model: Optional[str] = None
