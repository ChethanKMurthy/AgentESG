from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analysis_agent import AnalysisAgent
from app.agents.audit_agent import AuditAgent
from app.agents.base import AgentContext
from app.agents.data_agent import DataAgent
from app.agents.report_agent import ReportAgent
from app.agents.retrieval_agent import RetrievalAgent


class Orchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run(
        self,
        company_id: int,
        query: Optional[str] = None,
        top_k: int = 5,
        include_rag: bool = True,
        include_report: bool = True,
        request_id: Optional[str] = None,
    ) -> AgentContext:
        ctx = AgentContext(
            company_id=company_id,
            query=query,
            top_k=top_k,
            include_rag=include_rag,
            include_report=include_report,
            request_id=request_id,
        )

        await DataAgent(self.db).run(ctx)
        if ctx.company is None:
            await AuditAgent(self.db).run(ctx)
            return ctx

        await RetrievalAgent().run(ctx)
        await AnalysisAgent().run(ctx)
        await ReportAgent().run(ctx)
        await AuditAgent(self.db).run(ctx)
        return ctx
