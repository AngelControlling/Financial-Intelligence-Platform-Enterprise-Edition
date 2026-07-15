from __future__ import annotations

import pandas as pd
import plotly.express as px

from config.design_tokens import COLORS
from ui.plotly_theme import apply_enterprise_chart_style


def create_country_choropleth(
    dataframe: pd.DataFrame,
    *,
    country_column: str,
    value_column: str,
    title: str,
    location_mode: str = "country names",
    hover_columns: list[str] | None = None,
    height: int = 500,
):
    """Create an interactive country-level revenue, GP or shipment map."""

    grouped_columns = [
        country_column
    ]

    aggregation = {
        value_column: "sum",
    }

    if hover_columns:
        for column in hover_columns:
            if column in dataframe.columns:
                aggregation[column] = "sum"

    grouped = (
        dataframe.groupby(
            grouped_columns,
            dropna=False,
        )
        .agg(aggregation)
        .reset_index()
    )

    figure = px.choropleth(
        grouped,
        locations=country_column,
        locationmode=location_mode,
        color=value_column,
        hover_name=country_column,
        hover_data=[
            column
            for column in (
                hover_columns or []
            )
            if column in grouped.columns
        ],
        color_continuous_scale=[
            COLORS.background_card,
            COLORS.primary,
            COLORS.accent_cyan,
        ],
        title=title,
    )

    figure = apply_enterprise_chart_style(
        figure,
        height=height,
        show_legend=False,
    )

    figure.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        showcoastlines=True,
        coastlinecolor=COLORS.border_strong,
        projection_type="natural earth",
        landcolor=COLORS.background_elevated,
        oceancolor=COLORS.background_primary,
        showocean=True,
        showcountries=True,
        countrycolor=COLORS.border_subtle,
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


def create_origin_destination_map(
    dataframe: pd.DataFrame,
    *,
    origin_country_column: str,
    destination_country_column: str,
    value_column: str,
    title: str = "Origin to Destination Flow",
    height: int = 520,
):
    """
    Create a country-level route map.

    This component requires latitude and longitude columns to be added in a
    later data-enrichment phase. Until then, use `create_country_choropleth`
    for origin and destination views.
    """

    raise NotImplementedError(
        "Origin-destination arcs require country geocoding. "
        "Use create_country_choropleth for V2.0.3."
    )
