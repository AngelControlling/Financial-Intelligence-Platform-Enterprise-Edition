from __future__ import annotations

import pandas as pd

from models.full_pnl import (
    FullPnLResult,
    PnLLine,
)


class FullPnLIntelligenceEngine:
    """
    Builds a Controller-style P&L from any supported canonical aliases.

    It never invents missing values. A line is returned as unavailable when
    the active dataset does not contain the required information.
    """

    ALIASES = {
        "actual_revenue": (
            "actual_revenue",
            "revenue",
            "real_revenue",
            "Real_Revenue",
        ),
        "budget_revenue": (
            "estimated_revenue",
            "budget_revenue",
            "Budget_Revenue",
        ),
        "actual_direct_cost": (
            "actual_cost",
            "direct_cost",
            "real_cost",
            "Real_Cost",
        ),
        "budget_direct_cost": (
            "estimated_cost",
            "budget_cost",
            "Budget_Cost",
        ),
        "actual_gp": (
            "actual_gp",
            "gross_profit",
            "gp",
        ),
        "budget_gp": (
            "estimated_gp",
            "budget_gp",
            "Budget_GP",
        ),
        "actual_opex": (
            "actual_opex",
            "opex",
            "total_opex",
            "Total_OPEX",
        ),
        "budget_opex": (
            "estimated_opex",
            "budget_opex",
            "Budget_OPEX",
        ),
        "actual_personnel": (
            "actual_personnel_expense",
            "personnel_expense",
            "persex",
            "actual_persex",
            "Personnel_Expense",
        ),
        "budget_personnel": (
            "estimated_personnel_expense",
            "budget_personnel_expense",
            "budget_persex",
            "Budget_Personnel_Expense",
        ),
        "actual_depreciation": (
            "actual_depreciation",
            "depreciation",
            "actual_da",
        ),
        "budget_depreciation": (
            "estimated_depreciation",
            "budget_depreciation",
            "budget_da",
        ),
        "actual_headcount": (
            "actual_headcount",
            "headcount",
            "hc",
        ),
        "budget_headcount": (
            "budget_headcount",
            "budget_hc",
            "Budget_HC",
        ),
    }

    def analyze(
        self,
        dataframe: pd.DataFrame,
    ) -> FullPnLResult:
        values = {
            key: self._sum_aliases(
                dataframe,
                aliases,
            )
            for key, aliases in self.ALIASES.items()
        }

        actual_revenue = values["actual_revenue"]
        budget_revenue = values["budget_revenue"]
        actual_cost = values["actual_direct_cost"]
        budget_cost = values["budget_direct_cost"]

        actual_gp = values["actual_gp"]
        budget_gp = values["budget_gp"]

        if actual_gp is None and (
            actual_revenue is not None
            and actual_cost is not None
        ):
            actual_gp = (
                actual_revenue
                - actual_cost
            )

        if budget_gp is None and (
            budget_revenue is not None
            and budget_cost is not None
        ):
            budget_gp = (
                budget_revenue
                - budget_cost
            )

        actual_opex = values["actual_opex"]
        budget_opex = values["budget_opex"]
        actual_personnel = values[
            "actual_personnel"
        ]
        budget_personnel = values[
            "budget_personnel"
        ]

        actual_operating_profit = (
            actual_gp
            - (actual_opex or 0.0)
            - (actual_personnel or 0.0)
            if actual_gp is not None
            and (
                actual_opex is not None
                or actual_personnel is not None
            )
            else None
        )
        budget_operating_profit = (
            budget_gp
            - (budget_opex or 0.0)
            - (budget_personnel or 0.0)
            if budget_gp is not None
            and (
                budget_opex is not None
                or budget_personnel is not None
            )
            else None
        )

        actual_da = values[
            "actual_depreciation"
        ]
        budget_da = values[
            "budget_depreciation"
        ]

        actual_ebitda = (
            actual_operating_profit
            + actual_da
            if (
                actual_operating_profit
                is not None
                and actual_da is not None
            )
            else None
        )
        budget_ebitda = (
            budget_operating_profit
            + budget_da
            if (
                budget_operating_profit
                is not None
                and budget_da is not None
            )
            else None
        )

        lines = [
            self._line(
                "Revenue",
                actual_revenue,
                budget_revenue,
                higher_is_favorable=True,
            ),
            self._line(
                "Direct Cost",
                actual_cost,
                budget_cost,
                higher_is_favorable=False,
            ),
            self._line(
                "Gross Profit",
                actual_gp,
                budget_gp,
                higher_is_favorable=True,
            ),
            self._line(
                "OPEX",
                actual_opex,
                budget_opex,
                higher_is_favorable=False,
            ),
            self._line(
                "Personnel Expense",
                actual_personnel,
                budget_personnel,
                higher_is_favorable=False,
            ),
            self._line(
                "Operating Profit",
                actual_operating_profit,
                budget_operating_profit,
                higher_is_favorable=True,
            ),
            self._line(
                "EBITDA",
                actual_ebitda,
                budget_ebitda,
                higher_is_favorable=True,
            ),
        ]

        available_values = sum(
            value is not None
            for value in values.values()
        )
        coverage = (
            available_values
            / len(values)
            * 100
        )

        actual_hc = values[
            "actual_headcount"
        ]
        budget_hc = values[
            "budget_headcount"
        ]

        return FullPnLResult(
            lines=lines,
            actual_gp_margin=self._ratio(
                actual_gp,
                actual_revenue,
            ),
            budget_gp_margin=self._ratio(
                budget_gp,
                budget_revenue,
            ),
            actual_operating_margin=self._ratio(
                actual_operating_profit,
                actual_revenue,
            ),
            budget_operating_margin=self._ratio(
                budget_operating_profit,
                budget_revenue,
            ),
            actual_cost_per_employee=self._ratio(
                actual_personnel,
                actual_hc,
            ),
            budget_cost_per_employee=self._ratio(
                budget_personnel,
                budget_hc,
            ),
            actual_headcount=actual_hc,
            budget_headcount=budget_hc,
            data_coverage_pct=coverage,
        )

    def _line(
        self,
        name: str,
        actual: float | None,
        budget: float | None,
        *,
        higher_is_favorable: bool,
    ) -> PnLLine:
        if actual is None or budget is None:
            return PnLLine(
                name=name,
                actual=actual,
                budget=budget,
                variance=None,
                variance_pct=None,
                favorable=None,
            )

        variance = actual - budget
        variance_pct = (
            variance / abs(budget)
            if budget
            else None
        )
        favorable = (
            variance >= 0
            if higher_is_favorable
            else variance <= 0
        )

        return PnLLine(
            name=name,
            actual=actual,
            budget=budget,
            variance=variance,
            variance_pct=variance_pct,
            favorable=favorable,
        )

    @staticmethod
    def _sum_aliases(
        dataframe: pd.DataFrame,
        aliases: tuple[str, ...],
    ) -> float | None:
        for column in aliases:
            if column not in dataframe.columns:
                continue

            series = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

            if series.notna().any():
                return float(
                    series.fillna(0.0).sum()
                )

        return None

    @staticmethod
    def _ratio(
        numerator: float | None,
        denominator: float | None,
    ) -> float | None:
        if (
            numerator is None
            or denominator in {
                None,
                0,
            }
        ):
            return None

        return numerator / denominator
