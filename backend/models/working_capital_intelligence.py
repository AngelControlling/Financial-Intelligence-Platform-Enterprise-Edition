from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class WorkingCapitalIntelligenceResult:
    total_ar: float
    total_ap: float
    net_working_capital: float
    overdue_ar: float
    overdue_ap: float
    overdue_ar_pct: float
    overdue_ap_pct: float
    ar_90_plus: float
    ap_90_plus: float
    dso: float | None
    dpo: float | None
    dso_method: str
    dpo_method: str
    collection_risk_score: float
    collection_risk_level: str
    payment_pressure_score: float
    payment_pressure_level: str
    top_5_ar_concentration: float
    top_5_ap_concentration: float
    top_overdue_ar: pd.DataFrame
    top_overdue_ap: pd.DataFrame
    bucket_summary: pd.DataFrame
    data_quality_note: str
