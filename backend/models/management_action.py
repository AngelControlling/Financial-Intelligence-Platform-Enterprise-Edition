from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

@dataclass
class ManagementAction:
    title: str
    description: str
    action_type: str
    priority: str
    owner: str = "Unassigned"
    status: str = "Open"
    due_date: str = ""
    period_label: str = ""
    source_alert_id: str = ""
    source_dimension: str = ""
    source_value: str = ""
    expected_impact: float = 0.0
    impact_metric: str = "Gross Profit"
    action_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
