
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

import pandas as pd


class UniversalDateParserEngine:
    """
    Parses heterogeneous ERP, Excel, CSV and manually entered date values.

    Supported examples include:
    - 2026-01-01
    - 2026/01/01
    - 2026.01.01
    - 01-01-2026
    - 01/01/2026
    - 01.01.2026
    - 2026-ene-01
    - 2026-01-ene
    - 01-ene-2026
    - ene-01-2026
    - 20260101
    - 01 ene 2026
    - enero 01 2026
    - Excel serial dates
    - pandas.Timestamp / datetime / date
    """

    MONTH_ALIASES: dict[str, int] = {
        "jan": 1,
        "january": 1,
        "ene": 1,
        "enero": 1,
        "feb": 2,
        "february": 2,
        "febrero": 2,
        "mar": 3,
        "march": 3,
        "marzo": 3,
        "apr": 4,
        "april": 4,
        "abr": 4,
        "abril": 4,
        "may": 5,
        "mayo": 5,
        "jun": 6,
        "june": 6,
        "junio": 6,
        "jul": 7,
        "july": 7,
        "julio": 7,
        "aug": 8,
        "august": 8,
        "ago": 8,
        "agosto": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "septiembre": 9,
        "setiembre": 9,
        "oct": 10,
        "october": 10,
        "octubre": 10,
        "nov": 11,
        "november": 11,
        "noviembre": 11,
        "dec": 12,
        "december": 12,
        "dic": 12,
        "diciembre": 12,
    }

    EXCEL_EPOCH = pd.Timestamp("1899-12-30")

    def parse_value(
        self,
        value: Any,
    ) -> pd.Timestamp:
        """Parse one value into pandas.Timestamp or return NaT."""

        if value is None:
            return pd.NaT

        try:
            if pd.isna(value):
                return pd.NaT
        except Exception:
            pass

        if isinstance(
            value,
            (
                pd.Timestamp,
                datetime,
                date,
            ),
        ):
            return pd.Timestamp(value)

        if isinstance(value, (int, float)):
            return self._parse_numeric_value(value)

        text = self._normalize_text(str(value))

        if not text:
            return pd.NaT

        if self._looks_like_excel_serial(text):
            parsed_serial = self._parse_excel_serial(text)

            if pd.notna(parsed_serial):
                return parsed_serial

        compact_numeric = re.fullmatch(r"\d{8}", text)

        if compact_numeric:
            parsed_compact = self._parse_compact_numeric(text)

            if pd.notna(parsed_compact):
                return parsed_compact

        parsed_named_month = self._parse_named_month_date(text)

        if pd.notna(parsed_named_month):
            return parsed_named_month

        parsed_iso = self._parse_known_numeric_formats(text)

        if pd.notna(parsed_iso):
            return parsed_iso

        return self._safe_pandas_parse(text)

    def parse_series(
        self,
        series: pd.Series,
    ) -> pd.Series:
        """Parse a pandas Series while preserving its original index."""

        return series.map(self.parse_value)

    def parse_dataframe_columns(
        self,
        dataframe: pd.DataFrame,
        columns: list[str] | set[str] | tuple[str, ...],
    ) -> pd.DataFrame:
        """Parse selected dataframe columns if they exist."""

        df = dataframe.copy()

        for column in columns:
            if column in df.columns:
                df[column] = self.parse_series(
                    df[column]
                )

        return df

    def invalid_count(
        self,
        series: pd.Series,
    ) -> int:
        """Count values that cannot be interpreted as dates."""

        parsed = self.parse_series(series)

        return int(parsed.isna().sum())

    def _parse_numeric_value(
        self,
        value: int | float,
    ) -> pd.Timestamp:
        if isinstance(value, float) and value.is_integer():
            value = int(value)

        if isinstance(value, int):
            text = str(value)

            if len(text) == 8:
                parsed_compact = self._parse_compact_numeric(text)

                if pd.notna(parsed_compact):
                    return parsed_compact

            if 20000 <= value <= 80000:
                return self.EXCEL_EPOCH + pd.to_timedelta(
                    value,
                    unit="D",
                )

        return pd.NaT

    def _parse_compact_numeric(
        self,
        text: str,
    ) -> pd.Timestamp:
        candidates = []

        if 1900 <= int(text[:4]) <= 2100:
            candidates.append(
                (
                    int(text[:4]),
                    int(text[4:6]),
                    int(text[6:8]),
                )
            )

        if 1900 <= int(text[4:8]) <= 2100:
            candidates.append(
                (
                    int(text[4:8]),
                    int(text[2:4]),
                    int(text[:2]),
                )
            )

        for year, month, day in candidates:
            try:
                return pd.Timestamp(
                    year=year,
                    month=month,
                    day=day,
                )
            except ValueError:
                continue

        return pd.NaT

    def _parse_named_month_date(
        self,
        text: str,
    ) -> pd.Timestamp:
        tokens = [
            token
            for token in re.split(
                r"[\s/_\-.]+",
                text,
            )
            if token
        ]

        if len(tokens) < 2:
            return pd.NaT

        year = None
        month = None
        numeric_tokens: list[int] = []

        for token in tokens:
            if token in self.MONTH_ALIASES:
                month = self.MONTH_ALIASES[token]
                continue

            if token.isdigit():
                numeric_tokens.append(int(token))

                if len(token) == 4 and 1900 <= int(token) <= 2100:
                    year = int(token)

        if month is None:
            return pd.NaT

        if year is None:
            possible_years = [
                number
                for number in numeric_tokens
                if 1900 <= number <= 2100
            ]

            if possible_years:
                year = possible_years[0]

        if year is None:
            return pd.NaT

        day_candidates = [
            number
            for number in numeric_tokens
            if number != year and 1 <= number <= 31
        ]

        day = 1

        if day_candidates:
            day = day_candidates[0]

        try:
            return pd.Timestamp(
                year=year,
                month=month,
                day=day,
            )
        except ValueError:
            return pd.NaT

    def _parse_known_numeric_formats(
        self,
        text: str,
    ) -> pd.Timestamp:
        normalized = re.sub(
            r"[/.]",
            "-",
            text,
        )

        patterns = [
            (
                r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$",
                ("year", "month", "day"),
            ),
            (
                r"^(?P<day>\d{1,2})-(?P<month>\d{1,2})-(?P<year>\d{4})$",
                ("year", "month", "day"),
            ),
        ]

        for pattern, _ in patterns:
            match = re.fullmatch(pattern, normalized)

            if not match:
                continue

            try:
                return pd.Timestamp(
                    year=int(match.group("year")),
                    month=int(match.group("month")),
                    day=int(match.group("day")),
                )
            except ValueError:
                return pd.NaT

        return pd.NaT

    def _safe_pandas_parse(
        self,
        text: str,
    ) -> pd.Timestamp:
        for dayfirst in (False, True):
            try:
                parsed = pd.to_datetime(
                    text,
                    errors="coerce",
                    dayfirst=dayfirst,
                )

                if pd.notna(parsed):
                    return pd.Timestamp(parsed)
            except Exception:
                continue

        return pd.NaT

    def _parse_excel_serial(
        self,
        text: str,
    ) -> pd.Timestamp:
        try:
            serial = float(text)

            if 20000 <= serial <= 80000:
                return self.EXCEL_EPOCH + pd.to_timedelta(
                    serial,
                    unit="D",
                )
        except Exception:
            pass

        return pd.NaT

    @staticmethod
    def _looks_like_excel_serial(
        text: str,
    ) -> bool:
        return bool(
            re.fullmatch(
                r"\d{5}(?:\.0+)?",
                text,
            )
        )

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        text = value.strip().lower()

        replacements = {
            "ã±": "ñ",
            "ã¡": "á",
            "ã©": "é",
            "ã­": "í",
            "ã³": "ó",
            "ãº": "ú",
            "â": "",
            ",": " ",
        }

        for bad_text, correct_text in replacements.items():
            text = text.replace(
                bad_text,
                correct_text,
            )

        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        text = "".join(
            character
            for character in text
            if not unicodedata.combining(
                character
            )
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text
