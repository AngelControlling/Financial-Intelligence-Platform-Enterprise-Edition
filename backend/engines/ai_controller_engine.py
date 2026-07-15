from __future__ import annotations

import pandas as pd

from engines.cfo_radar_engine import (
    CFORadarEngine,
)
from engines.opportunity_finder_engine import (
    OpportunityFinderEngine,
)
from engines.root_cause_engine import (
    RootCauseEngine,
)
from models.controller_narrative import (
    ControllerNarrative,
)


class AIControllerEngine:
    """
    Generates a Controller-style management narrative.

    This version is deterministic and does not require an external LLM.
    It combines period-aligned KPIs, root causes, opportunities and
    CFO Radar signals.
    """

    def generate(
        self,
        dataframe: pd.DataFrame,
        *,
        period_label: str,
        comparison_label: str,
        summary: dict,
        variance: dict,
        data_quality_score: float,
    ) -> ControllerNarrative:
        revenue = float(
            summary.get(
                "actual_revenue",
                0.0,
            )
        )
        gross_profit = float(
            summary.get(
                "actual_gp",
                0.0,
            )
        )
        margin = float(
            summary.get(
                "actual_gp_margin",
                0.0,
            )
        )

        revenue_variance = float(
            variance.get(
                "revenue_variance_pct",
                0.0,
            )
        )
        gp_variance = float(
            variance.get(
                "gp_variance_pct",
                0.0,
            )
        )
        margin_variance = float(
            variance.get(
                "margin_variance_pp",
                0.0,
            )
        )

        root_cause = RootCauseEngine().analyze(
            dataframe,
            metric="Gross Profit",
        )
        opportunities = (
            OpportunityFinderEngine()
            .find(
                dataframe,
                max_opportunities=5,
            )
        )
        radar = CFORadarEngine().evaluate(
            dataframe,
            summary=summary,
            variance=variance,
            data_quality_score=(
                data_quality_score
            ),
        )

        executive_summary = (
            self._executive_summary(
                period_label=period_label,
                comparison_label=comparison_label,
                revenue=revenue,
                gross_profit=gross_profit,
                margin=margin,
                revenue_variance=(
                    revenue_variance
                ),
                gp_variance=gp_variance,
                margin_variance=(
                    margin_variance
                ),
            )
        )

        what_happened = (
            self._what_happened(
                comparison_label=(
                    comparison_label
                ),
                revenue_variance=(
                    revenue_variance
                ),
                gp_variance=gp_variance,
                margin_variance=(
                    margin_variance
                ),
            )
        )

        why_it_happened = (
            self._why_it_happened(
                root_cause
            )
        )

        business_risk = (
            self._business_risk(
                radar
            )
        )

        actions = (
            self._recommended_actions(
                root_cause=root_cause,
                opportunities=opportunities,
                radar=radar,
            )
        )

        no_action_outlook = (
            self._no_action_outlook(
                revenue=revenue,
                gross_profit=gross_profit,
                gp_variance=gp_variance,
                margin_variance=(
                    margin_variance
                ),
            )
        )

        confidence = self._confidence(
            data_quality_score=(
                data_quality_score
            ),
            root_cause_count=len(
                root_cause.top_causes
            ),
            opportunity_count=len(
                opportunities
            ),
        )

        priority = self._priority(
            radar.overall_score
        )

        return ControllerNarrative(
            executive_summary=(
                executive_summary
            ),
            what_happened=what_happened,
            why_it_happened=(
                why_it_happened
            ),
            business_risk=business_risk,
            recommended_actions=actions,
            no_action_outlook=(
                no_action_outlook
            ),
            confidence_score=confidence,
            management_priority=priority,
        )

    @staticmethod
    def _executive_summary(
        *,
        period_label: str,
        comparison_label: str,
        revenue: float,
        gross_profit: float,
        margin: float,
        revenue_variance: float,
        gp_variance: float,
        margin_variance: float,
    ) -> str:
        return (
            f"For {period_label}, Revenue closed at "
            f"${revenue:,.0f}, "
            f"{abs(revenue_variance):.1%} "
            f"{'above' if revenue_variance >= 0 else 'below'} "
            f"{comparison_label}. Gross Profit reached "
            f"${gross_profit:,.0f}, "
            f"{abs(gp_variance):.1%} "
            f"{'above' if gp_variance >= 0 else 'below'} target. "
            f"GP Margin was {margin:.1%}, "
            f"{margin_variance * 100:+.2f} pp versus target."
        )

    @staticmethod
    def _what_happened(
        *,
        comparison_label: str,
        revenue_variance: float,
        gp_variance: float,
        margin_variance: float,
    ) -> str:
        if (
            revenue_variance >= 0
            and gp_variance < 0
        ):
            return (
                f"Revenue outperformed {comparison_label}, "
                "but the additional sales did not convert into "
                "Gross Profit. This indicates a profitability "
                "conversion issue rather than a demand issue."
            )

        if (
            revenue_variance < 0
            and gp_variance >= 0
        ):
            return (
                "Revenue was below target, but Gross Profit was "
                "protected through favorable mix, pricing or cost "
                "discipline."
            )

        if (
            revenue_variance >= 0
            and gp_variance >= 0
            and margin_variance >= 0
        ):
            return (
                "The business exceeded target across Revenue, "
                "Gross Profit and Margin, indicating balanced and "
                "profitable growth."
            )

        return (
            "Revenue and profitability were below target, "
            "requiring coordinated commercial and operational "
            "corrective actions."
        )

    @staticmethod
    def _why_it_happened(
        root_cause,
    ) -> str:
        if not root_cause.dominant_path:
            return (
                "The available data does not provide enough "
                "business dimensions to isolate a dominant cause."
            )

        path = " → ".join(
            (
                node.dimension
                .replace("_", " ")
                .title()
                + ": "
                + node.value
            )
            for node in root_cause.dominant_path
        )

        terminal = (
            root_cause.dominant_path[
                -1
            ]
        )

        return (
            f"The dominant Gross Profit variance path is "
            f"{path}. The terminal driver contributes "
            f"${terminal.variance:+,.0f}, equivalent to "
            f"{terminal.contribution_pct:.1%} of the total "
            "identified variance."
        )

    @staticmethod
    def _business_risk(
        radar,
    ) -> str:
        highest = radar.signals[0]

        return (
            f"The overall CFO Radar score is "
            f"{radar.overall_score:.0f}/100 "
            f"({radar.overall_level}). The primary risk is "
            f"{highest.category}: {highest.headline}. "
            f"{highest.explanation}"
        )

    @staticmethod
    def _recommended_actions(
        *,
        root_cause,
        opportunities,
        radar,
    ) -> list[str]:
        actions: list[str] = []

        if root_cause.dominant_path:
            terminal = (
                root_cause.dominant_path[
                    -1
                ]
            )
            actions.append(
                "Run a shipment-level profitability review for "
                f"{terminal.dimension.replace('_', ' ')} "
                f"{terminal.value} and validate pricing, direct "
                "cost and accrual accuracy."
            )

        for signal in radar.signals[:2]:
            actions.append(
                signal.recommended_action
            )

        for opportunity in opportunities[:2]:
            actions.append(
                (
                    f"{opportunity.recommended_action} "
                    f"Estimated GP upside: "
                    f"${opportunity.estimated_gp_upside:,.0f}."
                )
            )

        unique: list[str] = []

        for action in actions:
            if action not in unique:
                unique.append(action)

        return unique[:5]

    @staticmethod
    def _no_action_outlook(
        *,
        revenue: float,
        gross_profit: float,
        gp_variance: float,
        margin_variance: float,
    ) -> str:
        gp_gap = abs(
            gross_profit
            * gp_variance
        )
        margin_exposure = abs(
            revenue
            * margin_variance
        )

        total_exposure = max(
            gp_gap,
            margin_exposure,
        )

        if (
            gp_variance >= 0
            and margin_variance >= 0
        ):
            return (
                "If no corrective action is taken, current "
                "performance remains favorable; however, the main "
                "risk is losing the positive commercial and cost "
                "drivers in subsequent periods."
            )

        return (
            "If no corrective action is taken and the current "
            "performance pattern continues, the period-level "
            f"profitability exposure is approximately "
            f"${total_exposure:,.0f}. This value is directional "
            "and should be validated against the rolling forecast."
        )

    @staticmethod
    def _confidence(
        *,
        data_quality_score: float,
        root_cause_count: int,
        opportunity_count: int,
    ) -> float:
        dimension_score = min(
            (
                root_cause_count
                + opportunity_count
            )
            / 10,
            1.0,
        )

        confidence = (
            float(
                data_quality_score
            )
            / 100
            * 0.75
            + dimension_score
            * 0.25
        )

        return round(
            min(
                max(
                    confidence,
                    0.0,
                ),
                1.0,
            ),
            2,
        )

    @staticmethod
    def _priority(
        score: float,
    ) -> str:
        if score >= 80:
            return "Critical"
        if score >= 60:
            return "High"
        if score >= 35:
            return "Medium"
        return "Low"
