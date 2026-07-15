from __future__ import annotations

import streamlit as st

from core.session_manager import SessionManager
from services.period_intelligence_service import (
    PeriodIntelligenceService,
)
from services.workspace_data_service import (
    WorkspaceDataService,
)
from ui.period_selector import render_period_selector
from ui.workspace_components import render_empty_state
from workspaces.mission_control_native import (
    render_enterprise_mission_control,
)


def render_mission_control_shell() -> None:
    session = SessionManager()
    session.initialize()

    service = WorkspaceDataService(session)
    context = service.get_active_freight_context()

    if context is None:
        render_empty_state(
            title="Mission Control is waiting for active Actuals",
            message=(
                "Open Data Center, validate an Actuals version "
                "and activate it."
            ),
            action_label="Open Data Center",
            action_workspace="data_center",
        )
        return

    selection = render_period_selector(
        context.dataframe
    )

    aligned_context = (
        PeriodIntelligenceService().apply(
            context,
            selection,
        )
    )

    st.info(
        "Active Comparison: "
        f"{aligned_context.selected_period_label} Actual "
        f"vs {aligned_context.comparison_label} "
        f"for the same period."
    )

    if aligned_context.dataframe.empty:
        st.warning(
            "No records exist for the selected period."
        )
        return

    render_enterprise_mission_control(
        aligned_context
    )
