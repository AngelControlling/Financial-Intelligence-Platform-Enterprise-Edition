from __future__ import annotations

from copy import deepcopy

from config.design_tokens import (
    CHART_COLOR_SEQUENCE,
    COLORS,
)


PLOTLY_ENTERPRISE_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "color": COLORS.text_secondary,
        "family": "Segoe UI, Inter, Arial, sans-serif",
    },
    "title": {
        "font": {
            "color": COLORS.text_primary,
            "size": 18,
        },
        "x": 0.01,
        "xanchor": "left",
    },
    "legend": {
        "font": {
            "color": COLORS.text_secondary,
        },
        "bgcolor": "rgba(0,0,0,0)",
    },
    "margin": {
        "l": 45,
        "r": 20,
        "t": 60,
        "b": 45,
    },
    "hoverlabel": {
        "bgcolor": COLORS.background_card,
        "bordercolor": COLORS.border_strong,
        "font": {
            "color": COLORS.text_primary,
        },
    },
    "xaxis": {
        "gridcolor": COLORS.border_subtle,
        "zerolinecolor": COLORS.border_subtle,
        "linecolor": COLORS.border_subtle,
        "tickfont": {
            "color": COLORS.text_muted,
        },
        "title_font": {
            "color": COLORS.text_muted,
        },
    },
    "yaxis": {
        "gridcolor": COLORS.border_subtle,
        "zerolinecolor": COLORS.border_subtle,
        "linecolor": COLORS.border_subtle,
        "tickfont": {
            "color": COLORS.text_muted,
        },
        "title_font": {
            "color": COLORS.text_muted,
        },
    },
}


def apply_enterprise_chart_style(
    figure,
    *,
    height: int | None = None,
    show_legend: bool | None = None,
):
    """Apply the enterprise Plotly theme to a figure."""

    layout = deepcopy(
        PLOTLY_ENTERPRISE_LAYOUT
    )

    if height is not None:
        layout["height"] = height

    if show_legend is not None:
        layout["showlegend"] = show_legend

    figure.update_layout(**layout)

    return figure


def enterprise_color_sequence() -> list[str]:
    """Return a copy of the approved V2 chart palette."""

    return list(CHART_COLOR_SEQUENCE)
