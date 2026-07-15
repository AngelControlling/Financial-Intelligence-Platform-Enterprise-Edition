import pandas as pd

from engines.full_pnl_engine import (
    FullPnLIntelligenceEngine,
)


def test_full_pnl_calculates_operating_profit() -> None:
    dataframe = pd.DataFrame(
        {
            "actual_revenue": [1000.0],
            "estimated_revenue": [900.0],
            "actual_cost": [600.0],
            "estimated_cost": [550.0],
            "actual_gp": [400.0],
            "estimated_gp": [350.0],
            "actual_opex": [100.0],
            "estimated_opex": [90.0],
            "actual_personnel_expense": [80.0],
            "estimated_personnel_expense": [75.0],
        }
    )

    result = (
        FullPnLIntelligenceEngine()
        .analyze(dataframe)
    )

    operating = next(
        line
        for line in result.lines
        if line.name == "Operating Profit"
    )

    assert operating.actual == 220.0
    assert operating.budget == 185.0
    assert operating.favorable is True


def test_missing_values_are_not_invented() -> None:
    dataframe = pd.DataFrame(
        {
            "actual_revenue": [1000.0],
            "actual_gp": [300.0],
        }
    )

    result = (
        FullPnLIntelligenceEngine()
        .analyze(dataframe)
    )

    opex = next(
        line
        for line in result.lines
        if line.name == "OPEX"
    )

    assert opex.actual is None
    assert opex.budget is None
