from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ControllerNarrative:
    executive_summary: str
    what_happened: str
    why_it_happened: str
    business_risk: str
    recommended_actions: list[str] = field(
        default_factory=list
    )
    no_action_outlook: str = ""
    confidence_score: float = 0.0
    management_priority: str = "Medium"
