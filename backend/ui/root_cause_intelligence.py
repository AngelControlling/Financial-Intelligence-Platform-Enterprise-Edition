from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.root_cause_engine import (
    RootCauseEngine,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
)


DIMENSION_LABELS = {
    "mode": "Mode",
    "product": "Product",
    "customer": "Customer",
    "trade_lane": "Trade Lane",
}


def render_root_cause_intelligence(
    dataframe: pd.DataFrame,
    *,
    comparison_label: str,
) -> None:
    st.markdown(
        "### Root Cause Intelligence"
    )
    st.caption(
        "Trace the dominant path explaining the selected-period "
        f"variance versus {comparison_label}."
    )

    metric = st.selectbox(
        "Root Cause Metric",
        options=[
            "Gross Profit",
            "Revenue",
        ],
        key="root_cause_metric",
    )

    result = RootCauseEngine().analyze(
        dataframe,
        metric=metric,
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(
        4
    )

    metric_1.metric(
        f"Actual {metric}",
        f"${result.total_actual:,.0f}",
    )
    metric_2.metric(
        f"{comparison_label} {metric}",
        f"${result.total_target:,.0f}",
    )
    metric_3.metric(
        "Net Variance",
        f"${result.total_variance:+,.0f}",
    )
    metric_4.metric(
        "Explained by Top Causes",
        f"{result.explained_variance_pct:.0%}",
    )

    if result.dominant_path:
        st.markdown(
            "#### Dominant Root Cause Path"
        )

        cols = st.columns(
            len(result.dominant_path)
        )

        for column, node in zip(
            cols,
            result.dominant_path,
        ):
            with column:
                st.markdown(
                    f"**{DIMENSION_LABELS.get(node.dimension, node.dimension.title())}**"
                )
                st.metric(
                    node.value,
                    f"${node.variance:+,.0f}",
                    f"{node.variance_pct:+.1%}",
                )
                st.caption(
                    f"{node.contribution_pct:.1%} "
                    "of total variance"
                )

    if result.top_causes:
        st.markdown(
            "#### Top Root Causes"
        )

        labels = [
            (
                f"{DIMENSION_LABELS.get(node.dimension, node.dimension.title())}: "
                f"{node.value}"
            )
            for node in result.top_causes
        ]
        values = [
            node.variance
            for node in result.top_causes
        ]

        figure = go.Figure(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                text=[
                    f"${value:+,.0f}"
                    for value in values
                ],
                textposition="outside",
            )
        )
        figure.update_layout(
            title=(
                f"Top {metric} Root Causes"
            ),
            xaxis_title="Variance",
            yaxis_title="",
        )
        figure = apply_enterprise_chart_style(
            figure,
            height=460,
        )
        figure.update_yaxes(
            autorange="reversed"
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

        detail = pd.DataFrame(
            [
                {
                    "Level": node.level,
                    "Dimension": DIMENSION_LABELS.get(
                        node.dimension,
                        node.dimension.title(),
                    ),
                    "Root Cause": node.value,
                    "Actual": node.actual,
                    comparison_label: node.target,
                    "Variance": node.variance,
                    "Variance %": node.variance_pct,
                    "Contribution %": node.contribution_pct,
                }
                for node in result.top_causes
            ]
        )

        st.dataframe(
            detail.style.format(
                {
                    "Actual": "${:,.0f}",
                    comparison_label: "${:,.0f}",
                    "Variance": "${:+,.0f}",
                    "Variance %": "{:+.1%}",
                    "Contribution %": "{:.1%}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    if result.dominant_path:
        dominant = result.dominant_path[
            -1
        ]

        st.warning(
            "**Root Cause Conclusion**\n\n"
            f"The dominant {metric} variance path ends at "
            f"{DIMENSION_LABELS.get(dominant.dimension, dominant.dimension.title())} "
            f"**{dominant.value}**, contributing "
            f"${dominant.variance:+,.0f} "
            f"({dominant.variance_pct:+.1%}) versus "
            f"{comparison_label}."
        )
