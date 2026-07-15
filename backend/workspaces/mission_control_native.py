from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core.session_manager import SessionManager
from engines.executive_alert_engine import ExecutiveAlertEngine
from engines.executive_commentary_engine import ExecutiveCommentaryEngine
from engines.health_score_engine import HealthScoreEngine
from services.management_action_service import ManagementActionService
from services.workspace_data_service import ActiveFreightContext
from ui.ai_controller import render_ai_controller
from ui.cfo_radar import render_cfo_radar
from ui.executive_action_center import render_executive_action_center
from ui.executive_alerts import render_executive_alerts
from ui.executive_brief import render_executive_brief
from ui.financial_impact_simulator import render_financial_impact_simulator
from ui.full_pnl_intelligence import render_full_pnl_intelligence
from ui.gauges import create_target_gauge
from ui.mission_control_components import (
    ExecutiveKPI,
    render_executive_kpi_grid,
    render_health_strip,
)
from ui.opportunity_finder import render_opportunity_finder
from ui.plotly_theme import apply_enterprise_chart_style
from ui.profitability_matrix import render_profitability_matrix
from ui.root_cause_intelligence import render_root_cause_intelligence
from ui.variance_bridge import render_variance_bridge
from ui.working_capital_intelligence import (
    render_working_capital_intelligence,
)


def render_enterprise_mission_control(
    context: ActiveFreightContext,
) -> None:
    """Render Mission Control through executive navigation tabs."""

    dataframe = context.dataframe
    summary = context.summary
    variance = context.variance_summary

    alerts = ExecutiveAlertEngine().generate(
        dataframe,
        comparison_label=context.comparison_label,
        max_alerts=8,
    )

    session = SessionManager()
    session.initialize()

    st.markdown("## Mission Control")
    st.caption(
        "Executive financial intelligence organized by management decision flow."
    )

    tabs = st.tabs(
        [
            "Executive Overview",
            "Financial Performance",
            "Drivers & Root Cause",
            "Opportunities & Simulation",
            "Risk & Actions",
            "Executive Report",
        ]
    )

    with tabs[0]:
        _render_executive_overview(
            context=context,
            dataframe=dataframe,
            summary=summary,
            variance=variance,
        )

    with tabs[1]:
        _render_financial_performance(
            context=context,
            dataframe=dataframe,
        )

    with tabs[2]:
        _render_drivers_and_root_cause(
            context=context,
            dataframe=dataframe,
        )

    with tabs[3]:
        _render_opportunities_and_simulation(
            dataframe=dataframe,
        )

    with tabs[4]:
        _render_risk_and_actions(
            context=context,
            dataframe=dataframe,
            summary=summary,
            variance=variance,
            alerts=alerts,
        )

    with tabs[5]:
        _render_executive_report(
            context=context,
            dataframe=dataframe,
            summary=summary,
            variance=variance,
            alerts=alerts,
            session=session,
        )


