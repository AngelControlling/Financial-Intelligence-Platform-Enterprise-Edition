from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RootCauseNode:
    level: int
    dimension: str
    value: str
    variance: float
    variance_pct: float
    contribution_pct: float
    actual: float
    target: float
    children: list["RootCauseNode"] = field(
        default_factory=list
    )


@dataclass(frozen=True)
class RootCauseResult:
    metric: str
    total_variance: float
    total_actual: float
    total_target: float
    dominant_path: list[RootCauseNode]
    top_causes: list[RootCauseNode]
    explained_variance_pct: float
