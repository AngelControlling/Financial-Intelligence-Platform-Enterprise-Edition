from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.financial_impact_simulator import (
    FinancialImpactSimulator,
)
from models.impact_scenario import (
    ImpactScenario,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
)


def render_financial_impact_simulator(
    dataframe: pd.DataFrame,
) -> None:
    st.markdown(
        "### Financial Impact Simulator"
    )
    st.caption(
        "Estimate the effect of commercial and operational decisions "
        "on Revenue, Gross Profit and Margin."
    )

    with st.expander(
        "Scenario Assumptions",
        expanded=True,
    ):
        col_1, col_2, col_3, col_4 = st.columns(4)

        with col_1:
            revenue_growth = st.slider(
                "Revenue Growth",
                min_value=-10.0,
                max_value=20.0,
                value=0.0,
                step=0.5,
                format="%.1f%%",
                key="impact_revenue_growth",
            ) / 100

        with col_2:
            margin_improvement = st.slider(
                "Margin Improvement",
                min_value=-5.0,
                max_value=5.0,
                value=0.0,
                step=0.25,
                format="%.2f pp",
                key="impact_margin_improvement",
            ) / 100

        with col_3:
            cost_reduction = st.slider(
                "Direct Cost Reduction",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.5,
                format="%.1f%%",
                key="impact_cost_reduction",
            ) / 100

        with col_4:
            volume_growth = st.slider(
                "Volume Growth",
                min_value=-10.0,
                max_value=20.0,
                value=0.0,
                step=0.5,
                format="%.1f%%",
                key="impact_volume_growth",
            ) / 100

    scenario = ImpactScenario(
        scenario_name="Management Scenario",
        revenue_growth_pct=revenue_growth,
        margin_improvement_pp=margin_improvement,
        cost_reduction_pct=cost_reduction,
        volume_growth_pct=volume_growth,
    )

    simulator = FinancialImpactSimulator()
    result = simulator.simulate(
        dataframe,
        scenario,
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        "Projected Revenue",
        f"${result.projected_revenue:,.0f}",
        f"${result.revenue_impact:+,.0f}",
    )
    metric_2.metric(
        "Projected Gross Profit",
        f"${result.projected_gp:,.0f}",
        f"${result.gp_impact:+,.0f}",
    )
    metric_3.metric(
        "Projected Margin",
        f"{result.projected_margin:.1%}",
        f"{result.margin_impact_pp * 100:+.2f} pp",
    )
    metric_4.metric(
        "Projected Direct Cost",
        f"${result.projected_cost:,.0f}",
        f"${result.cost_impact:+,.0f}",
    )

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        bridge = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=[
                    "absolute",
                    "relative",
                    "total",
                ],
                x=[
                    "Base GP",
                    "Scenario Impact",
                    "Projected GP",
                ],
                y=[
                    result.base_gp,
                    result.gp_impact,
                    result.projected_gp,
                ],
                text=[
                    f"${result.base_gp:,.0f}",
                    f"${result.gp_impact:+,.0f}",
                    f"${result.projected_gp:,.0f}",
                ],
                textposition="outside",
            )
        )
        bridge.update_layout(
            title="Gross Profit Scenario Bridge",
            showlegend=False,
        )
        bridge = apply_enterprise_chart_style(
            bridge,
            height=420,
        )
        st.plotly_chart(
            bridge,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with chart_2:
        comparison = go.Figure()
        comparison.add_bar(
            x=[
                "Revenue",
                "Gross Profit",
                "Direct Cost",
            ],
            y=[
                result.base_revenue,
                result.base_gp,
                result.base_cost,
            ],
            name="Current",
        )
        comparison.add_bar(
            x=[
                "Revenue",
                "Gross Profit",
                "Direct Cost",
            ],
            y=[
                result.projected_revenue,
                result.projected_gp,
                result.projected_cost,
            ],
            name="Projected",
        )
        comparison.update_layout(
            title="Current vs Projected",
            barmode="group",
        )
        comparison = apply_enterprise_chart_style(
            comparison,
            height=420,
        )
        st.plotly_chart(
            comparison,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    st.markdown(
        "#### Management Interpretation"
    )

    if result.gp_impact > 0:
        st.success(
            f"The selected scenario generates an estimated "
            f"Gross Profit improvement of ${result.gp_impact:,.0f} "
            f"and increases margin by "
            f"{result.margin_impact_pp * 100:+.2f} pp."
        )
    elif result.gp_impact < 0:
        st.warning(
            f"The selected scenario reduces Gross Profit by "
            f"${abs(result.gp_impact):,.0f}. Review the assumptions "
            f"before incorporating them into the forecast."
        )
    else:
        st.info(
            "The current assumptions do not materially change "
            "Gross Profit."
        )

    st.markdown(
        "#### Revenue / Margin Sensitivity"
    )

    sensitivity = simulator.sensitivity_table(
        dataframe,
        revenue_growth_options=[
            -0.05,
            0.00,
            0.05,
            0.10,
        ],
        margin_improvement_options=[
            0.00,
            0.01,
            0.02,
            0.03,
        ],
    )

    pivot = sensitivity.pivot(
        index="Margin Improvement pp",
        columns="Revenue Growth",
        values="GP Impact",
    )

    pivot.index = [
        f"{value * 100:+.0f} pp"
        for value in pivot.index
    ]
    pivot.columns = [
        f"{value:+.0%}"
        for value in pivot.columns
    ]

    heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            text=[
                [
                    f"${value:+,.0f}"
                    for value in row
                ]
                for row in pivot.values
            ],
            texttemplate="%{text}",
            hovertemplate=(
                "Revenue Growth: %{x}<br>"
                "Margin Improvement: %{y}<br>"
                "GP Impact: %{text}"
                "<extra></extra>"
            ),
            colorbar={
                "title": "GP Impact",
            },
        )
    )

    heatmap.update_layout(
        title="Executive Sensitivity Heatmap",
        xaxis_title="Revenue Growth",
        yaxis_title="Margin Improvement",
    )

    heatmap = apply_enterprise_chart_style(
        heatmap,
        height=430,
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    with st.expander(
        "Sensitivity Detail Table"
    ):
        st.dataframe(
            pivot.style.format(
                "${:+,.0f}"
            ),
            use_container_width=True,
        )