def _render_executive_overview(
    *,
    context: ActiveFreightContext,
    dataframe: pd.DataFrame,
    summary: dict,
    variance: dict,
) -> None:
    health = HealthScoreEngine().calculate(
        summary=summary,
        variance_summary=variance,
        dataframe=dataframe,
        data_quality_score=context.data_quality_score,
    )

    revenue_actual = float(
        summary.get("actual_revenue", 0.0)
    )
    revenue_target = float(
        summary.get("estimated_revenue", 0.0)
    )
    gp_actual = float(
        summary.get("actual_gp", 0.0)
    )
    gp_target = float(
        summary.get("estimated_gp", 0.0)
    )
    margin_actual = float(
        summary.get("actual_gp_margin", 0.0)
    )
    margin_target = float(
        summary.get("estimated_gp_margin", 0.0)
    )

    revenue_delta = float(
        variance.get("revenue_variance_pct", 0.0)
    )
    gp_delta = float(
        variance.get("gp_variance_pct", 0.0)
    )
    margin_pp = float(
        variance.get("margin_variance_pp", 0.0)
    )

    render_health_strip(
        score=health.overall_score,
        revenue_delta=revenue_delta,
        gp_delta=gp_delta,
        margin_pp=margin_pp,
        operations_score=health.operational_score,
        data_quality_score=health.data_quality_score,
        comparison_label=context.comparison_label,
    )

    render_executive_kpi_grid(
        [
            ExecutiveKPI(
                title="Revenue",
                value=f"${revenue_actual:,.0f}",
                subtitle="Actual Revenue",
                delta=(
                    f"{revenue_delta:+.1%} "
                    f"vs {context.comparison_label}"
                ),
                status=(
                    "success"
                    if revenue_delta >= 0
                    else "danger"
                ),
                target=f"Target ${revenue_target:,.0f}",
                icon="R",
            ),
            ExecutiveKPI(
                title="Gross Profit",
                value=f"${gp_actual:,.0f}",
                subtitle="Actual GP",
                delta=(
                    f"{gp_delta:+.1%} "
                    f"vs {context.comparison_label}"
                ),
                status=(
                    "success"
                    if gp_delta >= 0
                    else "danger"
                ),
                target=f"Target ${gp_target:,.0f}",
                icon="GP",
            ),
            ExecutiveKPI(
                title="GP Margin",
                value=f"{margin_actual:.1%}",
                subtitle="Profitability",
                delta=f"{margin_pp * 100:+.2f} pp",
                status=(
                    "success"
                    if margin_pp >= 0
                    else "danger"
                ),
                target=f"Target {margin_target:.1%}",
                icon="%",
            ),
            ExecutiveKPI(
                title="Shipments",
                value=f"{summary.get('shipments', 0):,.0f}",
                subtitle="Operational Volume",
                status="info",
                icon="S",
            ),
            ExecutiveKPI(
                title="Tons",
                value=f"{summary.get('weight_tons', 0):,.1f}",
                subtitle="Air / Ground Volume",
                status="neutral",
                icon="T",
            ),
            ExecutiveKPI(
                title="TEUs",
                value=f"{summary.get('teus', 0):,.1f}",
                subtitle="Ocean Volume",
                status="neutral",
                icon="U",
            ),
            ExecutiveKPI(
                title="GP / Shipment",
                value=f"${summary.get('gp_per_shipment', 0):,.0f}",
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
            ExecutiveKPI(
                title="Data Quality",
                value=f"{context.data_quality_score:.0f}%",
                subtitle="Canonical Readiness",
                status=(
                    "success"
                    if context.data_quality_score >= 90
                    else "warning"
                ),
                target="Target 100%",
                icon="DQ",
            ),
        ],
        columns=4,
    )

    st.markdown("### Performance vs Baseline")
    st.caption(
        "Target achievement for Revenue, Gross Profit and Margin."
    )

    gauge_1, gauge_2, gauge_3 = st.columns(3)

    with gauge_1:
        st.markdown(
            f"#### Revenue vs {context.comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=revenue_actual,
                target=revenue_target,
                prefix="$",
            ),
            use_container_width=True,
            key="tab_revenue_gauge",
            config={"displayModeBar": False},
        )

    with gauge_2:
        st.markdown(
            f"#### GP vs {context.comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=gp_actual,
                target=gp_target,
                prefix="$",
            ),
            use_container_width=True,
            key="tab_gp_gauge",
            config={"displayModeBar": False},
        )

    with gauge_3:
        st.markdown(
            f"#### Margin vs {context.comparison_label}"
        )
        st.plotly_chart(
            create_target_gauge(
                title="",
                actual=margin_actual * 100,
                target=margin_target * 100,
                suffix="%",
            ),
            use_container_width=True,
            key="tab_margin_gauge",
            config={"displayModeBar": False},
        )

    _render_business_drivers(dataframe)
    _render_executive_detail(dataframe)


def _render_business_drivers(
    dataframe: pd.DataFrame,
) -> None:
    st.markdown("### Business Drivers")

    driver_1, driver_2 = st.columns(2)

    with driver_1:
        if {
            "customer",
            "actual_revenue",
            "actual_gp",
        }.issubset(dataframe.columns):
            customers = (
                dataframe.groupby(
                    "customer",
                    dropna=False,
                )
                .agg(
                    Revenue=("actual_revenue", "sum"),
                    GP=("actual_gp", "sum"),
                )
                .reset_index()
                .sort_values(
                    "GP",
                    ascending=False,
                )
                .head(12)
            )

            figure = px.bar(
                customers,
                x="customer",
                y="GP",
                color="Revenue",
                title="Top Customers by GP",
                text_auto=".3s",
            )
            figure = apply_enterprise_chart_style(
                figure,
                height=420,
            )
            st.plotly_chart(
                figure,
                use_container_width=True,
                key="tab_customer_driver",
            )

    with driver_2:
        if {
            "trade_lane",
            "actual_revenue",
            "actual_gp",
        }.issubset(dataframe.columns):
            lanes = (
                dataframe.groupby(
                    "trade_lane",
                    dropna=False,
                )
                .agg(
                    Revenue=("actual_revenue", "sum"),
                    GP=("actual_gp", "sum"),
                )
                .reset_index()
                .sort_values(
                    "GP",
                    ascending=False,
                )
                .head(12)
            )

            figure = px.bar(
                lanes,
                x="trade_lane",
                y="GP",
                color="Revenue",
                title="Top Trade Lanes by GP",
                text_auto=".3s",
            )
            figure = apply_enterprise_chart_style(
                figure,
                height=420,
            )
            st.plotly_chart(
                figure,
                use_container_width=True,
                key="tab_lane_driver",
            )


