from __future__ import annotations

import streamlit as st

from engines.ai_controller_engine import AIControllerEngine
from engines.executive_brief_engine import ExecutiveBriefEngine
from models.executive_alert import ExecutiveAlert
from models.management_action import ManagementAction
from services.ai_executive_report_service import AIExecutiveReportService
from services.executive_brief_export_service import ExecutiveBriefExportService
from ui.executive_report_launcher import render_executive_report_launcher


def render_executive_brief(
    *,
    dataframe,
    period_label: str,
    comparison_label: str,
    summary: dict,
    variance: dict,
    alerts: list[ExecutiveAlert],
    actions: list[ManagementAction],
    company: str,
    currency: str,
    data_quality_score: float,
) -> None:
    st.markdown("### AI Executive Report")
    st.caption(
        "Generate a Controller-ready management report "
        "in a new browser tab."
    )

    brief = ExecutiveBriefEngine().build(
        period_label=period_label,
        comparison_label=comparison_label,
        summary=summary,
        variance=variance,
        alerts=alerts,
        actions=actions,
    )

    narrative = AIControllerEngine().generate(
        dataframe,
        period_label=period_label,
        comparison_label=comparison_label,
        summary=summary,
        variance=variance,
        data_quality_score=data_quality_score,
    )

    report_html = AIExecutiveReportService().build_html(
        brief=brief,
        narrative=narrative,
        company=company,
        currency=currency,
        controller_name="Finance Controller",
    )

    render_executive_report_launcher(report_html)

    csv_bytes = ExecutiveBriefExportService().to_csv(brief)
    safe_period = period_label.replace(" ", "_").replace("/", "-")

    with st.expander("Supporting financial data"):
        st.download_button(
            "Download Supporting Data CSV",
            data=csv_bytes,
            file_name=f"FIP_Executive_Data_{safe_period}.csv",
            mime="text/csv",
            use_container_width=True,
        )
