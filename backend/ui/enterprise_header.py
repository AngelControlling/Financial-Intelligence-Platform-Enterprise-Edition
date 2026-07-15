from __future__ import annotations

from html import escape

from config.enterprise_config import CONFIG
from ui.html_renderer import render_html


def render_enterprise_header() -> None:
    """Render the fixed product header shared by all workspaces."""

    render_html(
        '<div class="fip-shell-header">'
        '<div>'
        f'<div class="fip-shell-eyebrow">{escape(CONFIG.product_subtitle.upper())}</div>'
        f'<div class="fip-shell-title">{escape(CONFIG.product_name)}</div>'
        f'<div class="fip-shell-subtitle">{escape(CONFIG.edition)}</div>'
        '</div>'
        f'<div class="fip-shell-badge">V{escape(CONFIG.version)}</div>'
        '</div>'
    )
