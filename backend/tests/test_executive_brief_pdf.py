from models.executive_brief import (
    ExecutiveBrief,
)
from services.executive_brief_pdf_service import (
    ExecutiveBriefPDFService,
)


def test_pdf_is_generated() -> None:
    brief = ExecutiveBrief(
        title="Executive Financial Brief",
        period_label="YTD 2026",
        comparison_label="Budget",
        headline="Revenue is ahead of target.",
        financial_summary=(
            "Revenue and Gross Profit summary."
        ),
        operational_summary=(
            "Shipment and volume summary."
        ),
        risks=["Margin compression."],
        opportunities=["Ocean growth."],
        actions=["Review pricing - Controller - Open"],
        kpis={
            "Revenue": 1000000.0,
            "Revenue Variance %": 0.05,
            "Gross Profit": 250000.0,
            "GP Variance %": -0.02,
            "GP Margin": 0.25,
            "Margin Variance pp": -0.01,
            "Shipments": 100,
            "TEUs": 50,
        },
    )

    payload = (
        ExecutiveBriefPDFService()
        .build(
            brief,
            company="Test Company",
            currency="USD",
        )
    )

    assert payload.startswith(b"%PDF")
    assert len(payload) > 1000
