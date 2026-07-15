from pathlib import Path

import pandas as pd

from models.data_lake import DatasetVersion
from repositories.data_lake_repository import (
    DataLakeRepository,
)


def test_repository_saves_and_activates(
    tmp_path: Path,
) -> None:
    repository = DataLakeRepository(
        tmp_path
    )

    dataframe = pd.DataFrame(
        {
            "actual_revenue": [100.0],
            "actual_cost": [70.0],
        }
    )

    version_id = repository.create_version_id(
        "actuals"
    )
    storage_file = (
        repository.save_dataframe(
            "actuals",
            version_id,
            dataframe,
        )
    )

    version = DatasetVersion(
        version_id=version_id,
        dataset_type="actuals",
        version_label="Test",
        source_name="test.xlsx",
        sheet_name="Sheet1",
        storage_file=storage_file,
        status="validated",
        rows=1,
        columns=2,
        quality_score=100.0,
        mapping_score=100.0,
        health_score=100.0,
        company="Test",
        currency="USD",
        period_label="2026",
    )

    repository.save_version(version)
    repository.activate(
        "actuals",
        version_id,
    )

    active = repository.active_version(
        "actuals"
    )

    assert active is not None
    assert active.version_id == version_id
    assert len(
        repository.load_active_dataframe(
            "actuals"
        )
    ) == 1
