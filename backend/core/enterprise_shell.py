from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from config.enterprise_config import CONFIG
from core.navigation_manager import NavigationManager
from core.notification_manager import NotificationManager
from core.router import Router
from core.session_manager import SessionManager
from core.state_manager import StateManager
from core.workspace_manager import WorkspaceManager
from core.workspace_registry import WorkspaceRegistry
from ui.component_registry import apply_enterprise_ui
from ui.enterprise_header import render_enterprise_header
from ui.elevenlabs_agent import render_global_elevenlabs_agent


class EnterpriseShell:
    """Top-level lifecycle and visual shell for FIP Enterprise."""

    def __init__(
        self,
        register_workspaces: Callable[
            [WorkspaceRegistry],
            None,
        ],
    ) -> None:
        self.session = SessionManager()
        self.session.initialize()

        self.state = StateManager(
            self.session
        )

        self.notifications = NotificationManager(
            self.session
        )

        self.registry = WorkspaceRegistry()
        register_workspaces(
            self.registry
        )

        self.router = Router(
            registry=self.registry,
            state=self.state,
        )

        self.navigation = NavigationManager(
            registry=self.registry,
            router=self.router,
            state=self.state,
            notifications=self.notifications,
        )

        self.workspace_manager = WorkspaceManager(
            registry=self.registry,
            router=self.router,
        )

    def run(self) -> None:
        st.set_page_config(
            page_title=CONFIG.product_name,
            page_icon="📊",
            layout=CONFIG.layout,
            initial_sidebar_state=(
                CONFIG.sidebar_state
            ),
        )

        apply_enterprise_ui()
        render_global_elevenlabs_agent()
        self.navigation.render()
        render_enterprise_header()
        self.workspace_manager.render()
