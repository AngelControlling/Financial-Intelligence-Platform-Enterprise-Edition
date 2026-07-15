
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BaselineOption:
    key: str
    label: str
    revenue_column: str
    cost_column: str


@dataclass(frozen=True)
class BaselineSelectionResult:
    dataframe: pd.DataFrame
    selected_key: str
    selected_label: str
    revenue_source: str
    cost_source: str


class BaselineClassificationEngine:
    """
    Detects and applies available financial comparison baselines.

    The current Variance Engine expects:
    - budget_revenue
    - budget_cost

    This engine preserves that interface by copying the selected baseline
    into those working columns while retaining the original source fields.
    """

    BASELINES: tuple[BaselineOption, ...] = (
        BaselineOption(
            key="budget",
            label="Budget",
            revenue_column="budget_revenue",
            cost_column="budget_cost",
        ),
        BaselineOption(
            key="reserve",
            label="Reserve",
            revenue_column="reserve_revenue",
            cost_column="reserve_cost",
        ),
        BaselineOption(
            key="forecast",
            label="Forecast",
            revenue_column="forecast_revenue",
            cost_column="forecast_cost",
        ),
        BaselineOption(
            key="prior_year",
            label="Prior Year",
            revenue_column="prior_year_revenue",
            cost_column="prior_year_cost",
        ),
    )

    def available_baselines(
        self,
        dataframe: pd.DataFrame,
    ) -> list[BaselineOption]:
        """Return complete revenue/cost baselines available in the data."""

        available: list[BaselineOption] = []

        for option in self.BASELINES:
            if {
                option.revenue_column,
                option.cost_column,
            }.issubset(dataframe.columns):
                available.append(option)

        return available

    def default_baseline(
        self,
        dataframe: pd.DataFrame,
    ) -> BaselineOption:
        """
        Return the preferred available baseline.

        Priority:
        Budget > Reserve > Forecast > Prior Year.
        """

        available = self.available_baselines(
            dataframe
        )

        if not available:
            raise ValueError(
                "No complete comparison baseline was found. "
                "A revenue and cost pair is required."
            )

        return available[0]

    def get_option(
        self,
        dataframe: pd.DataFrame,
        selected_key: str,
    ) -> BaselineOption:
        """Validate and return one selected baseline option."""

        available = {
            option.key: option
            for option in self.available_baselines(
                dataframe
            )
        }

        if selected_key not in available:
            available_labels = ", ".join(
                option.label
                for option in available.values()
            )

            raise ValueError(
                f"Baseline '{selected_key}' is not available. "
                f"Available baselines: {available_labels or 'None'}."
            )

        return available[selected_key]

    def apply_baseline(
        self,
        dataframe: pd.DataFrame,
        selected_key: str,
    ) -> BaselineSelectionResult:
        """
        Apply the selected baseline to the working comparison columns.

        The source columns remain unchanged.
        """

        option = self.get_option(
            dataframe,
            selected_key,
        )

        df = dataframe.copy()

        df["budget_revenue"] = pd.to_numeric(
            df[option.revenue_column],
            errors="coerce",
        ).fillna(0.0)

        df["budget_cost"] = pd.to_numeric(
            df[option.cost_column],
            errors="coerce",
        ).fillna(0.0)

        df["_comparison_baseline_key"] = (
            option.key
        )

        df["_comparison_baseline_label"] = (
            option.label
        )

        return BaselineSelectionResult(
            dataframe=df,
            selected_key=option.key,
            selected_label=option.label,
            revenue_source=option.revenue_column,
            cost_source=option.cost_column,
        )

    def baseline_audit(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Return a structured audit of detected baseline pairs."""

        records: list[dict] = []

        for option in self.BASELINES:
            revenue_available = (
                option.revenue_column
                in dataframe.columns
            )

            cost_available = (
                option.cost_column
                in dataframe.columns
            )

            records.append(
                {
                    "Baseline_Key": option.key,
                    "Baseline_Label": option.label,
                    "Revenue_Column": option.revenue_column,
                    "Cost_Column": option.cost_column,
                    "Revenue_Available": revenue_available,
                    "Cost_Available": cost_available,
                    "Complete": (
                        revenue_available
                        and cost_available
                    ),
                }
            )

        return pd.DataFrame(records)
