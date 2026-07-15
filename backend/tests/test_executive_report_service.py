from models.executive_brief import (
    ExecutiveBrief,
)
from services.executive_report_service import (
    ExecutiveReportService,
)


def test_report_contains_print_and_management_sections() -> None:
    brief = ExecutiveBrief(
title="Executive Financial Report",
period_label="YTD 2026",
comparison_label="Budget",
headline="Performance requires attention.",
financial_summary="Financial summary.",
operational_summary="Operational summary.",
risks=["Margin risk."],
opportunities=["Growth opportunity."],
actions=["Pricing action."],
kpis={
    "Revenue": 1000.0,
    "Gross Profit": 250.0,
    "GP Margin": 0.25,
},
    )

    html = ExecutiveReportService().build_html(
brief,
company="Test Company",
currency="USD",
    )

    assert "window.print()" in html
    assert "Top Risks" in html
    assert "Open Management Actions" in html
    assert "Test Company" in html
