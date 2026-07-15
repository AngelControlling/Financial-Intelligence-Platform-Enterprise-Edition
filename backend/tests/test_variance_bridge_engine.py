import pandas as pd

from engines.variance_bridge_engine import (
    VarianceBridgeEngine,
)


def test_variance_bridge_reconciles_to_total() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A", "B", "C"],
            "actual_revenue": [120.0, 80.0, 110.0],
            "estimated_revenue": [100.0, 100.0, 100.0],
            "actual_gp": [40.0, 15.0, 35.0],
            "estimated_gp": [30.0, 25.0, 30.0],
        }
    )

    result = VarianceBridgeEngine().analyze(
        dataframe,
        metric="Revenue",
        dimension="customer",
    )

    assert result.actual_total == 310.0
    assert result.target_total == 300.0
    assert result.variance_total == 10.0
    assert round(
        result.contributors[
            "Variance"
        ].sum(),
        2,
    ) == 10.0


def test_dimension_availability() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A"],
            "mode": ["Air"],
        }
    )

    dimensions = (
        VarianceBridgeEngine()
        .available_dimensions(dataframe)
    )

    assert dimensions == [
        "customer",
        "mode",
    ]
