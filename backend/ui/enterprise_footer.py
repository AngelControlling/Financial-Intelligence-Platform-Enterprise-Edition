from __future__ import annotations

from datetime import datetime
from html import escape

from config.enterprise_config import CONFIG
from core.state_manager import StateManager
from ui.html_renderer import render_html


def render_enterprise_footer(
    state: StateManager,
) -> None:
    """Render a consistent audit-friendly workspace footer."""

    render_html(
        '<div class="fip-footer">'
        f'<div>{escape(CONFIG.product_name)} · {escape(CONFIG.edition)}</div>'
        f'<div>Company: {escape(state.company)} · Currency: {escape(state.currency)}</div>'
        f'<div>Session refresh: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>'
        '</div>'
    )
