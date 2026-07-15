from __future__ import annotations

from ui.enterprise_theme import apply_enterprise_theme
from ui.executive_alerts import apply_executive_alert_css
from ui.mission_control_components import apply_mission_control_css
from ui.workspace_components import render_workspace_component_css


def apply_enterprise_ui() -> None:
    """Apply the full Enterprise visual framework."""

    apply_enterprise_theme()
    render_workspace_component_css()
    apply_mission_control_css()
    apply_executive_alert_css()
