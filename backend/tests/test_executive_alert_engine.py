import pandas as pd

from engines.executive_alert_engine import (
    ExecutiveAlertEngine,
)


def test_alerts_rank_negative_gp_and_margin() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A", "B"],
            "trade_lane": ["MEX-USA", "EU-MEX"],
            "mode": ["Air", "Ocean"],
            "product": ["Air Export", "FCL Import"],
            "actual_revenue": [900.0, 1100.0],
            "estimated_revenue": [1000.0, 1000.0],
            "actual_gp": [100.0, 350.0],
            "estimated_gp": [250.0, 300.0],
        }
    )

    alerts = ExecutiveAlertEngine().generate(
        dataframe,
        comparison_label="Budget",
        max_alerts=8,
    )

    assert alerts
    assert any(
        alert.severity in {"critical", "high"}
        for alert in alerts
    )
    assert any(
        alert.dimension == "customer"
        for alert in alerts
    )


def test_positive_opportunity_is_detected() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A"],
            "actual_revenue": [1200.0],
            "estimated_revenue": [1000.0],
            "actual_gp": [400.0],
            "estimated_gp": [250.0],
        }
    )

    alerts = ExecutiveAlertEngine().generate(
        dataframe,
        comparison_label="Budget",
    )

    assert any(
        alert.severity == "success"
        for alert in alerts
    )
