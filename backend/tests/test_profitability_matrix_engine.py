import pandas as pd

from engines.profitability_matrix_engine import (
    ProfitabilityMatrixEngine,
)


def test_profitability_quadrants_and_concentration() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A", "B", "C", "D"],
            "shipment": ["S1", "S2", "S3", "S4"],
            "actual_revenue": [
                1000.0,
                900.0,
                200.0,
                100.0,
            ],
            "actual_gp": [
                300.0,
                50.0,
                80.0,
                -20.0,
            ],
        }
    )

    result = (
        ProfitabilityMatrixEngine()
        .analyze(
            dataframe,
            dimension="customer",
        )
    )

    assert result.total_revenue == 2200.0
    assert result.total_gp == 410.0
    assert result.loss_making_count == 1
    assert "Quadrant" in result.dataframe.columns
    assert result.top_5_revenue_concentration == 1.0


def test_supported_dimensions() -> None:
    dataframe = pd.DataFrame(
        {
            "customer": ["A"],
            "mode": ["Air"],
        }
    )

    dimensions = (
        ProfitabilityMatrixEngine()
        .available_dimensions(
            dataframe
        )
    )

    assert dimensions == [
        "customer",
        "mode",
    ]
