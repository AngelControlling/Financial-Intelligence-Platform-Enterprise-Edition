from __future__ import annotations

import streamlit as st


ENTERPRISE_CSS = """
<style>
:root {
    --fip-bg: #07111f;
    --fip-bg-2: #0a1828;
    --fip-panel: #10243d;
    --fip-panel-2: #0d1b2f;
    --fip-border: #1d3a5f;
    --fip-border-strong: #2b5688;
    --fip-text: #f4f7fb;
    --fip-text-2: #c7d4e3;
    --fip-muted: #8fa5bd;
    --fip-disabled: #60758d;
    --fip-primary: #2f80ed;
    --fip-cyan: #22d3ee;
    --fip-purple: #8b5cf6;
    --fip-success: #22c55e;
    --fip-warning: #f59e0b;
    --fip-danger: #ef4444;
    --fip-radius: 14px;
    --fip-shadow: 0 10px 28px rgba(0,0,0,.22);
}

html, body, [class*="css"] {
    font-family: "Segoe UI", Inter, Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 88% 4%, rgba(47,128,237,.10), transparent 30%),
        linear-gradient(180deg, var(--fip-bg) 0%, var(--fip-bg-2) 100%);
    color: var(--fip-text);
}

.block-container {
    max-width: 1680px;
    padding-top: 1rem;
    padding-left: 1.35rem;
    padding-right: 1.35rem;
    padding-bottom: 2.5rem;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #081426 0%, #0a1a31 100%);
    border-right: 1px solid var(--fip-border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: .75rem;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 42px;
    justify-content: flex-start;
    border: 1px solid rgba(143,165,189,.20);
    border-radius: 10px;
    background: rgba(255,255,255,.025);
    color: var(--fip-text-2);
    font-weight: 650;
    box-shadow: none;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--fip-border-strong);
    background: rgba(47,128,237,.10);
    color: white;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background:
        linear-gradient(90deg, var(--fip-primary), var(--fip-purple));
    border-color: transparent;
    color: white;
    box-shadow: 0 0 18px rgba(47,128,237,.22);
}

h1, h2, h3, h4 {
    color: var(--fip-text) !important;
    letter-spacing: -.025em;
}

hr {
    border-color: var(--fip-border);
}

[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid var(--fip-border);
}

.fip-shell-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: center;
    background:
        linear-gradient(145deg, rgba(15,34,58,.98), rgba(8,22,39,.98));
    border: 1px solid var(--fip-border);
    border-radius: var(--fip-radius);
    padding: .85rem 1rem;
    box-shadow: var(--fip-shadow);
    margin-bottom: .85rem;
}

.fip-shell-eyebrow {
    color: var(--fip-cyan);
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .11em;
}

.fip-shell-title {
    color: var(--fip-text);
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -.035em;
    margin-top: .12rem;
}

.fip-shell-subtitle {
    color: var(--fip-muted);
    font-size: .78rem;
    margin-top: .15rem;
}

.fip-shell-badge {
    padding: .35rem .55rem;
    border-radius: 999px;
    color: white;
    background: linear-gradient(90deg, var(--fip-primary), var(--fip-purple));
    font-size: .70rem;
    font-weight: 800;
    white-space: nowrap;
}

.fip-workspace-banner {
    background:
        linear-gradient(145deg, rgba(16,36,61,.98), rgba(10,25,43,.98));
    border: 1px solid var(--fip-border);
    border-radius: var(--fip-radius);
    padding: .9rem 1rem;
    margin-bottom: .9rem;
    box-shadow: var(--fip-shadow);
}

.fip-workspace-title {
    color: var(--fip-text);
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -.04em;
}

.fip-workspace-description {
    color: var(--fip-muted);
    font-size: .82rem;
    margin-top: .18rem;
}

.fip-context-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(115px, 1fr));
    gap: .55rem;
    margin-top: .75rem;
    padding-top: .65rem;
    border-top: 1px solid var(--fip-border);
}

.fip-context-item {
    border-right: 1px solid var(--fip-border);
    padding-right: .55rem;
}

.fip-context-item:last-child {
    border-right: 0;
}

.fip-context-label {
    color: var(--fip-disabled);
    font-size: .61rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
}

.fip-context-value {
    color: var(--fip-text-2);
    font-size: .76rem;
    font-weight: 700;
    margin-top: .12rem;
}

.fip-footer {
    margin-top: 1.25rem;
    padding-top: .75rem;
    border-top: 1px solid var(--fip-border);
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    color: var(--fip-disabled);
    font-size: .68rem;
}

.fip-notification-card {
    background: rgba(255,255,255,.025);
    border: 1px solid var(--fip-border);
    border-radius: 10px;
    padding: .6rem .7rem;
    margin-bottom: .45rem;
}

.fip-notification-title {
    color: var(--fip-text-2);
    font-size: .75rem;
    font-weight: 750;
}

.fip-notification-message {
    color: var(--fip-muted);
    font-size: .68rem;
    margin-top: .12rem;
}

@media (max-width: 800px) {
    .fip-shell-header {
        align-items: flex-start;
    }

    .fip-shell-title {
        font-size: 1.15rem;
    }
}
</style>
"""


def apply_enterprise_theme() -> None:
    """Apply the FIP Enterprise visual system."""

    if hasattr(st, "html"):
        st.html(ENTERPRISE_CSS)
    else:
        st.markdown(
            ENTERPRISE_CSS,
            unsafe_allow_html=True,
        )
