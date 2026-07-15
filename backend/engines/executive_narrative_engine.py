
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class NarrativePackage:
    """Deterministic executive communication package."""

    executive_summary: str
    cfo_email_subject: str
    cfo_email_body: str
    meeting_talking_points: list[str]
    management_actions: list[str]


class ExecutiveNarrativeEngine:
    """Builds deterministic executive narratives from validated engine outputs."""

    def build_package(
        self,
        variance_summary: dict,
        overall_insights: pd.DataFrame,
        dimension_insights: pd.DataFrame,
        recommendations: pd.DataFrame,
        selected_dimension_label: str,
        company_name: str = "Financial Intelligence Platform",
        reporting_period: str = "Current Period",
    ) -> NarrativePackage:
        executive_summary = self._build_executive_summary(
            variance_summary=variance_summary,
            dimension_insights=dimension_insights,
            selected_dimension_label=selected_dimension_label,
        )

        management_actions = self._build_management_actions(
            recommendations=recommendations,
            limit=5,
        )

        talking_points = self._build_talking_points(
            variance_summary=variance_summary,
            overall_insights=overall_insights,
            dimension_insights=dimension_insights,
            recommendations=recommendations,
            selected_dimension_label=selected_dimension_label,
        )

        subject = (
            f"{company_name} | Financial Performance Summary | "
            f"{reporting_period}"
        )

        email_body = self._build_cfo_email(
            company_name=company_name,
            reporting_period=reporting_period,
            executive_summary=executive_summary,
            management_actions=management_actions,
        )

        return NarrativePackage(
            executive_summary=executive_summary,
            cfo_email_subject=subject,
            cfo_email_body=email_body,
            meeting_talking_points=talking_points,
            management_actions=management_actions,
        )

    def build_narrative_table(
        self,
        variance_summary: dict,
        overall_insights: pd.DataFrame,
        dimension_insights: pd.DataFrame,
        recommendations: pd.DataFrame,
        selected_dimension_label: str,
    ) -> pd.DataFrame:
        """Returns narrative sections as a structured table."""

        package = self.build_package(
            variance_summary=variance_summary,
            overall_insights=overall_insights,
            dimension_insights=dimension_insights,
            recommendations=recommendations,
            selected_dimension_label=selected_dimension_label,
        )

        records = [
            {
                "Section": "Executive Summary",
                "Narrative": package.executive_summary,
            }
        ]

        records.extend(
            {
                "Section": "Management Action",
                "Narrative": action,
            }
            for action in package.management_actions
        )

        records.extend(
            {
                "Section": "Meeting Talking Point",
                "Narrative": point,
            }
            for point in package.meeting_talking_points
        )

        return pd.DataFrame(records)

    def _build_executive_summary(
        self,
        variance_summary: dict,
        dimension_insights: pd.DataFrame,
        selected_dimension_label: str,
    ) -> str:
        revenue_variance = float(
            variance_summary["revenue_variance"]
        )
        revenue_variance_pct = float(
            variance_summary["revenue_variance_pct"]
        )
        cost_variance = float(
            variance_summary["cost_variance"]
        )
        cost_variance_pct = float(
            variance_summary["cost_variance_pct"]
        )
        gp_variance = float(
            variance_summary["gp_variance"]
        )
        gp_variance_pct = float(
            variance_summary["gp_variance_pct"]
        )
        margin_variance_pp = float(
            variance_summary["margin_variance_pp"]
        )

        revenue_text = self._variance_sentence(
            metric="Revenue",
            amount=revenue_variance,
            percentage=revenue_variance_pct,
            favorable_when_positive=True,
        )

        cost_text = self._variance_sentence(
            metric="Cost",
            amount=cost_variance,
            percentage=cost_variance_pct,
            favorable_when_positive=False,
        )

        gp_text = self._variance_sentence(
            metric="Gross Profit",
            amount=gp_variance,
            percentage=gp_variance_pct,
            favorable_when_positive=True,
        )

        margin_direction = (
            "improved"
            if margin_variance_pp > 0
            else "deteriorated"
            if margin_variance_pp < 0
            else "remained stable"
        )

        margin_text = (
            f"GP Margin {margin_direction} by "
            f"{abs(margin_variance_pp) * 100:.2f} percentage points "
            "versus Budget."
        )

        driver_text = ""

        if not dimension_insights.empty:
            top_driver = dimension_insights.iloc[0]
            driver_text = (
                f" The largest {selected_dimension_label.lower()} driver "
                f"was {top_driver['Business_Value']}, with a GP variance "
                f"of ${float(top_driver['GP_Variance']):,.0f}."
            )

        return (
            f"{revenue_text} {cost_text} {gp_text} {margin_text}"
            f"{driver_text}"
        )

    def _build_cfo_email(
        self,
        company_name: str,
        reporting_period: str,
        executive_summary: str,
        management_actions: list[str],
    ) -> str:
        action_lines = "\n".join(
            f"- {action}" for action in management_actions
        )

        if not action_lines:
            action_lines = "- No immediate material actions identified."

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        return (
            f"Dear CFO,\n\n"
            f"Please find below the financial performance summary for "
            f"{company_name} — {reporting_period}.\n\n"
            f"Executive summary\n"
            f"{executive_summary}\n\n"
            f"Priority management actions\n"
            f"{action_lines}\n\n"
            f"The analysis was generated from validated Actual vs Budget "
            f"results and deterministic business rules. All figures should "
            f"be reviewed by Finance before external distribution.\n\n"
            f"Generated: {generated_at}\n\n"
            f"Regards,\n"
            f"Business Controlling"
        )

    def _build_management_actions(
        self,
        recommendations: pd.DataFrame,
        limit: int,
    ) -> list[str]:
        if recommendations.empty:
            return []

        priority_order = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Normal": 0,
        }

        working = recommendations.copy()
        working["Priority_Order"] = (
            working["Priority"]
            .map(priority_order)
            .fillna(0)
        )

        working = (
            working.sort_values(
                ["Priority_Order", "Business_Area"],
                ascending=[False, True],
            )
            .head(limit)
        )

        actions: list[str] = []

        for _, row in working.iterrows():
            actions.append(
                f"{row['Priority']} — {row['Business_Area']}: "
                f"{row['Recommended_Action']} "
                f"Owner: {row['Action_Owner']}; "
                f"timeframe: {row['Timeframe']}."
            )

        return actions

    def _build_talking_points(
        self,
        variance_summary: dict,
        overall_insights: pd.DataFrame,
        dimension_insights: pd.DataFrame,
        recommendations: pd.DataFrame,
        selected_dimension_label: str,
    ) -> list[str]:
        points: list[str] = []

        gp_variance = float(
            variance_summary["gp_variance"]
        )
        gp_direction = (
            "favorable"
            if gp_variance >= 0
            else "unfavorable"
        )

        points.append(
            f"Gross Profit variance is {gp_direction} by "
            f"${abs(gp_variance):,.0f} versus Budget."
        )

        if not dimension_insights.empty:
            top_driver = dimension_insights.iloc[0]
            points.append(
                f"Main {selected_dimension_label.lower()} driver: "
                f"{top_driver['Business_Value']} "
                f"(${float(top_driver['GP_Variance']):,.0f} GP variance)."
            )

        if not overall_insights.empty:
            critical = overall_insights[
                overall_insights["Severity"].isin(
                    ["Critical", "High"]
                )
            ]

            for _, row in critical.head(2).iterrows():
                points.append(
                    f"{row['Category']}: {row['Headline']}"
                )

        if not recommendations.empty:
            top_action = recommendations.iloc[0]
            points.append(
                f"Immediate action: {top_action['Recommended_Action']} "
                f"Owner: {top_action['Action_Owner']}."
            )

        return points

    @staticmethod
    def _variance_sentence(
        metric: str,
        amount: float,
        percentage: float,
        favorable_when_positive: bool,
    ) -> str:
        if amount == 0:
            return f"{metric} was on Budget."

        if favorable_when_positive:
            direction = (
                "above Budget"
                if amount > 0
                else "below Budget"
            )
        else:
            direction = (
                "above Budget"
                if amount > 0
                else "below Budget"
            )

        return (
            f"{metric} finished {direction} by "
            f"${abs(amount):,.0f} ({percentage:+.1%})."
        )
