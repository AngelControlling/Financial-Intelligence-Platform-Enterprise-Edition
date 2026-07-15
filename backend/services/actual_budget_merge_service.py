from __future__ import annotations

import pandas as pd


class ActualBudgetMergeService:
    """
    Applies the active external budget to shipment-level Actuals.

    Budget totals are allocated across actual rows within the common grain so
    summing estimated values never duplicates the annual budget.
    """

    DIMENSION_PAIRS = [
        ("year", "Fiscal_Year"),
        ("month_num", "month_num"),
        ("country", "Country"),
        ("mode", "Mode"),
        ("product", "Product"),
        ("trade_lane", "Trade_Lane"),
    ]

    def apply(
        self,
        actuals: pd.DataFrame,
        budget: pd.DataFrame,
    ) -> pd.DataFrame:
        if actuals.empty or budget.empty:
            return actuals.copy()

        output = actuals.copy()
        budget_df = budget.copy()

        if "year" not in output.columns:
            if "period" in output.columns:
                period = pd.to_datetime(
                    output["period"],
                    errors="coerce",
                )
                output["year"] = period.dt.year
                output["month_num"] = period.dt.month

        common_pairs = [
            pair
            for pair in self.DIMENSION_PAIRS
            if pair[0] in output.columns
            and pair[1] in budget_df.columns
        ]

        # Year and month are required to avoid annual duplication.
        required = {
            "year",
            "month_num",
        }
        actual_key_names = {
            pair[0]
            for pair in common_pairs
        }
        if not required.issubset(actual_key_names):
            return output

        actual_keys = [
            pair[0]
            for pair in common_pairs
        ]
        budget_keys = [
            pair[1]
            for pair in common_pairs
        ]

        rename_budget = {
            budget_name: actual_name
            for actual_name, budget_name
            in common_pairs
            if budget_name != actual_name
        }
        budget_df = budget_df.rename(
            columns=rename_budget
        )

        budget_agg = (
            budget_df.groupby(
                actual_keys,
                dropna=False,
            )
            .agg(
                external_budget_revenue=(
                    "budget_revenue",
                    "sum",
                ),
                external_budget_cost=(
                    "budget_cost",
                    "sum",
                ),
                external_budget_gp=(
                    "budget_gp",
                    "sum",
                ),
                external_budget_shipments=(
                    "budget_shipments",
                    "sum",
                ),
                external_budget_teus=(
                    "budget_teus",
                    "sum",
                ),
                external_budget_tons=(
                    "budget_tons",
                    "sum",
                ),
            )
            .reset_index()
        )

        output["_fip_row_id"] = range(len(output))

        group_actual = (
            output.groupby(
                actual_keys,
                dropna=False,
            )["actual_revenue"]
            .transform("sum")
        )
        group_count = (
            output.groupby(
                actual_keys,
                dropna=False,
            )["_fip_row_id"]
            .transform("count")
        )

        output["_fip_allocation"] = (
            output["actual_revenue"]
            / group_actual.replace(0, pd.NA)
        )
        output["_fip_allocation"] = (
            output["_fip_allocation"]
            .fillna(1.0 / group_count)
        )

        output = output.merge(
            budget_agg,
            on=actual_keys,
            how="left",
        )

        allocation = output[
            "_fip_allocation"
        ].fillna(0.0)

        output["estimated_revenue"] = (
            output[
                "external_budget_revenue"
            ].fillna(0.0)
            * allocation
        )
        output["estimated_cost"] = (
            output[
                "external_budget_cost"
            ].fillna(0.0)
            * allocation
        )
        output["estimated_gp"] = (
            output["estimated_revenue"]
            - output["estimated_cost"]
        )

        output.drop(
            columns=[
                "_fip_row_id",
                "_fip_allocation",
            ],
            inplace=True,
            errors="ignore",
        )

        return output
