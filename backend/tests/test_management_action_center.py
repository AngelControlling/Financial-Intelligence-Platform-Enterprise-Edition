from pathlib import Path
from engines.management_action_engine import ManagementActionEngine
from models.executive_alert import ExecutiveAlert
from repositories.management_action_repository import ManagementActionRepository

def test_alert_becomes_action() -> None:
    alert = ExecutiveAlert(
        alert_id="a1",
        severity="critical",
        category="Margin",
        title="Margin compression",
        metric="-4 pp",
        message="Below target",
        recommended_action="Review pricing.",
        variance_value=-100000.0,
    )
    action = ManagementActionEngine().propose(
        [alert],
        period_label="YTD 2026",
    )[0]
    assert action.priority == "Critical"
    assert action.expected_impact == 100000.0

def test_duplicate_prevention(tmp_path: Path) -> None:
    repository = ManagementActionRepository(tmp_path/"actions.json")
    alert = ExecutiveAlert(
        alert_id="a1",
        severity="high",
        category="Gross Profit",
        title="GP below target",
        metric="-10%",
        message="Below target",
        recommended_action="Review costs.",
    )
    action = ManagementActionEngine().propose(
        [alert],
        period_label="Q1 2026",
    )[0]
    repository.save(action)
    repository.save(action)
    assert len(repository.list_all()) == 1
