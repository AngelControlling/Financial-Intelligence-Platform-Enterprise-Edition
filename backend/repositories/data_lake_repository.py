from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from models.data_lake import DatasetVersion


class DataLakeRepository:
    """
    Local enterprise repository.

    DataFrames are stored as Pickle because the current project does not
    require pyarrow. Metadata and active-version pointers are stored as JSON.
    """

    def __init__(
        self,
        root_path: str | Path | None = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.root_path = Path(
            root_path
            or project_root / "storage" / "data_lake"
        )

        self.datasets_path = self.root_path / "datasets"
        self.metadata_path = self.root_path / "metadata"
        self.profiles_path = self.root_path / "mapping_profiles"
        self.active_file = self.root_path / "active_versions.json"

        for path in [
            self.datasets_path,
            self.metadata_path,
            self.profiles_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        if not self.active_file.exists():
            self._write_json(self.active_file, {})

    def create_version_id(
        self,
        dataset_type: str,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return (
            f"{dataset_type}_{timestamp}_"
            f"{uuid4().hex[:6]}"
        )

    def save_dataframe(
        self,
        dataset_type: str,
        version_id: str,
        dataframe: pd.DataFrame,
    ) -> str:
        dataset_dir = self.datasets_path / dataset_type
        dataset_dir.mkdir(parents=True, exist_ok=True)

        file_path = dataset_dir / f"{version_id}.pkl"
        dataframe.to_pickle(file_path)

        return str(file_path.relative_to(self.root_path))

    def load_dataframe(
        self,
        storage_file: str,
    ) -> pd.DataFrame:
        return pd.read_pickle(
            self.root_path / storage_file
        )

    def save_version(
        self,
        version: DatasetVersion,
    ) -> None:
        metadata_dir = self.metadata_path / version.dataset_type
        metadata_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(
            metadata_dir / f"{version.version_id}.json",
            version.to_dict(),
        )

    def get_version(
        self,
        dataset_type: str,
        version_id: str,
    ) -> DatasetVersion | None:
        file_path = (
            self.metadata_path
            / dataset_type
            / f"{version_id}.json"
        )

        if not file_path.exists():
            return None

        return DatasetVersion(
            **self._read_json(file_path)
        )

    def list_versions(
        self,
        dataset_type: str,
    ) -> list[DatasetVersion]:
        metadata_dir = self.metadata_path / dataset_type

        if not metadata_dir.exists():
            return []

        versions = [
            DatasetVersion(
                **self._read_json(file_path)
            )
            for file_path in metadata_dir.glob("*.json")
        ]

        return sorted(
            versions,
            key=lambda item: item.created_at,
            reverse=True,
        )

    def activate(
        self,
        dataset_type: str,
        version_id: str,
    ) -> DatasetVersion:
        version = self.get_version(
            dataset_type,
            version_id,
        )

        if version is None:
            raise ValueError(
                f"Version not found: {version_id}"
            )

        active = self._read_json(self.active_file)
        active[dataset_type] = version_id
        self._write_json(self.active_file, active)

        version.status = "active"
        version.activated_at = datetime.now().isoformat(
            timespec="seconds"
        )
        self.save_version(version)

        return version

    def active_version(
        self,
        dataset_type: str,
    ) -> DatasetVersion | None:
        active = self._read_json(self.active_file)
        version_id = active.get(dataset_type)

        if not version_id:
            return None

        return self.get_version(
            dataset_type,
            version_id,
        )

    def load_active_dataframe(
        self,
        dataset_type: str,
    ) -> pd.DataFrame | None:
        version = self.active_version(dataset_type)

        if version is None:
            return None

        return self.load_dataframe(
            version.storage_file
        )

    def save_mapping_profile(
        self,
        profile_id: str,
        payload: dict[str, Any],
    ) -> None:
        self._write_json(
            self.profiles_path / f"{profile_id}.json",
            payload,
        )

    def get_mapping_profile(
        self,
        profile_id: str,
    ) -> dict[str, Any] | None:
        file_path = (
            self.profiles_path / f"{profile_id}.json"
        )
        return (
            self._read_json(file_path)
            if file_path.exists()
            else None
        )

    def list_mapping_profiles(
        self,
    ) -> list[dict[str, Any]]:
        return [
            self._read_json(file_path)
            for file_path
            in self.profiles_path.glob("*.json")
        ]

    @staticmethod
    def _write_json(
        file_path: Path,
        payload: dict[str, Any],
    ) -> None:
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        file_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _read_json(
        file_path: Path,
    ) -> dict[str, Any]:
        return json.loads(
            file_path.read_text(
                encoding="utf-8"
            )
        )
