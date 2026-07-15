from __future__ import annotations

import streamlit as st

from config.design_tokens import (
    COLORS,
    LAYOUT,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
)


def build_enterprise_css() -> str:
    """Return the centralized CSS for Financial Intelligence Platform V2."""

    return f"""
    <style>
    :root {{
        --fip-bg-primary: {COLORS.background_primary};
        --fip-bg-secondary: {COLORS.background_secondary};
        --fip-bg-elevated: {COLORS.background_elevated};
        --fip-bg-card: {COLORS.background_card};
        --fip-bg-card-hover: {COLORS.background_card_hover};
        --fip-bg-sidebar: {COLORS.background_sidebar};

        --fip-border-subtle: {COLORS.border_subtle};
        --fip-border-strong: {COLORS.border_strong};

        --fip-text-primary: {COLORS.text_primary};
        --fip-text-secondary: {COLORS.text_secondary};
        --fip-text-muted: {COLORS.text_muted};
        --fip-text-disabled: {COLORS.text_disabled};

        --fip-primary: {COLORS.primary};
        --fip-primary-hover: {COLORS.primary_hover};
        --fip-secondary: {COLORS.secondary};
        --fip-cyan: {COLORS.accent_cyan};
        --fip-purple: {COLORS.accent_purple};

        --fip-success: {COLORS.success};
        --fip-warning: {COLORS.warning};
        --fip-danger: {COLORS.danger};
        --fip-critical: {COLORS.critical};
        --fip-info: {COLORS.info};

        --fip-radius-sm: {RADIUS.small};
        --fip-radius-md: {RADIUS.medium};
        --fip-radius-lg: {RADIUS.large};
        --fip-radius-pill: {RADIUS.pill};

        --fip-shadow-subtle: {SHADOWS.subtle};
        --fip-shadow-card: {SHADOWS.card};
        --fip-shadow-elevated: {SHADOWS.elevated};

        --fip-space-xs: {SPACING.xs};
        --fip-space-sm: {SPACING.sm};
        --fip-space-md: {SPACING.md};
        --fip-space-lg: {SPACING.lg};
        --fip-space-xl: {SPACING.xl};
    }}

    html, body, [class*="css"] {{
        font-family: {TYPOGRAPHY.font_family};
    }}

    .stApp {{
        background:
            radial-gradient(
                circle at 88% 4%,
                rgba(47, 128, 237, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 12% 96%,
                rgba(20, 184, 166, 0.08),
                transparent 24%
            ),
            linear-gradient(
                180deg,
                var(--fip-bg-primary) 0%,
                var(--fip-bg-secondary) 100%
            );
        color: var(--fip-text-primary);
    }}

    .block-container {{
        max-width: {LAYOUT.max_width};
        padding-top: {LAYOUT.content_padding_top};
        padding-right: {LAYOUT.content_padding_horizontal};
        padding-bottom: {LAYOUT.content_padding_bottom};
        padding-left: {LAYOUT.content_padding_horizontal};
    }}

    [data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                var(--fip-bg-sidebar) 0%,
                #0A1A31 100%
            );
        border-right: 1px solid var(--fip-border-subtle);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--fip-text-primary);
    }}

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {{
        color: var(--fip-text-muted) !important;
    }}

    h1, h2, h3, h4 {{
        color: var(--fip-text-primary) !important;
        letter-spacing: -0.025em;
    }}

    h1 {{
        font-size: {TYPOGRAPHY.size_h1};
        font-weight: {TYPOGRAPHY.weight_extrabold};
    }}

    h2 {{
        font-size: {TYPOGRAPHY.size_h2};
        font-weight: {TYPOGRAPHY.weight_bold};
    }}

    h3 {{
        font-size: {TYPOGRAPHY.size_h3};
        font-weight: {TYPOGRAPHY.weight_semibold};
    }}

    p, span, label {{
        color: inherit;
    }}

    hr {{
        border-color: var(--fip-border-subtle);
    }}

    [data-testid="stMetric"] {{
        background:
            linear-gradient(
                180deg,
                rgba(16, 36, 61, 0.98),
                rgba(11, 27, 46, 0.98)
            );
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-lg);
        padding: 1rem 1.1rem;
        box-shadow: var(--fip-shadow-card);
        transition:
            transform 160ms ease,
            border-color 160ms ease,
            background-color 160ms ease;
    }}

    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        border-color: var(--fip-border-strong);
        background: var(--fip-bg-card-hover);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--fip-text-muted) !important;
        font-size: {TYPOGRAPHY.size_small};
        font-weight: {TYPOGRAPHY.weight_semibold};
    }}

    [data-testid="stMetricValue"] {{
        color: var(--fip-text-primary) !important;
        font-size: {TYPOGRAPHY.size_metric};
        font-weight: {TYPOGRAPHY.weight_extrabold};
        letter-spacing: -0.035em;
    }}

    [data-testid="stTabs"] {{
        border-bottom: 1px solid var(--fip-border-subtle);
    }}

    [data-testid="stTabs"] button {{
        color: var(--fip-text-muted);
        font-weight: {TYPOGRAPHY.weight_semibold};
        border-radius: var(--fip-radius-sm) var(--fip-radius-sm) 0 0;
        padding: 0.65rem 0.9rem;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--fip-cyan) !important;
        border-bottom: 2px solid var(--fip-cyan) !important;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        background:
            linear-gradient(
                90deg,
                var(--fip-primary),
                var(--fip-purple)
            );
        color: white;
        border: 0;
        border-radius: var(--fip-radius-md);
        font-weight: {TYPOGRAPHY.weight_bold};
        padding: 0.58rem 1rem;
        box-shadow: {SHADOWS.glow_primary};
        transition:
            transform 160ms ease,
            filter 160ms ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        transform: translateY(-1px);
        filter: brightness(1.08);
    }}

    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div,
    .stDateInput > div > div {{
        background-color: #0B1A2D !important;
        border: 1px solid var(--fip-border-subtle) !important;
        border-radius: var(--fip-radius-md) !important;
        color: var(--fip-text-primary) !important;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stExpander"] {{
        background: rgba(13, 27, 47, 0.94);
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-md);
        overflow: hidden;
        box-shadow: var(--fip-shadow-subtle);
    }}

    [data-testid="stAlert"] {{
        border-radius: var(--fip-radius-md);
        border: 1px solid var(--fip-border-subtle);
    }}

    .fip-enterprise-panel {{
        background:
            linear-gradient(
                180deg,
                rgba(16, 36, 61, 0.98),
                rgba(11, 27, 46, 0.98)
            );
        border: 1px solid var(--fip-border-subtle);
        border-radius: var(--fip-radius-lg);
        padding: 1rem;
        box-shadow: var(--fip-shadow-card);
    }}

    .fip-panel-title {{
        color: var(--fip-text-primary);
        font-size: {TYPOGRAPHY.size_h3};
        font-weight: {TYPOGRAPHY.weight_bold};
        margin-bottom: 0.25rem;
    }}

    .fip-panel-caption {{
        color: var(--fip-text-muted);
        font-size: {TYPOGRAPHY.size_small};
    }}

    .fip-divider {{
        height: 1px;
        background: var(--fip-border-subtle);
        margin: 1rem 0;
    }}

    .fip-scroll-area {{
        scrollbar-color:
            var(--fip-border-strong)
            var(--fip-bg-secondary);
        scrollbar-width: thin;
    }}

    @media (max-width: 900px) {{
        .block-container {{
            padding-right: 1rem;
            padding-left: 1rem;
        }}
    }}
    </style>
    """


def apply_enterprise_theme() -> None:
    """Apply the centralized V2 theme to a Streamlit application."""

    st.markdown(
        build_enterprise_css(),
        unsafe_allow_html=True,
    )
