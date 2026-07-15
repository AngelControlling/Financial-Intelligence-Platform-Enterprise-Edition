from __future__ import annotations

import pandas as pd
import streamlit as st

from engines.ai_controller_engine import (
    AIControllerEngine,
)


def render_ai_controller(
    dataframe: pd.DataFrame,
    *,
    period_label: str,
    comparison_label: str,
    summary: dict,
    variance: dict,
    data_quality_score: float,
) -> None:
    st.markdown("### AI Controller")
    st.caption(
        "Controller-style interpretation of what happened, "
        "why it happened and what management should do next."
    )

    narrative = (
        AIControllerEngine()
        .generate(
            dataframe,
            period_label=period_label,
            comparison_label=(
                comparison_label
            ),
            summary=summary,
            variance=variance,
            data_quality_score=(
                data_quality_score
            ),
        )
    )

    metric_1, metric_2 = st.columns(2)

    metric_1.metric(
        "Management Priority",
        narrative.management_priority,
    )
    metric_2.metric(
        "Analysis Confidence",
        f"{narrative.confidence_score:.0%}",
    )

    st.info(
        "**Executive Summary**\n\n"
        + narrative.executive_summary
    )

    col_1, col_2 = st.columns(2)

    with col_1:
        st.success(
            "**What Happened**\n\n"
            + narrative.what_happened
        )
        st.warning(
            "**Business Risk**\n\n"
            + narrative.business_risk
        )

    with col_2:
        st.info(
            "**Why It Happened**\n\n"
            + narrative.why_it_happened
        )
        st.warning(
            "**If No Action Is Taken**\n\n"
            + narrative.no_action_outlook
        )

    st.markdown(
        "#### Recommended Management Actions"
    )

    for index, action in enumerate(
        narrative.recommended_actions,
        start=1,
    ):
        st.write(
            f"**{index}.** {action}"
        )
