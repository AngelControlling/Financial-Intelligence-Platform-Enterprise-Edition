from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

import pandas as pd

from models.data_lake import DatasetVersion


class DataLakeRepository:
    """
    Cross-platform enterprise repository.

    DataFrames are stored as Pickle. Metadata and active-version pointers
    are stored as JSON.

    Important:
    Metadata created on Windows can contain backslashes in storage_file.
    Streamlit Community Cloud runs on Linux, so all stored paths are
    normalized before access.
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

        self._initialize_storage()

    def _initialize_storage(self) -> None:
        for path in [
            self.root_path,
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

        # Always persist portable POSIX-style relative paths.
        return file_path.relative_to(
            self.root_path
        ).as_posix()

    def load_dataframe(
        self,
        storage_file: str,
    ) -> pd.DataFrame | None:
        file_path = self._resolve_storage_file(
            storage_file
        )

        if not file_path.exists():
            return None

        try:
            return pd.read_pickle(file_path)
        except (
            FileNotFoundError,
            OSError,
            EOFError,
            ValueError,
        ):
            return None

    def _resolve_storage_file(
        self,
        storage_file: str,
    ) -> Path:
        """
        Normalize paths saved by Windows so they work on Linux.

        Example:
        datasets\\actuals\\file.pkl
        becomes:
        datasets/actuals/file.pkl
        """
        portable = str(storage_file).replace(
            "\\",
            "/",
        )
        relative = PurePosixPath(portable)

        # Prevent absolute-path metadata from escaping the data lake.
        safe_parts = [
            part
            for part in relative.parts
            if part not in {
                "",
                ".",
                "..",
                "/",
            }
        ]

        return self.root_path.joinpath(
            *safe_parts
        )

    def save_version(
        self,
        version: DatasetVersion,
    ) -> None:
        metadata_dir = self.metadata_path / version.dataset_type
        metadata_dir.mkdir(parents=True, exist_ok=True)

        payload = version.to_dict()

        if payload.get("storage_file"):
            payload["storage_file"] = str(
                payload["storage_file"]
            ).replace("\\", "/")

        self._write_json(
            metadata_dir / f"{version.version_id}.json",
            payload,
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

        try:
            payload = self._read_json(file_path)
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            return None

        storage_file = payload.get(
            "storage_file"
        )
        if storage_file:
            payload["storage_file"] = str(
                storage_file
            ).replace("\\", "/")

        try:
            return DatasetVersion(**payload)
        except TypeError:
            return None

    def list_versions(
        self,
        dataset_type: str,
    ) -> list[DatasetVersion]:
        metadata_dir = self.metadata_path / dataset_type

        if not metadata_dir.exists():
            return []

        versions: list[DatasetVersion] = []

        for file_path in metadata_dir.glob("*.json"):
            try:
                payload = self._read_json(file_path)

                if payload.get("storage_file"):
                    payload["storage_file"] = str(
                        payload["storage_file"]
                    ).replace("\\", "/")

                versions.append(
                    DatasetVersion(**payload)
                )
            except (
                FileNotFoundError,
                json.JSONDecodeError,
                OSError,
                TypeError,
            ):
                continue

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

        dataframe = self.load_dataframe(
            version.storage_file
        )
        if dataframe is None:
            raise ValueError(
                "The selected version metadata exists, "
                "but its dataset file is unavailable."
            )

        active = self._safe_active_versions()
        active[dataset_type] = version_id
        self._write_json(
            self.active_file,
            active,
        )

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
        active = self._safe_active_versions()
        version_id = active.get(dataset_type)

        if not version_id:
            return None

        version = self.get_version(
            dataset_type,
            version_id,
        )

        if version is None:
            self._remove_stale_active_pointer(
                dataset_type
            )
            return None

        if not self._resolve_storage_file(
            version.storage_file
        ).exists():
            self._remove_stale_active_pointer(
                dataset_type
            )
            return None

        return version

    def load_active_dataframe(
        self,
        dataset_type: str,
    ) -> pd.DataFrame | None:
        version = self.active_version(
            dataset_type
        )

        if version is None:
            return None

        dataframe = self.load_dataframe(
            version.storage_file
        )

        if dataframe is None:
            self._remove_stale_active_pointer(
                dataset_type
            )

        return dataframe

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
            self.profiles_path
            / f"{profile_id}.json"
        )

        if not file_path.exists():
            return None

        try:
            return self._read_json(file_path)
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            return None

    def list_mapping_profiles(
        self,
    ) -> list[dict[str, Any]]:
        profiles = []

        for file_path in self.profiles_path.glob(
            "*.json"
        ):
            try:
                profiles.append(
                    self._read_json(file_path)
                )
            except (
                FileNotFoundError,
                json.JSONDecodeError,
                OSError,
            ):
                continue

        return profiles

    def _safe_active_versions(
        self,
    ) -> dict[str, Any]:
        if not self.active_file.exists():
            self._write_json(
                self.active_file,
                {},
            )
            return {}

        try:
            payload = self._read_json(
                self.active_file
            )
            return (
                payload
                if isinstance(payload, dict)
                else {}
            )
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            self._write_json(
                self.active_file,
                {},
            )
            return {}

    def _remove_stale_active_pointer(
        self,
        dataset_type: str,
    ) -> None:
        active = self._safe_active_versions()

        if dataset_type in active:
            active.pop(
                dataset_type,
                None,
            )
            self._write_json(
                self.active_file,
                active,
            )

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
