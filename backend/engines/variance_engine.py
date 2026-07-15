from __future__ import annotations

import numpy as np
import pandas as pd


class VarianceEngine:
    """Calculates and explains Actual vs Budget variances."""

    ALLOWED_DIMENSIONS = {
        "mode",
        "product",
        "customer",
        "trade_lane",
        "forwarder",
        "origin",
        "destination",
        "period",
    }

    REQUIRED_COLUMNS = {
        "shipment",
        "actual_revenue",
        "actual_cost",
        "budget_revenue",
        "budget_cost",
    }

    def prepare_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Validates data and calculates row-level variances."""
        missing_columns = sorted(
            self.REQUIRED_COLUMNS - set(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas requeridas para Variance Engine: "
                + ", ".join(missing_columns)
            )

        df = dataframe.copy()

        numeric_columns = [
            "actual_revenue",
            "actual_cost",
            "budget_revenue",
            "budget_cost",
            "tons",
            "teus",
        ]

        for column in numeric_columns:
            if column not in df.columns:
                df[column] = 0.0

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        df["actual_gp"] = (
            df["actual_revenue"] - df["actual_cost"]
        )

        df["budget_gp"] = (
            df["budget_revenue"] - df["budget_cost"]
        )

        df["revenue_variance"] = (
            df["actual_revenue"] - df["budget_revenue"]
        )

        df["cost_variance"] = (
            df["actual_cost"] - df["budget_cost"]
        )

        df["gp_variance"] = (
            df["actual_gp"] - df["budget_gp"]
        )

        df["actual_gp_margin"] = np.where(
            df["actual_revenue"] != 0,
            df["actual_gp"] / df["actual_revenue"],
            0.0,
        )

        df["budget_gp_margin"] = np.where(
            df["budget_revenue"] != 0,
            df["budget_gp"] / df["budget_revenue"],
            0.0,
        )

        df["margin_variance_pp"] = (
            df["actual_gp_margin"]
            - df["budget_gp_margin"]
        )

        return df

    def overall_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:
        """Returns consolidated Actual vs Budget performance."""
        df = self.prepare_data(dataframe)

        actual_revenue = float(df["actual_revenue"].sum())
        budget_revenue = float(df["budget_revenue"].sum())

        actual_cost = float(df["actual_cost"].sum())
        budget_cost = float(df["budget_cost"].sum())

        actual_gp = float(df["actual_gp"].sum())
        budget_gp = float(df["budget_gp"].sum())

        actual_margin = (
            actual_gp / actual_revenue
            if actual_revenue
            else 0.0
        )

        budget_margin = (
            budget_gp / budget_revenue
            if budget_revenue
            else 0.0
        )

        revenue_variance = actual_revenue - budget_revenue
        cost_variance = actual_cost - budget_cost
        gp_variance = actual_gp - budget_gp

        return {
            "actual_revenue": actual_revenue,
            "budget_revenue": budget_revenue,
            "revenue_variance": revenue_variance,
            "revenue_variance_pct": self._safe_divide(
                revenue_variance,
                budget_revenue,
            ),
            "actual_cost": actual_cost,
            "budget_cost": budget_cost,
            "cost_variance": cost_variance,
            "cost_variance_pct": self._safe_divide(
                cost_variance,
                budget_cost,
            ),
            "actual_gp": actual_gp,
            "budget_gp": budget_gp,
            "gp_variance": gp_variance,
            "gp_variance_pct": self._safe_divide(
                gp_variance,
                abs(budget_gp),
            ),
            "actual_gp_margin": actual_margin,
            "budget_gp_margin": budget_margin,
            "margin_variance_pp": (
                actual_margin - budget_margin
            ),
        }

    def dimension_variance(
        self,
        dataframe: pd.DataFrame,
        dimension: str,
    ) -> pd.DataFrame:
        """Aggregates variances by one business dimension."""
        if dimension not in self.ALLOWED_DIMENSIONS:
            raise ValueError(
                f"Dimensión no permitida: {dimension}"
            )

        df = self.prepare_data(dataframe)

        if dimension not in df.columns:
            df[dimension] = "Unassigned"

        df[dimension] = (
            df[dimension]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
        )

        summary = (
            df.groupby(dimension, dropna=False)
            .agg(
                Shipments=("shipment", "nunique"),
                Actual_Revenue=("actual_revenue", "sum"),
                Budget_Revenue=("budget_revenue", "sum"),
                Revenue_Variance=("revenue_variance", "sum"),
                Actual_Cost=("actual_cost", "sum"),
                Budget_Cost=("budget_cost", "sum"),
                Cost_Variance=("cost_variance", "sum"),
                Actual_GP=("actual_gp", "sum"),
                Budget_GP=("budget_gp", "sum"),
                GP_Variance=("gp_variance", "sum"),
                Tons=("tons", "sum"),
                TEUs=("teus", "sum"),
            )
            .reset_index()
        )

        summary["Revenue_Variance_Pct"] = np.where(
            summary["Budget_Revenue"] != 0,
            summary["Revenue_Variance"]
            / summary["Budget_Revenue"],
            0.0,
        )

        summary["Cost_Variance_Pct"] = np.where(
            summary["Budget_Cost"] != 0,
            summary["Cost_Variance"]
            / summary["Budget_Cost"],
            0.0,
        )

        summary["GP_Variance_Pct"] = np.where(
            summary["Budget_GP"] != 0,
            summary["GP_Variance"]
            / summary["Budget_GP"].abs(),
            0.0,
        )

        summary["Actual_GP_Margin"] = np.where(
            summary["Actual_Revenue"] != 0,
            summary["Actual_GP"]
            / summary["Actual_Revenue"],
            0.0,
        )

        summary["Budget_GP_Margin"] = np.where(
            summary["Budget_Revenue"] != 0,
            summary["Budget_GP"]
            / summary["Budget_Revenue"],
            0.0,
        )

        summary["Margin_Variance_PP"] = (
            summary["Actual_GP_Margin"]
            - summary["Budget_GP_Margin"]
        )

        summary["Absolute_GP_Impact"] = (
            summary["GP_Variance"].abs()
        )

        summary["Direction"] = np.select(
            [
                summary["GP_Variance"] > 0,
                summary["GP_Variance"] < 0,
            ],
            [
                "Favorable",
                "Unfavorable",
            ],
            default="Neutral",
        )

        total_absolute_impact = float(
            summary["Absolute_GP_Impact"].sum()
        )

        if total_absolute_impact:
            summary["Impact_Contribution"] = (
                summary["Absolute_GP_Impact"]
                / total_absolute_impact
            )
        else:
            summary["Impact_Contribution"] = 0.0

        return summary.sort_values(
            "Absolute_GP_Impact",
            ascending=False,
        ).reset_index(drop=True)

    def top_drivers(
        self,
        dataframe: pd.DataFrame,
        dimension: str,
        limit: int = 5,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Returns top favorable and unfavorable GP drivers."""
        summary = self.dimension_variance(
            dataframe,
            dimension,
        )

        positive = (
            summary[summary["GP_Variance"] > 0]
            .sort_values(
                "GP_Variance",
                ascending=False,
            )
            .head(limit)
            .reset_index(drop=True)
        )

        negative = (
            summary[summary["GP_Variance"] < 0]
            .sort_values(
                "GP_Variance",
                ascending=True,
            )
            .head(limit)
            .reset_index(drop=True)
        )

        return positive, negative

    def pareto_analysis(
        self,
        dataframe: pd.DataFrame,
        dimension: str,
    ) -> pd.DataFrame:
        """Ranks dimensions by absolute GP impact."""
        pareto = self.dimension_variance(
            dataframe,
            dimension,
        ).copy()

        total_impact = float(
            pareto["Absolute_GP_Impact"].sum()
        )

        if total_impact:
            pareto["Pareto_Contribution"] = (
                pareto["Absolute_GP_Impact"]
                / total_impact
            )

            pareto["Cumulative_Contribution"] = (
                pareto["Pareto_Contribution"].cumsum()
            )
        else:
            pareto["Pareto_Contribution"] = 0.0
            pareto["Cumulative_Contribution"] = 0.0

        pareto["Pareto_80_Flag"] = np.where(
            pareto["Cumulative_Contribution"] <= 0.80,
            "Primary Driver",
            "Secondary Driver",
        )

        return pareto

    def executive_findings(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        """Creates deterministic executive findings."""
        summary = self.overall_summary(dataframe)
        findings: list[str] = []

        revenue_direction = (
            "above"
            if summary["revenue_variance"] >= 0
            else "below"
        )

        findings.append(
            "Revenue finished "
            f"{revenue_direction} Budget by "
            f"${abs(summary['revenue_variance']):,.0f} "
            f"({summary['revenue_variance_pct']:+.1%})."
        )

        cost_direction = (
            "above"
            if summary["cost_variance"] >= 0
            else "below"
        )

        findings.append(
            "Cost finished "
            f"{cost_direction} Budget by "
            f"${abs(summary['cost_variance']):,.0f} "
            f"({summary['cost_variance_pct']:+.1%})."
        )

        gp_direction = (
            "favorable"
            if summary["gp_variance"] >= 0
            else "unfavorable"
        )

        findings.append(
            "Gross Profit variance was "
            f"{gp_direction} by "
            f"${abs(summary['gp_variance']):,.0f} "
            f"({summary['gp_variance_pct']:+.1%})."
        )

        margin_direction = (
            "improved"
            if summary["margin_variance_pp"] >= 0
            else "deteriorated"
        )

        findings.append(
            "GP Margin "
            f"{margin_direction} by "
            f"{abs(summary['margin_variance_pp']) * 100:.2f} "
            "percentage points versus Budget."
        )

        mode_summary = self.dimension_variance(
            dataframe,
            "mode",
        )

        if not mode_summary.empty:
            main_mode = mode_summary.iloc[0]

            findings.append(
                f"{main_mode['mode']} generated the largest "
                "absolute GP variance impact at "
                f"${main_mode['GP_Variance']:,.0f}."
            )

        return findings

    @staticmethod
    def _safe_divide(
        numerator: float,
        denominator: float,
    ) -> float:
        if denominator == 0:
            return 0.0

        return numerator / denominator