from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class DatasetDescriptor:
    dataset_type: str
    version: str
    status: str = "missing"
    company: str = ""
    currency: str = "USD"
    fiscal_year: int | None = None
    period_label: str = ""
    rows: int = 0
    quality_score: float = 0.0
    mapping_score: float = 0.0
    health_score: float = 0.0
    loaded_at: datetime | None = None
    activated_at: datetime | None = None
    source_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    @property
    def is_active(self) -> bool: return self.status == "active"
    @property
    def is_ready(self) -> bool: return self.status in {"validated", "active"}
