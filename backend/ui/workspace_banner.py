from __future__ import annotations

from html import escape

from core.state_manager import StateManager
from models.workspace import WorkspaceDefinition
from ui.html_renderer import render_html


def render_workspace_banner(
    workspace: WorkspaceDefinition,
    state: StateManager,
) -> None:
    """Render active workspace identity and business context."""

    render_html(
        '<div class="fip-workspace-banner">'
        f'<div class="fip-workspace-title">{escape(workspace.icon)} {escape(workspace.label)}</div>'
        f'<div class="fip-workspace-description">{escape(workspace.description or "Enterprise workspace")}</div>'
        '<div class="fip-context-strip">'
        '<div class="fip-context-item">'
        '<div class="fip-context-label">Company</div>'
        f'<div class="fip-context-value">{escape(state.company)}</div>'
        '</div>'
        '<div class="fip-context-item">'
        '<div class="fip-context-label">Currency</div>'
        f'<div class="fip-context-value">{escape(state.currency)}</div>'
        '</div>'
        '<div class="fip-context-item">'
        '<div class="fip-context-label">Workspace</div>'
        f'<div class="fip-context-value">{escape(workspace.key)}</div>'
        '</div>'
        '<div class="fip-context-item">'
        '<div class="fip-context-label">Status</div>'
        '<div class="fip-context-value">Ready</div>'
        '</div>'
        '</div>'
        '</div>'
    )
