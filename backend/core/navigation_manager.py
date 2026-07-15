from __future__ import annotations

from core.notification_manager import NotificationManager
from core.router import Router
from core.state_manager import StateManager
from core.workspace_registry import WorkspaceRegistry
from ui.enterprise_sidebar import render_enterprise_sidebar


class NavigationManager:
    """Delegates navigation rendering to the Enterprise UI layer."""

    def __init__(
        self,
        registry: WorkspaceRegistry,
        router: Router,
        state: StateManager,
        notifications: NotificationManager,
    ) -> None:
        self.registry = registry
        self.router = router
        self.state = state
        self.notifications = notifications

    def render(self) -> None:
        render_enterprise_sidebar(
            registry=self.registry,
            router=self.router,
            state=self.state,
            notifications=self.notifications,
        )
