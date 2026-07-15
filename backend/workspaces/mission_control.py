from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from engines.health_score_engine import (
    HealthScoreEngine,
)
from ui.cards import (
    KPICard,
    render_kpi_grid,
)
from ui.layout import (
    enterprise_panel,
    section_header,
)
from ui.mission_control import (
    MissionControlSignal,
    render_mission_control_strip,
)
from ui.tables import (
    add_rank_column,
    render_enterprise_table,
)
from ui.visual_registry import (
    create_country_choropleth,
    create_profitability_treemap,
    create_target_gauge,
    create_variance_waterfall,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
    enterprise_color_sequence,
)


def render_mission_control_workspace(
    *,
    dataframe: pd.DataFrame,
    summary: dict,
    variance_summary: dict,
    comparison_label: str,
    selected_period_label: str,
    company_name: str,
    currency: str = "USD",
    data_quality_score: float = 100.0,
) -> None:
    """
    Render the first Financial Intelligence Platform V2 workspace.

    This page is independent from `app.py` and can be tested later through
    a controlled integration.
    """

    health_engine = HealthScoreEngine()

    health = health_engine.calculate(
        summary=summary,
        variance_summary=variance_summary,
        dataframe=dataframe,
        data_quality_score=data_quality_score,
    )

    render_mission_control_strip(
        title="Financial Health",
        score=f"{health.overall_score:.0f}/100",
        status=health.status,
        signals=[
            MissionControlSignal(
                label="Revenue",
                value=(
                    f"{variance_summary.get('revenue_variance_pct', 0.0):+.1%}"
                ),
                status=health.signals[
                    "Revenue"
                ],
                detail=f"vs {comparison_label}",
            ),
            MissionControlSignal(
                label="Gross Profit",
                value=(
                    f"{variance_summary.get('gp_variance_pct', 0.0):+.1%}"
                ),
                status=health.signals[
                    "Gross Profit"
                ],
                detail=f"vs {comparison_label}",
            ),
            MissionControlSignal(
                label="Margin",
                value=(
                    f"{variance_summary.get('margin_variance_pp', 0.0) * 100:+.2f} pp"
                ),
                status=health.signals[
                    "Margin"
                ],
            ),
            MissionControlSignal(
                label="Operations",
                value=(
                    f"{health.operational_score:.0f}"
                ),
                status=health.signals[
                    "Operations"
                ],
                detail="Health score",
            ),
            MissionControlSignal(
                label="Data Quality",
                value=(
                    f"{health.data_quality_score:.0f}%"
                ),
                status=health.signals[
                    "Data Quality"
                ],
            ),
        ],
    )

    revenue_target = float(
        summary.get(
            "estimated_revenue",
            0.0,
        )
    )

    gp_target = float(
        summary.get(
            "estimated_gp",
            0.0,
        )
    )

    margin_target = float(
        summary.get(
            "estimated_gp_margin",
            0.0,
        )
    )

    revenue_actual = float(
        summary.get(
            "actual_revenue",
            0.0,
        )
    )

    gp_actual = float(
        summary.get(
            "actual_gp",
            0.0,
        )
    )

    margin_actual = float(
        summary.get(
            "actual_gp_margin",
            0.0,
        )
    )

    render_kpi_grid(
        [
            KPICard(
                title="Revenue",
                value=f"${revenue_actual:,.0f}",
                delta=(
                    f"{variance_summary.get('revenue_variance_pct', 0.0):+.1%} "
                    f"vs {comparison_label}"
                ),
                status=health.signals[
                    "Revenue"
                ],
                subtitle="Actual Revenue",
                icon="R",
                progress=(
                    revenue_actual
                    / revenue_target
                    if revenue_target
                    else 1.0
                ),
                target_label=(
                    f"Target ${revenue_target:,.0f}"
                ),
            ),
            KPICard(
                title="Gross Profit",
                value=f"${gp_actual:,.0f}",
                delta=(
                    f"{variance_summary.get('gp_variance_pct', 0.0):+.1%} "
                    f"vs {comparison_label}"
                ),
                status=health.signals[
                    "Gross Profit"
                ],
                subtitle="Actual GP",
                icon="GP",
                progress=(
                    gp_actual
                    / gp_target
                    if gp_target
                    else 1.0
                ),
                target_label=(
                    f"Target ${gp_target:,.0f}"
                ),
            ),
            KPICard(
                title="GP Margin",
                value=f"{margin_actual:.1%}",
                delta=(
                    f"{variance_summary.get('margin_variance_pp', 0.0) * 100:+.2f} pp"
                ),
                status=health.signals[
                    "Margin"
                ],
                subtitle="Profitability",
                icon="%",
                progress=(
                    margin_actual
                    / margin_target
                    if margin_target
                    else 1.0
                ),
                target_label=(
                    f"Target {margin_target:.1%}"
                ),
            ),
            KPICard(
                title="Shipments",
                value=f"{summary.get('shipments', 0):,.0f}",
                subtitle="Operational Volume",
                status="info",
                icon="S",
            ),
            KPICard(
                title="Tons",
                value=f"{summary.get('weight_tons', 0.0):,.1f}",
                subtitle="Air / Ground Volume",
                status="neutral",
                icon="T",
            ),
            KPICard(
                title="TEUs",
                value=f"{summary.get('teus', 0.0):,.1f}",
                subtitle="Ocean Volume",
                status="neutral",
                icon="U",
            ),
            KPICard(
                title="GP / Shipment",
                value=f"${summary.get('gp_per_shipment', 0.0):,.0f}",
                subtitle="Unit Economics",
                status=(
                    "success"
                    if summary.get(
                        "gp_per_shipment",
                        0.0,
                    ) > 0
                    else "danger"
                ),
                icon="P",
            ),
            KPICard(
                title="Data Quality",
                value=f"{health.data_quality_score:.0f}%",
                subtitle="Canonical Model Readiness",
                status=health.signals[
                    "Data Quality"
                ],
                icon="DQ",
                progress=(
                    health.data_quality_score
                    / 100.0
                ),
                target_label="Target 100%",
            ),
        ],
        columns=4,
    )

    section_header(
        "Performance vs Baseline",
        (
            "Target achievement for revenue, gross profit "
            "and gross margin"
        ),
    )

    gauge_1, gauge_2, gauge_3 = st.columns(3)

    with gauge_1:
        st.markdown(
            f"#### Revenue vs {comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=revenue_actual,
                target=revenue_target,
                prefix="$",
            ),
            use_container_width=True,
            key="mission_control_revenue_gauge",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    with gauge_2:
        st.markdown(
            f"#### GP vs {comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=gp_actual,
                target=gp_target,
                prefix="$",
            ),
            use_container_width=True,
            key="mission_control_gp_gauge",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    with gauge_3:
        st.markdown(
            f"#### Margin vs {comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=margin_actual * 100,
                target=margin_target * 100,
                suffix="%",
            ),
            use_container_width=True,
            key="mission_control_margin_gauge",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    section_header(
        "Business Drivers",
        "Customer concentration, trade lanes and profitability",
    )

    driver_col_1, driver_col_2 = st.columns(2)

    with driver_col_1:
        if {
            "customer",
            "actual_revenue",
            "actual_gp_margin",
        }.issubset(dataframe.columns):
            customer_summary = (
                dataframe.groupby(
                    "customer",
                    dropna=False,
                )
                .agg(
                    actual_revenue=(
                        "actual_revenue",
                        "sum",
                    ),
                    actual_cost=(
                        "actual_cost",
                        "sum",
                    ),
                    actual_gp=(
                        "actual_gp",
                        "sum",
                    ),
                )
                .reset_index()
            )

            customer_summary[
                "actual_gp_margin"
            ] = (
                customer_summary[
                    "actual_gp"
                ]
                / customer_summary[
                    "actual_revenue"
                ].replace(0, pd.NA)
            ).fillna(0.0)

            st.plotly_chart(
                create_profitability_treemap(
                    customer_summary,
                    dimension="customer",
                    value_column=(
                        "actual_revenue"
                    ),
                    color_column=(
                        "actual_gp_margin"
                    ),
                    title=(
                        "Customer Revenue Concentration"
                    ),
                ),
                use_container_width=True,
            )

    with driver_col_2:
        if {
            "trade_lane",
            "actual_revenue",
            "actual_gp",
        }.issubset(dataframe.columns):
            lane_summary = (
                dataframe.groupby(
                    "trade_lane",
                    dropna=False,
                )
                .agg(
                    Revenue=(
                        "actual_revenue",
                        "sum",
                    ),
                    GP=(
                        "actual_gp",
                        "sum",
                    ),
                    Shipments=(
                        "shipment",
                        "nunique",
                    ),
                )
                .reset_index()
                .sort_values(
                    "GP",
                    ascending=False,
                )
                .head(12)
            )

            lane_figure = px.bar(
                lane_summary,
                x="trade_lane",
                y="GP",
                color="Revenue",
                text_auto=".3s",
                title="Top Trade Lanes by GP",
                color_continuous_scale=(
                    enterprise_color_sequence()
                ),
                hover_data=[
                    "Revenue",
                    "Shipments",
                ],
            )

            lane_figure = apply_enterprise_chart_style(
                lane_figure,
                height=450,
            )

            st.plotly_chart(
                lane_figure,
                use_container_width=True,
            )

    section_header(
        "Geographic Intelligence",
        "Revenue concentration by origin and destination country",
    )

    map_col_1, map_col_2 = st.columns(2)

    with map_col_1:
        if {
            "origin",
            "actual_revenue",
        }.issubset(dataframe.columns):
            try:
                st.plotly_chart(
                    create_country_choropleth(
                        dataframe,
                        country_column="origin",
                        value_column=(
                            "actual_revenue"
                        ),
                        title=(
                            "Revenue by Origin"
                        ),
                        hover_columns=[
                            "actual_gp",
                        ],
                    ),
                    use_container_width=True,
                )
            except Exception:
                st.info(
                    "Origin map requires country-level values "
                    "recognized by Plotly."
                )

    with map_col_2:
        if {
            "destination",
            "actual_revenue",
        }.issubset(dataframe.columns):
            try:
                st.plotly_chart(
                    create_country_choropleth(
                        dataframe,
                        country_column=(
                            "destination"
                        ),
                        value_column=(
                            "actual_revenue"
                        ),
                        title=(
                            "Revenue by Destination"
                        ),
                        hover_columns=[
                            "actual_gp",
                        ],
                    ),
                    use_container_width=True,
                )
            except Exception:
                st.info(
                    "Destination map requires country-level values "
                    "recognized by Plotly."
                )

    section_header(
        "Variance Bridge",
        f"Gross Profit movement from {comparison_label} to Actual",
    )

    revenue_impact = float(
        variance_summary.get(
            "revenue_variance",
            0.0,
        )
    )

    cost_impact = float(
        -variance_summary.get(
            "cost_variance",
            0.0,
        )
    )

    st.plotly_chart(
        create_variance_waterfall(
            labels=[
                f"{comparison_label} GP",
                "Revenue Impact",
                "Cost Impact",
                "Actual GP",
            ],
            values=[
                gp_target,
                revenue_impact,
                cost_impact,
                gp_actual,
            ],
            title=(
                f"{comparison_label} to Actual GP Bridge"
            ),
        ),
        use_container_width=True,
    )

    section_header(
        "Executive Driver Table",
        "Highest gross-profit customers in the selected context",
    )

    if {
        "customer",
        "actual_revenue",
        "actual_cost",
        "actual_gp",
    }.issubset(dataframe.columns):
        executive_customer_table = (
            dataframe.groupby(
                "customer",
                dropna=False,
            )
            .agg(
                Revenue=(
                    "actual_revenue",
                    "sum",
                ),
                Cost=(
                    "actual_cost",
                    "sum",
                ),
                GP=(
                    "actual_gp",
                    "sum",
                ),
                Shipments=(
                    "shipment",
                    "nunique",
                ),
            )
            .reset_index()
            .sort_values(
                "GP",
                ascending=False,
            )
            .head(15)
        )

        executive_customer_table[
            "GP Margin"
        ] = (
            executive_customer_table[
                "GP"
            ]
            / executive_customer_table[
                "Revenue"
            ].replace(0, pd.NA)
        ).fillna(0.0)

        executive_customer_table = (
            add_rank_column(
                executive_customer_table
            )
        )

        render_enterprise_table(
            executive_customer_table,
            title="Top Customers",
            subtitle="Revenue, GP, margin and shipment contribution",
            hide_index=True,
        )
