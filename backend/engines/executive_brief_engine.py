from __future__ import annotations

from models.executive_alert import ExecutiveAlert
from models.executive_brief import ExecutiveBrief
from models.management_action import ManagementAction


class ExecutiveBriefEngine:
    """Builds a CFO-ready period summary from validated outputs."""

    def build(
        self,
        *,
        period_label: str,
        comparison_label: str,
        summary: dict,
        variance: dict,
        alerts: list[ExecutiveAlert],
        actions: list[ManagementAction],
    ) -> ExecutiveBrief:
        revenue = float(
            summary.get("actual_revenue", 0.0)
        )
        gp = float(
            summary.get("actual_gp", 0.0)
        )
        margin = float(
            summary.get("actual_gp_margin", 0.0)
        )
        shipments = float(
            summary.get("shipments", 0.0)
        )
        tons = float(
            summary.get("weight_tons", 0.0)
        )
        teus = float(
            summary.get("teus", 0.0)
        )

        revenue_var = float(
            variance.get(
                "revenue_variance_pct",
                0.0,
            )
        )
        gp_var = float(
            variance.get(
                "gp_variance_pct",
                0.0,
            )
        )
        margin_pp = float(
            variance.get(
                "margin_variance_pp",
                0.0,
            )
        )

        headline = self._headline(
            revenue_var=revenue_var,
            gp_var=gp_var,
            margin_pp=margin_pp,
        )

        financial_summary = (
            f"Revenue closed at ${revenue:,.0f}, "
            f"{abs(revenue_var):.1%} "
            f"{'above' if revenue_var >= 0 else 'below'} "
            f"{comparison_label}. Gross Profit was ${gp:,.0f}, "
            f"{abs(gp_var):.1%} "
            f"{'above' if gp_var >= 0 else 'below'} target. "
            f"GP Margin finished at {margin:.1%}, "
            f"{margin_pp * 100:+.2f} pp versus target."
        )

        operational_summary = (
            f"The period recorded {shipments:,.0f} shipments, "
            f"{tons:,.1f} tons and {teus:,.1f} TEUs."
        )

        risks = [
            alert.message
            for alert in alerts
            if alert.severity in {
                "critical",
                "high",
                "medium",
            }
        ][:5]

        opportunities = [
            alert.message
            for alert in alerts
            if alert.severity == "success"
        ][:5]

        open_actions = [
            action
            for action in actions
            if action.status
            not in {
                "Completed",
                "Cancelled",
            }
        ]

        action_lines = [
            (
                f"{action.title} — "
                f"{action.owner} — "
                f"{action.status}"
                + (
                    f" — due {action.due_date}"
                    if action.due_date
                    else ""
                )
            )
            for action in open_actions[:8]
        ]

        return ExecutiveBrief(
            title="Executive Financial Brief",
            period_label=period_label,
            comparison_label=comparison_label,
            headline=headline,
            financial_summary=financial_summary,
            operational_summary=operational_summary,
            risks=risks,
            opportunities=opportunities,
            actions=action_lines,
            kpis={
                "Revenue": revenue,
                "Revenue Variance %": revenue_var,
                "Gross Profit": gp,
                "GP Variance %": gp_var,
                "GP Margin": margin,
                "Margin Variance pp": margin_pp,
                "Shipments": shipments,
                "Tons": tons,
                "TEUs": teus,
            },
        )

    @staticmethod
    def _headline(
        *,
        revenue_var: float,
        gp_var: float,
        margin_pp: float,
    ) -> str:
        if (
            revenue_var >= 0
            and gp_var >= 0
            and margin_pp >= 0
        ):
            return (
                "Performance is ahead of target across Revenue, "
                "Gross Profit and Margin."
            )

        if (
            revenue_var >= 0
            and (
                gp_var < 0
                or margin_pp < 0
            )
        ):
            return (
                "Revenue is ahead of target, but profitability "
                "conversion requires management attention."
            )

        if (
            revenue_var < 0
            and gp_var >= 0
        ):
            return (
                "Revenue is below target, while cost discipline "
                "is protecting Gross Profit."
            )

        return (
            "Revenue and profitability are below target and "
            "require corrective commercial and operational action."
        )
