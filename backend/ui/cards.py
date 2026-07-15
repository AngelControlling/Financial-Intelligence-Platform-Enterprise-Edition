from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable

import streamlit as st

from ui.html_renderer import render_html


@dataclass(frozen=True)
class KPICard:
    title: str
    value: str
    delta: str | None = None
    status: str = "neutral"
    subtitle: str | None = None
    icon: str | None = None
    progress: float | None = None
    target_label: str | None = None


_STATUS_CLASS = {
    "success": "fip-kpi-success",
    "warning": "fip-kpi-warning",
    "danger": "fip-kpi-danger",
    "critical": "fip-kpi-critical",
    "info": "fip-kpi-info",
    "neutral": "fip-kpi-neutral",
}


def _normalize_progress(value: float | None) -> float | None:
    if value is None:
        return None
    return max(0.0, min(float(value), 1.0))


def render_kpi_card(card: KPICard) -> None:
    """Render a premium KPI card using Streamlit native HTML."""

    status_class = _STATUS_CLASS.get(
        card.status.casefold(),
        _STATUS_CLASS["neutral"],
    )

    icon_html = (
        f'<div class="fip-kpi-icon">{escape(card.icon)}</div>'
        if card.icon
        else ""
    )

    subtitle_html = (
        f'<div class="fip-kpi-subtitle">{escape(card.subtitle)}</div>'
        if card.subtitle
        else ""
    )

    delta_html = (
        f'<div class="fip-kpi-delta {status_class}">{escape(card.delta)}</div>'
        if card.delta
        else ""
    )

    progress_html = ""
    progress_value = _normalize_progress(card.progress)

    if progress_value is not None:
        width = progress_value * 100
        target_html = (
            f'<span>{escape(card.target_label)}</span>'
            if card.target_label
            else ""
        )

        progress_html = (
            '<div class="fip-kpi-progress-wrap">'
            '<div class="fip-kpi-progress-track">'
            f'<div class="fip-kpi-progress-fill {status_class}" '
            f'style="width:{width:.1f}%"></div>'
            '</div>'
            '<div class="fip-kpi-progress-meta">'
            f'<span>{width:.0f}%</span>{target_html}'
            '</div>'
            '</div>'
        )

    html = (
        '<div class="fip-kpi-card">'
        '<div class="fip-kpi-topline">'
        '<div>'
        f'<div class="fip-kpi-title">{escape(card.title)}</div>'
        f'{subtitle_html}'
        '</div>'
        f'{icon_html}'
        '</div>'
        f'<div class="fip-kpi-value">{escape(card.value)}</div>'
        f'{delta_html}'
        f'{progress_html}'
        '</div>'
    )

    render_html(html)


def render_kpi_grid(
    cards: Iterable[KPICard],
    columns: int = 4,
) -> None:
    card_list = list(cards)
    if not card_list:
        return

    columns = max(1, int(columns))

    for start in range(0, len(card_list), columns):
        row_cards = card_list[start:start + columns]
        row_columns = st.columns(len(row_cards), gap="medium")

        for column, card in zip(row_columns, row_cards):
            with column:
                render_kpi_card(card)


def component_css() -> str:
    return """
    <style>
    .fip-kpi-card {
        min-height: 176px;
        background: linear-gradient(155deg, rgba(17,39,65,.98), rgba(9,24,42,.98));
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-lg);
        padding: 1rem 1.05rem;
        box-shadow: var(--fip-shadow-card);
        transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
        overflow: hidden;
        position: relative;
        box-sizing: border-box;
    }
    .fip-kpi-card::after {
        content: "";
        position: absolute;
        width: 110px;
        height: 110px;
        right: -52px;
        top: -56px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(47,128,237,.18), transparent 70%);
        pointer-events: none;
    }
    .fip-kpi-card:hover {
        transform: translateY(-3px);
        border-color: var(--fip-border-strong);
        background: var(--fip-bg-card-hover);
    }
    .fip-kpi-topline {
        display: flex;
        justify-content: space-between;
        gap: .75rem;
        align-items: flex-start;
    }
    .fip-kpi-title {
        color: var(--fip-text-muted);
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .055em;
    }
    .fip-kpi-subtitle {
        color: var(--fip-text-disabled);
        font-size: .72rem;
        margin-top: .18rem;
    }
    .fip-kpi-icon {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(47,128,237,.12);
        border: 1px solid rgba(47,128,237,.26);
        font-size: .85rem;
        font-weight: 800;
        color: var(--fip-text-primary);
    }
    .fip-kpi-value {
        color: var(--fip-text-primary);
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -.04em;
        margin-top: .7rem;
    }
    .fip-kpi-delta {
        display: inline-flex;
        align-items: center;
        width: fit-content;
        margin-top: .35rem;
        padding: .2rem .5rem;
        border-radius: var(--fip-radius-pill);
        font-size: .73rem;
        font-weight: 700;
        background: rgba(255,255,255,.035);
        border: 1px solid currentColor;
    }
    .fip-kpi-progress-wrap { margin-top: .8rem; }
    .fip-kpi-progress-track {
        height: 6px;
        background: rgba(143,165,189,.16);
        border-radius: var(--fip-radius-pill);
        overflow: hidden;
    }
    .fip-kpi-progress-fill {
        height: 100%;
        border-radius: var(--fip-radius-pill);
        background: currentColor;
        box-shadow: 0 0 10px currentColor;
    }
    .fip-kpi-progress-meta {
        display: flex;
        justify-content: space-between;
        gap: .5rem;
        color: var(--fip-text-muted);
        font-size: .7rem;
        margin-top: .35rem;
    }
    .fip-kpi-success { color: var(--fip-success); }
    .fip-kpi-warning { color: var(--fip-warning); }
    .fip-kpi-danger { color: var(--fip-danger); }
    .fip-kpi-critical { color: var(--fip-critical); }
    .fip-kpi-info { color: var(--fip-info); }
    .fip-kpi-neutral { color: var(--fip-text-muted); }
    </style>
    """


def apply_component_css() -> None:
    render_html(component_css())
