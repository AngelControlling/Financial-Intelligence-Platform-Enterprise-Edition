from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from core.session_manager import SessionManager
from repositories.data_lake_repository import DataLakeRepository
from services.actual_budget_merge_service import ActualBudgetMergeService
from services.actuals_ingestion_service import ActualsIngestionService


@dataclass(frozen=True)
class ActiveFreightContext:
    dataframe: pd.DataFrame
    summary: dict[str, Any]
    variance_summary: dict[str, Any]
    comparison_label: str
    selected_period_label: str
    data_quality_score: float


class WorkspaceDataService:
    """
    Reads active enterprise datasets and applies the active external Budget.

    Persistent Data Lake versions are the source of truth.
    """

    FREIGHT_CONTEXT_KEY = "fip_active_freight_context"

    def __init__(
        self,
        session: SessionManager | None = None,
        repository: DataLakeRepository | None = None,
    ) -> None:
        self.session = session or SessionManager()
        self.session.initialize()
        self.repository = repository or DataLakeRepository()

    def get_active_freight_context(
        self,
    ) -> ActiveFreightContext | None:
        cached = self.session.get(
            self.FREIGHT_CONTEXT_KEY
        )

        if cached is not None:
            return cached

        ingestion = ActualsIngestionService(
            self.repository
        )
        payload = ingestion.build_active_context()

        if payload is None:
            return None

        dataframe = payload["dataframe"]
        comparison_label = payload["comparison_label"]

        active_budget = self.repository.active_version(
            "budget"
        )
        budget_df = self.repository.load_active_dataframe(
            "budget"
        )

        if (
            active_budget is not None
            and budget_df is not None
        ):
            dataframe = ActualBudgetMergeService().apply(
                dataframe,
                budget_df,
            )
            comparison_label = "Budget"

            payload["summary"] = (
                ingestion.kpi_engine.executive_summary(
                    dataframe
                )
            )
            payload["variance_summary"] = (
                ingestion.variance_engine.overall_summary(
                    dataframe
                )
            )

        context = ActiveFreightContext(
            dataframe=dataframe,
            summary=payload["summary"],
            variance_summary=payload[
                "variance_summary"
            ],
            comparison_label=comparison_label,
            selected_period_label=payload[
                "selected_period_label"
            ],
            data_quality_score=payload[
                "data_quality_score"
            ],
        )

        self.session.set(
            self.FREIGHT_CONTEXT_KEY,
            context,
        )
        return context

    def clear_active_freight_context(
        self,
    ) -> None:
        self.session.delete(
            self.FREIGHT_CONTEXT_KEY
        )

    def get_dataset(
        self,
        dataset_type: str,
    ):
        return self.repository.active_version(
            dataset_type
        )

    def list_datasets(self) -> dict:
        dataset_types = [
            "actuals",
            "budget",
            "forecast",
            "prior_year",
            "working_capital",
            "fx_rates",
        ]

        return {
            dataset_type: version
            for dataset_type in dataset_types
            if (
                version
                := self.repository.active_version(
                    dataset_type
                )
            )
            is not None
        }
