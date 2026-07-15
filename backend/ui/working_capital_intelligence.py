from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.working_capital_intelligence_engine import (
    WorkingCapitalIntelligenceEngine,
)
from services.working_capital_intelligence_service import (
    WorkingCapitalIntelligenceService,
)
from ui.plotly_theme import apply_enterprise_chart_style


def render_working_capital_intelligence(
    actuals_dataframe: pd.DataFrame,
) -> None:
    st.markdown("### Working Capital Intelligence")
    st.caption(
        "Active AR/AP aging, cash conversion, liquidity exposure "
        "and collection priorities."
    )

    service = WorkingCapitalIntelligenceService()
    working_capital = service.load_active()

    if working_capital is None:
        st.info(
            "No active Working Capital version is available. "
            "Activate one in Data Center to enable this section."
        )
        return

    full_actuals = service.load_active_actuals()

    result = WorkingCapitalIntelligenceEngine().analyze(
        working_capital,
        external_actuals=full_actuals,
    )

    row_1 = st.columns(4)
    row_1[0].metric(
        "Open AR",
        f"${result.total_ar:,.0f}",
        f"{result.overdue_ar_pct:.1%} overdue",
        delta_color="inverse",
    )
    row_1[1].metric(
        "Open AP",
        f"${result.total_ap:,.0f}",
        f"{result.overdue_ap_pct:.1%} overdue",
        delta_color="inverse",
    )
    row_1[2].metric(
        "Net Working Capital",
        f"${result.net_working_capital:+,.0f}",
    )
    row_1[3].metric(
        "AR 90+",
        f"${result.ar_90_plus:,.0f}",
        f"{result.ar_90_plus / result.total_ar:.1%} of AR"
        if result.total_ar else None,
        delta_color="inverse",
    )

    row_2 = st.columns(4)
    row_2[0].metric(
        "Estimated DSO",
        _format_days(result.dso),
        help=result.dso_method,
    )
    row_2[1].metric(
        "Estimated DPO",
        _format_days(result.dpo),
        help=result.dpo_method,
    )
    row_2[2].metric(
        "Collection Risk",
        f"{result.collection_risk_score:.0f}/100",
        result.collection_risk_level,
        delta_color="inverse",
    )
    row_2[3].metric(
        "Payment Pressure",
        f"{result.payment_pressure_score:.0f}/100",
        result.payment_pressure_level,
        delta_color="inverse",
    )

    method_1, method_2 = st.columns(2)
    method_1.caption(f"DSO methodology: {result.dso_method}")
    method_2.caption(f"DPO methodology: {result.dpo_method}")

    chart_1, chart_2 = st.columns(2)

    with chart_1:
        pivot = (
            result.bucket_summary.pivot(
                index="aging_bucket",
                columns="document_type",
                values="open_amount",
            )
            .fillna(0.0)
            .reindex(
                ["Current", "0-30", "31-45", "46-60", "61-90", "90+"],
                fill_value=0.0,
            )
        )

        figure = go.Figure()
        for document_type in ["AR", "AP"]:
            if document_type in pivot.columns:
                figure.add_bar(
                    x=list(pivot.index),
                    y=pivot[document_type].tolist(),
                    name=document_type,
                )

        figure.update_layout(
            title="AR / AP Aging Profile",
            barmode="group",
            xaxis_title="Aging Bucket",
            yaxis_title="Open Amount",
        )
        figure = apply_enterprise_chart_style(figure, height=430)
        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with chart_2:
        gauge = go.Figure()
        for value, title, domain in [
            (
                result.collection_risk_score,
                f"Collection Risk<br>{result.collection_risk_level}",
                [0, 0.48],
            ),
            (
                result.payment_pressure_score,
                f"Payment Pressure<br>{result.payment_pressure_level}",
                [0.52, 1],
            ),
        ]:
            gauge.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    title={"text": title},
                    domain={"x": domain, "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "steps": [
                            {"range": [0, 35], "color": "rgba(34,197,94,.18)"},
                            {"range": [35, 60], "color": "rgba(245,158,11,.18)"},
                            {"range": [60, 80], "color": "rgba(249,115,22,.20)"},
                            {"range": [80, 100], "color": "rgba(239,68,68,.20)"},
                        ],
                    },
                )
            )

        gauge.update_layout(title="Liquidity Risk Signals")
        gauge = apply_enterprise_chart_style(gauge, height=430)
        st.plotly_chart(
            gauge,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    concentration_1, concentration_2 = st.columns(2)
    concentration_1.metric(
        "Top 5 AR Concentration",
        f"{result.top_5_ar_concentration:.1%}",
    )
    concentration_2.metric(
        "Top 5 AP Concentration",
        f"{result.top_5_ap_concentration:.1%}",
    )

    st.markdown("#### Collection and Payment Priorities")
    ar_tab, ap_tab = st.tabs(
        ["Top Overdue Customers", "Top Overdue Suppliers"]
    )

    with ar_tab:
        _render_priority_table(
            result.top_overdue_ar,
            "No overdue AR documents were detected.",
        )
    with ap_tab:
        _render_priority_table(
            result.top_overdue_ap,
            "No overdue AP documents were detected.",
        )

    if result.collection_risk_level == "Critical":
        st.error(
            "**Collection escalation required.** "
            f"Overdue AR is ${result.overdue_ar:,.0f}, including "
            f"${result.ar_90_plus:,.0f} aged 90+ days."
        )
    elif result.collection_risk_level == "High":
        st.warning(
            "Collections require immediate management attention. "
            "Prioritize the largest overdue customers and 90+ balances."
        )
    elif result.collection_risk_level == "Medium":
        st.info(
            "Collections require structured follow-up, with focus on "
            "aging migration and customer concentration."
        )
    else:
        st.success("Collection exposure is currently controlled.")

    st.caption(result.data_quality_note)


def _render_priority_table(
    dataframe: pd.DataFrame,
    empty_text: str,
) -> None:
    if dataframe.empty:
        st.success(empty_text)
        return

    display = dataframe.rename(
        columns={
            "counterparty": "Counterparty",
            "open_amount": "Open Amount",
            "days_overdue": "Max Days Overdue",
        }
    )
    st.dataframe(
        display.style.format(
            {
                "Open Amount": "${:,.0f}",
                "Max Days Overdue": "{:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _format_days(value: float | None) -> str:
    return f"{value:.1f} days" if value is not None else "N/A"
