from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutiveBrief:
    title: str
    period_label: str
    comparison_label: str
    headline: str
    financial_summary: str
    operational_summary: str
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    kpis: dict[str, Any] = field(default_factory=dict)
