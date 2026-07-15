from __future__ import annotations

import streamlit as st


def render_html(html: str) -> None:
    """Render HTML without Markdown code-block interpretation."""

    clean_html = " ".join(
        line.strip()
        for line in str(html).splitlines()
        if line.strip()
    )

    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(
            clean_html,
            unsafe_allow_html=True,
        )
