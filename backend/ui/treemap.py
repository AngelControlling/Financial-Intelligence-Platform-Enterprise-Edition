from __future__ import annotations

import pandas as pd
import plotly.express as px

from ui.plotly_theme import (
    apply_enterprise_chart_style,
    enterprise_color_sequence,
)


def create_profitability_treemap(
    dataframe: pd.DataFrame,
    *,
    dimension: str,
    value_column: str = "actual_revenue",
    color_column: str = "actual_gp_margin",
    title: str | None = None,
    parent_dimension: str | None = None,
    height: int = 450,
):
    """Create an executive treemap for customer, product or route exposure."""

    path = [dimension]

    if parent_dimension:
        path = [
            parent_dimension,
            dimension,
        ]

    figure = px.treemap(
        dataframe,
        path=path,
        values=value_column,
        color=color_column,
        color_continuous_scale=[
            "#EF4444",
            "#F59E0B",
            "#22C55E",
        ],
        title=title,
        hover_data=[
            column
            for column in [
                "actual_revenue",
                "actual_cost",
                "actual_gp",
                "actual_gp_margin",
            ]
            if column in dataframe.columns
        ],
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_traces(
        textinfo="label+value+percent parent",
        marker={
            "line": {
                "width": 1,
                "color": "rgba(255,255,255,0.12)",
            }
        },
    )

    return figure
