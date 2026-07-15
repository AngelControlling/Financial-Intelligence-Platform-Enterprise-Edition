from __future__ import annotations

import pandas as pd
import plotly.express as px

from config.design_tokens import COLORS
from ui.plotly_theme import apply_enterprise_chart_style


def create_financial_heatmap(
    dataframe: pd.DataFrame,
    *,
    row_dimension: str,
    column_dimension: str,
    value_column: str,
    aggregation: str = "sum",
    title: str | None = None,
    height: int = 430,
):
    """Create a financial heatmap by two business dimensions."""

    pivot = pd.pivot_table(
        dataframe,
        index=row_dimension,
        columns=column_dimension,
        values=value_column,
        aggfunc=aggregation,
        fill_value=0,
    )

    figure = px.imshow(
        pivot,
        text_auto=".3s",
        aspect="auto",
        color_continuous_scale=[
            [0.0, COLORS.danger],
            [0.50, COLORS.background_elevated],
            [1.0, COLORS.success],
        ],
        title=title,
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_layout(
        coloraxis_colorbar={
            "title": value_column,
            "tickfont": {
                "color": COLORS.text_muted,
            },
        }
    )

    return figure
