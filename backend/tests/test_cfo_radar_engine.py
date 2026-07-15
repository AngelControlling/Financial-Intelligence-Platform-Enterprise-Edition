import pandas as pd

from engines.cfo_radar_engine import (
    CFORadarEngine,
)


def test_cfo_radar_detects_material_risk() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": [
                "A",
                "A",
                "B",
            ],
            "actual_revenue": [
                800.0,
                100.0,
                100.0,
            ],
            "actual_gp": [
                -50.0,
                10.0,
                20.0,
            ],
        }
    )

    result = CFORadarEngine().evaluate(
        dataframe,
        summary={},
        variance={
            "revenue_variance_pct": -0.15,
            "gp_variance_pct": -0.25,
            "margin_variance_pp": -0.04,
        },
        data_quality_score=95.0,
    )

    assert result.overall_score > 0
    assert result.risk_count >= 1
    assert result.top_risk


def test_cfo_radar_low_risk_case() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": [
                "A",
                "B",
                "C",
            ],
            "actual_revenue": [
                300.0,
                300.0,
                400.0,
            ],
            "actual_gp": [
                90.0,
                90.0,
                120.0,
            ],
        }
    )

    result = CFORadarEngine().evaluate(
        dataframe,
        summary={},
        variance={
            "revenue_variance_pct": 0.05,
            "gp_variance_pct": 0.05,
            "margin_variance_pp": 0.01,
        },
        data_quality_score=100.0,
    )

    assert result.critical_count == 0
