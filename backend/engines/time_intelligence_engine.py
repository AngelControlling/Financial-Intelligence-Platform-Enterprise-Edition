
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass(frozen=True)
class TimePreparationResult:
    dataframe: pd.DataFrame
    parsed_count: int
    unparsed_count: int


class TimeIntelligenceEngine:
    """Normalizes heterogeneous date values into month/year filters."""

    MONTH_ALIASES = {
        "ene": 1, "enero": 1, "jan": 1, "january": 1,
        "feb": 2, "febrero": 2, "february": 2,
        "mar": 3, "marzo": 3, "march": 3,
        "abr": 4, "abril": 4, "apr": 4, "april": 4,
        "may": 5, "mayo": 5,
        "jun": 6, "junio": 6, "june": 6,
        "jul": 7, "julio": 7, "july": 7,
        "ago": 8, "agosto": 8, "aug": 8, "august": 8,
        "sep": 9, "sept": 9, "septiembre": 9,
        "setiembre": 9, "september": 9,
        "oct": 10, "octubre": 10, "october": 10,
        "nov": 11, "noviembre": 11, "november": 11,
        "dic": 12, "diciembre": 12, "dec": 12, "december": 12,
    }

    SPANISH_MONTHS = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    def prepare_periods(
        self,
        dataframe: pd.DataFrame,
        period_column: str = "period",
        year_column: str = "year",
    ) -> TimePreparationResult:
        if period_column not in dataframe.columns:
            raise ValueError(
                f"La columna canónica '{period_column}' no existe."
            )

        df = dataframe.copy()

        parsed_values = df.apply(
            lambda row: self._parse_period_value(
                row.get(period_column),
                row.get(year_column)
                if year_column in df.columns
                else None,
            ),
            axis=1,
        )

        df["_period_date"] = pd.to_datetime(
            parsed_values,
            errors="coerce",
        )

        df["_period_year"] = df["_period_date"].dt.year
        df["_period_month"] = df["_period_date"].dt.month

        df["_period_month_key"] = (
            df["_period_year"]
            .astype("Int64")
            .astype(str)
            + "-"
            + df["_period_month"]
            .astype("Int64")
            .astype(str)
            .str.zfill(2)
        )

        df.loc[
            df["_period_date"].isna(),
            "_period_month_key",
        ] = pd.NA

        return TimePreparationResult(
            dataframe=df,
            parsed_count=int(
                df["_period_date"].notna().sum()
            ),
            unparsed_count=int(
                df["_period_date"].isna().sum()
            ),
        )

    def available_months(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        return sorted(
            dataframe["_period_month_key"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    def available_years(
        self,
        dataframe: pd.DataFrame,
    ) -> list[int]:
        return sorted(
            dataframe["_period_year"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

    def filter_month(
        self,
        dataframe: pd.DataFrame,
        month_key: str,
    ) -> pd.DataFrame:
        return dataframe[
            dataframe["_period_month_key"] == month_key
        ].copy()

    def filter_year(
        self,
        dataframe: pd.DataFrame,
        year: int,
    ) -> pd.DataFrame:
        return dataframe[
            dataframe["_period_year"] == int(year)
        ].copy()

    def month_label(self, month_key: str) -> str:
        try:
            year_text, month_text = str(month_key).split("-")
            month_name = self.SPANISH_MONTHS[
                int(month_text)
            ]
            return f"{month_name} {year_text}"
        except Exception:
            return str(month_key)

    def _parse_period_value(
        self,
        period_value,
        year_value=None,
    ):
        if period_value is None or pd.isna(period_value):
            return pd.NaT

        if isinstance(
            period_value,
            (
                pd.Timestamp,
                datetime,
            ),
        ):
            return pd.Timestamp(period_value)

        text = self._normalize_text(
            str(period_value)
        )

        if not text:
            return pd.NaT

        # Excel serial date.
        if re.fullmatch(r"\d{5}", text):
            try:
                serial_value = int(text)
                return (
                    pd.Timestamp("1899-12-30")
                    + pd.to_timedelta(
                        serial_value,
                        unit="D",
                    )
                )
            except Exception:
                pass

        # Numeric formats:
        # 01-01-2025, 01/01/2025, 2025-01-01.
        numeric_date = pd.to_datetime(
            text,
            errors="coerce",
            dayfirst=True,
        )

        if pd.notna(numeric_date):
            return numeric_date

        tokens = [
            token
            for token in re.split(
                r"[\s/_\-]+",
                text,
            )
            if token
        ]

        month_number = None
        year_number = self._extract_year(
            year_value
        )
        day_number = 1

        for token in tokens:
            if token in self.MONTH_ALIASES:
                month_number = self.MONTH_ALIASES[
                    token
                ]
                break

        numeric_tokens = [
            int(token)
            for token in tokens
            if token.isdigit()
        ]

        explicit_years = [
            value
            for value in numeric_tokens
            if 1900 <= value <= 2100
        ]

        if explicit_years:
            year_number = explicit_years[0]

        other_numbers = [
            value
            for value in numeric_tokens
            if value not in explicit_years
        ]

        if month_number is not None:
            valid_days = [
                value
                for value in other_numbers
                if 1 <= value <= 31
            ]

            if valid_days:
                day_number = valid_days[0]

            if year_number is None:
                return pd.NaT

            try:
                return pd.Timestamp(
                    year=year_number,
                    month=month_number,
                    day=day_number,
                )
            except ValueError:
                return pd.NaT

        # Month number in one column + separate year column.
        if (
            len(numeric_tokens) == 1
            and 1 <= numeric_tokens[0] <= 12
            and year_number is not None
        ):
            return pd.Timestamp(
                year=year_number,
                month=numeric_tokens[0],
                day=1,
            )

        return pd.NaT

    @staticmethod
    def _extract_year(value):
        if value is None or pd.isna(value):
            return None

        match = re.search(
            r"(19|20)\d{2}",
            str(value),
        )

        if match:
            return int(match.group())

        return None

    @staticmethod
    def _normalize_text(value: str) -> str:
        text = value.strip().lower()

        replacements = {
            "ã±": "ñ",
            "ã¡": "á",
            "ã©": "é",
            "ã­": "í",
            "ã³": "ó",
            "ãº": "ú",
            "â": "",
        }

        for bad, good in replacements.items():
            text = text.replace(
                bad,
                good,
            )

        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        return "".join(
            character
            for character in text
            if not unicodedata.combining(
                character
            )
        )
