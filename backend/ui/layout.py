from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import streamlit as st


def section_header(
    title: str,
    subtitle: str | None = None,
) -> None:
    """Render a consistent enterprise section header."""

    subtitle_html = (
        f'<div class="fip-panel-caption">{subtitle}</div>'
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div style="margin: 0.25rem 0 0.85rem 0;">
            <div class="fip-panel-title">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def enterprise_panel(
    title: str | None = None,
    subtitle: str | None = None,
) -> Iterator[None]:
    """
    Create a reusable visual panel.

    Streamlit does not provide a native HTML container that safely wraps
    arbitrary widgets. This helper renders the panel heading consistently
    and yields a normal Streamlit container for its contents.
    """

    with st.container():
        if title:
            section_header(
                title=title,
                subtitle=subtitle,
            )

        yield


def horizontal_divider() -> None:
    """Render the approved V2 divider."""

    st.markdown(
        '<div class="fip-divider"></div>',
        unsafe_allow_html=True,
    )
