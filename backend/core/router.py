from __future__ import annotations

import streamlit as st

from core.state_manager import StateManager
from core.workspace_registry import WorkspaceRegistry
from ui.enterprise_footer import render_enterprise_footer
from ui.workspace_banner import render_workspace_banner


class Router:
    """Resolves and renders the active Enterprise workspace."""

    def __init__(
        self,
        registry: WorkspaceRegistry,
        state: StateManager,
    ) -> None:
        self.registry = registry
        self.state = state

    def navigate(self, workspace_key: str) -> None:
        self.registry.get(workspace_key)
        self.state.set_current_workspace(
            workspace_key
        )
        st.rerun()

    def render(self) -> None:
        key = self.state.current_workspace

        if key not in self.registry.keys():
            key = "home"
            self.state.set_current_workspace(key)

        workspace = self.registry.get(key)

        missing = [
            capability
            for capability
            in workspace.required_capabilities
            if not self.state.has_capability(
                capability
            )
        ]

        render_workspace_banner(
            workspace=workspace,
            state=self.state,
        )

        if missing:
            st.warning(
                "This workspace is not ready. "
                f"Missing capabilities: "
                f"{', '.join(missing)}"
            )
        else:
            workspace.renderer()

        render_enterprise_footer(
            self.state
        )
