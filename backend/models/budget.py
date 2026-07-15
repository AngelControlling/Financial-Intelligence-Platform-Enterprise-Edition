from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class BudgetValidationResult:
    performance: pd.DataFrame
    opex: pd.DataFrame
    personnel: pd.DataFrame
    balance_sheet: pd.DataFrame
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    completeness_score: float = 0.0
    fiscal_years: list[int] = field(default_factory=list)
    currencies: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors
