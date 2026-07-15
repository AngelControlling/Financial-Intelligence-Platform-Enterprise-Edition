from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveAlert:
    alert_id: str
    severity: str
    category: str
    title: str
    metric: str
    message: str
    recommended_action: str
    dimension: str = ""
    dimension_value: str = ""
    actual_value: float = 0.0
    target_value: float = 0.0
    variance_value: float = 0.0
    variance_pct: float = 0.0
