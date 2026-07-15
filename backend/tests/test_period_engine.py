import pandas as pd

from engines.period_engine import PeriodEngine
from models.period import PeriodSelection


def _dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "year": [2026] * 12,
            "month_num": list(range(1, 13)),
            "actual_revenue": [100.0] * 12,
        }
    )


def test_quarter_filter() -> None:
    result = PeriodEngine().filter(
        _dataframe(),
        PeriodSelection(
            year=2026,
            view="Quarter",
            quarter=2,
        ),
    )
    assert result["month_num"].tolist() == [4, 5, 6]


def test_ytd_filter() -> None:
    result = PeriodEngine().filter(
        _dataframe(),
        PeriodSelection(
            year=2026,
            view="YTD",
            month=7,
        ),
    )
    assert len(result) == 7


def test_semester_filter() -> None:
    result = PeriodEngine().filter(
        _dataframe(),
        PeriodSelection(
            year=2026,
            view="Semester",
            semester=2,
        ),
    )
    assert result["month_num"].tolist() == [7, 8, 9, 10, 11, 12]
