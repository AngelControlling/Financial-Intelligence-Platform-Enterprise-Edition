from __future__ import annotations

from typing import Mapping

import pandas as pd
import streamlit as st


def render_enterprise_table(
    dataframe: pd.DataFrame,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    height: int | None = None,
    hide_index: bool = True,
    column_config: Mapping | None = None,
) -> None:
    """Render a consistently configured enterprise data table."""

    if title:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.5rem;">
                <div class="fip-panel-title">
                    {title}
                </div>
                {
                    f'<div class="fip-panel-caption">{subtitle}</div>'
                    if subtitle
                    else ""
                }
            </div>
            """,
            unsafe_allow_html=True,
        )

    if dataframe.empty:
        st.info(
            "No data is available for the selected context."
        )
        return

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=hide_index,
        height=height,
        column_config=column_config,
    )


def add_rank_column(
    dataframe: pd.DataFrame,
    column_name: str = "Rank",
) -> pd.DataFrame:
    """Return a copy with a one-based ranking column."""

    df = dataframe.copy()

    df.insert(
        0,
        column_name,
        range(1, len(df) + 1),
    )

    return df
