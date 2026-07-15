from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveCommentary:
    performance: str
    drivers: str
    risks: str
    actions: str


class ExecutiveCommentaryEngine:
    """Creates deterministic CFO commentary from period-aligned KPIs."""

    def generate(
        self,
        *,
        period_label: str,
        comparison_label: str,
        summary: dict,
        variance: dict,
    ) -> ExecutiveCommentary:
        revenue_pct = float(
            variance.get(
                "revenue_variance_pct",
                0.0,
            )
        )
        gp_pct = float(
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

        performance = (
            f"For {period_label}, Revenue is "
            f"{abs(revenue_pct):.1%} "
            f"{'above' if revenue_pct >= 0 else 'below'} "
            f"{comparison_label}; Gross Profit is "
            f"{abs(gp_pct):.1%} "
            f"{'above' if gp_pct >= 0 else 'below'} target. "
            f"Margin variance is {margin_pp * 100:+.2f} pp."
        )

        if revenue_pct >= 0 and gp_pct < 0:
            drivers = (
                "Revenue growth is not converting into Gross Profit, "
                "indicating adverse mix, pricing pressure or higher "
                "direct freight costs."
            )
        elif revenue_pct < 0 and gp_pct >= 0:
            drivers = (
                "Lower Revenue is being offset by stronger unit economics "
                "and cost discipline."
            )
        elif revenue_pct >= 0 and gp_pct >= 0:
            drivers = (
                "Revenue and Gross Profit are both ahead of target, "
                "indicating positive volume and commercial performance."
            )
        else:
            drivers = (
                "Revenue and Gross Profit are both below target; "
                "volume, pricing and trade-lane performance require review."
            )

        risks = (
            "Margin deterioration is the primary risk."
            if margin_pp < 0
            else "No immediate margin deterioration is detected."
        )

        if gp_pct < 0 or margin_pp < 0:
            actions = (
                "Review pricing, shipment-level profitability, top customers "
                "and trade lanes; validate cost accruals and corrective actions."
            )
        else:
            actions = (
                "Protect current pricing and capacity discipline, while "
                "monitoring concentration and sustainability of performance."
            )

        return ExecutiveCommentary(
            performance=performance,
            drivers=drivers,
            risks=risks,
            actions=actions,
        )
