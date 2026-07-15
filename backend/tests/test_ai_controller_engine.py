import pandas as pd

from engines.ai_controller_engine import (
    AIControllerEngine,
)


def test_ai_controller_detects_profitability_conversion_issue() -> None:
    dataframe = pd.DataFrame(
        {
            "mode": ["Air", "Ocean"],
            "product": [
                "Air Export",
                "FCL Export",
            ],
            "customer": ["A", "B"],
            "trade_lane": [
                "MEX-USA",
                "MEX-ASIA",
            ],
            "shipment": ["S1", "S2"],
            "actual_revenue": [
                1200.0,
                1000.0,
            ],
            "estimated_revenue": [
                1000.0,
                1000.0,
            ],
            "actual_cost": [
                1100.0,
                700.0,
            ],
            "actual_gp": [
                100.0,
                300.0,
            ],
            "estimated_gp": [
                250.0,
                250.0,
            ],
        }
    )

    narrative = (
        AIControllerEngine()
        .generate(
            dataframe,
            period_label="Q1 2026",
            comparison_label="Budget",
            summary={
                "actual_revenue": 2200.0,
                "actual_gp": 400.0,
                "actual_gp_margin": (
                    400.0 / 2200.0
                ),
            },
            variance={
                "revenue_variance_pct": 0.10,
                "gp_variance_pct": -0.20,
                "margin_variance_pp": -0.05,
            },
            data_quality_score=100.0,
        )
    )

    assert (
        "profitability conversion"
        in narrative.what_happened
    )
    assert narrative.recommended_actions
    assert narrative.confidence_score > 0


def test_ai_controller_positive_case() -> None:
    dataframe = pd.DataFrame(
        {
            "mode": ["Ocean"],
            "actual_revenue": [1100.0],
            "estimated_revenue": [1000.0],
            "actual_cost": [700.0],
            "actual_gp": [400.0],
            "estimated_gp": [300.0],
        }
    )

    narrative = (
        AIControllerEngine()
        .generate(
            dataframe,
            period_label="YTD 2026",
            comparison_label="Budget",
            summary={
                "actual_revenue": 1100.0,
                "actual_gp": 400.0,
                "actual_gp_margin": (
                    400.0 / 1100.0
                ),
            },
            variance={
                "revenue_variance_pct": 0.10,
                "gp_variance_pct": 0.20,
                "margin_variance_pp": 0.03,
            },
            data_quality_score=100.0,
        )
    )

    assert (
        "balanced and profitable growth"
        in narrative.what_happened
    )
