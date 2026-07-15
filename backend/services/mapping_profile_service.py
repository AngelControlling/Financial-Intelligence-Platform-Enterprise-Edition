from __future__ import annotations

import hashlib
from datetime import datetime

from repositories.data_lake_repository import (
    DataLakeRepository,
)


class MappingProfileService:
    """Stores Controller-approved mapping decisions outside Python code."""

    def __init__(
        self,
        repository: DataLakeRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or DataLakeRepository()
        )

    @staticmethod
    def profile_id(
        dataset_type: str,
        source_name: str,
        sheet_name: str,
        columns: list[str],
    ) -> str:
        schema = "|".join(
            sorted(
                str(column).strip().casefold()
                for column in columns
            )
        )
        digest = hashlib.sha1(
            schema.encode("utf-8")
        ).hexdigest()[:12]

        source_token = (
            source_name
            .replace(" ", "_")
            .replace(".", "_")
            .lower()
        )

        return (
            f"{dataset_type}_"
            f"{source_token}_"
            f"{sheet_name.lower()}_"
            f"{digest}"
        )

    def save(
        self,
        *,
        dataset_type: str,
        source_name: str,
        sheet_name: str,
        columns: list[str],
        mapping: dict[str, str],
    ) -> str:
        profile_id = self.profile_id(
            dataset_type,
            source_name,
            sheet_name,
            columns,
        )

        self.repository.save_mapping_profile(
            profile_id,
            {
                "profile_id": profile_id,
                "dataset_type": dataset_type,
                "source_name": source_name,
                "sheet_name": sheet_name,
                "schema_columns": columns,
                "mapping": mapping,
                "confirmed_by": "Controller",
                "updated_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
            },
        )

        return profile_id

    def get(
        self,
        *,
        dataset_type: str,
        source_name: str,
        sheet_name: str,
        columns: list[str],
    ) -> dict[str, str] | None:
        profile_id = self.profile_id(
            dataset_type,
            source_name,
            sheet_name,
            columns,
        )
        profile = self.repository.get_mapping_profile(
            profile_id
        )

        return (
            profile.get("mapping")
            if profile
            else None
        )
