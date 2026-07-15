from __future__ import annotations

import streamlit as st

from engines.period_engine import PeriodEngine
from models.period import PeriodSelection


MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def render_period_selector(
    dataframe,
) -> PeriodSelection:
    engine = PeriodEngine()
    years = engine.available_years(dataframe)

    if not years:
        years = [2026]

    default_year = max(years)
    default_month = engine.latest_month(
        dataframe,
        default_year,
    )

    st.markdown("### Analysis Context")

    col_1, col_2, col_3, col_4 = st.columns(
        [1, 1, 1, 1]
    )

    with col_1:
        year = st.selectbox(
            "Fiscal Year",
            options=years,
            index=len(years) - 1,
            key="mission_control_year",
        )

    with col_2:
        view = st.selectbox(
            "View",
            options=list(PeriodEngine.VIEWS),
            index=3,
            key="mission_control_view",
        )

    month = default_month
    quarter = None
    semester = None

    with col_3:
        if view == "Month":
            month = st.selectbox(
                "Month",
                options=list(MONTHS),
                format_func=lambda value: MONTHS[value],
                index=max(default_month - 1, 0),
                key="mission_control_month",
            )
        elif view == "Quarter":
            quarter = st.selectbox(
                "Quarter",
                options=[1, 2, 3, 4],
                key="mission_control_quarter",
            )
        elif view == "Semester":
            semester = st.selectbox(
                "Semester",
                options=[1, 2],
                key="mission_control_semester",
            )
        elif view == "YTD":
            month = st.selectbox(
                "Through",
                options=list(MONTHS),
                format_func=lambda value: MONTHS[value],
                index=max(default_month - 1, 0),
                key="mission_control_ytd_month",
            )
        else:
            st.text_input(
                "Period",
                value="January–December",
                disabled=True,
                key="mission_control_full_year",
            )

    with col_4:
        st.text_input(
            "Baseline",
            value="Active Budget",
            disabled=True,
            key="mission_control_baseline",
        )

    return PeriodSelection(
        year=int(year),
        view=view,
        month=month,
        quarter=quarter,
        semester=semester,
    )
