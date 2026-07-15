from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class VarianceBridgeResult:
    metric: str
    dimension: str
    actual_total: float
    target_total: float
    variance_total: float
    variance_pct: float
    contributors: pd.DataFrame
    positive_contribution: float
    negative_contribution: float
    concentration_pct: float
