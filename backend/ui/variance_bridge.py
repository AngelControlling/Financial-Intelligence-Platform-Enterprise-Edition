from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.variance_bridge_engine import (
    VarianceBridgeEngine,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
)


DIMENSION_LABELS = {
    "customer": "Customer",
    "trade_lane": "Trade Lane",
    "mode": "Mode",
    "product": "Product",
}


def render_variance_bridge(
    dataframe: pd.DataFrame,
    *,
    comparison_label: str,
) -> None:
    st.markdown(
        "### Variance Bridge & Drill-Down"
    )
    st.caption(
        "Identify the business dimensions explaining "
        f"Actual vs {comparison_label}."
    )

    engine = VarianceBridgeEngine()
    dimensions = engine.available_dimensions(
        dataframe
    )

    if not dimensions:
        st.info(
            "No business dimensions are available "
            "for variance drill-down."
        )
        return

    filter_1, filter_2, filter_3 = st.columns(
        [1, 1, 1]
    )

    with filter_1:
        metric = st.selectbox(
            "Metric",
            options=[
                "Revenue",
                "Gross Profit",
            ],
            key="variance_bridge_metric",
        )

    with filter_2:
        dimension = st.selectbox(
            "Explain by",
            options=dimensions,
            format_func=lambda value: (
                DIMENSION_LABELS.get(
                    value,
                    value.title(),
                )
            ),
            key="variance_bridge_dimension",
        )

    with filter_3:
        top_n = st.selectbox(
            "Top Contributors",
            options=[5, 8, 10, 15],
            index=2,
            key="variance_bridge_top_n",
        )

    result = engine.analyze(
        dataframe,
        metric=metric,
        dimension=dimension,
        top_n=int(top_n),
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        f"Actual {metric}",
        f"${result.actual_total:,.0f}",
    )
    metric_2.metric(
        f"{comparison_label} {metric}",
        f"${result.target_total:,.0f}",
    )
    metric_3.metric(
        "Net Variance",
        f"${result.variance_total:,.0f}",
        f"{result.variance_pct:+.1%}",
    )
    metric_4.metric(
        "Top 3 Concentration",
        f"{result.concentration_pct:.0%}",
    )

    chart_data = result.contributors.copy()
    dimension_label = (
        DIMENSION_LABELS.get(
            dimension,
            dimension.title(),
        )
    )

    waterfall = go.Figure(
        go.Waterfall(
            name=metric,
            orientation="v",
            measure=[
                "absolute",
                *(
                    ["relative"]
                    * len(chart_data)
                ),
                "total",
            ],
            x=[
                comparison_label,
                *chart_data[
                    dimension
                ].astype(str).tolist(),
                "Actual",
            ],
            y=[
                result.target_total,
                *chart_data[
                    "Variance"
                ].tolist(),
                result.actual_total,
            ],
            text=[
                f"${result.target_total:,.0f}",
                *[
                    f"${value:+,.0f}"
                    for value in chart_data[
                        "Variance"
                    ]
                ],
                f"${result.actual_total:,.0f}",
            ],
            textposition="outside",
            connector={
                "line": {
                    "width": 1,
                }
            },
        )
    )

    waterfall.update_layout(
        title=(
            f"{metric} Variance Bridge by "
            f"{dimension_label}"
        ),
        yaxis_title=metric,
        showlegend=False,
    )

    waterfall = apply_enterprise_chart_style(
        waterfall,
        height=520,
    )

    st.plotly_chart(
        waterfall,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.markdown(
        f"#### {dimension_label} Contribution Detail"
    )

    display = chart_data[
        [
            dimension,
            "Actual",
            "Budget",
            "Variance",
            "Variance %",
            "Contribution %",
        ]
    ].copy()

    display.rename(
        columns={
            dimension: dimension_label,
            "Budget": comparison_label,
        },
        inplace=True,
    )

    st.dataframe(
        display.style.format(
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

    negative = (
        chart_data[
            chart_data["Variance"] < 0
        ]
        .sort_values(
            "Variance",
            ascending=True,
        )
        .head(3)
    )

    positive = (
        chart_data[
            chart_data["Variance"] > 0
        ]
        .sort_values(
            "Variance",
            ascending=False,
        )
        .head(3)
    )

    focus_1, focus_2 = st.columns(2)

    with focus_1:
        st.markdown(
            "#### Priority Risks"
        )

        if negative.empty:
            st.success(
                "No negative contributors were detected."
            )
        else:
            for _, row in negative.iterrows():
                st.error(
                    f"**{row[dimension]}** · "
                    f"${row['Variance']:+,.0f} "
                    f"({row['Variance %']:+.1%})"
                )

    with focus_2:
        st.markdown(
            "#### Positive Contributors"
        )

        if positive.empty:
            st.info(
                "No positive contributors were detected."
            )
        else:
            for _, row in positive.iterrows():
                st.success(
                    f"**{row[dimension]}** · "
                    f"${row['Variance']:+,.0f} "
                    f"({row['Variance %']:+.1%})"
                )
