from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
    """Enterprise color palette used across the V2 interface."""

    background_primary: str = "#07111F"
    background_secondary: str = "#091827"
    background_elevated: str = "#0D1B2F"
    background_card: str = "#10243D"
    background_card_hover: str = "#142C49"
    background_sidebar: str = "#081426"

    border_subtle: str = "#1C3657"
    border_strong: str = "#2B4D73"

    text_primary: str = "#F4F7FB"
    text_secondary: str = "#C7D4E3"
    text_muted: str = "#8FA5BD"
    text_disabled: str = "#60758D"

    primary: str = "#2F80ED"
    primary_hover: str = "#4A93F1"
    secondary: str = "#14B8A6"
    accent_cyan: str = "#22D3EE"
    accent_purple: str = "#8B5CF6"

    success: str = "#22C55E"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"
    critical: str = "#991B1B"
    info: str = "#38BDF8"

    chart_1: str = "#14B8A6"
    chart_2: str = "#2F80ED"
    chart_3: str = "#8B5CF6"
    chart_4: str = "#22D3EE"
    chart_5: str = "#F59E0B"
    chart_6: str = "#22C55E"
    chart_7: str = "#EF4444"


@dataclass(frozen=True)
class TypographyTokens:
    """Typography scale for executive and operational views."""

    font_family: str = '"Segoe UI", Inter, Arial, sans-serif'
    font_mono: str = '"Cascadia Code", "Roboto Mono", monospace'

    size_display: str = "2.25rem"
    size_h1: str = "1.85rem"
    size_h2: str = "1.45rem"
    size_h3: str = "1.15rem"
    size_metric: str = "1.85rem"
    size_body: str = "0.95rem"
    size_small: str = "0.82rem"
    size_caption: str = "0.74rem"

    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_extrabold: int = 800


@dataclass(frozen=True)
class SpacingTokens:
    """Consistent spacing values based on a 4-pixel scale."""

    xxs: str = "0.25rem"
    xs: str = "0.5rem"
    sm: str = "0.75rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"


@dataclass(frozen=True)
class RadiusTokens:
    """Border radius values for reusable components."""

    small: str = "8px"
    medium: str = "12px"
    large: str = "16px"
    pill: str = "999px"


@dataclass(frozen=True)
class ShadowTokens:
    """Elevation system for cards, menus and modal surfaces."""

    subtle: str = "0 4px 14px rgba(0, 0, 0, 0.16)"
    card: str = "0 10px 28px rgba(0, 0, 0, 0.22)"
    elevated: str = "0 18px 42px rgba(0, 0, 0, 0.30)"
    glow_primary: str = "0 0 18px rgba(47, 128, 237, 0.26)"
    glow_success: str = "0 0 16px rgba(34, 197, 94, 0.24)"
    glow_warning: str = "0 0 16px rgba(245, 158, 11, 0.24)"
    glow_danger: str = "0 0 16px rgba(239, 68, 68, 0.24)"


@dataclass(frozen=True)
class LayoutTokens:
    """Global layout rules for the V2 12-column visual system."""

    max_width: str = "1680px"
    content_padding_top: str = "1.25rem"
    content_padding_horizontal: str = "1.5rem"
    content_padding_bottom: str = "2.5rem"
    grid_gap: str = "1rem"
    sidebar_width: str = "280px"
    header_height: str = "72px"


COLORS = ColorTokens()
TYPOGRAPHY = TypographyTokens()
SPACING = SpacingTokens()
RADIUS = RadiusTokens()
SHADOWS = ShadowTokens()
LAYOUT = LayoutTokens()

CHART_COLOR_SEQUENCE = [
    COLORS.chart_1,
    COLORS.chart_2,
    COLORS.chart_3,
    COLORS.chart_4,
    COLORS.chart_5,
    COLORS.chart_6,
    COLORS.chart_7,
]

STATUS_COLORS = {
    "success": COLORS.success,
    "warning": COLORS.warning,
    "danger": COLORS.danger,
    "critical": COLORS.critical,
    "info": COLORS.info,
    "neutral": COLORS.text_muted,
}
