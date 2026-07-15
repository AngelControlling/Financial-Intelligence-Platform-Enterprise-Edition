from __future__ import annotations

import pandas as pd

from models.variance_bridge import VarianceBridgeResult


class VarianceBridgeEngine:
    """
    Explains Actual vs Budget variance by business dimension.

    Supported dimensions:
    - customer
    - trade_lane
    - mode
    - product

    Supported metrics:
    - Revenue
    - Gross Profit
"""

    DIMENSIONS = (
        "customer",
        "trade_lane",
        "mode",
        "product",
    )

    METRIC_COLUMNS = {
        "Revenue": (
            "actual_revenue",
            "estimated_revenue",
        ),
        "Gross Profit": (
            "actual_gp",
            "estimated_gp",
        ),
    }

    def available_dimensions(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        return [
            dimension
            for dimension in self.DIMENSIONS
            if dimension in dataframe.columns
        ]

    def analyze(
        self,
        dataframe: pd.DataFrame,
        *,
        metric: str,
        dimension: str,
        top_n: int = 10,
    ) -> VarianceBridgeResult:
        if metric not in self.METRIC_COLUMNS:
            raise ValueError(
                f"Unsupported metric: {metric}"
            )

        if dimension not in dataframe.columns:
            raise ValueError(
                f"Dimension not found: {dimension}"
            )

        actual_column, target_column = (
            self.METRIC_COLUMNS[metric]
        )

        required = {
            dimension,
            actual_column,
            target_column,
        }

        if not required.issubset(
            dataframe.columns
        ):
            missing = sorted(
                required
                - set(dataframe.columns)
            )
            raise ValueError(
                "Missing columns: "
                + ", ".join(missing)
            )

        working = dataframe.copy()
        working[dimension] = (
            working[dimension]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
            .replace("", "Unassigned")
        )

        for column in [
            actual_column,
            target_column,
        ]:
            working[column] = pd.to_numeric(
                working[column],
                errors="coerce",
            ).fillna(0.0)

        grouped = (
            working.groupby(
                dimension,
                dropna=False,
            )
            .agg(
                Actual=(
                    actual_column,
                    "sum",
                ),
                Budget=(
                    target_column,
                    "sum",
                ),
            )
            .reset_index()
        )

        grouped["Variance"] = (
            grouped["Actual"]
            - grouped["Budget"]
        )
        grouped["Variance %"] = grouped.apply(
            lambda row: self._variance_pct(
                row["Actual"],
                row["Budget"],
            ),
            axis=1,
        )
        grouped["Abs Variance"] = (
            grouped["Variance"].abs()
        )
        grouped["Contribution %"] = (
            grouped["Abs Variance"]
            / grouped["Abs Variance"].sum()
            if grouped["Abs Variance"].sum()
            else 0.0
        )

        grouped = grouped.sort_values(
            "Abs Variance",
            ascending=False,
        )

        if len(grouped) > top_n:
            top = grouped.head(top_n).copy()
            remainder = grouped.iloc[top_n:]

            other = pd.DataFrame(
                [
                    {
                        dimension: "Other",
                        "Actual": remainder[
                            "Actual"
                        ].sum(),
                        "Budget": remainder[
                            "Budget"
                        ].sum(),
                        "Variance": remainder[
                            "Variance"
                        ].sum(),
                        "Variance %": (
                            self._variance_pct(
                                remainder[
                                    "Actual"
                                ].sum(),
                                remainder[
                                    "Budget"
                                ].sum(),
                            )
                        ),
                        "Abs Variance": remainder[
                            "Variance"
                        ].abs().sum(),
                        "Contribution %": remainder[
                            "Abs Variance"
                        ].sum()
                        / grouped[
                            "Abs Variance"
                        ].sum()
                        if grouped[
                            "Abs Variance"
                        ].sum()
                        else 0.0,
                    }
                ]
            )

            grouped = pd.concat(
                [top, other],
                ignore_index=True,
            )

        actual_total = float(
            working[actual_column].sum()
        )
        target_total = float(
            working[target_column].sum()
        )
        variance_total = (
            actual_total
            - target_total
        )
        variance_pct = self._variance_pct(
            actual_total,
            target_total,
        )

        positive = float(
            grouped.loc[
                grouped["Variance"] > 0,
                "Variance",
            ].sum()
        )
        negative = float(
            grouped.loc[
                grouped["Variance"] < 0,
                "Variance",
            ].sum()
        )

        concentration = float(
            grouped.head(3)[
                "Abs Variance"
            ].sum()
            / grouped[
                "Abs Variance"
            ].sum()
        ) if grouped[
            "Abs Variance"
        ].sum() else 0.0

        return VarianceBridgeResult(
            metric=metric,
            dimension=dimension,
            actual_total=actual_total,
            target_total=target_total,
            variance_total=variance_total,
            variance_pct=variance_pct,
            contributors=grouped,
            positive_contribution=positive,
            negative_contribution=negative,
            concentration_pct=concentration,
        )

    @staticmethod
    def _variance_pct(
        actual: float,
        target: float,
    ) -> float:
        if target == 0:
            return 0.0

        return (
            actual - target
        ) / abs(target)
