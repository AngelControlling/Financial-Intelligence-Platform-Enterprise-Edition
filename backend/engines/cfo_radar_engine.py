from __future__ import annotations

import pandas as pd

from models.cfo_radar import (
    CFORadarResult,
    CFORadarSignal,
)


class CFORadarEngine:
    """Build a CFO risk radar from period-aligned financial outputs."""

    def evaluate(
        self,
        dataframe: pd.DataFrame,
        *,
        summary: dict,
        variance: dict,
        data_quality_score: float,
    ) -> CFORadarResult:
        signals = [
            self._revenue_signal(variance),
            self._gp_signal(variance),
            self._margin_signal(variance),
            self._concentration_signal(dataframe),
            self._loss_making_signal(dataframe),
            self._data_quality_signal(
                data_quality_score
            ),
        ]

        scores = [
            signal.score
            for signal in signals
        ]

        overall_score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )
        overall_level = self._level(
            overall_score
        )

        ranked = sorted(
            signals,
            key=lambda signal: signal.score,
            reverse=True,
        )

        return CFORadarResult(
            overall_score=round(
                overall_score,
                1,
            ),
            overall_level=overall_level,
            signals=ranked,
            top_risk=(
                ranked[0].category
                if ranked
                else "None"
            ),
            risk_count=sum(
                signal.level
                in {
                    "Medium",
                    "High",
                    "Critical",
                }
                for signal in signals
            ),
            critical_count=sum(
                signal.level == "Critical"
                for signal in signals
            ),
        )

    def _revenue_signal(
        self,
        variance: dict,
    ) -> CFORadarSignal:
        value = float(
            variance.get(
                "revenue_variance_pct",
                0.0,
            )
        )

        score = min(
            max(
                -value * 400,
                0.0,
            ),
            100.0,
        )

        return self._signal(
            category="Revenue",
            score=score,
            headline=f"{value:+.1%} vs Budget",
            explanation=(
                "Revenue performance is below target."
                if value < 0
                else "Revenue performance is at or above target."
            ),
            action=(
                "Review volume, pricing, lost business and customer mix."
                if value < 0
                else "Protect recurring commercial drivers."
            ),
        )

    def _gp_signal(
        self,
        variance: dict,
    ) -> CFORadarSignal:
        value = float(
            variance.get(
                "gp_variance_pct",
                0.0,
            )
        )

        score = min(
            max(
                -value * 450,
                0.0,
            ),
            100.0,
        )

        return self._signal(
            category="Gross Profit",
            score=score,
            headline=f"{value:+.1%} vs Budget",
            explanation=(
                "Gross Profit is below target and requires corrective action."
                if value < 0
                else "Gross Profit is at or above target."
            ),
            action=(
                "Review pricing, direct cost, accruals and shipment profitability."
                if value < 0
                else "Maintain pricing and cost discipline."
            ),
        )

    def _margin_signal(
        self,
        variance: dict,
    ) -> CFORadarSignal:
        value = float(
            variance.get(
                "margin_variance_pp",
                0.0,
            )
        )

        score = min(
            max(
                -value * 2500,
                0.0,
            ),
            100.0,
        )

        return self._signal(
            category="Margin",
            score=score,
            headline=(
                f"{value * 100:+.2f} pp "
                "vs Budget"
            ),
            explanation=(
                "Margin compression indicates adverse mix, pricing or cost."
                if value < 0
                else "Margin is stable or expanding."
            ),
            action=(
                "Prioritize low-margin customers, products and trade lanes."
                if value < 0
                else "Protect favorable mix and pricing."
            ),
        )

    def _concentration_signal(
        self,
        dataframe: pd.DataFrame,
    ) -> CFORadarSignal:
        if (
            dataframe.empty
            or "customer"
            not in dataframe.columns
            or "actual_revenue"
            not in dataframe.columns
        ):
            concentration = 0.0
        else:
            customer_revenue = (
                dataframe.groupby(
                    "customer",
                    dropna=False,
                )["actual_revenue"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )
            total = float(
                customer_revenue.sum()
            )
            concentration = (
                float(
                    customer_revenue.head(
                        5
                    ).sum()
                )
                / total
                if total
                else 0.0
            )

        score = min(
            max(
                (
                    concentration
                    - 0.35
                )
                / 0.45
                * 100,
                0.0,
            ),
            100.0,
        )

        return self._signal(
            category="Customer Concentration",
            score=score,
            headline=(
                f"Top 5 = "
                f"{concentration:.1%} of Revenue"
            ),
            explanation=(
                "Revenue dependency on the largest customers is elevated."
                if concentration >= 0.50
                else "Customer concentration remains controlled."
            ),
            action=(
                "Diversify the portfolio and protect strategic accounts."
                if concentration >= 0.50
                else "Continue monitoring concentration."
            ),
        )

    def _loss_making_signal(
        self,
        dataframe: pd.DataFrame,
    ) -> CFORadarSignal:
        if (
            dataframe.empty
            or "actual_gp"
            not in dataframe.columns
        ):
            loss_share = 0.0
        else:
            gp = pd.to_numeric(
                dataframe["actual_gp"],
                errors="coerce",
            ).fillna(0.0)

            loss_amount = abs(
                float(
                    gp[
                        gp < 0
                    ].sum()
                )
            )
            positive_amount = float(
                gp[
                    gp > 0
                ].sum()
            )

            denominator = (
                loss_amount
                + positive_amount
            )
            loss_share = (
                loss_amount
                / denominator
                if denominator
                else 0.0
            )

        score = min(
            loss_share * 400,
            100.0,
        )

        return self._signal(
            category="Loss-Making Business",
            score=score,
            headline=(
                f"{loss_share:.1%} of GP exposure"
            ),
            explanation=(
                "Loss-making activity is materially eroding profitability."
                if loss_share >= 0.10
                else "Loss-making exposure is limited."
            ),
            action=(
                "Review negative-GP shipments and define recovery or exit plans."
                if loss_share >= 0.10
                else "Maintain shipment-level monitoring."
            ),
        )

    def _data_quality_signal(
        self,
        data_quality_score: float,
    ) -> CFORadarSignal:
        score = min(
            max(
                100.0
                - float(
                    data_quality_score
                ),
                0.0,
            ),
            100.0,
        )

        return self._signal(
            category="Data Quality",
            score=score,
            headline=(
                f"{data_quality_score:.0f}% quality"
            ),
            explanation=(
                "Data quality may limit the reliability of management conclusions."
                if data_quality_score < 90
                else "Data quality supports reliable analysis."
            ),
            action=(
                "Resolve mapping, completeness and validation exceptions."
                if data_quality_score < 90
                else "Maintain current validation discipline."
            ),
        )

    def _signal(
        self,
        *,
        category: str,
        score: float,
        headline: str,
        explanation: str,
        action: str,
    ) -> CFORadarSignal:
        return CFORadarSignal(
            category=category,
            score=round(
                score,
                1,
            ),
            level=self._level(
                score
            ),
            headline=headline,
            explanation=explanation,
            recommended_action=action,
        )

    @staticmethod
    def _level(
        score: float,
    ) -> str:
        if score >= 80:
            return "Critical"
        if score >= 60:
            return "High"
        if score >= 35:
            return "Medium"
        return "Low"
