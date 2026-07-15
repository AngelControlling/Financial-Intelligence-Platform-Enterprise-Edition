from __future__ import annotations

from html import escape

import streamlit as st

from models.executive_alert import ExecutiveAlert
from ui.html_renderer import render_html


SEVERITY_LABELS = {
    "critical": "Critical",
    "high": "High",
    "medium": "Attention",
    "success": "Positive",
}


def render_executive_alerts(
    alerts: list[ExecutiveAlert],
) -> None:
    st.markdown("### Executive Alerts")
    st.caption(
        "Ranked material exceptions and opportunities "
        "for the selected reporting period."
    )

    if not alerts:
        st.success(
            "No material alerts were detected "
            "for the selected period."
        )
        return

    critical_count = sum(
        alert.severity == "critical"
        for alert in alerts
    )
    high_count = sum(
        alert.severity == "high"
        for alert in alerts
    )
    positive_count = sum(
        alert.severity == "success"
        for alert in alerts
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric(
        "Material Alerts",
        len(alerts),
    )
    metric_2.metric(
        "Critical",
        critical_count,
    )
    metric_3.metric(
        "High",
        high_count,
    )
    metric_4.metric(
        "Positive",
        positive_count,
    )

    for start in range(
        0,
        len(alerts),
        2,
    ):
        row = alerts[
            start:start + 2
        ]
        columns = st.columns(
            len(row),
            gap="medium",
        )

        for column, alert in zip(
            columns,
            row,
        ):
            with column:
                _render_alert_card(alert)


def _render_alert_card(
    alert: ExecutiveAlert,
) -> None:
    severity = (
        alert.severity
        if alert.severity
        in {
            "critical",
            "high",
            "medium",
            "success",
        }
        else "medium"
    )

    render_html(
        '<div class="fip-alert-card '
        f'fip-alert-{escape(severity)}">'
        '<div class="fip-alert-top">'
        f'<div class="fip-alert-category">'
        f'{escape(alert.category)}</div>'
        f'<div class="fip-alert-pill">'
        f'{escape(SEVERITY_LABELS.get(severity, severity.title()))}'
        '</div>'
        '</div>'
        f'<div class="fip-alert-title">{escape(alert.title)}</div>'
        f'<div class="fip-alert-metric">{escape(alert.metric)}</div>'
        f'<div class="fip-alert-message">{escape(alert.message)}</div>'
        '<div class="fip-alert-action-label">Recommended action</div>'
        f'<div class="fip-alert-action">'
        f'{escape(alert.recommended_action)}</div>'
        '</div>'
    )


def apply_executive_alert_css() -> None:
    render_html(
        """
        <style>
        .fip-alert-card {
            min-height: 235px;
            background:
                linear-gradient(
                    150deg,
                    rgba(16,36,61,.98),
                    rgba(9,24,42,.98)
                );
            border: 1px solid var(--fip-border);
            border-left-width: 5px;
            border-radius: var(--fip-radius);
            padding: .9rem;
            box-shadow: var(--fip-shadow);
            box-sizing: border-box;
            margin-bottom: .8rem;
        }
        .fip-alert-critical {
            border-left-color: #ef4444;
        }
        .fip-alert-high {
            border-left-color: #f97316;
        }
        .fip-alert-medium {
            border-left-color: #f59e0b;
        }
        .fip-alert-success {
            border-left-color: #22c55e;
        }
        .fip-alert-top {
            display: flex;
            justify-content: space-between;
            gap: .7rem;
            align-items: center;
        }
        .fip-alert-category {
            color: var(--fip-muted);
            font-size: .66rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .06em;
        }
        .fip-alert-pill {
            color: var(--fip-text-2);
            border: 1px solid currentColor;
            border-radius: 999px;
            padding: .20rem .48rem;
            font-size: .62rem;
            font-weight: 800;
            text-transform: uppercase;
        }
        .fip-alert-title {
            color: var(--fip-text);
            font-size: 1rem;
            font-weight: 820;
            margin-top: .65rem;
        }
        .fip-alert-metric {
            color: var(--fip-cyan);
            font-size: 1.45rem;
            font-weight: 860;
            margin-top: .35rem;
            letter-spacing: -.035em;
        }
        .fip-alert-message {
            color: var(--fip-muted);
            font-size: .74rem;
            line-height: 1.45;
            margin-top: .4rem;
        }
        .fip-alert-action-label {
            color: var(--fip-disabled);
            font-size: .61rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .05em;
            border-top: 1px solid var(--fip-border);
            padding-top: .5rem;
            margin-top: .65rem;
        }
        .fip-alert-action {
            color: var(--fip-text-2);
            font-size: .70rem;
            line-height: 1.4;
            margin-top: .2rem;
        }
        </style>
        """
    )
