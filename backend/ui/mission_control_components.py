from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable

import streamlit as st

from ui.html_renderer import render_html


@dataclass(frozen=True)
class ExecutiveKPI:
    title: str
    value: str
    subtitle: str
    delta: str = ""
    status: str = "neutral"
    target: str = ""
    icon: str = ""


_STATUS_CLASS = {
    "success": "success",
    "warning": "warning",
    "danger": "danger",
    "info": "info",
    "neutral": "neutral",
}


def render_executive_kpi(kpi: ExecutiveKPI) -> None:
    status = _STATUS_CLASS.get(
        kpi.status,
        "neutral",
    )

    delta_html = (
        f'<div class="fip-native-kpi-delta fip-native-{status}">'
        f'{escape(kpi.delta)}</div>'
        if kpi.delta
        else ""
    )

    target_html = (
        f'<div class="fip-native-kpi-target">{escape(kpi.target)}</div>'
        if kpi.target
        else ""
    )

    render_html(
        '<div class="fip-native-kpi-card">'
        '<div class="fip-native-kpi-top">'
        '<div>'
        f'<div class="fip-native-kpi-title">{escape(kpi.title)}</div>'
        f'<div class="fip-native-kpi-subtitle">{escape(kpi.subtitle)}</div>'
        '</div>'
        f'<div class="fip-native-kpi-icon">{escape(kpi.icon)}</div>'
        '</div>'
        f'<div class="fip-native-kpi-value">{escape(kpi.value)}</div>'
        f'{delta_html}'
        f'{target_html}'
        '</div>'
    )


def render_executive_kpi_grid(
    kpis: Iterable[ExecutiveKPI],
    columns: int = 4,
) -> None:
    items = list(kpis)

    for start in range(0, len(items), columns):
        row = items[start:start + columns]
        cols = st.columns(
            len(row),
            gap="medium",
        )

        for column, kpi in zip(cols, row):
            with column:
                render_executive_kpi(kpi)


def render_health_strip(
    *,
    score: float,
    revenue_delta: float,
    gp_delta: float,
    margin_pp: float,
    operations_score: float,
    data_quality_score: float,
    comparison_label: str,
) -> None:
    status = (
        "success"
        if score >= 90
        else "info"
        if score >= 75
        else "warning"
        if score >= 60
        else "danger"
    )

    render_html(
        '<div class="fip-native-health">'
        '<div class="fip-native-health-score">'
        '<div class="fip-native-health-label">Financial Health</div>'
        f'<div class="fip-native-health-value">{score:.0f}/100</div>'
        f'<div class="fip-native-health-live fip-native-{status}">● Live Status</div>'
        '</div>'
        '<div class="fip-native-health-signals">'
        + _signal(
            "Revenue",
            f"{revenue_delta:+.1%}",
            f"vs {comparison_label}",
            "success" if revenue_delta >= 0 else "danger",
        )
        + _signal(
            "Gross Profit",
            f"{gp_delta:+.1%}",
            f"vs {comparison_label}",
            "success" if gp_delta >= 0 else "danger",
        )
        + _signal(
            "Margin",
            f"{margin_pp * 100:+.2f} pp",
            "Profitability",
            "success" if margin_pp >= 0 else "danger",
        )
        + _signal(
            "Operations",
            f"{operations_score:.0f}",
            "Health score",
            "success" if operations_score >= 90 else "warning",
        )
        + _signal(
            "Data Quality",
            f"{data_quality_score:.0f}%",
            "Canonical readiness",
            "success" if data_quality_score >= 90 else "warning",
        )
        + '</div>'
        '</div>'
    )


def _signal(
    label: str,
    value: str,
    detail: str,
    status: str,
) -> str:
    return (
        '<div class="fip-native-signal">'
        f'<div class="fip-native-signal-label fip-native-{status}">'
        f'● {escape(label)}</div>'
        f'<div class="fip-native-signal-value">{escape(value)}</div>'
        f'<div class="fip-native-signal-detail">{escape(detail)}</div>'
        '</div>'
    )


def apply_mission_control_css() -> None:
    render_html(
        """
        <style>
        .fip-native-health {
            display: grid;
            grid-template-columns: 165px 1fr;
            gap: .8rem;
            background:
                linear-gradient(
                    145deg,
                    rgba(16,36,61,.98),
                    rgba(8,22,39,.98)
                );
            border: 1px solid var(--fip-border);
            border-radius: var(--fip-radius);
            padding: .8rem;
            box-shadow: var(--fip-shadow);
            margin-bottom: .9rem;
        }
        .fip-native-health-score {
            border-right: 1px solid var(--fip-border);
            padding-right: .8rem;
        }
        .fip-native-health-label {
            color: var(--fip-muted);
            font-size: .65rem;
            font-weight: 800;
            text-transform: uppercase;
        }
        .fip-native-health-value {
            color: var(--fip-text);
            font-size: 1.7rem;
            font-weight: 850;
            margin-top: .2rem;
        }
        .fip-native-health-live {
            font-size: .67rem;
            font-weight: 750;
            margin-top: .15rem;
        }
        .fip-native-health-signals {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(115px, 1fr));
            gap: .5rem;
        }
        .fip-native-signal {
            background: rgba(255,255,255,.025);
            border: 1px solid rgba(143,165,189,.14);
            border-radius: 10px;
            padding: .55rem .62rem;
        }
        .fip-native-signal-label {
            font-size: .66rem;
            font-weight: 750;
        }
        .fip-native-signal-value {
            color: var(--fip-text);
            font-size: .95rem;
            font-weight: 850;
            margin-top: .28rem;
        }
        .fip-native-signal-detail {
            color: var(--fip-disabled);
            font-size: .61rem;
            margin-top: .12rem;
        }
        .fip-native-kpi-card {
            min-height: 172px;
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
        .fip-native-kpi-top {
            display: flex;
            justify-content: space-between;
            gap: .6rem;
        }
        .fip-native-kpi-title {
            color: var(--fip-text-2);
            font-size: .72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .045em;
        }
        .fip-native-kpi-subtitle {
            color: var(--fip-disabled);
            font-size: .64rem;
            margin-top: .12rem;
        }
        .fip-native-kpi-icon {
            width: 32px;
            height: 32px;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            background: rgba(47,128,237,.14);
            border: 1px solid rgba(47,128,237,.30);
            font-size: .72rem;
            font-weight: 850;
        }
        .fip-native-kpi-value {
            color: var(--fip-text);
            font-size: 1.55rem;
            font-weight: 850;
            letter-spacing: -.04em;
            margin-top: .72rem;
        }
        .fip-native-kpi-delta {
            display: inline-flex;
            padding: .20rem .46rem;
            border-radius: 999px;
            border: 1px solid currentColor;
            font-size: .66rem;
            font-weight: 750;
            margin-top: .35rem;
        }
        .fip-native-kpi-target {
            color: var(--fip-muted);
            font-size: .63rem;
            margin-top: .5rem;
            padding-top: .42rem;
            border-top: 1px solid var(--fip-border);
        }
        .fip-native-success { color: var(--fip-success); }
        .fip-native-info { color: var(--fip-cyan); }
        .fip-native-warning { color: var(--fip-warning); }
        .fip-native-danger { color: var(--fip-danger); }
        .fip-native-neutral { color: var(--fip-muted); }

        @media (max-width: 850px) {
            .fip-native-health {
                grid-template-columns: 1fr;
            }

            .fip-native-health-score {
                border-right: 0;
                border-bottom: 1px solid var(--fip-border);
                padding-bottom: .6rem;
            }
        }
        </style>
        """
    )
