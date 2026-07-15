from __future__ import annotations

import plotly.graph_objects as go

from config.design_tokens import COLORS


def create_target_gauge(
    *,
    title: str,
    actual: float,
    target: float,
    suffix: str = "",
    prefix: str = "",
    max_value: float | None = None,
    height: int = 245,
):
    """
    Create a stable gauge.

    The title is intentionally NOT rendered inside Plotly. Streamlit renders
    the visual title outside the figure to avoid Plotly showing `undefined`.
    """

    actual = float(actual or 0.0)
    target = float(target or 0.0)

    achievement = actual / target if target else 0.0

    if max_value is None:
        max_value = max(
            target * 1.25,
            actual * 1.10,
            1.0,
        )

    bar_color = (
        COLORS.success
        if achievement >= 1.0
        else COLORS.warning
        if achievement >= 0.90
        else COLORS.danger
    )

    indicator = go.Indicator(
        mode="gauge+number+delta",
        value=actual,
        domain={
            "x": [0.0, 1.0],
            "y": [0.0, 1.0],
        },
        number={
            "prefix": prefix,
            "suffix": suffix,
            "font": {
                "size": 30,
                "color": COLORS.text_primary,
            },
        },
        delta={
            "reference": target,
            "relative": True,
            "valueformat": ".1%",
            "position": "bottom",
            "increasing": {
                "color": COLORS.success,
            },
            "decreasing": {
                "color": COLORS.danger,
            },
        },
        gauge={
            "shape": "angular",
            "axis": {
                "range": [0, max_value],
                "tickcolor": COLORS.text_muted,
                "tickfont": {
                    "color": COLORS.text_muted,
                    "size": 10,
                },
            },
            "bar": {
                "color": bar_color,
                "thickness": 0.28,
            },
            "bgcolor": COLORS.background_elevated,
            "borderwidth": 1,
            "bordercolor": COLORS.border_subtle,
            "steps": [
                {
                    "range": [
                        0,
                        max(target * 0.90, 0),
                    ],
                    "color": "rgba(239,68,68,0.12)",
                },
                {
                    "range": [
                        max(target * 0.90, 0),
                        max(target, 0),
                    ],
                    "color": "rgba(245,158,11,0.14)",
                },
                {
                    "range": [
                        max(target, 0),
                        max_value,
                    ],
                    "color": "rgba(34,197,94,0.12)",
                },
            ],
            "threshold": {
                "line": {
                    "color": COLORS.text_primary,
                    "width": 3,
                },
                "thickness": 0.8,
                "value": target,
            },
        },
    )

    figure = go.Figure(
        data=[indicator]
    )

    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": COLORS.text_secondary,
            "family": (
                "Segoe UI, Inter, Arial, sans-serif"
            ),
        },
        margin={
            "l": 12,
            "r": 12,
            "t": 4,
            "b": 4,
        },
        showlegend=False,
        template=None,
        annotations=[],
    )

    # Remove any layout title object that Plotly may serialize as undefined.
    figure.layout.pop("title", None)

    return figure


def create_ratio_gauge(
    *,
    title: str,
    value: float,
    target: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
    suffix: str = "%",
    height: int = 245,
):
    return create_target_gauge(
        title=title,
        actual=value,
        target=target,
        suffix=suffix,
        max_value=maximum,
        height=height,
    )
