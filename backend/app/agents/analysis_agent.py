from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from app.agents.base import AgentContext, BaseAgent
from app.rule_engine import RuleEvaluator


class AnalysisAgent(BaseAgent):
    name = "analysis_agent"

    def __init__(self) -> None:
        self.evaluator = RuleEvaluator()

    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        if not ctx.company:
            raise RuntimeError("company not loaded")
        results = self.evaluator.evaluate(ctx.company, ctx.latest_metrics)
        ctx.rule_results = [asdict(r) for r in results]
        ctx.rule_summary = RuleEvaluator.summarize(results)
        return {
            "rules_evaluated": len(results),
            "triggered": ctx.rule_summary.get("triggered", 0),
        }
