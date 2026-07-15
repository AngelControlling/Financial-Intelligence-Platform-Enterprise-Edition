class DummyVersion:
    version_label = "Actuals Test"
    version_id = "actuals_test"


def test_dataset_version_contract() -> None:
    version = DummyVersion()

    assert version.version_label == "Actuals Test"
    assert version.version_id == "actuals_test"
