from models.controller_narrative import ControllerNarrative
from models.executive_brief import ExecutiveBrief
from services.ai_executive_report_service import AIExecutiveReportService


def test_report_contains_ai_sections() -> None:
    brief = ExecutiveBrief(
        title="Executive Financial Report",
        period_label="YTD 2026",
        comparison_label="Budget",
        headline="Headline",
        financial_summary="Financial summary",
        operational_summary="Operational summary",
        risks=["Margin risk"],
        opportunities=["Growth opportunity"],
        actions=["Existing action"],
        kpis={
            "Revenue": 1000.0,
            "Gross Profit": 250.0,
            "GP Margin": 0.25,
        },
    )
    narrative = ControllerNarrative(
        executive_summary="Executive summary",
        what_happened="What happened",
        why_it_happened="Why it happened",
        business_risk="Business risk",
        recommended_actions=["Review pricing"],
        no_action_outlook="No-action outlook",
        confidence_score=0.95,
        management_priority="High",
    )

    html = AIExecutiveReportService().build_html(
        brief=brief,
        narrative=narrative,
        company="Test Company",
        currency="USD",
    )

    assert "What Happened" in html
    assert "Why It Happened" in html
    assert "If No Action Is Taken" in html
    assert "Review pricing" in html
    assert "95%" in html
