from __future__ import annotations

import streamlit as st

from core.notification_manager import NotificationManager
from core.router import Router
from core.state_manager import StateManager
from core.workspace_registry import WorkspaceRegistry
from ui.notification_center import render_notification_center


def render_enterprise_sidebar(
    registry: WorkspaceRegistry,
    router: Router,
    state: StateManager,
    notifications: NotificationManager,
) -> None:
    """Render the Enterprise navigation and context controls."""

    st.sidebar.markdown("## FIP Enterprise")
    st.sidebar.caption(
        "Financial Intelligence Platform"
    )
    st.sidebar.divider()

    # Executive context controls.
    st.sidebar.caption("ENTERPRISE CONTEXT")

    company = st.sidebar.text_input(
        "Company",
        value=state.company,
        key="fip_sidebar_company",
    )

    currency = st.sidebar.selectbox(
        "Currency",
        options=[
            "USD",
            "MXN",
            "EUR",
            "CAD",
            "BRL",
        ],
        index=(
            ["USD", "MXN", "EUR", "CAD", "BRL"]
            .index(state.currency)
            if state.currency
            in ["USD", "MXN", "EUR", "CAD", "BRL"]
            else 0
        ),
        key="fip_sidebar_currency",
    )

    if company != state.company:
        state.set_company(company)

    if currency != state.currency:
        state.set_currency(currency)

    st.sidebar.divider()

    for section, workspaces in registry.grouped().items():
        st.sidebar.caption(section.upper())

        for workspace in workspaces:
            active = (
                workspace.key
                == state.current_workspace
            )

            if st.sidebar.button(
                f"{workspace.icon} {workspace.label}",
                key=f"fip_nav_{workspace.key}",
                use_container_width=True,
                type=(
                    "primary"
                    if active
                    else "secondary"
                ),
            ):
                router.navigate(workspace.key)

        st.sidebar.divider()

    render_notification_center(
        notifications
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "FIP Enterprise · V2.2"
    )
