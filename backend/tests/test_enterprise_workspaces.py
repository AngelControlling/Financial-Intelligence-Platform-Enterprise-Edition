from core.registry import (
    register_enterprise_workspaces,
)
from core.workspace_registry import (
    WorkspaceRegistry,
)


def test_frozen_workspace_keys() -> None:
    registry = WorkspaceRegistry()
    register_enterprise_workspaces(
        registry
    )

    assert registry.keys() == (
        "home",
        "mission_control",
        "financial",
        "operations",
        "data_center",
        "ai_center",
        "settings",
    )
