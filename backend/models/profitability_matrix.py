from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ProfitabilityMatrixResult:
    dimension: str
    dataframe: pd.DataFrame
    total_revenue: float
    total_gp: float
    overall_margin: float
    top_5_revenue_concentration: float
    top_5_gp_concentration: float
    loss_making_count: int
    low_margin_count: int
    high_value_count: int
    margin_threshold: float
    revenue_threshold: float
