from __future__ import annotations

from datetime import datetime

import streamlit as st

from core.session_manager import SessionManager
from services.workspace_data_service import WorkspaceDataService
from ui.workspace_components import StatusCard, render_status_grid


def _navigate(workspace_key: str) -> None:
    st.session_state["fip_current_workspace"] = workspace_key
    st.rerun()


def _version_label(dataset) -> str:
    if dataset is None:
        return "Not loaded"

    return getattr(
        dataset,
        "version_label",
        getattr(
            dataset,
            "version_id",
            "Active",
        ),
    )


def render_home_workspace() -> None:
    """Enterprise Home driven only by active Data Lake versions."""

    session = SessionManager()
    session.initialize()

    service = WorkspaceDataService(session)
    datasets = service.list_datasets()

    actuals = datasets.get("actuals")
    budget = datasets.get("budget")
    forecast = datasets.get("forecast")
    prior_year = datasets.get("prior_year")
    working_capital = datasets.get("working_capital")
    fx_rates = datasets.get("fx_rates")

    st.markdown("### Enterprise Overview")
    st.caption(
        "Active data sources, analytical readiness and platform health."
    )

    render_status_grid(
        [
            StatusCard(
                title="Actuals",
                status="Active" if actuals else "Missing",
                metric=(
                    f"{actuals.rows:,} rows"
                    if actuals
                    else "Not loaded"
                ),
                description=(
                    actuals.period_label
                    if actuals
                    else "Monthly financial and freight results"
                ),
                meta=(
                    _version_label(actuals)
                    if actuals
                    else "Open Data Center"
                ),
                icon="A",
            ),
            StatusCard(
                title="Budget",
                status="Active" if budget else "Missing",
                metric=_version_label(budget),
                description=(
                    "Annual P&L, operations, OPEX and PERSEX"
                ),
                meta=(
                    f"Health {budget.health_score:.0f}%"
                    if budget
                    else "Reserved in frozen V2 scope"
                ),
                icon="B",
            ),
            StatusCard(
                title="Forecast",
                status="Active" if forecast else "Missing",
                metric=_version_label(forecast),
                description="Rolling forecast and scenarios",
                meta=(
                    f"Health {forecast.health_score:.0f}%"
                    if forecast
                    else "Not activated"
                ),
                icon="F",
            ),
            StatusCard(
                title="Working Capital",
                status=(
                    "Active"
                    if working_capital
                    else "Missing"
                ),
                metric=(
                    f"{working_capital.rows:,} items"
                    if working_capital
                    else "Not loaded"
                ),
                description="AR, AP, open items and aging",
                meta=(
                    _version_label(working_capital)
                    if working_capital
                    else "Open Data Center"
                ),
                icon="WC",
            ),
            StatusCard(
                title="Prior Year",
                status=(
                    "Active"
                    if prior_year
                    else "Missing"
                ),
                metric=_version_label(prior_year),
                description="Historical comparison baseline",
                meta=(
                    f"Health {prior_year.health_score:.0f}%"
                    if prior_year
                    else "Not activated"
                ),
                icon="PY",
            ),
            StatusCard(
                title="FX Rates",
                status="Active" if fx_rates else "Missing",
                metric=_version_label(fx_rates),
                description="Currency conversion master",
                meta=(
                    f"Health {fx_rates.health_score:.0f}%"
                    if fx_rates
                    else "Not activated"
                ),
                icon="FX",
            ),
        ],
        columns=3,
    )

    active_count = len(datasets)
    expected_count = 6
    platform_health = round(
        active_count
        / expected_count
        * 100
    )

    st.markdown("### Platform Readiness")

    ready_1, ready_2, ready_3, ready_4 = st.columns(4)

    ready_1.metric(
        "Active Sources",
        f"{active_count}/{expected_count}",
    )
    ready_2.metric(
        "Platform Readiness",
        f"{platform_health}%",
    )
    ready_3.metric(
        "Actuals Quality",
        (
            f"{actuals.quality_score:.0f}%"
            if actuals
            else "—"
        ),
    )
    ready_4.metric(
        "Last Refresh",
        datetime.now().strftime("%H:%M"),
    )

    st.markdown("### Quick Access")

    action_1, action_2, action_3 = st.columns(3)

    with action_1:
        if st.button(
            "Launch Mission Control",
            use_container_width=True,
            type="primary",
            disabled=actuals is None,
        ):
            _navigate("mission_control")

        st.caption(
            "Uses the active Actuals version."
        )

    with action_2:
        if st.button(
            "Open Data Center",
            use_container_width=True,
        ):
            _navigate("data_center")

        st.caption(
            "Validate, version and activate datasets."
        )

    with action_3:
        if st.button(
            "Open Financial",
            use_container_width=True,
            disabled=actuals is None,
        ):
            _navigate("financial")

        st.caption(
            "P&L, Budget, OPEX and Working Capital."
        )
