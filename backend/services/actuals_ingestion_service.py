from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd

from engines.baseline_classification_engine import (
    BaselineClassificationEngine,
)
from engines.freight_intelligence_engine import (
    FreightIntelligenceEngine,
)
from engines.freight_kpi_engine import (
    FreightKPIEngine,
)
from engines.semantic_mapping_engine import (
    SemanticMappingEngine,
)
from engines.time_intelligence_engine import (
    TimeIntelligenceEngine,
)
from engines.variance_engine import (
    VarianceEngine,
)
from models.data_lake import DatasetVersion
from repositories.data_lake_repository import (
    DataLakeRepository,
)
from services.data_quality_service import (
    DataQualityService,
)
from services.mapping_profile_service import (
    MappingProfileService,
)


@dataclass
class ActualsPreview:
    dataframe: pd.DataFrame
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    synthesized_columns: list[str]
    warnings: list[str]
    missing_required_columns: list[str]
    scores: dict[str, float]
    available_baselines: list[str]
    profile_applied: bool


class ActualsIngestionService:
    """Orchestrates mapping, validation, versioning and activation."""

    REQUIRED_COLUMNS = {
        "actual_revenue",
        "actual_cost",
        "period",
    }

    def __init__(
        self,
        repository: DataLakeRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or DataLakeRepository()
        )
        self.mapping_engine = (
            SemanticMappingEngine()
        )
        self.baseline_engine = (
            BaselineClassificationEngine()
        )
        self.freight_engine = (
            FreightIntelligenceEngine()
        )
        self.kpi_engine = FreightKPIEngine()
        self.variance_engine = VarianceEngine()
        self.time_engine = (
            TimeIntelligenceEngine()
        )
        self.quality_service = (
            DataQualityService()
        )
        self.profile_service = (
            MappingProfileService(
                self.repository
            )
        )

    def preview(
        self,
        dataframe: pd.DataFrame,
        *,
        source_name: str,
        sheet_name: str,
        manual_mapping: dict[str, str] | None = None,
    ) -> ActualsPreview:
        source_df = dataframe.copy()

        saved_mapping = self.profile_service.get(
            dataset_type="actuals",
            source_name=source_name,
            sheet_name=sheet_name,
            columns=[
                str(column)
                for column in source_df.columns
            ],
        )

        mapping_to_apply = (
            manual_mapping
            or saved_mapping
        )

        if mapping_to_apply:
            source_df = source_df.rename(
                columns=mapping_to_apply
            )

        result = (
            self.mapping_engine.map_dataframe(
                source_df
            )
        )

        canonical = result.dataframe

        available_baselines = [
            option.label
            for option in (
                self.baseline_engine
                .available_baselines(
                    canonical
                )
            )
        ]

        scores = self.quality_service.score(
            canonical,
            required_columns=(
                self.REQUIRED_COLUMNS
            ),
            mapped_count=len(
                result.mapped_columns
            ),
            source_column_count=len(
                dataframe.columns
            ),
        )

        return ActualsPreview(
            dataframe=canonical,
            mapped_columns=(
                result.mapped_columns
            ),
            unmapped_columns=(
                result.unmapped_columns
            ),
            synthesized_columns=(
                result.synthesized_columns
            ),
            warnings=result.warnings,
            missing_required_columns=(
                result.missing_required_columns
            ),
            scores=scores,
            available_baselines=(
                available_baselines
            ),
            profile_applied=(
                saved_mapping is not None
            ),
        )

    def save_mapping_profile(
        self,
        *,
        source_name: str,
        sheet_name: str,
        source_columns: list[str],
        mapping: dict[str, str],
    ) -> str:
        return self.profile_service.save(
            dataset_type="actuals",
            source_name=source_name,
            sheet_name=sheet_name,
            columns=source_columns,
            mapping=mapping,
        )

    def create_version(
        self,
        preview: ActualsPreview,
        *,
        source_name: str,
        sheet_name: str,
        version_label: str,
        company: str,
        currency: str,
        comparison_label: str,
    ) -> DatasetVersion:
        if preview.missing_required_columns:
            raise ValueError(
                "Cannot create a version while "
                "required columns are missing."
            )

        canonical = preview.dataframe.copy()

        available = {
            option.label: option.key
            for option in (
                self.baseline_engine
                .available_baselines(
                    canonical
                )
            )
        }

        if comparison_label not in available:
            raise ValueError(
                f"Baseline not available: "
                f"{comparison_label}"
            )

        baseline_result = (
            self.baseline_engine
            .apply_baseline(
                canonical,
                available[comparison_label],
            )
        )

        prepared = self.kpi_engine.prepare_data(
            baseline_result.dataframe
        )
        prepared = self.freight_engine.prepare_data(
            prepared
        )
        time_result = self.time_engine.prepare_periods(
            prepared,
            period_column="period",
            year_column="year",
        )
        prepared = time_result.dataframe

        version_id = (
            self.repository.create_version_id(
                "actuals"
            )
        )
        storage_file = (
            self.repository.save_dataframe(
                "actuals",
                version_id,
                prepared,
            )
        )

        period_label = (
            f"{prepared['period'].min()} "
            f"to {prepared['period'].max()}"
            if "period" in prepared.columns
            and not prepared.empty
            else "All Periods"
        )

        version = DatasetVersion(
            version_id=version_id,
            dataset_type="actuals",
            version_label=version_label,
            source_name=source_name,
            sheet_name=sheet_name,
            storage_file=storage_file,
            status="validated",
            rows=len(prepared),
            columns=len(prepared.columns),
            quality_score=(
                preview.scores[
                    "quality_score"
                ]
            ),
            mapping_score=(
                preview.scores[
                    "mapping_score"
                ]
            ),
            health_score=(
                preview.scores[
                    "health_score"
                ]
            ),
            company=company,
            currency=currency,
            period_label=period_label,
            comparison_label=(
                comparison_label
            ),
            warnings=preview.warnings,
            mapped_columns=(
                preview.mapped_columns
            ),
            unmapped_columns=(
                preview.unmapped_columns
            ),
            synthesized_columns=(
                preview.synthesized_columns
            ),
            metadata={
                "created_by": "Controller",
                "time_unparsed_count": (
                    time_result.unparsed_count
                ),
            },
        )

        self.repository.save_version(
            version
        )

        return version

    def activate(
        self,
        version_id: str,
    ) -> DatasetVersion:
        return self.repository.activate(
            "actuals",
            version_id,
        )

    def build_active_context(
        self,
    ) -> dict[str, Any] | None:
        version = (
            self.repository.active_version(
                "actuals"
            )
        )
        dataframe = (
            self.repository
            .load_active_dataframe(
                "actuals"
            )
        )

        if version is None or dataframe is None:
            return None

        return {
            "version": version,
            "dataframe": dataframe,
            "summary": (
                self.kpi_engine
                .executive_summary(
                    dataframe
                )
            ),
            "variance_summary": (
                self.variance_engine
                .overall_summary(
                    dataframe
                )
            ),
            "comparison_label": (
                version.comparison_label
                or "Budget"
            ),
            "selected_period_label": (
                version.period_label
                or "All Periods"
            ),
            "data_quality_score": (
                version.quality_score
            ),
        }
