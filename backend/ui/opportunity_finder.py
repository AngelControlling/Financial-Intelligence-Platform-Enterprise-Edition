from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from engines.opportunity_finder_engine import (
    OpportunityFinderEngine,
)
from ui.html_renderer import render_html


PRIORITY_CLASS = {
    "Critical": "critical",
    "High": "high",
    "Medium": "medium",
    "Low": "low",
}


def render_opportunity_finder(
    dataframe: pd.DataFrame,
) -> None:
    apply_opportunity_finder_css()

    st.markdown("### Opportunity Finder")
    st.caption(
        "Identify growth, margin recovery and replication "
        "opportunities for the selected period."
    )

    opportunities = OpportunityFinderEngine().find(
        dataframe,
        max_opportunities=12,
    )

    if not opportunities:
        st.info(
            "No material business opportunities "
            "were detected for the selected period."
        )
        return

    total_gp_upside = sum(
        item.estimated_gp_upside
        for item in opportunities
    )
    total_revenue_upside = sum(
        item.estimated_revenue_upside
        for item in opportunities
    )
    high_confidence = sum(
        item.confidence_score >= 0.85
        for item in opportunities
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )
    metric_1.metric(
        "Detected Opportunities",
        len(opportunities),
    )
    metric_2.metric(
        "Estimated GP Upside",
        f"${total_gp_upside:,.0f}",
    )
    metric_3.metric(
        "Estimated Revenue Upside",
        f"${total_revenue_upside:,.0f}",
    )
    metric_4.metric(
        "High-Confidence",
        high_confidence,
    )

    categories = sorted(
        {
            item.category
            for item in opportunities
        }
    )
    selected = st.multiselect(
        "Opportunity Categories",
        options=categories,
        default=categories,
        key="opportunity_categories",
    )

    filtered = [
        item
        for item in opportunities
        if item.category in selected
    ]

    for start in range(0, len(filtered), 2):
        row = filtered[start:start + 2]
        columns = st.columns(
            len(row),
            gap="medium",
        )

        for column, item in zip(
            columns,
            row,
        ):
            with column:
                _render_opportunity_card(item)

    st.markdown("#### Opportunity Portfolio")

    portfolio = pd.DataFrame(
        [
            {
                "Priority": item.priority,
                "Category": item.category,
                "Dimension": (
                    item.dimension
                    .replace("_", " ")
                    .title()
                ),
                "Value": item.value,
                "Revenue": item.revenue,
                "GP": item.gross_profit,
                "Margin": item.margin,
                "Revenue Share": item.revenue_share,
                "Revenue Upside": (
                    item.estimated_revenue_upside
                ),
                "GP Upside": (
                    item.estimated_gp_upside
                ),
                "Confidence": (
                    item.confidence_score
                ),
            }
            for item in filtered
        ]
    )

    st.dataframe(
        portfolio.style.format(
            {
                "Revenue": "${:,.0f}",
                "GP": "${:,.0f}",
                "Margin": "{:.1%}",
                "Revenue Share": "{:.1%}",
                "Revenue Upside": "${:,.0f}",
                "GP Upside": "${:,.0f}",
                "Confidence": "{:.0%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _render_opportunity_card(
    opportunity,
) -> None:
    priority_class = PRIORITY_CLASS.get(
        opportunity.priority,
        "medium",
    )

    render_html(
        '<div class="fip-opportunity-card '
        f'fip-opportunity-{escape(priority_class)}">'
        '<div class="fip-opportunity-top">'
        f'<div class="fip-opportunity-category">'
        f'{escape(opportunity.category)}</div>'
        f'<div class="fip-opportunity-priority">'
        f'{escape(opportunity.priority)}</div>'
        '</div>'
        f'<div class="fip-opportunity-title">'
        f'{escape(opportunity.title)}</div>'
        f'<div class="fip-opportunity-value">'
        f'{escape(opportunity.value)}</div>'
        '<div class="fip-opportunity-metrics">'
        f'<span>Margin {opportunity.margin:.1%}</span>'
        f'<span>GP Upside ${opportunity.estimated_gp_upside:,.0f}</span>'
        f'<span>Confidence {opportunity.confidence_score:.0%}</span>'
        '</div>'
        f'<div class="fip-opportunity-rationale">'
        f'{escape(opportunity.rationale)}</div>'
        '<div class="fip-opportunity-action-label">'
        'Recommended action</div>'
        f'<div class="fip-opportunity-action">'
        f'{escape(opportunity.recommended_action)}</div>'
        '</div>'
    )


def apply_opportunity_finder_css() -> None:
    render_html(
        """
        <style>
        .fip-opportunity-card {
            min-height: 255px;
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
            margin-bottom: .8rem;
        }
        .fip-opportunity-critical {
            border-left-color: #ef4444;
        }
        .fip-opportunity-high {
            border-left-color: #f97316;
        }
        .fip-opportunity-medium {
            border-left-color: #22c55e;
        }
        .fip-opportunity-low {
            border-left-color: #2f80ed;
        }
        .fip-opportunity-top {
            display: flex;
            justify-content: space-between;
            gap: .7rem;
            align-items: center;
        }
        .fip-opportunity-category {
            color: var(--fip-cyan);
            font-size: .66rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .06em;
        }
        .fip-opportunity-priority {
            color: var(--fip-text-2);
            border: 1px solid currentColor;
            border-radius: 999px;
            padding: .18rem .46rem;
            font-size: .62rem;
            font-weight: 800;
        }
        .fip-opportunity-title {
            color: var(--fip-text);
            font-size: 1rem;
            font-weight: 820;
            margin-top: .62rem;
        }
        .fip-opportunity-value {
            color: var(--fip-cyan);
            font-size: 1.28rem;
            font-weight: 850;
            margin-top: .25rem;
        }
        .fip-opportunity-metrics {
            display: flex;
            flex-wrap: wrap;
            gap: .35rem;
            margin-top: .45rem;
        }
        .fip-opportunity-metrics span {
            color: var(--fip-text-2);
            border: 1px solid var(--fip-border);
            border-radius: 999px;
            padding: .18rem .42rem;
            font-size: .61rem;
        }
        .fip-opportunity-rationale {
            color: var(--fip-muted);
            font-size: .72rem;
            line-height: 1.45;
            margin-top: .58rem;
        }
        .fip-opportunity-action-label {
            color: var(--fip-disabled);
            font-size: .61rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .05em;
            border-top: 1px solid var(--fip-border);
            padding-top: .5rem;
            margin-top: .62rem;
        }
        .fip-opportunity-action {
            color: var(--fip-text-2);
            font-size: .70rem;
            line-height: 1.4;
            margin-top: .2rem;
        }
        </style>
        """
    )
