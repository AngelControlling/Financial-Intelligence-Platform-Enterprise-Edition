from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable

from ui.html_renderer import render_html


@dataclass(frozen=True)
class HeaderContextItem:
    label: str
    value: str
    status: str = "neutral"


def render_enterprise_header(
    title: str,
    subtitle: str,
    context_items: Iterable[HeaderContextItem] | None = None,
    eyebrow: str = "FINANCIAL INTELLIGENCE PLATFORM",
) -> None:
    """Render the compact enterprise header with Streamlit native HTML."""

    context_html = ""

    if context_items:
        items = "".join(
            (
                '<div class="fip-header-context-item">'
                f'<div class="fip-header-context-label">{escape(item.label)}</div>'
                f'<div class="fip-header-context-value">{escape(item.value)}</div>'
                '</div>'
            )
            for item in context_items
        )

        context_html = (
            '<div class="fip-header-context">'
            f'{items}'
            '</div>'
        )

    html = (
        '<div class="fip-enterprise-header">'
        '<div class="fip-header-main">'
        '<div>'
        f'<div class="fip-header-eyebrow">{escape(eyebrow)}</div>'
        f'<div class="fip-header-title">{escape(title)}</div>'
        f'<div class="fip-header-subtitle">{escape(subtitle)}</div>'
        '</div>'
        '<div class="fip-header-brandmark">FI</div>'
        '</div>'
        f'{context_html}'
        '</div>'
    )

    render_html(html)


def component_css() -> str:
    return """
    <style>
    .fip-enterprise-header {
        background: linear-gradient(145deg, rgba(15,34,58,.98), rgba(8,22,39,.98));
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-lg);
        padding: 1rem 1.15rem;
        box-shadow: var(--fip-shadow-card);
        margin-bottom: .85rem;
        box-sizing: border-box;
    }
    .fip-header-main {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
    }
    .fip-header-eyebrow {
        color: var(--fip-cyan);
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .12em;
    }
    .fip-header-title {
        color: var(--fip-text-primary);
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -.04em;
        margin-top: .12rem;
        line-height: 1.15;
    }
    .fip-header-subtitle {
        color: var(--fip-text-muted);
        font-size: .84rem;
        margin-top: .22rem;
    }
    .fip-header-brandmark {
        width: 42px;
        height: 42px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: .85rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--fip-primary), var(--fip-purple));
        box-shadow: 0 0 18px rgba(47,128,237,.28);
        flex: 0 0 auto;
    }
    .fip-header-context {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: .5rem;
        margin-top: .8rem;
        padding-top: .7rem;
        border-top: 1px solid var(--fip-border-subtle);
    }
    .fip-header-context-item {
        padding-right: .55rem;
        border-right: 1px solid var(--fip-border-subtle);
    }
    .fip-header-context-item:last-child { border-right: 0; }
    .fip-header-context-label {
        color: var(--fip-text-disabled);
        font-size: .62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .05em;
    }
    .fip-header-context-value {
        color: var(--fip-text-secondary);
        font-size: .78rem;
        font-weight: 700;
        margin-top: .12rem;
    }
    @media (max-width: 700px) {
        .fip-header-title { font-size: 1.35rem; }
        .fip-header-context { grid-template-columns: repeat(2, 1fr); }
    }
    </style>
    """


def apply_component_css() -> None:
    from ui.html_renderer import render_html
    render_html(component_css())
