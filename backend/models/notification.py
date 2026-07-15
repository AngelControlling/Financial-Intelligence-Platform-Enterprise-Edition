from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Notification:
    title: str
    message: str
    severity: str = "info"
    workspace_key: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    notification_id: str = ""
    def __post_init__(self) -> None:
        if not self.notification_id: self.notification_id = str(uuid4())
