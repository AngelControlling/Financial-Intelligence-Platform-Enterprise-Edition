import pandas as pd

from engines.working_capital_intelligence_engine import (
    WorkingCapitalIntelligenceEngine,
)


def test_ytd_invoice_activity_produces_realistic_days() -> None:
    as_of = pd.Timestamp("2026-07-15")
    dataframe = pd.DataFrame(
        {
            "document_type": ["AR", "AR", "AP"],
            "counterparty": ["A", "B", "S"],
            "original_amount": [1000.0, 1000.0, 1500.0],
            "open_amount": [500.0, 400.0, 600.0],
            "invoice_date": [
                pd.Timestamp("2026-01-15"),
                pd.Timestamp("2026-06-01"),
                pd.Timestamp("2026-03-01"),
            ],
            "days_overdue": [100, 0, 45],
            "is_overdue": [True, False, True],
            "aging_bucket": ["90+", "Current", "31-45"],
            "as_of_date": [as_of, as_of, as_of],
        }
    )

    result = WorkingCapitalIntelligenceEngine().analyze(dataframe)

    assert round(result.dso, 1) == 88.2
    assert round(result.dpo, 1) == 78.4
    assert result.dso_method.startswith("YTD")
    assert result.collection_risk_level in {
        "Low", "Medium", "High", "Critical"
    }


def test_risk_does_not_automatically_saturate() -> None:
    dataframe = pd.DataFrame(
        {
            "document_type": ["AR", "AR"],
            "counterparty": ["A", "B"],
            "original_amount": [1000.0, 1000.0],
            "open_amount": [800.0, 200.0],
            "invoice_date": [
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2026-06-01"),
            ],
            "days_overdue": [60, 10],
            "is_overdue": [True, True],
            "aging_bucket": ["46-60", "0-30"],
            "as_of_date": [
                pd.Timestamp("2026-07-15"),
                pd.Timestamp("2026-07-15"),
            ],
        }
    )

    result = WorkingCapitalIntelligenceEngine().analyze(dataframe)
    assert result.collection_risk_score < 100
