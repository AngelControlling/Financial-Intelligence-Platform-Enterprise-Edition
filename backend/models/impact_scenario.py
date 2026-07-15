from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImpactScenario:
    scenario_name: str
    revenue_growth_pct: float
    margin_improvement_pp: float
    cost_reduction_pct: float
    volume_growth_pct: float


@dataclass(frozen=True)
class ImpactSimulationResult:
    scenario_name: str
    base_revenue: float
    base_cost: float
    base_gp: float
    base_margin: float
    projected_revenue: float
    projected_cost: float
    projected_gp: float
    projected_margin: float
    revenue_impact: float
    cost_impact: float
    gp_impact: float
    margin_impact_pp: float
