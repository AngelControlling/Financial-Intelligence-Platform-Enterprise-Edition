from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable

import streamlit as st

from ui.html_renderer import render_html


@dataclass(frozen=True)
class StatusCard:
    title: str
    status: str
    description: str
    metric: str = "—"
    meta: str = ""
    icon: str = "•"


_STATUS_CLASS = {
    "active": "success",
    "ready": "success",
    "healthy": "success",
    "online": "success",
    "validated": "info",
    "pending": "warning",
    "missing": "neutral",
    "attention": "warning",
    "critical": "danger",
}


def render_status_card(
    card: StatusCard,
) -> None:
    status_key = card.status.casefold()
    color_class = _STATUS_CLASS.get(
        status_key,
        "neutral",
    )

    render_html(
        '<div class="fip-status-card">'
        '<div class="fip-status-card-top">'
        f'<div class="fip-status-card-icon">{escape(card.icon)}</div>'
        f'<div class="fip-status-pill fip-status-{escape(color_class)}">'
        f'{escape(card.status)}</div>'
        '</div>'
        f'<div class="fip-status-card-title">{escape(card.title)}</div>'
        f'<div class="fip-status-card-metric">{escape(card.metric)}</div>'
        f'<div class="fip-status-card-description">{escape(card.description)}</div>'
        f'<div class="fip-status-card-meta">{escape(card.meta)}</div>'
        '</div>'
    )


def render_status_grid(
    cards: Iterable[StatusCard],
    columns: int = 3,
) -> None:
    card_list = list(cards)
    if not card_list:
        return

    for start in range(
        0,
        len(card_list),
        columns,
    ):
        row = card_list[
            start:start + columns
        ]
        cols = st.columns(
            len(row),
            gap="medium",
        )

        for column, card in zip(
            cols,
            row,
        ):
            with column:
                render_status_card(card)


def render_empty_state(
    *,
    title: str,
    message: str,
    action_label: str | None = None,
    action_workspace: str | None = None,
) -> None:
    render_html(
        '<div class="fip-empty-state">'
        '<div class="fip-empty-icon">◈</div>'
        f'<div class="fip-empty-title">{escape(title)}</div>'
        f'<div class="fip-empty-message">{escape(message)}</div>'
        '</div>'
    )

    if (
        action_label
        and action_workspace
        and st.button(
            action_label,
            key=(
                "fip_empty_action_"
                f"{action_workspace}"
            ),
            type="primary",
        )
    ):
        st.session_state[
            "fip_current_workspace"
        ] = action_workspace
        st.rerun()


def render_workspace_component_css() -> None:
    render_html(
        """
        <style>
        .fip-status-card {
            min-height: 185px;
            background:
                linear-gradient(
                    150deg,
                    rgba(16,36,61,.98),
                    rgba(9,24,42,.98)
                );
            border: 1px solid var(--fip-border);
            border-radius: var(--fip-radius);
            padding: .9rem;
            box-shadow: var(--fip-shadow);
            box-sizing: border-box;
        }
        .fip-status-card-top {
            display: flex;
            justify-content: space-between;
            gap: .6rem;
            align-items: center;
        }
        .fip-status-card-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            background: rgba(47,128,237,.14);
            border: 1px solid rgba(47,128,237,.30);
            font-weight: 800;
        }
        .fip-status-pill {
            padding: .24rem .5rem;
            border-radius: 999px;
            font-size: .65rem;
            font-weight: 800;
            text-transform: uppercase;
            border: 1px solid currentColor;
        }
        .fip-status-success { color: var(--fip-success); }
        .fip-status-info { color: var(--fip-cyan); }
        .fip-status-warning { color: var(--fip-warning); }
        .fip-status-danger { color: var(--fip-danger); }
        .fip-status-neutral { color: var(--fip-muted); }
        .fip-status-card-title {
            color: var(--fip-text-2);
            font-size: .75rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: .045em;
            margin-top: .75rem;
        }
        .fip-status-card-metric {
            color: var(--fip-text);
            font-size: 1.55rem;
            font-weight: 850;
            letter-spacing: -.04em;
            margin-top: .35rem;
        }
        .fip-status-card-description {
            color: var(--fip-muted);
            font-size: .73rem;
            margin-top: .35rem;
            min-height: 34px;
        }
        .fip-status-card-meta {
            color: var(--fip-disabled);
            font-size: .65rem;
            margin-top: .6rem;
            padding-top: .5rem;
            border-top: 1px solid var(--fip-border);
        }
        .fip-empty-state {
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background:
                linear-gradient(
                    145deg,
                    rgba(16,36,61,.74),
                    rgba(8,22,39,.70)
                );
            border: 1px dashed var(--fip-border-strong);
            border-radius: var(--fip-radius);
            padding: 2rem;
            margin-bottom: .8rem;
        }
        .fip-empty-icon {
            color: var(--fip-cyan);
            font-size: 2.2rem;
        }
        .fip-empty-title {
            color: var(--fip-text);
            font-size: 1.2rem;
            font-weight: 800;
            margin-top: .5rem;
        }
        .fip-empty-message {
            color: var(--fip-muted);
            font-size: .82rem;
            max-width: 620px;
            margin-top: .35rem;
        }
        </style>
        """
    )
