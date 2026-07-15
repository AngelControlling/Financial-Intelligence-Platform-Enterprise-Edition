from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines.cfo_radar_engine import (
    CFORadarEngine,
)
from ui.plotly_theme import (
    apply_enterprise_chart_style,
)


def render_cfo_radar(
    dataframe: pd.DataFrame,
    *,
    summary: dict,
    variance: dict,
    data_quality_score: float,
) -> None:
    st.markdown("### CFO Radar")
    st.caption(
        "Executive risk surveillance for the selected reporting period."
    )

    result = CFORadarEngine().evaluate(
        dataframe,
        summary=summary,
        variance=variance,
        data_quality_score=data_quality_score,
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        "Overall Risk Score",
        f"{result.overall_score:.0f}/100",
    )
    metric_2.metric(
        "Risk Level",
        result.overall_level,
    )
    metric_3.metric(
        "Top Risk",
        result.top_risk,
    )
    metric_4.metric(
        "Critical Signals",
        result.critical_count,
    )

    categories = [
        signal.category
        for signal in result.signals
    ]
    scores = [
        signal.score
        for signal in result.signals
    ]

    radar = go.Figure(
        data=go.Scatterpolar(
            r=scores + scores[:1],
            theta=categories + categories[:1],
            fill="toself",
            name="Risk Score",
        )
    )

    radar.update_layout(
        title="Executive Risk Profile",
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
            }
        },
        showlegend=False,
    )

    radar = apply_enterprise_chart_style(
        radar,
        height=470,
    )

    st.plotly_chart(
        radar,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.markdown(
        "#### Risk Signals"
    )

    for start in range(
        0,
        len(result.signals),
        2,
    ):
        row = result.signals[
            start:start + 2
        ]
        columns = st.columns(
            len(row)
        )

        for column, signal in zip(
            columns,
            row,
        ):
            with column:
                if signal.level == "Critical":
                    container = st.error
                elif signal.level == "High":
                    container = st.warning
                elif signal.level == "Medium":
                    container = st.info
                else:
                    container = st.success

                container(
                    f"**{signal.category} · "
                    f"{signal.score:.0f}/100 · "
                    f"{signal.level}**\n\n"
                    f"{signal.headline}\n\n"
                    f"{signal.explanation}\n\n"
                    f"**Action:** "
                    f"{signal.recommended_action}"
                )
