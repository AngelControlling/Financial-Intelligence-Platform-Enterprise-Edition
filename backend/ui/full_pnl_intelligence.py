from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.full_pnl_engine import (
    FullPnLIntelligenceEngine,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
)


def render_full_pnl_intelligence(
    dataframe: pd.DataFrame,
    *,
    comparison_label: str,
) -> None:
    st.markdown(
        "### Full P&L Intelligence"
    )
    st.caption(
        "Extend management analysis from Revenue and Gross Profit "
        "to OPEX, Personnel Expense and Operating Profit."
    )

    result = (
        FullPnLIntelligenceEngine()
        .analyze(dataframe)
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        "GP Margin",
        _format_pct(
            result.actual_gp_margin
        ),
        _margin_delta(
            result.actual_gp_margin,
            result.budget_gp_margin,
        ),
    )
    metric_2.metric(
        "Operating Margin",
        _format_pct(
            result.actual_operating_margin
        ),
        _margin_delta(
            result.actual_operating_margin,
            result.budget_operating_margin,
        ),
    )
    metric_3.metric(
        "Headcount",
        _format_number(
            result.actual_headcount
        ),
        _number_delta(
            result.actual_headcount,
            result.budget_headcount,
        ),
    )
    metric_4.metric(
        "Cost per Employee",
        _format_money(
            result.actual_cost_per_employee
        ),
        _money_delta(
            result.actual_cost_per_employee,
            result.budget_cost_per_employee,
        ),
    )

    available_lines = [
        line
        for line in result.lines
        if (
            line.actual is not None
            or line.budget is not None
        )
    ]

    if not available_lines:
        st.warning(
            "The active dataset does not contain Full P&L fields yet. "
            "Revenue and Gross Profit analysis remains available."
        )
        return

    actual_values = [
        line.actual or 0.0
        for line in available_lines
    ]
    budget_values = [
        line.budget or 0.0
        for line in available_lines
    ]
    labels = [
        line.name
        for line in available_lines
    ]

    figure = go.Figure()
    figure.add_bar(
        x=labels,
        y=actual_values,
        name="Actual",
    )
    figure.add_bar(
        x=labels,
        y=budget_values,
        name=comparison_label,
    )
    figure.update_layout(
        title=(
            "Actual vs "
            f"{comparison_label} — Full P&L"
        ),
        barmode="group",
        yaxis_title="Amount",
    )
    figure = apply_enterprise_chart_style(
        figure,
        height=450,
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    table = pd.DataFrame(
        [
            {
                "P&L Line": line.name,
                "Actual": line.actual,
                comparison_label: line.budget,
                "Variance": line.variance,
                "Variance %": line.variance_pct,
                "Status": (
                    "Favorable"
                    if line.favorable is True
                    else "Unfavorable"
                    if line.favorable is False
                    else "Not Available"
                ),
            }
            for line in result.lines
        ]
    )

    st.dataframe(
        table.style.format(
            {
                "Actual": _table_money,
                comparison_label: _table_money,
                "Variance": _table_signed_money,
                "Variance %": _table_pct,
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    missing_lines = [
        line.name
        for line in result.lines
        if (
            line.actual is None
            and line.budget is None
        )
    ]

    if missing_lines:
        st.info(
            "**Data coverage notice:** "
            + ", ".join(missing_lines)
            + " are not present in the active dataset. "
            "No values were estimated or fabricated."
        )

    if result.data_coverage_pct < 70:
        st.warning(
            f"Full P&L data coverage is "
            f"{result.data_coverage_pct:.0f}%. "
            "For the presentation, the module will show available lines "
            "and clearly flag missing inputs."
        )


def _format_pct(
    value: float | None,
) -> str:
    return (
        f"{value:.1%}"
        if value is not None
        else "N/A"
    )


def _format_number(
    value: float | None,
) -> str:
    return (
        f"{value:,.0f}"
        if value is not None
        else "N/A"
    )


def _format_money(
    value: float | None,
) -> str:
    return (
        f"${value:,.0f}"
        if value is not None
        else "N/A"
    )


def _margin_delta(
    actual: float | None,
    budget: float | None,
) -> str | None:
    if actual is None or budget is None:
        return None
    return f"{(actual - budget) * 100:+.2f} pp"


def _number_delta(
    actual: float | None,
    budget: float | None,
) -> str | None:
    if actual is None or budget is None:
        return None
    return f"{actual - budget:+,.0f}"


def _money_delta(
    actual: float | None,
    budget: float | None,
) -> str | None:
    if actual is None or budget is None:
        return None
    return f"${actual - budget:+,.0f}"


def _table_money(
    value,
) -> str:
    return (
        "N/A"
        if pd.isna(value)
        else f"${value:,.0f}"
    )


def _table_signed_money(
    value,
) -> str:
    return (
        "N/A"
        if pd.isna(value)
        else f"${value:+,.0f}"
    )


def _table_pct(
    value,
) -> str:
    return (
        "N/A"
        if pd.isna(value)
        else f"{value:+.1%}"
    )
