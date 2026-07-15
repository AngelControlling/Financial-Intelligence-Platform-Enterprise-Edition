from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable

from ui.html_renderer import render_html


@dataclass(frozen=True)
class MissionControlSignal:
    label: str
    value: str
    status: str
    detail: str | None = None


_STATUS_ICON = {
    "success": "●",
    "warning": "●",
    "danger": "●",
    "critical": "●",
    "info": "●",
    "neutral": "●",
}


def render_mission_control_strip(
    title: str,
    score: str,
    signals: Iterable[MissionControlSignal],
    status: str = "success",
) -> None:
    """Render Mission Control signals using native HTML."""

    signal_html = "".join(
        (
            '<div class="fip-mission-signal">'
            '<div class="fip-mission-signal-top">'
            f'<span class="fip-mission-dot fip-mission-{escape(signal.status.casefold())}">'
            f'{_STATUS_ICON.get(signal.status.casefold(), "●")}</span>'
            f'<span class="fip-mission-label">{escape(signal.label)}</span>'
            '</div>'
            f'<div class="fip-mission-value">{escape(signal.value)}</div>'
            + (
                f'<div class="fip-mission-detail">{escape(signal.detail)}</div>'
                if signal.detail
                else ""
            )
            + '</div>'
        )
        for signal in signals
    )

    html = (
        '<div class="fip-mission-control">'
        '<div class="fip-mission-score-block">'
        f'<div class="fip-mission-title">{escape(title)}</div>'
        f'<div class="fip-mission-score">{escape(score)}</div>'
        f'<div class="fip-mission-score-status fip-mission-{escape(status.casefold())}">'
        f'{_STATUS_ICON.get(status.casefold(), "●")} Live Status'
        '</div>'
        '</div>'
        f'<div class="fip-mission-signals">{signal_html}</div>'
        '</div>'
    )

    render_html(html)


def component_css() -> str:
    return """
    <style>
    .fip-mission-control {
        display: grid;
        grid-template-columns: 170px 1fr;
        gap: .85rem;
        background: linear-gradient(135deg, rgba(13,27,47,.98), rgba(8,22,39,.98));
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-lg);
        padding: .8rem;
        box-shadow: var(--fip-shadow-card);
        margin-bottom: .9rem;
        box-sizing: border-box;
    }
    .fip-mission-score-block {
        border-right: 1px solid var(--fip-border-subtle);
        padding-right: .85rem;
    }
    .fip-mission-title {
        color: var(--fip-text-muted);
        font-size: .68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .06em;
    }
    .fip-mission-score {
        color: var(--fip-text-primary);
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -.045em;
        margin-top: .2rem;
    }
    .fip-mission-score-status {
        font-size: .68rem;
        font-weight: 700;
        margin-top: .15rem;
    }
    .fip-mission-signals {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(105px, 1fr));
        gap: .5rem;
    }
    .fip-mission-signal {
        min-height: 72px;
        padding: .58rem .65rem;
        background: rgba(255,255,255,.025);
        border: 1px solid rgba(143,165,189,.12);
        border-radius: var(--fip-radius-md);
        box-sizing: border-box;
    }
    .fip-mission-signal-top {
        display: flex;
        align-items: center;
        gap: .32rem;
    }
    .fip-mission-dot {
        font-size: .58rem;
        filter: drop-shadow(0 0 5px currentColor);
    }
    .fip-mission-label {
        color: var(--fip-text-muted);
        font-size: .67rem;
        font-weight: 700;
    }
    .fip-mission-value {
        color: var(--fip-text-primary);
        font-size: .95rem;
        font-weight: 800;
        margin-top: .3rem;
    }
    .fip-mission-detail {
        color: var(--fip-text-disabled);
        font-size: .62rem;
        margin-top: .1rem;
    }
    .fip-mission-success { color: var(--fip-success); }
    .fip-mission-warning { color: var(--fip-warning); }
    .fip-mission-danger { color: var(--fip-danger); }
    .fip-mission-critical { color: #F87171; }
    .fip-mission-info { color: var(--fip-info); }
    .fip-mission-neutral { color: var(--fip-text-muted); }
    @media (max-width: 850px) {
        .fip-mission-control { grid-template-columns: 1fr; }
        .fip-mission-score-block {
            border-right: 0;
            border-bottom: 1px solid var(--fip-border-subtle);
            padding-right: 0;
            padding-bottom: .65rem;
        }
    }
    </style>
    """


def apply_component_css() -> None:
    render_html(component_css())
