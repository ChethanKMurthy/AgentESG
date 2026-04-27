from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.rule_engine.csrd_rules import CSRD_RULES
from app.rule_engine.types import Rule, RuleResult

logger = get_logger(__name__)


class RuleEvaluator:
    def __init__(self, rules: Optional[List[Rule]] = None) -> None:
        self.rules: List[Rule] = rules if rules is not None else list(CSRD_RULES)

    def evaluate(
        self,
        company: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
    ) -> List[RuleResult]:
        out: List[RuleResult] = []
        for rule in self.rules:
            try:
                triggered = bool(rule.when(company, metrics))
                msg = rule.message(company, metrics) if triggered else rule.description
            except Exception as exc:
                logger.warning("rule_eval_failed", rule=rule.id, error=str(exc))
                triggered, msg = False, f"evaluation error: {exc}"
            out.append(
                RuleResult(
                    rule_id=rule.id,
                    category=rule.category,
                    severity=rule.severity,
                    triggered=triggered,
                    message=msg,
                    citations=list(rule.citations),
                )
            )
        return out

    @staticmethod
    def summarize(results: List[RuleResult]) -> Dict[str, int]:
        sev_counts: Dict[str, int] = {}
        triggered = 0
        for r in results:
            if r.triggered:
                triggered += 1
                sev_counts[r.severity] = sev_counts.get(r.severity, 0) + 1
        return {"total": len(results), "triggered": triggered, **sev_counts}
