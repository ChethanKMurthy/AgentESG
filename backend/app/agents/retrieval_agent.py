from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.base import AgentContext, BaseAgent
from app.rag import get_rag_service


class RetrievalAgent(BaseAgent):
    name = "retrieval_agent"

    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        if not ctx.include_rag:
            return {"skipped": True}
        rag = get_rag_service()
        query_text = ctx.query or self._default_query(ctx)
        hits = await rag.query(query_text, top_k=ctx.top_k)
        ctx.retrieved = [
            {
                "index": i + 1,
                "chunk_id": h.chunk.chunk_id,
                "source": h.chunk.source,
                "score": float(h.score),
                "text": h.chunk.text,
            }
            for i, h in enumerate(hits)
        ]
        return {"query": query_text, "retrieved": len(ctx.retrieved)}

    @staticmethod
    def _default_query(ctx: AgentContext) -> str:
        c = ctx.company or {}
        parts = [
            "ESG compliance and CSRD applicability",
            f"sector {c.get('sector')}" if c.get("sector") else "",
            f"country {c.get('country')}" if c.get("country") else "",
        ]
        return " ".join(p for p in parts if p).strip() or "ESG compliance overview"