def _render_executive_detail(
    dataframe: pd.DataFrame,
) -> None:
    st.markdown("### Executive Detail")

    required = {
        "customer",
        "actual_revenue",
        "actual_cost",
        "actual_gp",
        "shipment",
    }

    if not required.issubset(dataframe.columns):
        st.info(
            "Customer-level executive detail is unavailable "
            "for the selected dataset."
        )
        return

    table = (
        dataframe.groupby(
            "customer",
            dropna=False,
        )
        .agg(
            Revenue=("actual_revenue", "sum"),
            Cost=("actual_cost", "sum"),
            GP=("actual_gp", "sum"),
            Shipments=("shipment", "nunique"),
        )
        .reset_index()
        .sort_values(
            "GP",
            ascending=False,
        )
        .head(15)
    )

    table["GP Margin"] = (
        table["GP"]
        / table["Revenue"].replace(
            0,
            pd.NA,
        )
    ).fillna(0.0)

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


def _render_financial_performance(
    *,
    context: ActiveFreightContext,
    dataframe: pd.DataFrame,
) -> None:
    render_full_pnl_intelligence(
        dataframe,
        comparison_label=context.comparison_label,
    )
    render_working_capital_intelligence(
        dataframe,
    )
    render_variance_bridge(
        dataframe,
        comparison_label=context.comparison_label,
    )


def _render_drivers_and_root_cause(
    *,
    context: ActiveFreightContext,
    dataframe: pd.DataFrame,
) -> None:
    render_root_cause_intelligence(
        dataframe,
        comparison_label=context.comparison_label,
    )
    render_profitability_matrix(
        dataframe,
    )


def _render_opportunities_and_simulation(
    *,
    dataframe: pd.DataFrame,
) -> None:
    render_opportunity_finder(
        dataframe,
    )
    render_financial_impact_simulator(
        dataframe,
    )


def _render_risk_and_actions(
    *,
    context: ActiveFreightContext,
    dataframe: pd.DataFrame,
    summary: dict,
    variance: dict,
    alerts,
) -> None:
    render_cfo_radar(
        dataframe,
        summary=summary,
        variance=variance,
        data_quality_score=(
            context.data_quality_score
        ),
    )

    render_ai_controller(
        dataframe,
        period_label=(
            context.selected_period_label
        ),
        comparison_label=(
            context.comparison_label
        ),
        summary=summary,
        variance=variance,
        data_quality_score=(
            context.data_quality_score
        ),
    )

    render_executive_alerts(alerts)

    render_executive_action_center(
        alerts,
        period_label=context.selected_period_label,
    )

    st.markdown("### Executive Commentary")

    commentary = (
        ExecutiveCommentaryEngine()
        .generate(
            period_label=(
                context.selected_period_label
            ),
            comparison_label=(
                context.comparison_label
            ),
            summary=summary,
            variance=variance,
        )
    )

    commentary_1, commentary_2 = st.columns(2)

    with commentary_1:
        st.success(
            "**Performance**\n\n"
            + commentary.performance
        )
        st.info(
            "**Drivers**\n\n"
            + commentary.drivers
        )

    with commentary_2:
        st.warning(
            "**Risks**\n\n"
            + commentary.risks
        )
        st.info(
            "**Recommended Actions**\n\n"
            + commentary.actions
        )


def _render_executive_report(
    *,
    context: ActiveFreightContext,
    dataframe: pd.DataFrame,
    summary: dict,
    variance: dict,
    alerts,
    session: SessionManager,
) -> None:
    st.info(
        "The report uses the same active period, Budget baseline, "
        "alerts and management actions shown in Mission Control."
    )

    render_executive_brief(
        dataframe=dataframe,
        period_label=context.selected_period_label,
        comparison_label=context.comparison_label,
        summary=summary,
        variance=variance,
        alerts=alerts,
        actions=ManagementActionService().list_all(),
        company=session.get(
            "fip_company",
            "Enterprise Freight Demo",
        ),
        currency=session.get(
            "fip_currency",
            "USD",
        ),
        data_quality_score=(
            context.data_quality_score
        ),
    )
