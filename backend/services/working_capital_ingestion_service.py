from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from engines.working_capital_aging_engine import (
    WorkingCapitalAgingEngine,
)
from engines.working_capital_semantic_mapping_engine import (
    WorkingCapitalSemanticMappingEngine,
)
from models.data_lake import DatasetVersion
from repositories.data_lake_repository import (
    DataLakeRepository,
)
from services.data_quality_service import (
    DataQualityService,
)


@dataclass
class WorkingCapitalPreview:
    dataframe: pd.DataFrame
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    synthesized_columns: list[str]
    warnings: list[str]
    missing_required_columns: list[str]
    scores: dict[str, float]


class WorkingCapitalIngestionService:
    REQUIRED_COLUMNS = {
        "document_id",
        "counterparty",
        "document_type",
        "invoice_date",
        "due_date",
        "original_amount",
        "open_amount",
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
            WorkingCapitalSemanticMappingEngine()
        )
        self.aging_engine = (
            WorkingCapitalAgingEngine()
        )
        self.quality_service = (
            DataQualityService()
        )

    def preview(
        self,
        dataframe: pd.DataFrame,
    ) -> WorkingCapitalPreview:
        result = self.mapping_engine.map_dataframe(
            dataframe
        )

        scores = self.quality_service.score(
            result.dataframe,
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

        return WorkingCapitalPreview(
            dataframe=result.dataframe,
            mapped_columns=result.mapped_columns,
            unmapped_columns=result.unmapped_columns,
            synthesized_columns=(
                result.synthesized_columns
            ),
            warnings=result.warnings,
            missing_required_columns=(
                result.missing_required_columns
            ),
            scores=scores,
        )

    def create_version(
        self,
        previews: list[WorkingCapitalPreview],
        *,
        source_name: str,
        version_label: str,
        company: str,
        currency: str,
    ) -> DatasetVersion:
        if not previews:
            raise ValueError(
                "At least one AR/AP sheet is required."
            )

        missing = sorted(
            {
                column
                for preview in previews
                for column in (
                    preview.missing_required_columns
                )
            }
        )

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        combined = pd.concat(
            [
                preview.dataframe
                for preview in previews
            ],
            ignore_index=True,
        )

        analysis = self.aging_engine.analyze(
            combined
        )
        aged = analysis.dataframe

        version_id = (
            self.repository.create_version_id(
                "working_capital"
            )
        )
        storage_file = (
            self.repository.save_dataframe(
                "working_capital",
                version_id,
                aged,
            )
        )

        quality = sum(
            preview.scores["quality_score"]
            for preview in previews
        ) / len(previews)

        mapping = sum(
            preview.scores["mapping_score"]
            for preview in previews
        ) / len(previews)

        health = sum(
            preview.scores["health_score"]
            for preview in previews
        ) / len(previews)

        version = DatasetVersion(
            version_id=version_id,
            dataset_type="working_capital",
            version_label=version_label,
            source_name=source_name,
            sheet_name="Multiple AR/AP Sheets",
            storage_file=storage_file,
            status="validated",
            rows=len(aged),
            columns=len(aged.columns),
            quality_score=round(quality, 1),
            mapping_score=round(mapping, 1),
            health_score=round(health, 1),
            company=company,
            currency=currency,
            period_label="As-of Aging",
            warnings=[
                warning
                for preview in previews
                for warning in preview.warnings
            ],
            mapped_columns={
                source: canonical
                for preview in previews
                for source, canonical
                in preview.mapped_columns.items()
            },
            unmapped_columns=sorted(
                {
                    column
                    for preview in previews
                    for column in (
                        preview.unmapped_columns
                    )
                }
            ),
            synthesized_columns=sorted(
                {
                    column
                    for preview in previews
                    for column in (
                        preview.synthesized_columns
                    )
                }
            ),
            metadata={
                "summary": analysis.summary,
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
            "working_capital",
            version_id,
        )
