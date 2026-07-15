from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CFORadarSignal:
    category: str
    score: float
    level: str
    headline: str
    explanation: str
    recommended_action: str


@dataclass(frozen=True)
class CFORadarResult:
    overall_score: float
    overall_level: str
    signals: list[CFORadarSignal]
    top_risk: str
    risk_count: int
    critical_count: int
