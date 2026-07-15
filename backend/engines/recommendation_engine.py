from __future__ import annotations

import pandas as pd


class RecommendationEngine:
    """Converts deterministic insights into prioritized business actions."""

    PRIORITY_ORDER = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "Normal": 0,
    }

    def generate_recommendations(
        self,
        overall_insights: pd.DataFrame,
        dimension_insights: pd.DataFrame,
        alert_insights: pd.DataFrame,
    ) -> pd.DataFrame:
        """Generates consolidated recommendations from available insights."""

        recommendations: list[dict] = []

        recommendations.extend(
            self._recommend_from_overall_insights(
                overall_insights
            )
        )

        recommendations.extend(
            self._recommend_from_dimension_insights(
                dimension_insights
            )
        )

        recommendations.extend(
            self._recommend_from_alert_insights(
                alert_insights
            )
        )

        if not recommendations:
            return self._empty_recommendations()

        result = pd.DataFrame(recommendations)

        result["Priority_Order"] = (
            result["Priority"]
            .map(self.PRIORITY_ORDER)
            .fillna(0)
        )

        result = (
            result.sort_values(
                [
                    "Priority_Order",
                    "Direction",
                    "Business_Area",
                ],
                ascending=[False, True, True],
            )
            .drop(columns=["Priority_Order"])
            .drop_duplicates(
                subset=[
                    "Business_Area",
                    "Business_Value",
                    "Recommended_Action",
                ]
            )
            .reset_index(drop=True)
        )

        result.insert(
            0,
            "Recommendation_ID",
            [
                f"REC-{index:04d}"
                for index in range(1, len(result) + 1)
            ],
        )

        return result

    def priority_summary(
        self,
        recommendations: pd.DataFrame,
    ) -> dict:
        """Summarizes recommendation volume and priority."""

        if recommendations.empty:
            return {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "finance": 0,
                "commercial": 0,
                "operations": 0,
            }

        return {
            "total": int(len(recommendations)),
            "critical": int(
                (
                    recommendations["Priority"]
                    == "Critical"
                ).sum()
            ),
            "high": int(
                (
                    recommendations["Priority"]
                    == "High"
                ).sum()
            ),
            "medium": int(
                (
                    recommendations["Priority"]
                    == "Medium"
                ).sum()
            ),
            "finance": int(
                (
                    recommendations["Business_Area"]
                    == "Finance"
                ).sum()
            ),
            "commercial": int(
                (
                    recommendations["Business_Area"]
                    == "Commercial"
                ).sum()
            ),
            "operations": int(
                (
                    recommendations["Business_Area"]
                    == "Operations"
                ).sum()
            ),
        }

    def immediate_actions(
        self,
        recommendations: pd.DataFrame,
        limit: int = 5,
    ) -> pd.DataFrame:
        """Returns the highest-priority immediate actions."""

        if recommendations.empty:
            return recommendations.copy()

        urgent = recommendations[
            recommendations["Priority"].isin(
                ["Critical", "High"]
            )
        ].copy()

        if urgent.empty:
            urgent = recommendations.copy()

        urgent["Priority_Order"] = (
            urgent["Priority"]
            .map(self.PRIORITY_ORDER)
            .fillna(0)
        )

        return (
            urgent.sort_values(
                "Priority_Order",
                ascending=False,
            )
            .drop(columns=["Priority_Order"])
            .head(limit)
            .reset_index(drop=True)
        )

    def action_plan_by_owner(
        self,
        recommendations: pd.DataFrame,
    ) -> pd.DataFrame:
        """Creates a management action-plan summary."""

        if recommendations.empty:
            return pd.DataFrame(
                columns=[
                    "Action_Owner",
                    "Total_Actions",
                    "Critical",
                    "High",
                    "Medium",
                    "Main_Area",
                ]
            )

        working = recommendations.copy()

        owner_summary = (
            working.groupby(
                "Action_Owner",
                dropna=False,
            )
            .agg(
                Total_Actions=(
                    "Recommendation_ID",
                    "count",
                ),
                Critical=(
                    "Priority",
                    lambda values: int(
                        (values == "Critical").sum()
                    ),
                ),
                High=(
                    "Priority",
                    lambda values: int(
                        (values == "High").sum()
                    ),
                ),
                Medium=(
                    "Priority",
                    lambda values: int(
                        (values == "Medium").sum()
                    ),
                ),
                Main_Area=(
                    "Business_Area",
                    lambda values: (
                        values.mode().iloc[0]
                        if not values.mode().empty
                        else "Unassigned"
                    ),
                ),
            )
            .reset_index()
        )

        return owner_summary.sort_values(
            [
                "Critical",
                "High",
                "Total_Actions",
            ],
            ascending=False,
        ).reset_index(drop=True)

    def executive_action_bullets(
        self,
        recommendations: pd.DataFrame,
        limit: int = 5,
    ) -> list[str]:
        """Creates concise management action bullets."""

        immediate = self.immediate_actions(
            recommendations,
            limit=limit,
        )

        bullets: list[str] = []

        for _, row in immediate.iterrows():
            bullets.append(
                f"{row['Priority']} priority — "
                f"{row['Business_Area']}: "
                f"{row['Recommended_Action']} "
                f"Owner: {row['Action_Owner']}."
            )

        if not bullets:
            bullets.append(
                "No material corrective actions were identified."
            )

        return bullets

    def _recommend_from_overall_insights(
        self,
        insights: pd.DataFrame,
    ) -> list[dict]:
        if insights.empty:
            return []

        recommendations: list[dict] = []

        for _, row in insights.iterrows():
            category = str(row["Category"])
            direction = str(row["Direction"])
            severity = str(row["Severity"])

            if category == "Revenue":
                if direction == "Unfavorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Commercial",
                            business_value="Total Revenue",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Review shipment volume, pricing, "
                                "customer losses and sales pipeline."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Commercial Director",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Recover revenue gap and protect "
                                "future commercial performance."
                            ),
                        )
                    )
                elif direction == "Favorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Commercial",
                            business_value="Total Revenue",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Validate whether revenue upside is "
                                "driven by sustainable volume, "
                                "pricing or customer mix."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Commercial Controller",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Preserve and replicate favorable "
                                "revenue drivers."
                            ),
                        )
                    )

            elif category == "Cost":
                if direction == "Unfavorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Operations",
                            business_value="Total Cost",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Review carrier rates, purchased "
                                "transportation, operational "
                                "inefficiencies and accrual accuracy."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Operations Manager",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Reduce cost overruns and improve "
                                "cost-to-serve."
                            ),
                        )
                    )
                elif direction == "Favorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Finance",
                            business_value="Total Cost",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Validate whether savings are "
                                "recurring and confirm that service "
                                "quality was not affected."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Business Controller",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Confirm sustainable savings and "
                                "avoid under-accrual risk."
                            ),
                        )
                    )

            elif category == "Gross Profit":
                if direction == "Unfavorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Finance",
                            business_value="Gross Profit",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Prioritize the largest negative GP "
                                "drivers and assign corrective action "
                                "owners."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Finance Manager",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Recover GP and improve financial "
                                "performance against Budget."
                            ),
                        )
                    )
                elif direction == "Favorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Finance",
                            business_value="Gross Profit",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Identify and document the main "
                                "drivers behind the favorable GP "
                                "result."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Business Controller",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Replicate profitable practices "
                                "across other segments."
                            ),
                        )
                    )

            elif category == "GP Margin":
                if direction == "Unfavorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Commercial",
                            business_value="GP Margin",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Review pricing, customer mix, "
                                "carrier mix and cost-to-serve."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Commercial Director",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Restore margin and improve revenue "
                                "quality."
                            ),
                        )
                    )
                elif direction == "Favorable":
                    recommendations.append(
                        self._build_recommendation(
                            source="Overall Insight",
                            business_area="Finance",
                            business_value="GP Margin",
                            priority=severity,
                            direction=direction,
                            action=(
                                "Validate whether margin improvement "
                                "comes from pricing, mix or temporary "
                                "cost effects."
                            ),
                            rationale=str(row["Evidence"]),
                            owner="Business Controller",
                            timeframe=self._timeframe(
                                severity
                            ),
                            expected_impact=(
                                "Confirm sustainability of margin "
                                "improvement."
                            ),
                        )
                    )

        return recommendations

    def _recommend_from_dimension_insights(
        self,
        insights: pd.DataFrame,
    ) -> list[dict]:
        if insights.empty:
            return []

        recommendations: list[dict] = []

        for _, row in insights.iterrows():
            dimension = str(row["Dimension"])
            value = str(row["Business_Value"])
            direction = str(row["Direction"])
            severity = str(row["Severity"])

            area, owner = self._area_and_owner(
                dimension
            )

            if direction == "Unfavorable":
                action = self._negative_dimension_action(
                    dimension,
                    value,
                )
                expected_impact = (
                    "Reduce the unfavorable variance and "
                    "improve GP performance."
                )
            elif direction == "Favorable":
                action = self._positive_dimension_action(
                    dimension,
                    value,
                )
                expected_impact = (
                    "Preserve and replicate the favorable "
                    "business driver."
                )
            else:
                action = (
                    f"Continue monitoring {value} and validate "
                    "its financial classification."
                )
                expected_impact = (
                    "Maintain financial visibility."
                )

            recommendations.append(
                self._build_recommendation(
                    source="Dimension Insight",
                    business_area=area,
                    business_value=value,
                    priority=severity,
                    direction=direction,
                    action=action,
                    rationale=str(row["Evidence"]),
                    owner=owner,
                    timeframe=self._timeframe(
                        severity
                    ),
                    expected_impact=expected_impact,
                )
            )

        return recommendations

    def _recommend_from_alert_insights(
        self,
        insights: pd.DataFrame,
    ) -> list[dict]:
        if insights.empty:
            return []

        recommendations: list[dict] = []

        for _, row in insights.iterrows():
            dimension = str(row["Dimension"])
            value = str(row["Business_Value"])
            severity = str(row["Severity"])
            direction = str(row["Direction"])

            area, default_owner = self._area_and_owner(
                dimension
            )

            escalation_owner = str(
                row.get(
                    "Escalation_Owner",
                    default_owner,
                )
            )

            if direction == "Unfavorable":
                action = (
                    f"Open a formal action plan for {value}, "
                    "validate root cause and assign a recovery "
                    "target."
                )
                expected_impact = (
                    "Mitigate the material downside and restore "
                    "performance."
                )
            else:
                action = (
                    f"Validate the sustainability of the material "
                    f"favorable variance generated by {value}."
                )
                expected_impact = (
                    "Protect favorable performance and identify "
                    "replication opportunities."
                )

            recommendations.append(
                self._build_recommendation(
                    source="Material Alert",
                    business_area=area,
                    business_value=value,
                    priority=severity,
                    direction=direction,
                    action=action,
                    rationale=str(row["Evidence"]),
                    owner=escalation_owner,
                    timeframe=self._timeframe(
                        severity
                    ),
                    expected_impact=expected_impact,
                )
            )

        return recommendations

    @staticmethod
    def _build_recommendation(
        source: str,
        business_area: str,
        business_value: str,
        priority: str,
        direction: str,
        action: str,
        rationale: str,
        owner: str,
        timeframe: str,
        expected_impact: str,
    ) -> dict:
        return {
            "Source": source,
            "Business_Area": business_area,
            "Business_Value": business_value,
            "Priority": priority,
            "Direction": direction,
            "Recommended_Action": action,
            "Business_Rationale": rationale,
            "Action_Owner": owner,
            "Timeframe": timeframe,
            "Expected_Impact": expected_impact,
            "Status": "Open",
        }

    @staticmethod
    def _timeframe(priority: str) -> str:
        timeframe_map = {
            "Critical": "Immediate / 24 hours",
            "High": "Within 3 business days",
            "Medium": "Within 10 business days",
            "Low": "Monitor during current month",
            "Normal": "No immediate action",
        }

        return timeframe_map.get(
            priority,
            "Monitor during current month",
        )

    @staticmethod
    def _area_and_owner(
        dimension: str,
    ) -> tuple[str, str]:
        commercial_dimensions = {
            "customer",
            "product",
            "trade_lane",
        }

        operational_dimensions = {
            "forwarder",
            "origin",
            "destination",
            "mode",
        }

        if dimension in commercial_dimensions:
            return "Commercial", "Commercial Director"

        if dimension in operational_dimensions:
            return "Operations", "Operations Manager"

        return "Finance", "Business Controller"

    @staticmethod
    def _negative_dimension_action(
        dimension: str,
        value: str,
    ) -> str:
        actions = {
            "customer": (
                f"Review pricing, shipment mix, contractual terms "
                f"and cost-to-serve for customer {value}."
            ),
            "product": (
                f"Review profitability model, volume and pricing "
                f"for product {value}."
            ),
            "trade_lane": (
                f"Review pricing, carrier costs and volume mix "
                f"for trade lane {value}."
            ),
            "forwarder": (
                f"Review rates, service performance and cost "
                f"allocation for forwarder {value}."
            ),
            "origin": (
                f"Review operational execution and supplier costs "
                f"at origin {value}."
            ),
            "destination": (
                f"Review destination costs, handling and service "
                f"performance for {value}."
            ),
            "mode": (
                f"Prepare a recovery plan for {value} freight "
                "performance."
            ),
            "period": (
                f"Investigate the unfavorable performance recorded "
                f"in period {value}."
            ),
        }

        return actions.get(
            dimension,
            f"Investigate the unfavorable variance for {value}.",
        )

    @staticmethod
    def _positive_dimension_action(
        dimension: str,
        value: str,
    ) -> str:
        actions = {
            "customer": (
                f"Validate and replicate profitable commercial "
                f"conditions observed for customer {value}."
            ),
            "product": (
                f"Identify the favorable volume, pricing or cost "
                f"drivers for product {value}."
            ),
            "trade_lane": (
                f"Validate whether the favorable result for trade "
                f"lane {value} can be replicated."
            ),
            "forwarder": (
                f"Assess whether favorable conditions with "
                f"forwarder {value} can be extended."
            ),
            "origin": (
                f"Document the operational practices driving "
                f"favorable performance at origin {value}."
            ),
            "destination": (
                f"Validate the positive execution drivers at "
                f"destination {value}."
            ),
            "mode": (
                f"Identify and replicate the favorable performance "
                f"drivers in {value} freight."
            ),
            "period": (
                f"Document the favorable business drivers observed "
                f"in period {value}."
            ),
        }

        return actions.get(
            dimension,
            f"Validate and replicate the favorable result for {value}.",
        )

    @staticmethod
    def _empty_recommendations() -> pd.DataFrame:
        return pd.DataFrame(
            columns=[
                "Recommendation_ID",
                "Source",
                "Business_Area",
                "Business_Value",
                "Priority",
                "Direction",
                "Recommended_Action",
                "Business_Rationale",
                "Action_Owner",
                "Timeframe",
                "Expected_Impact",
                "Status",
            ]
        )