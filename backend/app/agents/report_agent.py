from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.agents.base import AgentContext, BaseAgent
from app.llm import get_llm_client
from app.llm.prompts import (
    REPORT_SYSTEM_PROMPT,
    REPORT_USER_TEMPLATE,
    format_context,
)


class ReportAgent(BaseAgent):
    name = "report_agent"

    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        if not ctx.include_report:
            return {"skipped": True}

        llm = get_llm_client()

        triggered = [r for r in ctx.rule_results if r.get("triggered")]
        findings_json = json.dumps(triggered, indent=2)
        company_json = json.dumps(ctx.company or {}, indent=2, default=str)
        metrics_json = json.dumps(ctx.latest_metrics or {}, indent=2, default=str)

        context_items = [
            {"index": r["index"], "source": r["source"], "text": r["text"]}
            for r in ctx.retrieved
        ]
        context_block = format_context(context_items)

        user_prompt = REPORT_USER_TEMPLATE.format(
            query=ctx.query or "(no user question; produce a full compliance brief)",
            company=company_json,
            metrics=metrics_json,
            findings=findings_json,
            context=context_block,
        )

        ctx.report = await llm.complete(REPORT_SYSTEM_PROMPT, user_prompt)
        return {
            "used_llm": llm.enabled,
            "triggered_findings": len(triggered),
            "context_items": len(context_items),
        }
