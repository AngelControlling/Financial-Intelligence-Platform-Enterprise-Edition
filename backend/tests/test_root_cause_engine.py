import pandas as pd

from engines.root_cause_engine import (
    RootCauseEngine,
)


def test_root_cause_follows_dominant_negative_path() -> None:
    dataframe = pd.DataFrame(
        {
            "mode": ["Air", "Air", "Ocean"],
            "product": [
                "Air Export",
                "Air Import",
                "FCL Export",
            ],
            "customer": ["A", "B", "C"],
            "trade_lane": [
                "MEX-USA",
                "EU-MEX",
                "MEX-Asia",
            ],
            "actual_gp": [
                100.0,
                200.0,
                500.0,
            ],
            "estimated_gp": [
                300.0,
                250.0,
                450.0,
            ],
            "actual_revenue": [
                1000.0,
                1200.0,
                2200.0,
            ],
            "estimated_revenue": [
                1100.0,
                1200.0,
                2100.0,
            ],
        }
    )

    result = RootCauseEngine().analyze(
        dataframe,
        metric="Gross Profit",
    )

    assert result.total_variance == -200.0
    assert result.dominant_path
    assert (
        result.dominant_path[0].value
        == "Air"
    )


def test_root_cause_supports_revenue() -> None:
    dataframe = pd.DataFrame(
        {
            "mode": ["Air"],
            "actual_gp": [200.0],
            "estimated_gp": [250.0],
            "actual_revenue": [900.0],
            "estimated_revenue": [1000.0],
        }
    )

    result = RootCauseEngine().analyze(
        dataframe,
        metric="Revenue",
    )

    assert result.total_variance == -100.0
