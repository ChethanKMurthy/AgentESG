from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.llm import get_llm_client
from app.roadmap.generator import RoadmapItem

logger = get_logger(__name__)


NARRATOR_SYSTEM_PROMPT = """You are Codename: Verdant ("V"), explaining why a specific ESG roadmap item \
belongs on this company's plan. Write with the restraint of a senior compliance partner.

Rules:
- Output 2-3 sentences, plain prose. No headers, no bullets, no markdown, no emoji.
- Reference the numeric evidence explicitly when available.
- Mention the framework (CSRD / ESRS E1 / ESRS G1 / GHG Protocol / SBTi) when it materially applies.
- Do NOT invent numbers, articles, or thresholds. If evidence is missing, say so.
- No sign-off, no flourish — just the explanation.
"""


def _item_user_prompt(
    item: RoadmapItem,
    company: Optional[Dict[str, Any]],
    metrics: Optional[Dict[str, Any]],
) -> str:
    drivers_lines = []
    for d in item.explanation.drivers:
        parts = [
            f"- kind={d.kind}",
            f"id={d.identifier}",
            f"severity={d.severity}",
            f"weight={d.weight}",
        ]
        if d.metric:
            parts.append(f"metric={d.metric}")
        if d.current is not None:
            parts.append(f"current={d.current}")
        if d.target is not None:
            parts.append(f"target={d.target}")
        parts.append(f"desc={d.description}")
        drivers_lines.append(" ".join(parts))
    drivers_block = "\n".join(drivers_lines) or "(none)"

    company_json = json.dumps(company or {}, default=str, indent=2)
    metrics_json = json.dumps(metrics or {}, default=str, indent=2)

    return (
        f"COMPANY:\n{company_json}\n\n"
        f"LATEST METRICS:\n{metrics_json}\n\n"
        f"ROADMAP ITEM:\n"
        f"- title: {item.title}\n"
        f"- category: {item.category}\n"
        f"- severity: {item.severity}\n"
        f"- horizon: {item.horizon}\n"
        f"- priority: {item.priority}\n"
        f"- evidence: {item.evidence}\n\n"
        f"DRIVERS:\n{drivers_block}\n\n"
        "Explain in 2-3 sentences why this item is on this company's roadmap now."
    )


async def narrate_items(
    items: List[RoadmapItem],
    company: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    concurrency: int = 4,
) -> None:
    """Mutate items in place, setting item.explanation.narrative when LLM enabled."""
    llm = get_llm_client()
    if not llm.enabled or not items:
        return
    sem = asyncio.Semaphore(concurrency)

    async def one(item: RoadmapItem) -> None:
        async with sem:
            try:
                text = await llm.complete(
                    NARRATOR_SYSTEM_PROMPT,
                    _item_user_prompt(item, company, metrics),
                    max_tokens=220,
                )
                item.explanation.narrative = text.strip()
            except Exception as exc:
                logger.warning("narrate_failed", item=item.id, error=str(exc))
                item.explanation.narrative = None

    await asyncio.gather(*(one(i) for i in items))
