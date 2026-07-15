from __future__ import annotations

import pandas as pd

from models.impact_scenario import (
    ImpactScenario,
    ImpactSimulationResult,
)


class FinancialImpactSimulator:
    """
    Simulates financial impact from controllable management levers.

    Levers:
    - Revenue growth
    - Margin improvement
    - Direct cost reduction
    - Volume growth
    """

    def simulate(
        self,
        dataframe: pd.DataFrame,
        scenario: ImpactScenario,
    ) -> ImpactSimulationResult:
        if dataframe.empty:
            raise ValueError(
                "Cannot simulate impact on an empty dataset."
            )

        base_revenue = self._sum(
            dataframe,
            "actual_revenue",
        )
        base_cost = self._sum(
            dataframe,
            "actual_cost",
        )
        base_gp = self._sum(
            dataframe,
            "actual_gp",
        )

        if base_gp == 0.0:
            base_gp = (
                base_revenue
                - base_cost
            )

        base_margin = (
            base_gp / base_revenue
            if base_revenue
            else 0.0
        )

        combined_revenue_growth = (
            scenario.revenue_growth_pct
            + scenario.volume_growth_pct
        )

        projected_revenue = (
            base_revenue
            * (
                1.0
                + combined_revenue_growth
            )
        )

        projected_cost = (
            base_cost
            * (
                1.0
                + scenario.volume_growth_pct
            )
            * (
                1.0
                - scenario.cost_reduction_pct
            )
        )

        target_margin = min(
            max(
                base_margin
                + scenario.margin_improvement_pp,
                -1.0,
            ),
            1.0,
        )

        gp_from_margin = (
            projected_revenue
            * target_margin
        )

        gp_from_cost = (
            projected_revenue
            - projected_cost
        )

        projected_gp = max(
            gp_from_margin,
            gp_from_cost,
        )

        projected_cost = (
            projected_revenue
            - projected_gp
        )

        projected_margin = (
            projected_gp
            / projected_revenue
            if projected_revenue
            else 0.0
        )

        return ImpactSimulationResult(
            scenario_name=scenario.scenario_name,
            base_revenue=base_revenue,
            base_cost=base_cost,
            base_gp=base_gp,
            base_margin=base_margin,
            projected_revenue=projected_revenue,
            projected_cost=projected_cost,
            projected_gp=projected_gp,
            projected_margin=projected_margin,
            revenue_impact=(
                projected_revenue
                - base_revenue
            ),
            cost_impact=(
                projected_cost
                - base_cost
            ),
            gp_impact=(
                projected_gp
                - base_gp
            ),
            margin_impact_pp=(
                projected_margin
                - base_margin
            ),
        )

    def sensitivity_table(
        self,
        dataframe: pd.DataFrame,
        *,
        revenue_growth_options: list[float],
        margin_improvement_options: list[float],
    ) -> pd.DataFrame:
        rows = []

        for revenue_growth in revenue_growth_options:
            for margin_improvement in margin_improvement_options:
                result = self.simulate(
                    dataframe,
                    ImpactScenario(
                        scenario_name=(
                            f"Revenue {revenue_growth:+.1%} / "
                            f"Margin {margin_improvement * 100:+.1f} pp"
                        ),
                        revenue_growth_pct=revenue_growth,
                        margin_improvement_pp=margin_improvement,
                        cost_reduction_pct=0.0,
                        volume_growth_pct=0.0,
                    ),
                )

                rows.append(
                    {
                        "Revenue Growth": revenue_growth,
                        "Margin Improvement pp": (
                            margin_improvement
                        ),
                        "Projected GP": (
                            result.projected_gp
                        ),
                        "GP Impact": (
                            result.gp_impact
                        ),
                        "Projected Margin": (
                            result.projected_margin
                        ),
                    }
                )

        return pd.DataFrame(rows)

    @staticmethod
    def _sum(
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        if column not in dataframe.columns:
            return 0.0

        return float(
            pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )
            .fillna(0.0)
            .sum()
        )
