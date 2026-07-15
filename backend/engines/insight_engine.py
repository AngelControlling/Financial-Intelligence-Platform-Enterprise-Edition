from __future__ import annotations

import pandas as pd


class InsightEngine:
    """Converts deterministic financial results into structured insights."""

    def overall_insights(
        self,
        variance_summary: dict,
    ) -> pd.DataFrame:
        """Creates consolidated financial insights."""

        insights: list[dict] = []

        insights.append(
            self._build_metric_insight(
                category="Revenue",
                amount=variance_summary["revenue_variance"],
                percentage=variance_summary[
                    "revenue_variance_pct"
                ],
                favorable_when_positive=True,
                evidence=(
                    f"Actual Revenue: "
                    f"${variance_summary['actual_revenue']:,.0f} | "
                    f"Budget Revenue: "
                    f"${variance_summary['budget_revenue']:,.0f}"
                ),
                positive_action=(
                    "Validate whether the favorable revenue result "
                    "is driven by sustainable volume, pricing or mix."
                ),
                negative_action=(
                    "Review volume, pricing, customer losses and "
                    "commercial execution."
                ),
            )
        )

        insights.append(
            self._build_metric_insight(
                category="Cost",
                amount=variance_summary["cost_variance"],
                percentage=variance_summary[
                    "cost_variance_pct"
                ],
                favorable_when_positive=False,
                evidence=(
                    f"Actual Cost: "
                    f"${variance_summary['actual_cost']:,.0f} | "
                    f"Budget Cost: "
                    f"${variance_summary['budget_cost']:,.0f}"
                ),
                positive_action=(
                    "Confirm whether cost savings are recurring and "
                    "do not affect operational service."
                ),
                negative_action=(
                    "Review carrier rates, purchased transportation, "
                    "operational inefficiencies and accrual accuracy."
                ),
            )
        )

        insights.append(
            self._build_metric_insight(
                category="Gross Profit",
                amount=variance_summary["gp_variance"],
                percentage=variance_summary[
                    "gp_variance_pct"
                ],
                favorable_when_positive=True,
                evidence=(
                    f"Actual GP: "
                    f"${variance_summary['actual_gp']:,.0f} | "
                    f"Budget GP: "
                    f"${variance_summary['budget_gp']:,.0f}"
                ),
                positive_action=(
                    "Identify the customers, products and trade lanes "
                    "responsible for the favorable GP result."
                ),
                negative_action=(
                    "Prioritize the largest unfavorable GP drivers "
                    "and define corrective actions."
                ),
            )
        )

        margin_variance = variance_summary[
            "margin_variance_pp"
        ]

        margin_direction = (
            "Favorable"
            if margin_variance > 0
            else "Unfavorable"
            if margin_variance < 0
            else "Neutral"
        )

        margin_severity = self._severity_from_percentage(
            abs(margin_variance)
        )

        insights.append(
            {
                "Category": "GP Margin",
                "Direction": margin_direction,
                "Severity": margin_severity,
                "Headline": (
                    f"GP Margin changed by "
                    f"{margin_variance * 100:+.2f} percentage points."
                ),
                "Evidence": (
                    f"Actual GP Margin: "
                    f"{variance_summary['actual_gp_margin']:.2%} | "
                    f"Budget GP Margin: "
                    f"{variance_summary['budget_gp_margin']:.2%}"
                ),
                "Recommended_Focus": (
                    "Review pricing, customer mix and cost-to-serve."
                    if margin_variance < 0
                    else
                    "Confirm whether margin improvement is sustainable."
                ),
                "Impact_Amount": margin_variance,
                "Impact_Percentage": margin_variance,
            }
        )

        return pd.DataFrame(insights)

    def dimension_insights(
        self,
        dimension_variance: pd.DataFrame,
        dimension: str,
        limit: int = 5,
    ) -> pd.DataFrame:
        """Creates insights from GP variance by business dimension."""

        required_columns = {
            dimension,
            "GP_Variance",
            "GP_Variance_Pct",
            "Margin_Variance_PP",
            "Impact_Contribution",
            "Direction",
        }

        missing_columns = sorted(
            required_columns
            - set(dimension_variance.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas para Insight Engine: "
                + ", ".join(missing_columns)
            )

        insights: list[dict] = []

        ranked_data = (
            dimension_variance
            .sort_values(
                "Absolute_GP_Impact",
                ascending=False,
            )
            .head(limit)
        )

        for _, row in ranked_data.iterrows():
            business_value = str(row[dimension])
            gp_variance = float(row["GP_Variance"])
            gp_variance_pct = float(
                row["GP_Variance_Pct"]
            )
            margin_variance_pp = float(
                row["Margin_Variance_PP"]
            )
            contribution = float(
                row["Impact_Contribution"]
            )
            direction = str(row["Direction"])

            severity = self._severity_from_percentage(
                max(
                    abs(gp_variance_pct),
                    abs(contribution),
                )
            )

            if direction == "Favorable":
                recommended_focus = (
                    "Validate the driver and determine whether it can "
                    "be replicated across other business segments."
                )
            elif direction == "Unfavorable":
                recommended_focus = (
                    "Investigate pricing, volume, cost and mix drivers "
                    "and define a corrective action owner."
                )
            else:
                recommended_focus = (
                    "Monitor performance; no material directional "
                    "impact was identified."
                )

            insights.append(
                {
                    "Dimension": dimension,
                    "Business_Value": business_value,
                    "Direction": direction,
                    "Severity": severity,
                    "Headline": (
                        f"{business_value} generated a GP variance of "
                        f"${gp_variance:,.0f}."
                    ),
                    "Evidence": (
                        f"GP variance: {gp_variance_pct:+.1%} | "
                        f"Margin variance: "
                        f"{margin_variance_pp * 100:+.2f} pp | "
                        f"Impact contribution: "
                        f"{contribution:.1%}"
                    ),
                    "Recommended_Focus": recommended_focus,
                    "GP_Variance": gp_variance,
                    "GP_Variance_Pct": gp_variance_pct,
                    "Margin_Variance_PP": margin_variance_pp,
                    "Impact_Contribution": contribution,
                }
            )

        return pd.DataFrame(insights)

    def material_alert_insights(
        self,
        material_alerts: pd.DataFrame,
        dimension: str,
        limit: int = 10,
    ) -> pd.DataFrame:
        """Converts material Rules Engine alerts into insights."""

        if material_alerts.empty:
            return pd.DataFrame(
                columns=[
                    "Dimension",
                    "Business_Value",
                    "Severity",
                    "Direction",
                    "Headline",
                    "Evidence",
                    "Escalation_Owner",
                    "Recommended_Focus",
                ]
            )

        required_columns = {
            "Business_Value",
            "Severity",
            "Direction",
            "Variance_Amount",
            "Variance_Percentage",
            "Rule_Triggered",
            "Escalation_Owner",
        }

        missing_columns = sorted(
            required_columns
            - set(material_alerts.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas de alertas para Insight Engine: "
                + ", ".join(missing_columns)
            )

        severity_order = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Normal": 0,
        }

        alerts = material_alerts.copy()

        alerts["Severity_Order"] = (
            alerts["Severity"]
            .map(severity_order)
            .fillna(0)
        )

        alerts = (
            alerts
            .sort_values(
                [
                    "Severity_Order",
                    "Absolute_Amount",
                ],
                ascending=[False, False],
            )
            .head(limit)
        )

        records: list[dict] = []

        for _, row in alerts.iterrows():
            direction = str(row["Direction"])

            if direction == "Unfavorable":
                recommended_focus = (
                    "Assign an owner, validate the root cause and "
                    "define a recovery action."
                )
            elif direction == "Favorable":
                recommended_focus = (
                    "Validate sustainability and assess replication "
                    "opportunities."
                )
            else:
                recommended_focus = (
                    "Monitor the variance and confirm classification."
                )

            records.append(
                {
                    "Dimension": dimension,
                    "Business_Value": row["Business_Value"],
                    "Severity": row["Severity"],
                    "Direction": direction,
                    "Headline": (
                        f"{row['Business_Value']} triggered a "
                        f"{str(row['Severity']).lower()} material alert."
                    ),
                    "Evidence": (
                        f"Variance: "
                        f"${row['Variance_Amount']:,.0f} | "
                        f"{row['Variance_Percentage']:+.1%} | "
                        f"{row['Rule_Triggered']}"
                    ),
                    "Escalation_Owner": row[
                        "Escalation_Owner"
                    ],
                    "Recommended_Focus": recommended_focus,
                }
            )

        return pd.DataFrame(records)

    def concentration_insight(
        self,
        pareto_data: pd.DataFrame,
        dimension: str,
    ) -> dict:
        """Explains variance concentration using Pareto results."""

        if pareto_data.empty:
            return {
                "Headline": "No variance concentration was detected.",
                "Evidence": "The selected dataset contains no impact.",
                "Primary_Drivers": 0,
                "Total_Drivers": 0,
                "Concentration": 0.0,
            }

        primary_drivers = pareto_data[
            pareto_data["Pareto_80_Flag"]
            == "Primary Driver"
        ]

        primary_count = int(len(primary_drivers))
        total_count = int(len(pareto_data))

        if primary_count == 0:
            primary_count = 1

        selected_primary = pareto_data.head(
            primary_count
        )

        concentration = float(
            selected_primary[
                "Pareto_Contribution"
            ].sum()
        )

        top_values = (
            selected_primary[dimension]
            .astype(str)
            .head(3)
            .tolist()
        )

        top_values_text = ", ".join(top_values)

        return {
            "Headline": (
                f"{primary_count} of {total_count} "
                f"{dimension} values explain approximately "
                f"{concentration:.1%} of the absolute GP variance."
            ),
            "Evidence": (
                f"Main drivers: {top_values_text}"
                if top_values_text
                else "No primary drivers available."
            ),
            "Primary_Drivers": primary_count,
            "Total_Drivers": total_count,
            "Concentration": concentration,
        }

    def executive_bullets(
        self,
        overall_insights: pd.DataFrame,
        dimension_insights: pd.DataFrame,
        concentration: dict,
    ) -> list[str]:
        """Creates concise deterministic executive bullets."""

        bullets: list[str] = []

        for _, row in overall_insights.iterrows():
            bullets.append(
                f"{row['Category']}: {row['Headline']} "
                f"Direction: {row['Direction']}."
            )

        if not dimension_insights.empty:
            top_driver = dimension_insights.iloc[0]

            bullets.append(
                f"Largest business driver: "
                f"{top_driver['Business_Value']} with "
                f"${top_driver['GP_Variance']:,.0f} GP variance."
            )

        bullets.append(concentration["Headline"])

        return bullets

    def _build_metric_insight(
        self,
        category: str,
        amount: float,
        percentage: float,
        favorable_when_positive: bool,
        evidence: str,
        positive_action: str,
        negative_action: str,
    ) -> dict:
        if amount == 0:
            direction = "Neutral"
        elif favorable_when_positive:
            direction = (
                "Favorable"
                if amount > 0
                else "Unfavorable"
            )
        else:
            direction = (
                "Unfavorable"
                if amount > 0
                else "Favorable"
            )

        severity = self._severity_from_percentage(
            abs(percentage)
        )

        if direction == "Favorable":
            recommended_focus = positive_action
        elif direction == "Unfavorable":
            recommended_focus = negative_action
        else:
            recommended_focus = (
                "Continue monitoring performance."
            )

        return {
            "Category": category,
            "Direction": direction,
            "Severity": severity,
            "Headline": (
                f"{category} variance was "
                f"${amount:,.0f} ({percentage:+.1%})."
            ),
            "Evidence": evidence,
            "Recommended_Focus": recommended_focus,
            "Impact_Amount": amount,
            "Impact_Percentage": percentage,
        }

    @staticmethod
    def _severity_from_percentage(
        absolute_percentage: float,
    ) -> str:
        if absolute_percentage >= 0.10:
            return "Critical"

        if absolute_percentage >= 0.05:
            return "High"

        if absolute_percentage >= 0.02:
            return "Medium"

        if absolute_percentage > 0:
            return "Low"

        return "Normal"