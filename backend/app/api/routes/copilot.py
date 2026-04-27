from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.data_agent import _company_to_dict, _metric_to_dict
from app.api.deps import db_session
from app.llm import get_llm_client
from app.llm.prompts import (
    BRIEFING_SYSTEM_PROMPT,
    BRIEFING_USER_TEMPLATE,
    COPILOT_SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    format_company_context,
    format_context,
)
from app.models.audit import AuditLog
from app.models.company import Company
from app.models.esg_metrics import ESGMetric
from app.rag import get_rag_service
from app.schemas.copilot import (
    BriefingFinding,
    Citation,
    CopilotBriefResponse,
    CopilotQueryRequest,
    CopilotQueryResponse,
    IngestRequest,
    IngestResponse,
    RAGStats,
)

router = APIRouter()


def _snippet(text: str, n: int = 240) -> str:
    t = " ".join(text.split())
    return t if len(t) <= n else t[:n] + "…"


async def _load_company_block(db: AsyncSession, company_id: Optional[int]) -> str:
    if company_id is None:
        return ""
    company = await db.get(Company, company_id)
    if not company:
        return ""
    row = (
        await db.execute(
            select(ESGMetric)
            .where(ESGMetric.company_id == company_id)
            .order_by(ESGMetric.year.desc())
            .limit(1)
        )
    ).scalars().first()
    return format_company_context(
        _company_to_dict(company),
        _metric_to_dict(row) if row else None,
    )


async def _retrieve(query: str, top_k: Optional[int], rerank: bool):
    rag = get_rag_service()
    hits = await rag.query(query, top_k=top_k, rerank=rerank)
    citations: List[Citation] = []
    for i, h in enumerate(hits):
        citations.append(
            Citation(
                index=i + 1,
                chunk_id=h.chunk.chunk_id,
                source=h.chunk.source,
                score=float(h.score),
                snippet=_snippet(h.chunk.text),
            )
        )
    context_items = [
        {"index": c.index, "source": c.source, "text": h.chunk.text}
        for c, h in zip(citations, hits)
    ]
    return hits, citations, context_items


@router.post("/ingest", response_model=IngestResponse)
async def ingest(payload: IngestRequest) -> IngestResponse:
    rag = get_rag_service()
    result = await rag.ingest(payload.root)
    return IngestResponse(**result)


@router.get("/stats", response_model=RAGStats)
async def stats() -> RAGStats:
    rag = get_rag_service()
    return RAGStats(**rag.stats())


@router.post("/query", response_model=CopilotQueryResponse)
async def query(
    payload: CopilotQueryRequest,
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> CopilotQueryResponse:
    llm = get_llm_client()

    hits, citations, context_items = await _retrieve(
        payload.query, payload.top_k, payload.rerank
    )
    company_block = await _load_company_block(db, payload.company_id)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=payload.query,
        context=format_context(context_items),
    )
    if company_block:
        user_prompt = f"{company_block}\n\n{user_prompt}"

    answer = await llm.complete(COPILOT_SYSTEM_PROMPT, user_prompt)

    request_id = getattr(request.state, "request_id", None)
    try:
        db.add(
            AuditLog(
                request_id=request_id or "",
                method=request.method,
                path=request.url.path,
                status_code=200,
                event_type="copilot_query",
                user_id=request.headers.get("x-user-id"),
                client_ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                payload={
                    "query": payload.query,
                    "retrieved": len(hits),
                    "top_k": payload.top_k,
                    "citations": [c.chunk_id for c in citations],
                    "company_id": payload.company_id,
                    "model": llm.model,
                    "used_llm": llm.enabled,
                },
            )
        )
        await db.commit()
    except Exception:
        await db.rollback()

    return CopilotQueryResponse(
        answer=answer,
        citations=citations,
        request_id=request_id,
        model=llm.model if llm.enabled else None,
        retrieved=len(hits),
        used_llm=llm.enabled,
        company_id=payload.company_id,
    )


@router.post("/stream")
async def stream(
    payload: CopilotQueryRequest,
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> StreamingResponse:
    llm = get_llm_client()

    hits, citations, context_items = await _retrieve(
        payload.query, payload.top_k, payload.rerank
    )
    company_block = await _load_company_block(db, payload.company_id)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=payload.query,
        context=format_context(context_items),
    )
    if company_block:
        user_prompt = f"{company_block}\n\n{user_prompt}"

    async def event_gen():
        meta = {
            "model": llm.model if llm.enabled else None,
            "used_llm": llm.enabled,
            "retrieved": len(hits),
            "company_id": payload.company_id,
        }
        yield f"event: meta\ndata: {json.dumps(meta)}\n\n"
        yield f"event: citations\ndata: {json.dumps([c.model_dump() for c in citations])}\n\n"
        try:
            async for chunk in llm.stream(COPILOT_SYSTEM_PROMPT, user_prompt):
                if not chunk:
                    continue
                yield f"event: token\ndata: {json.dumps({'delta': chunk})}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


@router.post("/brief", response_model=CopilotBriefResponse)
async def brief(
    payload: CopilotQueryRequest,
    request: Request,
    db: AsyncSession = Depends(db_session),
) -> CopilotBriefResponse:
    llm = get_llm_client()
    hits, citations, context_items = await _retrieve(
        payload.query, payload.top_k, payload.rerank
    )
    company_block = await _load_company_block(db, payload.company_id)
    user_prompt = BRIEFING_USER_TEMPLATE.format(
        question=payload.query,
        company_block=company_block or "(no company context attached)",
        context=format_context(context_items),
    )

    raw = await llm.complete(BRIEFING_SYSTEM_PROMPT, user_prompt)
    data = _extract_json(raw) or {}

    findings = []
    for f in data.get("findings", []) or []:
        try:
            findings.append(
                BriefingFinding(
                    severity=str(f.get("severity", "info")),
                    text=str(f.get("text", ""))[:300],
                    citation_indexes=[int(x) for x in (f.get("citation_indexes") or [])],
                )
            )
        except Exception:
            continue

    return CopilotBriefResponse(
        headline=str(data.get("headline") or "Briefing unavailable")[:160],
        verdict=str(data.get("verdict") or "indeterminate"),
        summary=str(data.get("summary") or raw[:320]),
        findings=findings,
        confidence=str(data.get("confidence") or "medium"),
        confidence_reason=data.get("confidence_reason"),
        citations=citations,
        company_id=payload.company_id,
        model=llm.model if llm.enabled else None,
        used_llm=llm.enabled,
    )
