import pandas as pd

from engines.financial_impact_simulator import (
    FinancialImpactSimulator,
)
from models.impact_scenario import (
    ImpactScenario,
)


def test_margin_improvement_increases_gp() -> None:
    dataframe = pd.DataFrame(
        {
            "actual_revenue": [1000.0],
            "actual_cost": [800.0],
            "actual_gp": [200.0],
        }
    )

    result = FinancialImpactSimulator().simulate(
        dataframe,
        ImpactScenario(
            scenario_name="Margin Recovery",
            revenue_growth_pct=0.0,
            margin_improvement_pp=0.02,
            cost_reduction_pct=0.0,
            volume_growth_pct=0.0,
        ),
    )

    assert result.projected_gp > result.base_gp
    assert round(
        result.margin_impact_pp,
        4,
    ) == 0.02


def test_revenue_growth_increases_revenue() -> None:
    dataframe = pd.DataFrame(
        {
            "actual_revenue": [1000.0],
            "actual_cost": [700.0],
            "actual_gp": [300.0],
        }
    )

    result = FinancialImpactSimulator().simulate(
        dataframe,
        ImpactScenario(
            scenario_name="Growth",
            revenue_growth_pct=0.10,
            margin_improvement_pp=0.0,
            cost_reduction_pct=0.0,
            volume_growth_pct=0.0,
        ),
    )

    assert result.projected_revenue == 1100.0
