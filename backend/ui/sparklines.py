from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import plotly.graph_objects as go

from config.design_tokens import COLORS
from ui.plotly_theme import apply_enterprise_chart_style


def create_sparkline(
    values: Sequence[float],
    *,
    x_values: Sequence | None = None,
    title: str | None = None,
    height: int = 120,
    show_area: bool = True,
):
    """Create a compact sparkline for KPI cards and executive ribbons."""

    series = pd.Series(
        values,
        dtype="float64",
    )

    if x_values is None:
        x_values = list(
            range(len(series))
        )

    line_color = (
        COLORS.success
        if len(series) < 2
        or series.iloc[-1] >= series.iloc[0]
        else COLORS.danger
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=list(x_values),
            y=series,
            mode="lines",
            line={
                "color": line_color,
                "width": 2.4,
                "shape": "spline",
            },
            fill=(
                "tozeroy"
                if show_area
                else None
            ),
            fillcolor=(
                "rgba(34,197,94,0.10)"
                if line_color == COLORS.success
                else "rgba(239,68,68,0.10)"
            ),
            hovertemplate="%{y:,.2f}<extra></extra>",
        )
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_layout(
        title=title,
        margin={
            "l": 4,
            "r": 4,
            "t": 25 if title else 4,
            "b": 4,
        },
        xaxis={
            "visible": False,
            "fixedrange": True,
        },
        yaxis={
            "visible": False,
            "fixedrange": True,
        },
        hovermode="x unified",
    )

    return figure
