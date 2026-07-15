from __future__ import annotations

import streamlit as st

from core.session_manager import SessionManager
from services.workspace_data_service import (
    WorkspaceDataService,
)
from ui.workspace_components import (
    StatusCard,
    render_empty_state,
    render_status_grid,
)


def render_financial_workspace() -> None:
    session = SessionManager()
    session.initialize()
    service = WorkspaceDataService(session)

    context = (
        service.get_active_freight_context()
    )

    if context is None:
        render_empty_state(
            title="Financial Intelligence requires active Actuals",
            message=(
                "P&L, Budget, Forecast, OPEX, Personnel and "
                "Working Capital will consume validated sources "
                "from Data Center."
            ),
            action_label="Open Data Center",
            action_workspace="data_center",
        )
        return

    summary = context.summary

    render_status_grid(
        [
            StatusCard(
                title="Revenue",
                status="Active",
                metric=(
                    f"${summary.get('actual_revenue', 0):,.0f}"
                ),
                description="Actual Revenue",
                meta=(
                    f"vs {context.comparison_label}"
                ),
                icon="R",
            ),
            StatusCard(
                title="Gross Profit",
                status="Active",
                metric=(
                    f"${summary.get('actual_gp', 0):,.0f}"
                ),
                description="Actual GP",
                meta=(
                    f"Margin "
                    f"{summary.get('actual_gp_margin', 0):.1%}"
                ),
                icon="GP",
            ),
            StatusCard(
                title="Budget Intelligence",
                status=(
                    "Ready"
                    if context.comparison_label
                    == "Budget"
                    else "Pending"
                ),
                metric=context.comparison_label,
                description="Active comparison baseline",
                meta="Annual template framework next",
                icon="B",
            ),
            StatusCard(
                title="OPEX",
                status="Pending",
                metric="Reserved",
                description="Monthly OPEX variance",
                meta="Included in Budget scope",
                icon="O",
            ),
            StatusCard(
                title="Personnel",
                status="Pending",
                metric="Reserved",
                description="PERSEX and headcount control",
                meta="Included in Budget scope",
                icon="P",
            ),
            StatusCard(
                title="Working Capital",
                status=(
                    "Ready"
                    if service.get_dataset(
                        "working_capital"
                    )
                    else "Missing"
                ),
                metric="AR / AP",
                description="Aging and open-item control",
                meta="Independent source",
                icon="WC",
            ),
        ],
        columns=3,
    )

    st.info(
        "Module 01C establishes the Financial Workspace contract. "
        "Budget, OPEX, Personnel and Working Capital pages will be "
        "connected through Data Center in the next modules."
    )
