from __future__ import annotations
from datetime import date, timedelta
import pandas as pd
import streamlit as st
from models.executive_alert import ExecutiveAlert
from services.management_action_service import ManagementActionService

def render_executive_action_center(
    alerts: list[ExecutiveAlert],
    *,
    period_label: str,
) -> None:
    st.markdown("### Executive Action Center")
    st.caption("Convert insights into accountable management actions.")

    service = ManagementActionService()
    proposal_tab, plan_tab = st.tabs(
        ["Recommended Actions", "Management Action Plan"]
    )

    with proposal_tab:
        proposals = service.proposals(
            alerts,
            period_label=period_label,
        )
        if not proposals:
            st.success("No action proposals are required.")
        for index, action in enumerate(proposals):
            col_1, col_2 = st.columns([4, 1])
            with col_1:
                st.markdown(
                    f"**{action.priority} · {action.title}**\n\n"
                    f"{action.description}\n\n"
                    f"Potential impact: ${action.expected_impact:,.0f}"
                )
            with col_2:
                if st.button(
                    "Add to Plan",
                    key=f"add_action_{index}_{action.source_alert_id}",
                    use_container_width=True,
                    type="primary"
                    if action.priority in {"Critical", "High"}
                    else "secondary",
                ):
                    service.add(action)
                    st.success("Action added.")
                    st.rerun()
            st.divider()

    with plan_tab:
        actions = service.list_all()
        if not actions:
            st.info("The Management Action Plan is empty.")
            return

        open_actions = [
            action for action in actions
            if action.status not in {"Completed", "Cancelled"}
        ]
        overdue = [
            action for action in open_actions
            if action.due_date and action.due_date < date.today().isoformat()
        ]
        potential = sum(action.expected_impact for action in open_actions)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Open Actions", len(open_actions))
        m2.metric("Critical", sum(a.priority == "Critical" for a in open_actions))
        m3.metric("Overdue", len(overdue))
        m4.metric("Potential Recovery", f"${potential:,.0f}")

        for action in actions:
            with st.expander(
                f"{action.priority} · {action.title} · {action.status}"
            ):
                st.write(action.description)
                c1, c2, c3 = st.columns(3)
                with c1:
                    owner = st.text_input(
                        "Owner",
                        value=action.owner,
                        key=f"owner_{action.action_id}",
                    )
                with c2:
                    options = [
                        "Open",
                        "In Progress",
                        "Blocked",
                        "Completed",
                        "Cancelled",
                    ]
                    status = st.selectbox(
                        "Status",
                        options=options,
                        index=options.index(action.status)
                        if action.status in options else 0,
                        key=f"status_{action.action_id}",
                    )
                with c3:
                    due = st.date_input(
                        "Due Date",
                        value=date.fromisoformat(action.due_date)
                        if action.due_date
                        else date.today() + timedelta(days=30),
                        key=f"due_{action.action_id}",
                    )

                b1, b2 = st.columns(2)
                with b1:
                    if st.button(
                        "Save Action",
                        key=f"save_{action.action_id}",
                        use_container_width=True,
                        type="primary",
                    ):
                        service.update(
                            action.action_id,
                            owner=owner,
                            status=status,
                            due_date=due.isoformat(),
                        )
                        st.success("Action updated.")
                        st.rerun()
                with b2:
                    if st.button(
                        "Delete Action",
                        key=f"delete_{action.action_id}",
                        use_container_width=True,
                    ):
                        service.delete(action.action_id)
                        st.rerun()

        st.markdown("#### Action Plan Export View")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Priority": a.priority,
                        "Action": a.title,
                        "Owner": a.owner,
                        "Status": a.status,
                        "Due Date": a.due_date,
                        "Period": a.period_label,
                        "Potential Impact": a.expected_impact,
                    }
                    for a in actions
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
