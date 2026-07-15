from engines.executive_brief_engine import (
    ExecutiveBriefEngine,
)


def test_brief_detects_profitability_conversion_risk() -> None:
    brief = ExecutiveBriefEngine().build(
        period_label="YTD 2026",
        comparison_label="Budget",
        summary={
            "actual_revenue": 1200.0,
            "actual_gp": 200.0,
            "actual_gp_margin": 0.1667,
            "shipments": 10,
            "weight_tons": 5,
            "teus": 2,
        },
        variance={
            "revenue_variance_pct": 0.20,
            "gp_variance_pct": -0.10,
            "margin_variance_pp": -0.05,
        },
        alerts=[],
        actions=[],
    )

    assert (
        "profitability conversion"
        in brief.headline
    )
    assert brief.period_label == "YTD 2026"
