from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HealthScoreResult:
    """Structured health-score output for Mission Control."""

    financial_score: float
    operational_score: float
    data_quality_score: float
    overall_score: float
    status: str
    signals: dict[str, str]


class HealthScoreEngine:
    """
    Calculates executive health scores for Mission Control.

    The engine is deterministic and uses only validated platform outputs.
    """

    def calculate(
        self,
        *,
        summary: dict,
        variance_summary: dict,
        dataframe: pd.DataFrame,
        data_quality_score: float = 100.0,
    ) -> HealthScoreResult:
        financial_score = self._financial_score(
            summary=summary,
            variance_summary=variance_summary,
        )

        operational_score = self._operational_score(
            summary=summary,
            dataframe=dataframe,
        )

        normalized_data_quality = float(
            np.clip(
                data_quality_score,
                0.0,
                100.0,
            )
        )

        overall_score = (
            financial_score * 0.50
            + operational_score * 0.30
            + normalized_data_quality * 0.20
        )

        status = self._score_status(
            overall_score
        )

        signals = {
            "Revenue": self._signal_from_delta(
                variance_summary.get(
                    "revenue_variance_pct",
                    0.0,
                )
            ),
            "Gross Profit": self._signal_from_delta(
                variance_summary.get(
                    "gp_variance_pct",
                    0.0,
                )
            ),
            "Margin": self._signal_from_delta(
                variance_summary.get(
                    "margin_variance_pp",
                    0.0,
                )
            ),
            "Operations": self._signal_from_score(
                operational_score
            ),
            "Data Quality": self._signal_from_score(
                normalized_data_quality
            ),
        }

        return HealthScoreResult(
            financial_score=round(
                financial_score,
                1,
            ),
            operational_score=round(
                operational_score,
                1,
            ),
            data_quality_score=round(
                normalized_data_quality,
                1,
            ),
            overall_score=round(
                overall_score,
                1,
            ),
            status=status,
            signals=signals,
        )

    def _financial_score(
        self,
        *,
        summary: dict,
        variance_summary: dict,
    ) -> float:
        revenue_achievement = self._achievement_score(
            actual=summary.get(
                "actual_revenue",
                0.0,
            ),
            target=summary.get(
                "estimated_revenue",
                0.0,
            ),
        )

        gp_achievement = self._achievement_score(
            actual=summary.get(
                "actual_gp",
                0.0,
            ),
            target=summary.get(
                "estimated_gp",
                0.0,
            ),
        )

        margin_achievement = self._achievement_score(
            actual=summary.get(
                "actual_gp_margin",
                0.0,
            ),
            target=summary.get(
                "estimated_gp_margin",
                0.0,
            ),
        )

        return float(
            np.clip(
                revenue_achievement * 0.35
                + gp_achievement * 0.40
                + margin_achievement * 0.25,
                0.0,
                100.0,
            )
        )

    def _operational_score(
        self,
        *,
        summary: dict,
        dataframe: pd.DataFrame,
    ) -> float:
        shipments = float(
            summary.get(
                "shipments",
                0.0,
            )
        )

        gp_per_shipment = float(
            summary.get(
                "gp_per_shipment",
                0.0,
            )
        )

        valid_dimensions = 0
        evaluated_dimensions = 0

        for column in [
            "customer",
            "trade_lane",
            "origin",
            "destination",
        ]:
            if column not in dataframe.columns:
                continue

            evaluated_dimensions += 1

            valid_values = (
                dataframe[column]
                .fillna("Unassigned")
                .astype(str)
                .str.casefold()
                .isin(
                    {
                        "unassigned",
                        "unclassified",
                        "nan",
                        "none",
                        "",
                    }
                )
                .mean()
            )

            if valid_values < 0.25:
                valid_dimensions += 1

        dimension_score = (
            valid_dimensions
            / evaluated_dimensions
            * 100.0
            if evaluated_dimensions
            else 50.0
        )

        shipment_score = (
            100.0
            if shipments > 0
            else 0.0
        )

        profitability_score = (
            100.0
            if gp_per_shipment > 0
            else 40.0
            if gp_per_shipment == 0
            else 0.0
        )

        return float(
            np.clip(
                shipment_score * 0.25
                + profitability_score * 0.45
                + dimension_score * 0.30,
                0.0,
                100.0,
            )
        )

    @staticmethod
    def _achievement_score(
        *,
        actual: float,
        target: float,
    ) -> float:
        if target == 0:
            return 100.0 if actual >= 0 else 0.0

        ratio = actual / target

        return float(
            np.clip(
                ratio * 100.0,
                0.0,
                120.0,
            )
        )

    @staticmethod
    def _score_status(
        score: float,
    ) -> str:
        if score >= 90:
            return "success"

        if score >= 75:
            return "info"

        if score >= 60:
            return "warning"

        return "danger"

    @staticmethod
    def _signal_from_delta(
        delta: float,
    ) -> str:
        if delta >= 0.03:
            return "success"

        if delta >= -0.02:
            return "info"

        if delta >= -0.05:
            return "warning"

        return "danger"

    @staticmethod
    def _signal_from_score(
        score: float,
    ) -> str:
        if score >= 90:
            return "success"

        if score >= 75:
            return "info"

        if score >= 60:
            return "warning"

        return "danger"
