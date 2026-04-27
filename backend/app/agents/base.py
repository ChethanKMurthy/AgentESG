from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentContext:
    company_id: int
    query: Optional[str] = None
    top_k: int = 5
    include_rag: bool = True
    include_report: bool = True
    request_id: Optional[str] = None

    company: Optional[Dict[str, Any]] = None
    latest_metrics: Optional[Dict[str, Any]] = None
    retrieved: List[Dict[str, Any]] = field(default_factory=list)
    rule_results: List[Dict[str, Any]] = field(default_factory=list)
    rule_summary: Dict[str, int] = field(default_factory=dict)
    report: Optional[str] = None

    trace: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    name: str = "base"

    async def run(self, ctx: AgentContext) -> None:
        t0 = time.perf_counter()
        status = "ok"
        error: Optional[str] = None
        summary: Dict[str, Any] = {}
        try:
            summary = await self._execute(ctx) or {}
        except Exception as exc:
            status = "error"
            error = f"{type(exc).__name__}: {exc}"
            ctx.errors.append(f"{self.name}: {error}")
            logger.warning("agent_failed", agent=self.name, error=error)
        duration_ms = (time.perf_counter() - t0) * 1000
        ctx.trace.append(
            {
                "agent": self.name,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "output_summary": summary,
                "error": error,
            }
        )

    @abstractmethod
    async def _execute(self, ctx: AgentContext) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
