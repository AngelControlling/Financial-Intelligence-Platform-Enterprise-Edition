from __future__ import annotations

from hashlib import sha1

import pandas as pd

from models.business_opportunity import BusinessOpportunity


class OpportunityFinderEngine:
    """Detect growth and margin-recovery opportunities."""

    DIMENSIONS = (
        "customer",
        "trade_lane",
        "product",
        "mode",
    )

    def find(
        self,
        dataframe: pd.DataFrame,
        *,
        max_opportunities: int = 12,
    ) -> list[BusinessOpportunity]:
        if dataframe.empty:
            return []

        opportunities: list[BusinessOpportunity] = []

        for dimension in self.DIMENSIONS:
            if dimension in dataframe.columns:
                opportunities.extend(
                    self._dimension_opportunities(
                        dataframe,
                        dimension=dimension,
                    )
                )

        ranked = sorted(
            opportunities,
            key=self._ranking_score,
            reverse=True,
        )

        unique: list[BusinessOpportunity] = []
        seen: set[tuple[str, str, str]] = set()

        for item in ranked:
            key = (
                item.category,
                item.dimension,
                item.value,
            )
            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

            if len(unique) >= max_opportunities:
                break

        return unique

    def _dimension_opportunities(
        self,
        dataframe: pd.DataFrame,
        *,
        dimension: str,
    ) -> list[BusinessOpportunity]:
        required = {
            dimension,
            "actual_revenue",
            "actual_gp",
        }
        if not required.issubset(dataframe.columns):
            return []

        df = dataframe.copy()
        df[dimension] = (
            df[dimension]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
            .replace("", "Unassigned")
        )

        for column in ["actual_revenue", "actual_gp"]:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        if "shipment" in df.columns:
            grouped = (
                df.groupby(dimension, dropna=False)
                .agg(
                    Revenue=("actual_revenue", "sum"),
                    GP=("actual_gp", "sum"),
                    Shipments=("shipment", "nunique"),
                )
                .reset_index()
            )
        else:
            grouped = (
                df.groupby(dimension, dropna=False)
                .agg(
                    Revenue=("actual_revenue", "sum"),
                    GP=("actual_gp", "sum"),
                )
                .reset_index()
            )
            grouped["Shipments"] = 0.0

        grouped["Margin"] = (
            grouped["GP"]
            / grouped["Revenue"].replace(0, pd.NA)
        ).fillna(0.0)

        total_revenue = float(grouped["Revenue"].sum())
        total_gp = float(grouped["GP"].sum())
        overall_margin = (
            total_gp / total_revenue
            if total_revenue
            else 0.0
        )

        grouped["Revenue Share"] = (
            grouped["Revenue"] / total_revenue
            if total_revenue
            else 0.0
        )

        revenue_median = (
            float(grouped["Revenue"].median())
            if not grouped.empty
            else 0.0
        )

        opportunities: list[BusinessOpportunity] = []

        scale_candidates = grouped[
            (
                grouped["Margin"]
                >= max(
                    overall_margin * 1.15,
                    overall_margin + 0.02,
                )
            )
            & (
                grouped["Revenue"]
                <= revenue_median
            )
        ].sort_values(
            "Margin",
            ascending=False,
        ).head(3)

        for _, row in scale_candidates.iterrows():
            revenue_upside = float(
                row["Revenue"] * 0.20
            )
            gp_upside = float(
                revenue_upside * row["Margin"]
            )
            opportunities.append(
                self._build(
                    category="Scale High Margin",
                    priority="High",
                    dimension=dimension,
                    value=str(row[dimension]),
                    title=(
                        "Scale profitable "
                        + dimension.replace("_", " ")
                    ),
                    rationale=(
                        f"Margin of {row['Margin']:.1%} is above the "
                        f"portfolio average of {overall_margin:.1%}, "
                        "while Revenue remains below the median."
                    ),
                    recommended_action=(
                        "Increase commercial focus, evaluate cross-sell "
                        "and confirm available operational capacity."
                    ),
                    row=row,
                    revenue_upside=revenue_upside,
                    gp_upside=gp_upside,
                    confidence=0.88,
                )
            )

        margin_candidates = grouped[
            (
                grouped["Revenue"]
                >= revenue_median
            )
            & (
                grouped["Margin"]
                < overall_margin
            )
            & (
                grouped["GP"] > 0
            )
        ].sort_values(
            "Revenue",
            ascending=False,
        ).head(3)

        for _, row in margin_candidates.iterrows():
            margin_gap = max(
                overall_margin
                - float(row["Margin"]),
                0.0,
            )
            gp_upside = float(
                row["Revenue"] * margin_gap
            )

            opportunities.append(
                self._build(
                    category="Margin Recovery",
                    priority=(
                        "Critical"
                        if margin_gap >= 0.03
                        else "High"
                    ),
                    dimension=dimension,
                    value=str(row[dimension]),
                    title=(
                        "Recover margin in high-value "
                        + dimension.replace("_", " ")
                    ),
                    rationale=(
                        f"Revenue of ${row['Revenue']:,.0f} is material, "
                        f"but Margin of {row['Margin']:.1%} trails the "
                        f"portfolio average by {margin_gap * 100:.2f} pp."
                    ),
                    recommended_action=(
                        "Review pricing, cost-to-serve, carrier rates, "
                        "accruals and shipment-level profitability."
                    ),
                    row=row,
                    revenue_upside=0.0,
                    gp_upside=gp_upside,
                    confidence=0.93,
                )
            )

        positive_candidates = grouped[
            (
                grouped["GP"] > 0
            )
            & (
                grouped["Revenue Share"] < 0.10
            )
            & (
                grouped["Margin"] >= overall_margin
            )
        ].sort_values(
            "GP",
            ascending=False,
        ).head(2)

        for _, row in positive_candidates.iterrows():
            revenue_upside = float(
                row["Revenue"] * 0.15
            )
            gp_upside = float(
                revenue_upside * row["Margin"]
            )
            opportunities.append(
                self._build(
                    category="Replicate Success",
                    priority="Medium",
                    dimension=dimension,
                    value=str(row[dimension]),
                    title="Replicate profitable growth pattern",
                    rationale=(
                        f"{row[dimension]} contributes positive GP with "
                        "limited concentration and above-average margin."
                    ),
                    recommended_action=(
                        "Identify the commercial and operational practices "
                        "behind performance and replicate them selectively."
                    ),
                    row=row,
                    revenue_upside=revenue_upside,
                    gp_upside=gp_upside,
                    confidence=0.82,
                )
            )

        if {
            "estimated_revenue",
            "estimated_gp",
        }.issubset(df.columns):
            budget_grouped = (
                df.groupby(dimension, dropna=False)
                .agg(
                    Actual_GP=("actual_gp", "sum"),
                    Budget_GP=("estimated_gp", "sum"),
                )
                .reset_index()
            )
            budget_grouped["GP Variance"] = (
                budget_grouped["Actual_GP"]
                - budget_grouped["Budget_GP"]
            )

            outperformance = budget_grouped[
                budget_grouped["GP Variance"] > 0
            ].sort_values(
                "GP Variance",
                ascending=False,
            ).head(2)

            for _, budget_row in outperformance.iterrows():
                base_row = grouped[
                    grouped[dimension]
                    == budget_row[dimension]
                ]
                if base_row.empty:
                    continue

                row = base_row.iloc[0]
                opportunities.append(
                    self._build(
                        category="Budget Outperformance",
                        priority="Medium",
                        dimension=dimension,
                        value=str(row[dimension]),
                        title=(
                            "Protect and expand above-budget performance"
                        ),
                        rationale=(
                            f"Gross Profit is "
                            f"${budget_row['GP Variance']:,.0f} "
                            "above Budget."
                        ),
                        recommended_action=(
                            "Protect pricing and capacity, confirm recurring "
                            "drivers and incorporate them into forecast assumptions."
                        ),
                        row=row,
                        revenue_upside=0.0,
                        gp_upside=float(
                            budget_row["GP Variance"]
                            * 0.50
                        ),
                        confidence=0.86,
                    )
                )

        return opportunities

    @staticmethod
    def _ranking_score(
        item: BusinessOpportunity,
    ) -> float:
        priority_score = {
            "Critical": 500,
            "High": 400,
            "Medium": 300,
            "Low": 200,
        }.get(item.priority, 200)

        return (
            priority_score
            + item.estimated_gp_upside / 100000
            + item.confidence_score * 10
        )

    @staticmethod
    def _build(
        *,
        category: str,
        priority: str,
        dimension: str,
        value: str,
        title: str,
        rationale: str,
        recommended_action: str,
        row,
        revenue_upside: float,
        gp_upside: float,
        confidence: float,
    ) -> BusinessOpportunity:
        opportunity_id = sha1(
            f"{category}|{dimension}|{value}".encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return BusinessOpportunity(
            opportunity_id=opportunity_id,
            category=category,
            priority=priority,
            dimension=dimension,
            value=value,
            title=title,
            rationale=rationale,
            recommended_action=recommended_action,
            revenue=float(row["Revenue"]),
            gross_profit=float(row["GP"]),
            margin=float(row["Margin"]),
            shipments=float(row["Shipments"]),
            revenue_share=float(
                row["Revenue Share"]
            ),
            estimated_revenue_upside=revenue_upside,
            estimated_gp_upside=gp_upside,
            confidence_score=confidence,
        )
