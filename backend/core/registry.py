from __future__ import annotations

from core.workspace_registry import (
    WorkspaceRegistry,
)
from models.workspace import (
    WorkspaceDefinition,
)
from workspaces.ai_center import (
    render_ai_center_workspace,
)
from workspaces.data_center import (
    render_data_center_workspace,
)
from workspaces.financial import (
    render_financial_workspace,
)
from workspaces.home import (
    render_home_workspace,
)
from workspaces.mission_control_shell import (
    render_mission_control_shell,
)
from workspaces.operations import (
    render_operations_workspace,
)
from workspaces.settings import (
    render_settings_workspace,
)


def register_enterprise_workspaces(
    registry: WorkspaceRegistry,
) -> None:
    """Register the frozen V2 enterprise navigation."""

    definitions = [
        WorkspaceDefinition(
            key="home",
            label="Home",
            icon="🏠",
            section="Executive",
            order=10,
            description=(
                "Enterprise overview, source readiness "
                "and direct analytical access."
            ),
            renderer=render_home_workspace,
        ),
        WorkspaceDefinition(
            key="mission_control",
            label="Mission Control",
            icon="📊",
            section="Executive",
            order=20,
            description=(
                "Executive financial and operational "
                "command center."
            ),
            renderer=(
                render_mission_control_shell
            ),
        ),
        WorkspaceDefinition(
            key="financial",
            label="Financial",
            icon="💰",
            section="Intelligence",
            order=10,
            description=(
                "P&L, Budget, Forecast, OPEX, Personnel "
                "and Working Capital intelligence."
            ),
            renderer=(
                render_financial_workspace
            ),
        ),
        WorkspaceDefinition(
            key="operations",
            label="Operations",
            icon="🚚",
            section="Intelligence",
            order=20,
            description=(
                "Air, Ocean, Ground, customers, "
                "trade lanes and operational volumes."
            ),
            renderer=(
                render_operations_workspace
            ),
        ),
        WorkspaceDefinition(
            key="data_center",
            label="Data Center",
            icon="📂",
            section="Administration",
            order=10,
            description=(
                "Centralized ingestion, validation, "
                "activation, versioning and history."
            ),
            renderer=(
                render_data_center_workspace
            ),
        ),
        WorkspaceDefinition(
            key="ai_center",
            label="AI Center",
            icon="🤖",
            section="Administration",
            order=20,
            description=(
                "Executive commentary, recommendations "
                "and conversational finance."
            ),
            renderer=(
                render_ai_center_workspace
            ),
        ),
        WorkspaceDefinition(
            key="settings",
            label="Settings",
            icon="⚙️",
            section="Administration",
            order=30,
            description=(
                "Enterprise context, roles and "
                "platform governance."
            ),
            renderer=(
                render_settings_workspace
            ),
        ),
    ]

    for definition in definitions:
        registry.register(definition)


# Backward-compatible alias for the Module 01A preview launcher.
register_placeholder_workspaces = (
    register_enterprise_workspaces
)
