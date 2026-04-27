from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, BaseAgent
from app.models.audit import AuditLog


class AuditAgent(BaseAgent):
    name = "audit_agent"

    def __init__(self, db: AsyncSession, path: str = "/api/analysis/full") -> None:
        self.db = db
        self.path = path

    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        records = 0
        for step in ctx.trace:
            self.db.add(
                AuditLog(
                    request_id=ctx.request_id or "",
                    method="POST",
                    path=self.path,
                    status_code=200 if step["status"] == "ok" else 500,
                    latency_ms=step.get("duration_ms"),
                    event_type=f"agent_{step['agent']}",
                    payload={
                        "company_id": ctx.company_id,
                        "summary": step.get("output_summary"),
                        "error": step.get("error"),
                    },
                )
            )
            records += 1

        self.db.add(
            AuditLog(
                request_id=ctx.request_id or "",
                method="POST",
                path=self.path,
                status_code=200 if not ctx.errors else 500,
                event_type="analysis_full",
                payload={
                    "company_id": ctx.company_id,
                    "query": ctx.query,
                    "rule_summary": ctx.rule_summary,
                    "retrieved": len(ctx.retrieved),
                    "errors": ctx.errors,
                },
            )
        )
        records += 1

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return {"audit_records": records}
