from pathlib import Path

from services.budget_ingestion_service import (
    BudgetIngestionService,
)
from services.smart_excel_reader import (
    SmartExcelReader,
)


def test_formatted_budget_template_is_detected() -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = (
        project_root
        / "backend"
        / "assets"
        / "templates"
        / "FIP_Budget_Template_v1.xlsx"
    )

    reader = SmartExcelReader(template)

    pnl = reader.read_sheet("Budget_PnL")
    operations = reader.read_sheet(
        "Budget_Operations"
    )

    assert "Fiscal_Year" in pnl.columns
    assert "Budget_Revenue" in pnl.columns
    assert "Budget_Shipments" in operations.columns

    result = BudgetIngestionService().validate(
        {
            "Budget_PnL": pnl,
            "Budget_Operations": operations,
            "Budget_OPEX": reader.read_sheet(
                "Budget_OPEX"
            ),
            "Budget_Personnel": reader.read_sheet(
                "Budget_Personnel"
            ),
            "Budget_BalanceSheet": reader.read_sheet(
                "Budget_BalanceSheet"
            ),
        }
    )

    assert result.valid
    assert len(result.performance) > 0
