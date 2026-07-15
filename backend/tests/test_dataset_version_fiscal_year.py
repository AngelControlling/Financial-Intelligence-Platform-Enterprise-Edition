from models.data_lake import DatasetVersion


def _base_payload() -> dict:
    return {
        "version_id": "budget_test",
        "dataset_type": "budget",
        "version_label": "Original FY2027",
        "source_name": "budget.xlsx",
        "sheet_name": "FIP Budget Standard",
        "storage_file": "datasets/budget_test.pkl",
        "status": "validated",
        "rows": 12,
        "columns": 15,
        "quality_score": 100.0,
        "mapping_score": 100.0,
        "health_score": 100.0,
        "company": "Enterprise Freight Demo",
        "currency": "USD",
        "period_label": "FY2027",
    }


def test_dataset_version_accepts_fiscal_year() -> None:
    payload = _base_payload()
    payload["fiscal_year"] = 2027

    version = DatasetVersion(**payload)

    assert version.fiscal_year == 2027
    assert version.version == "Original FY2027"


def test_old_metadata_remains_compatible() -> None:
    version = DatasetVersion(
        **_base_payload()
    )

    assert version.fiscal_year is None
