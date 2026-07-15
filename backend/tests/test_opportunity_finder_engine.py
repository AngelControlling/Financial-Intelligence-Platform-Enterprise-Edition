import pandas as pd

from engines.opportunity_finder_engine import (
    OpportunityFinderEngine,
)


def test_high_margin_low_scale_is_detected() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A", "B", "C"],
            "shipment": ["S1", "S2", "S3"],
            "actual_revenue": [
                1000.0,
                5000.0,
                2000.0,
            ],
            "actual_gp": [
                400.0,
                600.0,
                300.0,
            ],
        }
    )

    opportunities = (
        OpportunityFinderEngine()
        .find(dataframe)
    )

    assert opportunities
    assert any(
        item.category == "Scale High Margin"
        for item in opportunities
    )


def test_margin_recovery_is_detected() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A", "B"],
            "shipment": ["S1", "S2"],
            "actual_revenue": [
                10000.0,
                1000.0,
            ],
            "actual_gp": [
                500.0,
                400.0,
            ],
        }
    )

    opportunities = (
        OpportunityFinderEngine()
        .find(dataframe)
    )

    assert any(
        item.category == "Margin Recovery"
        for item in opportunities
    )
