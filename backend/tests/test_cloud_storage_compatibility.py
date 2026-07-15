from pathlib import Path

import pandas as pd

from repositories.data_lake_repository import (
    DataLakeRepository,
)


def test_windows_metadata_path_loads_on_linux(
    tmp_path: Path,
) -> None:
    repository = DataLakeRepository(tmp_path)

    dataset_dir = (
        tmp_path
        / "datasets"
        / "actuals"
    )
    dataset_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    expected = pd.DataFrame(
        {
            "value": [1, 2, 3]
        }
    )
    expected.to_pickle(
        dataset_dir / "actuals_demo.pkl"
    )

    loaded = repository.load_dataframe(
        r"datasets\actuals\actuals_demo.pkl"
    )

    assert loaded is not None
    pd.testing.assert_frame_equal(
        loaded,
        expected,
    )


def test_missing_dataset_returns_none(
    tmp_path: Path,
) -> None:
    repository = DataLakeRepository(tmp_path)

    assert repository.load_dataframe(
        "datasets/actuals/missing.pkl"
    ) is None


def test_storage_initializes_automatically(
    tmp_path: Path,
) -> None:
    repository = DataLakeRepository(tmp_path)

    assert repository.datasets_path.exists()
    assert repository.metadata_path.exists()
    assert repository.profiles_path.exists()
    assert repository.active_file.exists()
