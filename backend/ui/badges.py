from __future__ import annotations

from html import escape

import streamlit as st


_BADGE_ICONS = {
    "success": "●",
    "warning": "●",
    "danger": "●",
    "critical": "●",
    "info": "●",
    "neutral": "●",
}


def badge_html(
    label: str,
    status: str = "neutral",
    icon: str | None = None,
) -> str:
    """Return a compact enterprise status badge."""

    normalized_status = status.casefold()

    badge_icon = (
        icon
        if icon is not None
        else _BADGE_ICONS.get(
            normalized_status,
            "●",
        )
    )

    return (
        f'<span class="fip-status-badge '
        f'fip-status-{escape(normalized_status)}">'
        f'<span class="fip-status-dot">'
        f'{escape(badge_icon)}</span>'
        f'{escape(label)}</span>'
    )


def render_badge(
    label: str,
    status: str = "neutral",
    icon: str | None = None,
) -> None:
    """Render one status badge."""

    st.markdown(
        badge_html(
            label=label,
            status=status,
            icon=icon,
        ),
        unsafe_allow_html=True,
    )


def component_css() -> str:
    """Return CSS required by status badges."""

    return """
    <style>
    .fip-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.28rem 0.58rem;
        border-radius: var(--fip-radius-pill);
        border: 1px solid currentColor;
        background: rgba(255,255,255,0.035);
        font-size: 0.72rem;
        font-weight: 700;
        line-height: 1;
        white-space: nowrap;
    }

    .fip-status-dot {
        font-size: 0.6rem;
        filter: drop-shadow(0 0 5px currentColor);
    }

    .fip-status-success { color: var(--fip-success); }
    .fip-status-warning { color: var(--fip-warning); }
    .fip-status-danger { color: var(--fip-danger); }
    .fip-status-critical { color: #F87171; }
    .fip-status-info { color: var(--fip-info); }
    .fip-status-neutral { color: var(--fip-text-muted); }
    </style>
    """


def apply_component_css() -> None:
    """Inject badge CSS."""

    st.markdown(
        component_css(),
        unsafe_allow_html=True,
    )
