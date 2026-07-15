from __future__ import annotations

import numpy as np
import pandas as pd


class FreightKPIEngine:
    """Calculates freight financial and operational KPIs."""

    REQUIRED_COLUMNS = {
        "shipment",
        "mode",
        "actual_revenue",
        "actual_cost",
        "budget_revenue",
        "budget_cost",
        "period",
    }

    OPTIONAL_NUMERIC_COLUMNS = {
        "teus",
        "tons",
    }

    def validate_columns(self, dataframe: pd.DataFrame) -> list[str]:
        """Returns missing required canonical columns."""
        return sorted(
            self.REQUIRED_COLUMNS - set(dataframe.columns)
        )

    def prepare_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Cleans canonical data and calculates profitability."""
        missing_columns = self.validate_columns(dataframe)

        if missing_columns:
            raise ValueError(
                "Faltan columnas requeridas: "
                + ", ".join(missing_columns)
            )

        df = dataframe.copy()

        numeric_columns = [
            "actual_revenue",
            "actual_cost",
            "budget_revenue",
            "budget_cost",
            "teus",
            "tons",
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

    def executive_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:
        """Returns consolidated executive KPIs."""
        df = self.prepare_data(dataframe)

        actual_revenue = float(
            df["actual_revenue"].sum()
        )
        actual_cost = float(
            df["actual_cost"].sum()
        )
        actual_gp = float(
            df["actual_gp"].sum()
        )

        budget_revenue = float(
            df["budget_revenue"].sum()
        )
        budget_cost = float(
            df["budget_cost"].sum()
        )
        budget_gp = float(
            df["budget_gp"].sum()
        )

        shipments = int(
            df["shipment"].nunique()
        )
        tons = float(
            df["tons"].sum()
        )
        teus = float(
            df["teus"].sum()
        )

        actual_gp_margin = (
            actual_gp / actual_revenue
            if actual_revenue
            else 0.0
        )

        budget_gp_margin = (
            budget_gp / budget_revenue
            if budget_revenue
            else 0.0
        )

        return {
            "shipments": shipments,
            "weight_tons": tons,
            "teus": teus,
            "actual_revenue": actual_revenue,
            "actual_cost": actual_cost,
            "actual_gp": actual_gp,
            "actual_gp_margin": actual_gp_margin,
            "estimated_revenue": budget_revenue,
            "estimated_cost": budget_cost,
            "estimated_gp": budget_gp,
            "estimated_gp_margin": budget_gp_margin,
            "revenue_variance": (
                actual_revenue - budget_revenue
            ),
            "cost_variance": (
                actual_cost - budget_cost
            ),
            "gp_variance": (
                actual_gp - budget_gp
            ),
            "margin_variance_pp": (
                actual_gp_margin - budget_gp_margin
            ),
            "revenue_per_shipment": (
                actual_revenue / shipments
                if shipments
                else 0.0
            ),
            "gp_per_shipment": (
                actual_gp / shipments
                if shipments
                else 0.0
            ),
            "revenue_per_ton": (
                actual_revenue / tons
                if tons
                else 0.0
            ),
            "gp_per_ton": (
                actual_gp / tons
                if tons
                else 0.0
            ),
            "revenue_per_teu": (
                actual_revenue / teus
                if teus
                else 0.0
            ),
            "gp_per_teu": (
                actual_gp / teus
                if teus
                else 0.0
            ),
        }

    def forwarder_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Aggregates profitability by forwarder."""
        df = self.prepare_data(dataframe)

        if "forwarder" not in df.columns:
            df["forwarder"] = "Unassigned"

        summary = (
            df.groupby(
                "forwarder",
                dropna=False,
            )
            .agg(
                Shipments=("shipment", "nunique"),
                Weight_Tons=("tons", "sum"),
                TEUs=("teus", "sum"),
                Actual_Revenue=(
                    "actual_revenue",
                    "sum",
                ),
                Actual_Cost=(
                    "actual_cost",
                    "sum",
                ),
                Actual_GP=(
                    "actual_gp",
                    "sum",
                ),
                Estimated_GP=(
                    "budget_gp",
                    "sum",
                ),
                GP_Variance=(
                    "gp_variance",
                    "sum",
                ),
            )
            .reset_index()
            .rename(
                columns={
                    "forwarder": "Forwarder"
                }
            )
        )

        summary["GP_Margin"] = np.where(
            summary["Actual_Revenue"] != 0,
            summary["Actual_GP"]
            / summary["Actual_Revenue"],
            0.0,
        )

        summary["GP_per_Shipment"] = np.where(
            summary["Shipments"] != 0,
            summary["Actual_GP"]
            / summary["Shipments"],
            0.0,
        )

        return summary.sort_values(
            "Actual_GP",
            ascending=False,
        )