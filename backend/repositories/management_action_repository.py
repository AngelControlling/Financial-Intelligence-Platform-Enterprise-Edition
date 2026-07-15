from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from models.management_action import ManagementAction

class ManagementActionRepository:
    def __init__(self, file_path: str | Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.file_path = Path(
            file_path
            or project_root/"storage/action_center/management_actions.json"
        )
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write([])

    def list_all(self) -> list[ManagementAction]:
        return [ManagementAction(**item) for item in self._read()]

    def save(self, action: ManagementAction) -> ManagementAction:
        actions = self.list_all()
        duplicate = next(
            (
                item for item in actions
                if item.source_alert_id == action.source_alert_id
                and item.source_alert_id
                and item.status not in {"Completed", "Cancelled"}
            ),
            None,
        )
        if duplicate:
            return duplicate
        actions.append(action)
        self._write([item.to_dict() for item in actions])
        return action

    def update(
        self,
        action_id: str,
        *,
        owner: str,
        status: str,
        due_date: str,
    ) -> ManagementAction:
        actions = self.list_all()
        for action in actions:
            if action.action_id == action_id:
                action.owner = owner.strip() or "Unassigned"
                action.status = status
                action.due_date = due_date
                action.updated_at = datetime.now().isoformat(timespec="seconds")
                self._write([item.to_dict() for item in actions])
                return action
        raise ValueError(f"Action not found: {action_id}")

    def delete(self, action_id: str) -> None:
        actions = [
            item for item in self.list_all()
            if item.action_id != action_id
        ]
        self._write([item.to_dict() for item in actions])

    def _read(self) -> list[dict]:
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def _write(self, payload: list[dict]) -> None:
        self.file_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
