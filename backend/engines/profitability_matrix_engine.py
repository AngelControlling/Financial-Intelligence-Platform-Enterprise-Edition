from __future__ import annotations

import pandas as pd

from models.profitability_matrix import (
    ProfitabilityMatrixResult,
)


class ProfitabilityMatrixEngine:
    """
    Builds a CFO profitability and concentration matrix.

    Supported dimensions:
    - customer
    - trade_lane
    - mode
    - product
    """

    DIMENSIONS = (
        "customer",
        "trade_lane",
        "mode",
        "product",
    )

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
        dimension: str,
    ) -> ProfitabilityMatrixResult:
        required = {
            dimension,
            "actual_revenue",
            "actual_gp",
        }

        if not required.issubset(dataframe.columns):
            missing = sorted(
                required - set(dataframe.columns)
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
            "actual_revenue",
            "actual_gp",
        ]:
            working[column] = pd.to_numeric(
                working[column],
                errors="coerce",
            ).fillna(0.0)

        if "shipment" in working.columns:
            grouped = (
                working.groupby(
                    dimension,
                    dropna=False,
                )
                .agg(
                    Revenue=(
                        "actual_revenue",
                        "sum",
                    ),
                    GP=(
                        "actual_gp",
                        "sum",
                    ),
                    Shipments=(
                        "shipment",
                        "nunique",
                    ),
                )
                .reset_index()
            )
        else:
            grouped = (
                working.groupby(
                    dimension,
                    dropna=False,
                )
                .agg(
                    Revenue=(
                        "actual_revenue",
                        "sum",
                    ),
                    GP=(
                        "actual_gp",
                        "sum",
                    ),
                )
                .reset_index()
            )
            grouped["Shipments"] = 0

        grouped["GP Margin"] = (
            grouped["GP"]
            / grouped["Revenue"].replace(
                0,
                pd.NA,
            )
        ).fillna(0.0)

        grouped["GP / Shipment"] = (
            grouped["GP"]
            / grouped["Shipments"].replace(
                0,
                pd.NA,
            )
        ).fillna(0.0)

        total_revenue = float(
            grouped["Revenue"].sum()
        )
        total_gp = float(
            grouped["GP"].sum()
        )
        overall_margin = (
            total_gp / total_revenue
            if total_revenue
            else 0.0
        )

        revenue_threshold = float(
            grouped["Revenue"].median()
        ) if not grouped.empty else 0.0

        margin_threshold = overall_margin

        grouped["Quadrant"] = grouped.apply(
            lambda row: self._quadrant(
                revenue=float(row["Revenue"]),
                margin=float(row["GP Margin"]),
                revenue_threshold=revenue_threshold,
                margin_threshold=margin_threshold,
            ),
            axis=1,
        )

        grouped = grouped.sort_values(
            "Revenue",
            ascending=False,
        ).reset_index(drop=True)

        grouped["Revenue Share"] = (
            grouped["Revenue"]
            / total_revenue
            if total_revenue
            else 0.0
        )
        grouped["Cumulative Revenue Share"] = (
            grouped["Revenue Share"].cumsum()
        )

        gp_abs_total = float(
            grouped["GP"].abs().sum()
        )
        grouped["GP Contribution"] = (
            grouped["GP"].abs()
            / gp_abs_total
            if gp_abs_total
            else 0.0
        )

        top_5_revenue = float(
            grouped.head(5)["Revenue"].sum()
            / total_revenue
        ) if total_revenue else 0.0

        top_5_gp = float(
            grouped.head(5)["GP"].sum()
            / total_gp
        ) if total_gp else 0.0

        loss_making_count = int(
            (grouped["GP"] < 0).sum()
        )
        low_margin_count = int(
            (
                (grouped["GP"] >= 0)
                & (
                    grouped["GP Margin"]
                    < margin_threshold
                )
            ).sum()
        )
        high_value_count = int(
            (
                (grouped["Revenue"] >= revenue_threshold)
                & (
                    grouped["GP Margin"]
                    >= margin_threshold
                )
            ).sum()
        )

        return ProfitabilityMatrixResult(
            dimension=dimension,
            dataframe=grouped,
            total_revenue=total_revenue,
            total_gp=total_gp,
            overall_margin=overall_margin,
            top_5_revenue_concentration=top_5_revenue,
            top_5_gp_concentration=top_5_gp,
            loss_making_count=loss_making_count,
            low_margin_count=low_margin_count,
            high_value_count=high_value_count,
            margin_threshold=margin_threshold,
            revenue_threshold=revenue_threshold,
        )

    @staticmethod
    def _quadrant(
        *,
        revenue: float,
        margin: float,
        revenue_threshold: float,
        margin_threshold: float,
    ) -> str:
        high_revenue = revenue >= revenue_threshold
        high_margin = margin >= margin_threshold

        if high_revenue and high_margin:
            return "Protect & Grow"
        if high_revenue and not high_margin:
            return "Fix Margin"
        if not high_revenue and high_margin:
            return "Scale Selectively"
        return "Review / Exit"
