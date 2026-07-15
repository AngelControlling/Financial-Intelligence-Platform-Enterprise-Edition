from __future__ import annotations

from collections.abc import Sequence

import plotly.graph_objects as go

from config.design_tokens import COLORS
from ui.plotly_theme import apply_enterprise_chart_style


def create_variance_waterfall(
    *,
    labels: Sequence[str],
    values: Sequence[float],
    title: str,
    start_label: str = "Baseline",
    end_label: str = "Actual",
    height: int = 420,
):
    """
    Create a CFO-style variance bridge.

    `values` must contain:
    start amount, intermediate movements, final amount.
    """

    if len(labels) != len(values):
        raise ValueError(
            "labels and values must have the same length."
        )

    if len(values) < 2:
        raise ValueError(
            "At least baseline and actual values are required."
        )

    measures = [
        "absolute",
        *(
            "relative"
            for _ in values[1:-1]
        ),
        "total",
    ]

    figure = go.Figure(
        go.Waterfall(
            name=title,
            orientation="v",
            measure=measures,
            x=list(labels),
            y=list(values),
            connector={
                "line": {
                    "color": COLORS.border_strong,
                }
            },
            increasing={
                "marker": {
                    "color": COLORS.success,
                }
            },
            decreasing={
                "marker": {
                    "color": COLORS.danger,
                }
            },
            totals={
                "marker": {
                    "color": COLORS.primary,
                }
            },
            textposition="outside",
            texttemplate="%{y:,.3s}",
            hovertemplate="%{x}<br>%{y:,.2f}<extra></extra>",
        )
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_layout(
        title=title,
        waterfallgap=0.25,
    )

    return figure
