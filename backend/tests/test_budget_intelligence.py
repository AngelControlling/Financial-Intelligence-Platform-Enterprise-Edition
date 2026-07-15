import pandas as pd

from services.actual_budget_merge_service import (
    ActualBudgetMergeService,
)
from services.budget_ingestion_service import (
    BudgetIngestionService,
)


def test_budget_validation_and_merge() -> None:
    pnl = pd.DataFrame(
        {
            "Fiscal_Year": [2027],
            "Month": ["Jan"],
            "Country": ["Mexico"],
            "Mode": ["Air"],
            "Product": ["Air Export"],
            "Budget_Revenue": [1000.0],
            "Budget_Cost": [700.0],
        }
    )

    operations = pd.DataFrame(
        {
            "Fiscal_Year": [2027],
            "Month": ["Jan"],
            "Country": ["Mexico"],
            "Mode": ["Air"],
            "Product": ["Air Export"],
            "Budget_Shipments": [2.0],
            "Budget_TEUs": [0.0],
            "Budget_Tons": [1.0],
        }
    )

    result = BudgetIngestionService().validate(
        {
            "Budget_PnL": pnl,
            "Budget_Operations": operations,
        }
    )

    assert result.valid
    assert result.performance[
        "budget_gp"
    ].iloc[0] == 300.0

    actuals = pd.DataFrame(
        {
            "year": [2027, 2027],
            "month_num": [1, 1],
            "country": ["Mexico", "Mexico"],
            "mode": ["Air", "Air"],
            "product": ["Air Export", "Air Export"],
            "actual_revenue": [600.0, 400.0],
            "actual_cost": [400.0, 300.0],
        }
    )

    merged = ActualBudgetMergeService().apply(
        actuals,
        result.performance,
    )

    assert round(
        merged["estimated_revenue"].sum(),
        2,
    ) == 1000.0
    assert round(
        merged["estimated_cost"].sum(),
        2,
    ) == 700.0
