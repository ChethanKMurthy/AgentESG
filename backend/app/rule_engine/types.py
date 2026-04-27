from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Rule:
    id: str
    category: str
    severity: str  # info | low | medium | high | critical
    description: str
    when: Callable[[Dict[str, Any], Optional[Dict[str, Any]]], bool]
    message: Callable[[Dict[str, Any], Optional[Dict[str, Any]]], str]
    citations: List[str] = field(default_factory=list)


@dataclass
class RuleResult:
    rule_id: str
    category: str
    severity: str
    triggered: bool
    message: str
    citations: List[str] = field(default_factory=list)
