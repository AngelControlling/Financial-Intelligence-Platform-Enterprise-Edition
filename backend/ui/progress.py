from __future__ import annotations

from html import escape

import streamlit as st


def render_progress_indicator(
    label: str,
    value: float,
    target_label: str | None = None,
    status: str = "info",
) -> None:
    """Render an enterprise horizontal progress indicator."""

    normalized_value = max(
        0.0,
        min(float(value), 1.0),
    )

    target_html = (
        f'<span>{escape(target_label)}</span>'
        if target_label
        else ""
    )

    st.markdown(
        f"""
        <div class="fip-progress-component">
            <div class="fip-progress-heading">
                <span>{escape(label)}</span>
                <span>{normalized_value:.0%}</span>
            </div>

            <div class="fip-progress-track">
                <div
                    class="fip-progress-fill
                    fip-progress-{escape(status.casefold())}"
                    style="width: {normalized_value * 100:.1f}%;">
                </div>
            </div>

            <div class="fip-progress-footer">
                <span>0%</span>
                {target_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def component_css() -> str:
    """Return CSS required by progress indicators."""

    return """
    <style>
    .fip-progress-component {
        padding: 0.65rem 0;
    }

    .fip-progress-heading {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        color: var(--fip-text-secondary);
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .fip-progress-track {
        height: 8px;
        background: rgba(143,165,189,0.15);
        border-radius: var(--fip-radius-pill);
        overflow: hidden;
    }

    .fip-progress-fill {
        height: 100%;
        border-radius: var(--fip-radius-pill);
        background: currentColor;
        box-shadow: 0 0 12px currentColor;
    }

    .fip-progress-footer {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        color: var(--fip-text-disabled);
        font-size: 0.66rem;
        margin-top: 0.3rem;
    }

    .fip-progress-success { color: var(--fip-success); }
    .fip-progress-warning { color: var(--fip-warning); }
    .fip-progress-danger { color: var(--fip-danger); }
    .fip-progress-critical { color: #F87171; }
    .fip-progress-info { color: var(--fip-info); }
    .fip-progress-neutral { color: var(--fip-text-muted); }
    </style>
    """


def apply_component_css() -> None:
    """Inject progress CSS."""

    st.markdown(
        component_css(),
        unsafe_allow_html=True,
    )
