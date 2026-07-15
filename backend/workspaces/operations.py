from __future__ import annotations

import streamlit as st

from core.session_manager import SessionManager
from services.workspace_data_service import (
    WorkspaceDataService,
)
from ui.workspace_components import (
    render_empty_state,
)
from workspaces.mission_control import (
    render_mission_control_workspace,
)


def render_operations_workspace() -> None:
    session = SessionManager()
    session.initialize()
    service = WorkspaceDataService(session)
    context = (
        service.get_active_freight_context()
    )

    if context is None:
        render_empty_state(
            title="Operations Intelligence requires active Actuals",
            message=(
                "Air, Ocean, Ground, products, trade lanes and "
                "customers will consume the same active Data Center source."
            ),
            action_label="Open Data Center",
            action_workspace="data_center",
        )
        return

    dataframe = context.dataframe

    mode_options = sorted(
        dataframe["mode"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    ) if "mode" in dataframe.columns else []

    selected_modes = st.multiselect(
        "Mode",
        options=mode_options,
        default=mode_options,
        key="operations_workspace_modes",
    )

    filtered = (
        dataframe[
            dataframe["mode"].isin(
                selected_modes
            )
        ].copy()
        if mode_options
        else dataframe.copy()
    )

    st.metric(
        "Operational Records",
        f"{len(filtered):,}",
    )

    if "mode" in filtered.columns:
        mode_table = (
            filtered.groupby(
                "mode",
                dropna=False,
            )
            .agg(
                Shipments=(
                    "shipment",
                    "nunique",
                ),
                Revenue=(
                    "actual_revenue",
                    "sum",
                ),
                GP=(
                    "actual_gp",
                    "sum",
                ),
                Tons=(
                    "tons",
                    "sum",
                ),
                TEUs=(
                    "teus",
                    "sum",
                ),
            )
            .reset_index()
        )

        st.dataframe(
            mode_table,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Detailed Air and Ocean drill-down remains available "
        "in the existing V1 while Module 02 connects it to "
        "the permanent active dataset."
    )
