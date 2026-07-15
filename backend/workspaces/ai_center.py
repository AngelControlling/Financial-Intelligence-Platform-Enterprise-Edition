from __future__ import annotations

import streamlit as st

from ui.elevenlabs_agent import render_voice_agent_control_panel
from ui.workspace_components import StatusCard, render_status_grid


def render_ai_center_workspace() -> None:
    render_status_grid(
        [
            StatusCard(
                title="Executive Narrative",
                status="Ready",
                metric="Online",
                description="Automated management commentary",
                meta="Uses validated financial outputs",
                icon="EN",
            ),
            StatusCard(
                title="Recommendations",
                status="Ready",
                metric="Online",
                description="Action-oriented finance recommendations",
                meta="Rules and insight engines",
                icon="REC",
            ),
            StatusCard(
                title="Voice Controller",
                status="Ready",
                metric="ElevenLabs",
                description="Conversational voice interface",
                meta="Available globally in the lower-right corner",
                icon="VC",
            ),
        ],
        columns=3,
    )

    st.markdown("### Voice Controller")
    st.caption(
        "The ElevenLabs agent is mounted globally and remains available "
        "across Data Center, Mission Control and all intelligence workspaces."
    )
    render_voice_agent_control_panel()

    st.info(
        "The browser may request microphone permission the first time. "
        "The widget also requires internet access to ElevenLabs. "
        "Set ELEVENLABS_AGENT_ID to replace the default configured agent."
    )

    st.info(
        "AI consumes approved outputs and must not alter source data."
    )
