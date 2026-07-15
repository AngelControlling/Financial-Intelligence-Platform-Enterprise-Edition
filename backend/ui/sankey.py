from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import plotly.graph_objects as go

from config.design_tokens import CHART_COLOR_SEQUENCE
from ui.plotly_theme import apply_enterprise_chart_style


def create_business_flow_sankey(
    dataframe: pd.DataFrame,
    *,
    source_column: str,
    target_column: str,
    value_column: str,
    title: str | None = None,
    limit: int = 40,
    height: int = 500,
):
    """Create a Sankey flow between countries, routes, customers or modes."""

    grouped = (
        dataframe.groupby(
            [
                source_column,
                target_column,
            ],
            dropna=False,
        )[value_column]
        .sum()
        .reset_index()
        .sort_values(
            value_column,
            ascending=False,
        )
        .head(limit)
    )

    node_labels = list(
        dict.fromkeys(
            grouped[source_column]
            .astype(str)
            .tolist()
            + grouped[target_column]
            .astype(str)
            .tolist()
        )
    )

    node_index = {
        label: index
        for index, label in enumerate(
            node_labels
        )
    }

    source_indexes = (
        grouped[source_column]
        .astype(str)
        .map(node_index)
        .tolist()
    )

    target_indexes = (
        grouped[target_column]
        .astype(str)
        .map(node_index)
        .tolist()
    )

    values = (
        grouped[value_column]
        .astype(float)
        .tolist()
    )

    node_colors = [
        CHART_COLOR_SEQUENCE[
            index
            % len(CHART_COLOR_SEQUENCE)
        ]
        for index in range(
            len(node_labels)
        )
    ]

    figure = go.Figure(
        go.Sankey(
            arrangement="snap",
            node={
                "label": node_labels,
                "color": node_colors,
                "pad": 18,
                "thickness": 18,
                "line": {
                    "color": "rgba(255,255,255,0.18)",
                    "width": 1,
                },
            },
            link={
                "source": source_indexes,
                "target": target_indexes,
                "value": values,
                "color": "rgba(47,128,237,0.22)",
            },
        )
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_layout(
        title=title,
    )

    return figure
