from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass(frozen=True)
class WorkspaceDefinition:
    key: str
    label: str
    icon: str
    renderer: Callable[[], None]
    section: str = "General"
    order: int = 100
    enabled: bool = True
    description: str = ""
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
