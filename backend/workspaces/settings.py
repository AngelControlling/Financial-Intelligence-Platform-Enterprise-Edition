from __future__ import annotations

import streamlit as st

from core.session_manager import SessionManager


def render_settings_workspace() -> None:
    session = SessionManager()
    session.initialize()

    st.markdown("### Enterprise Context")

    company = st.text_input(
        "Company",
        value=session.get(
            "fip_company",
            "Enterprise Freight Demo",
        ),
        key="settings_company",
    )

    currency = st.selectbox(
        "Default Currency",
        options=[
            "USD",
            "MXN",
            "EUR",
            "CAD",
            "BRL",
        ],
        index=0,
        key="settings_currency",
    )

    role = st.selectbox(
        "User Role",
        options=[
            "CFO",
            "Controller",
            "FP&A",
            "Finance Manager",
            "Administrator",
        ],
        index=1,
        key="settings_role",
    )

    if st.button(
        "Save Enterprise Context",
        type="primary",
    ):
        session.set(
            "fip_company",
            company,
        )
        session.set(
            "fip_currency",
            currency,
        )
        session.set(
            "fip_user_role",
            role,
        )
        st.success(
            "Enterprise context updated."
        )

    st.divider()
    st.markdown("### Platform Rules")
    st.checkbox(
        "Require validation before activation",
        value=True,
        disabled=True,
    )
    st.checkbox(
        "Keep Mission Control free of upload controls",
        value=True,
        disabled=True,
    )
    st.checkbox(
        "Preserve dataset version history",
        value=True,
        disabled=True,
    )
