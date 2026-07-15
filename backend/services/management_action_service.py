from __future__ import annotations
from engines.management_action_engine import ManagementActionEngine
from models.executive_alert import ExecutiveAlert
from models.management_action import ManagementAction
from repositories.management_action_repository import ManagementActionRepository

class ManagementActionService:
    def __init__(self) -> None:
        self.repository = ManagementActionRepository()
        self.engine = ManagementActionEngine()

    def proposals(
        self,
        alerts: list[ExecutiveAlert],
        *,
        period_label: str,
    ) -> list[ManagementAction]:
        return self.engine.propose(alerts, period_label=period_label)

    def add(self, action: ManagementAction) -> ManagementAction:
        return self.repository.save(action)

    def list_all(self) -> list[ManagementAction]:
        return self.repository.list_all()

    def update(self, action_id: str, *, owner: str, status: str, due_date: str):
        return self.repository.update(
            action_id,
            owner=owner,
            status=status,
            due_date=due_date,
        )

    def delete(self, action_id: str) -> None:
        self.repository.delete(action_id)
