from __future__ import annotations

from html import escape

import streamlit as st

from core.notification_manager import NotificationManager
from ui.html_renderer import render_html


def render_notification_center(
    manager: NotificationManager,
) -> None:
    """Render compact notifications inside the sidebar."""

    notifications = manager.list_all()

    st.sidebar.caption("NOTIFICATIONS")

    if not notifications:
        st.sidebar.caption(
            "No active notifications"
        )
        return

    for notification in notifications[:5]:
        render_html(
            '<div class="fip-notification-card">'
            f'<div class="fip-notification-title">{escape(notification.title)}</div>'
            f'<div class="fip-notification-message">{escape(notification.message)}</div>'
            '</div>'
        )

    if st.sidebar.button(
        "Clear notifications",
        key="fip_clear_notifications",
        use_container_width=True,
    ):
        manager.clear()
        st.rerun()
