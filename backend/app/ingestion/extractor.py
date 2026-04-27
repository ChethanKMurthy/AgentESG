from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from app.core.logging import get_logger
from app.llm import get_llm_client

logger = get_logger(__name__)


EXTRACTION_SYSTEM_PROMPT = """You are an ESG disclosure parsing agent.
Extract structured ESG and company facts from an annual or sustainability disclosure report.

Output STRICT JSON only. No prose, no code fences, no commentary before or after the JSON.

Rules:
- If a field is not present or cannot be confidently inferred, use null. DO NOT invent values.
- Numbers must be numeric (not strings).
- Apply unit conversions so the value matches the field unit:
  * emissions: tonnes CO2-equivalent (tCO2e)
  * energy: megawatt-hours (MWh)
  * water: cubic metres (m3)
  * waste: tonnes
- female_employee_ratio: decimal 0 to 1.
- Percent fields (renewable_energy_percent, waste_recycled_percent, board_independence_percent): 0 to 100.
- year: fiscal reporting year. If a range is disclosed, pick the latest year.
- csrd_applicable: true only if the report explicitly states CSRD applicability.

Schema (use these keys exactly, do not add others):

{
  "company": {
    "company_name": "string|null",
    "country": "string|null",
    "eu_member_state": "string|null",
    "region": "string|null",
    "sector": "string|null",
    "industry": "string|null",
    "entity_type": "string|null",
    "listing_status": "string|null",
    "company_size_band": "string|null",
    "fiscal_year": "integer|null",
    "currency": "string|null",
    "revenue_usd": "number|null",
    "total_assets_usd": "number|null",
    "employees": "integer|null",
    "csrd_applicable": "boolean|null"
  },
  "metrics": {
    "year": "integer",
    "scope_1_emissions_tco2e": "number|null",
    "scope_2_emissions_tco2e": "number|null",
    "scope_3_emissions_tco2e": "number|null",
    "energy_consumption_mwh": "number|null",
    "renewable_energy_percent": "number|null",
    "water_usage_m3": "number|null",
    "waste_generated_tons": "number|null",
    "waste_recycled_percent": "number|null",
    "employee_count": "integer|null",
    "female_employee_ratio": "number|null",
    "board_independence_percent": "number|null",
    "incident_count": "integer|null",
    "esg_score": "number|null"
  },
  "extraction_notes": "string, <= 240 chars, what was ambiguous or inferred"
}
"""


def _parse_json(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```\s*$", "", t)
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


async def extract_from_text(text: str) -> Dict[str, Any]:
    llm = get_llm_client()
    if not llm.enabled:
        return {
            "company": {},
            "metrics": {"year": None},
            "extraction_notes": "LLM disabled — set ANTHROPIC_API_KEY to enable extraction.",
            "_raw": "",
        }

    user = f"REPORT TEXT (may be truncated):\n\n{text}"
    raw = await llm.complete(
        EXTRACTION_SYSTEM_PROMPT,
        user,
        max_tokens=4096,
    )
    parsed = _parse_json(raw)
    if parsed is None:
        logger.warning("disclosure_extract_parse_failed", preview=raw[:300])
        return {
            "company": {},
            "metrics": {"year": None},
            "extraction_notes": "parse_failed",
            "_raw": raw[:1000],
        }
    parsed.setdefault("company", {})
    parsed.setdefault("metrics", {})
    parsed.setdefault("extraction_notes", "")
    return parsed
