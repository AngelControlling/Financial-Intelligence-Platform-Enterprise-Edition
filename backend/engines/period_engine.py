from __future__ import annotations

import pandas as pd

from models.period import PeriodSelection


class PeriodEngine:
    """Aligns Actuals and Budget to one financial reporting period."""

    VIEWS = (
        "Month",
        "Quarter",
        "Semester",
        "YTD",
        "Full Year",
    )

    def prepare_time_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        df = dataframe.copy()

        if "year" not in df.columns:
            if "period" in df.columns:
                parsed = pd.to_datetime(
                    df["period"],
                    errors="coerce",
                )
                df["year"] = parsed.dt.year
                df["month_num"] = parsed.dt.month
            elif "Fiscal_Year" in df.columns:
                df["year"] = pd.to_numeric(
                    df["Fiscal_Year"],
                    errors="coerce",
                )

        if "month_num" not in df.columns:
            if "period" in df.columns:
                parsed = pd.to_datetime(
                    df["period"],
                    errors="coerce",
                )
                df["month_num"] = parsed.dt.month
            elif "Month" in df.columns:
                df["month_num"] = pd.to_numeric(
                    df["Month"],
                    errors="coerce",
                )

        return df

    def available_years(
        self,
        dataframe: pd.DataFrame,
    ) -> list[int]:
        df = self.prepare_time_columns(dataframe)
        if "year" not in df.columns:
            return []

        years = (
            pd.to_numeric(
                df["year"],
                errors="coerce",
            )
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )
        return sorted(years)

    def latest_month(
        self,
        dataframe: pd.DataFrame,
        year: int,
    ) -> int:
        df = self.prepare_time_columns(dataframe)

        subset = df[
            pd.to_numeric(
                df["year"],
                errors="coerce",
            )
            == year
        ]

        months = (
            pd.to_numeric(
                subset.get(
                    "month_num",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            .dropna()
            .astype(int)
        )

        return int(months.max()) if not months.empty else 12

    def filter(
        self,
        dataframe: pd.DataFrame,
        selection: PeriodSelection,
    ) -> pd.DataFrame:
        df = self.prepare_time_columns(dataframe)

        year_mask = (
            pd.to_numeric(
                df["year"],
                errors="coerce",
            )
            == selection.year
        )

        month = pd.to_numeric(
            df["month_num"],
            errors="coerce",
        )

        if selection.view == "Month":
            period_mask = month == selection.month
        elif selection.view == "Quarter":
            start = (selection.quarter - 1) * 3 + 1
            period_mask = month.between(start, start + 2)
        elif selection.view == "Semester":
            start = 1 if selection.semester == 1 else 7
            period_mask = month.between(start, start + 5)
        elif selection.view == "YTD":
            period_mask = month.between(1, selection.month)
        else:
            period_mask = month.between(1, 12)

        return df.loc[
            year_mask & period_mask
        ].copy()

    def context_label(
        self,
        selection: PeriodSelection,
    ) -> str:
        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        if selection.view == "Month":
            return (
                f"{month_names[selection.month]} "
                f"{selection.year}"
            )

        if selection.view == "Quarter":
            return (
                f"Q{selection.quarter} "
                f"{selection.year}"
            )

        if selection.view == "Semester":
            return (
                f"Semester {selection.semester} "
                f"{selection.year}"
            )

        if selection.view == "YTD":
            return (
                f"YTD through "
                f"{month_names[selection.month]} "
                f"{selection.year}"
            )

        return f"Full Year {selection.year}"
