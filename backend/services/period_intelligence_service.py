from __future__ import annotations

from services.workspace_data_service import ActiveFreightContext
from engines.period_engine import PeriodEngine
from engines.freight_kpi_engine import FreightKPIEngine
from engines.variance_engine import VarianceEngine
from models.period import PeriodSelection


class PeriodIntelligenceService:
    """Recalculates Mission Control for the selected reporting period."""

    def __init__(self) -> None:
        self.period_engine = PeriodEngine()
        self.kpi_engine = FreightKPIEngine()
        self.variance_engine = VarianceEngine()

    def apply(
        self,
        context: ActiveFreightContext,
        selection: PeriodSelection,
    ) -> ActiveFreightContext:
        filtered = self.period_engine.filter(
            context.dataframe,
            selection,
        )

        summary = self.kpi_engine.executive_summary(
            filtered
        )
        variance = self.variance_engine.overall_summary(
            filtered
        )

        return ActiveFreightContext(
            dataframe=filtered,
            summary=summary,
            variance_summary=variance,
            comparison_label=context.comparison_label,
            selected_period_label=(
                self.period_engine.context_label(
                    selection
                )
            ),
            data_quality_score=context.data_quality_score,
        )
