import pandas as pd

from engines.working_capital_intelligence_engine import (
    WorkingCapitalIntelligenceEngine,
)


def test_working_capital_metrics() -> None:
    dataframe = pd.DataFrame(
        {
            "document_type": [
                "AR",
                "AR",
                "AP",
            ],
            "counterparty": [
                "Customer A",
                "Customer B",
                "Supplier A",
            ],
            "open_amount": [
                1000.0,
                500.0,
                800.0,
            ],
            "is_overdue": [
                True,
                False,
                True,
            ],
            "days_overdue": [
                100,
                0,
                45,
            ],
            "aging_bucket": [
                "90+",
                "Current",
                "31-45",
            ],
        }
    )

    result = (
        WorkingCapitalIntelligenceEngine()
        .analyze(
            dataframe,
            period_revenue=3000.0,
            period_direct_cost=2000.0,
            period_days=30,
        )
    )

    assert result.total_ar == 1500.0
    assert result.total_ap == 800.0
    assert result.net_working_capital == 700.0
    assert result.ar_90_plus == 1000.0
    assert result.dso_proxy == 15.0


def test_missing_activity_keeps_days_unavailable() -> None:
    dataframe = pd.DataFrame(
        {
            "document_type": ["AR"],
            "counterparty": ["Customer A"],
            "open_amount": [1000.0],
            "is_overdue": [False],
            "days_overdue": [0],
            "aging_bucket": ["Current"],
        }
    )

    result = (
        WorkingCapitalIntelligenceEngine()
        .analyze(dataframe)
    )

    assert result.dso_proxy is None
    assert result.dpo_proxy is None
