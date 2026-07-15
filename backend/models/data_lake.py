from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MappingDecision:
    source_column: str
    canonical_column: str
    confidence: float
    origin: str = "automatic"
    confirmed: bool = False


@dataclass
class MappingProfile:
    profile_id: str
    dataset_type: str
    source_name: str
    sheet_name: str
    decisions: list[MappingDecision] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(
            timespec="seconds"
        )
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now().isoformat(
            timespec="seconds"
        )
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decisions"] = [
            asdict(item)
            for item in self.decisions
        ]
        return payload


@dataclass
class DatasetVersion:
    version_id: str
    dataset_type: str
    version_label: str
    source_name: str
    sheet_name: str
    storage_file: str
    status: str
    rows: int
    columns: int
    quality_score: float
    mapping_score: float
    health_score: float
    company: str
    currency: str
    period_label: str

    # Optional enterprise dimensions.
    fiscal_year: int | None = None
    comparison_label: str = ""

    warnings: list[str] = field(
        default_factory=list
    )
    mapped_columns: dict[str, str] = field(
        default_factory=dict
    )
    unmapped_columns: list[str] = field(
        default_factory=list
    )
    synthesized_columns: list[str] = field(
        default_factory=list
    )
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(
            timespec="seconds"
        )
    )
    activated_at: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def version(self) -> str:
        """
        Backward-compatible alias used by older V2 UI components.

        New code should use `version_label`.
        """

        return self.version_label

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
