from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engines.profitability_matrix_engine import (
    ProfitabilityMatrixEngine,
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


def render_profitability_matrix(
    dataframe: pd.DataFrame,
) -> None:
    st.markdown(
        "### Profitability & Concentration Intelligence"
    )
    st.caption(
        "Identify high-value business, margin leakage and "
        "commercial concentration for the selected period."
    )

    engine = ProfitabilityMatrixEngine()
    dimensions = engine.available_dimensions(
        dataframe
    )

    if not dimensions:
        st.info(
            "No supported profitability dimensions are available."
        )
        return

    selector_1, selector_2 = st.columns(
        [1, 3]
    )

    with selector_1:
        dimension = st.selectbox(
            "Analyze by",
            options=dimensions,
            format_func=lambda value: (
                DIMENSION_LABELS.get(
                    value,
                    value.title(),
                )
            ),
            key="profitability_matrix_dimension",
        )

    result = engine.analyze(
        dataframe,
        dimension=dimension,
    )
    label = DIMENSION_LABELS.get(
        dimension,
        dimension.title(),
    )

    with selector_2:
        st.info(
            "Quadrants use median Revenue and the selected-period "
            "overall GP Margin as decision thresholds."
        )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        "Top 5 Revenue Concentration",
        f"{result.top_5_revenue_concentration:.1%}",
    )
    metric_2.metric(
        "Top 5 GP Concentration",
        f"{result.top_5_gp_concentration:.1%}",
    )
    metric_3.metric(
        "Loss-Making Items",
        result.loss_making_count,
    )
    metric_4.metric(
        "Protect & Grow",
        result.high_value_count,
    )

    chart_1, chart_2 = st.columns(
        [1.3, 1]
    )

    with chart_1:
        bubble = px.scatter(
            result.dataframe,
            x="Revenue",
            y="GP Margin",
            size=(
                result.dataframe["GP"].abs()
                .clip(lower=1)
            ),
            color="Quadrant",
            hover_name=dimension,
            hover_data={
                "Revenue": ":,.0f",
                "GP": ":,.0f",
                "GP Margin": ":.1%",
                "Shipments": ":,.0f",
                "GP / Shipment": ":,.0f",
            },
            title=(
                f"{label} Profitability Matrix"
            ),
        )

        bubble.add_hline(
            y=result.margin_threshold,
            line_dash="dash",
            annotation_text=(
                f"Overall Margin "
                f"{result.margin_threshold:.1%}"
            ),
        )
        bubble.add_vline(
            x=result.revenue_threshold,
            line_dash="dash",
            annotation_text="Median Revenue",
        )

        bubble = apply_enterprise_chart_style(
            bubble,
            height=500,
        )
        bubble.update_yaxes(
            tickformat=".0%",
        )

        st.plotly_chart(
            bubble,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with chart_2:
        pareto_data = (
            result.dataframe
            .head(15)
            .copy()
        )

        pareto = go.Figure()
        pareto.add_bar(
            x=pareto_data[dimension],
            y=pareto_data["Revenue"],
            name="Revenue",
        )
        pareto.add_scatter(
            x=pareto_data[dimension],
            y=(
                pareto_data[
                    "Cumulative Revenue Share"
                ]
                * 100
            ),
            name="Cumulative Share",
            mode="lines+markers",
            yaxis="y2",
        )
        pareto.update_layout(
            title=(
                f"{label} Revenue Pareto"
            ),
            yaxis={
                "title": "Revenue",
            },
            yaxis2={
                "title": "Cumulative %",
                "overlaying": "y",
                "side": "right",
                "range": [0, 105],
            },
            legend={
                "orientation": "h",
            },
        )

        pareto = apply_enterprise_chart_style(
            pareto,
            height=500,
        )

        st.plotly_chart(
            pareto,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    st.markdown(
        f"#### {label} Portfolio Actions"
    )

    action_tabs = st.tabs(
        [
            "Protect & Grow",
            "Fix Margin",
            "Scale Selectively",
            "Review / Exit",
        ]
    )

    quadrants = [
        "Protect & Grow",
        "Fix Margin",
        "Scale Selectively",
        "Review / Exit",
    ]

    for tab, quadrant in zip(
        action_tabs,
        quadrants,
    ):
        with tab:
            subset = (
                result.dataframe[
                    result.dataframe[
                        "Quadrant"
                    ]
                    == quadrant
                ]
                .sort_values(
                    "Revenue",
                    ascending=False,
                )
                .head(20)
                .copy()
            )

            if subset.empty:
                st.info(
                    "No items in this quadrant."
                )
                continue

            display = subset[
                [
                    dimension,
                    "Revenue",
                    "GP",
                    "GP Margin",
                    "Shipments",
                    "GP / Shipment",
                    "Revenue Share",
                ]
            ].copy()

            display.rename(
                columns={
                    dimension: label,
                },
                inplace=True,
            )

            st.dataframe(
                display.style.format(
                    {
                        "Revenue": "${:,.0f}",
                        "GP": "${:,.0f}",
                        "GP Margin": "{:.1%}",
                        "Shipments": "{:,.0f}",
                        "GP / Shipment": "${:,.0f}",
                        "Revenue Share": "{:.1%}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(
        "#### Controller Focus"
    )

    focus_1, focus_2, focus_3 = st.columns(3)

    fix_margin = (
        result.dataframe[
            result.dataframe[
                "Quadrant"
            ]
            == "Fix Margin"
        ]
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(3)
    )

    losses = (
        result.dataframe[
            result.dataframe["GP"] < 0
        ]
        .sort_values(
            "GP",
            ascending=True,
        )
        .head(3)
    )

    concentration = (
        result.dataframe
        .sort_values(
            "Revenue",
            ascending=False,
        )
        .head(3)
    )

    with focus_1:
        st.markdown(
            "**Margin Leakage**"
        )
        if fix_margin.empty:
            st.success(
                "No high-revenue margin leakage detected."
            )
        else:
            for _, row in fix_margin.iterrows():
                st.warning(
                    f"{row[dimension]} · "
                    f"Revenue ${row['Revenue']:,.0f} · "
                    f"Margin {row['GP Margin']:.1%}"
                )

    with focus_2:
        st.markdown(
            "**Loss-Making Business**"
        )
        if losses.empty:
            st.success(
                "No loss-making items detected."
            )
        else:
            for _, row in losses.iterrows():
                st.error(
                    f"{row[dimension]} · "
                    f"GP ${row['GP']:,.0f}"
                )

    with focus_3:
        st.markdown(
            "**Concentration Watch**"
        )
        for _, row in concentration.iterrows():
            st.info(
                f"{row[dimension]} · "
                f"{row['Revenue Share']:.1%} "
                f"of Revenue"
            )
