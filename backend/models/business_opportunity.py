from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessOpportunity:
    opportunity_id: str
    category: str
    priority: str
    dimension: str
    value: str
    title: str
    rationale: str
    recommended_action: str
    revenue: float
    gross_profit: float
    margin: float
    shipments: float
    revenue_share: float
    estimated_revenue_upside: float
    estimated_gp_upside: float
    confidence_score: float
