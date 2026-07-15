from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PnLLine:
    name: str
    actual: float | None
    budget: float | None
    variance: float | None
    variance_pct: float | None
    favorable: bool | None


@dataclass(frozen=True)
class FullPnLResult:
    lines: list[PnLLine]
    actual_gp_margin: float | None
    budget_gp_margin: float | None
    actual_operating_margin: float | None
    budget_operating_margin: float | None
    actual_cost_per_employee: float | None
    budget_cost_per_employee: float | None
    actual_headcount: float | None
    budget_headcount: float | None
    data_coverage_pct: float
