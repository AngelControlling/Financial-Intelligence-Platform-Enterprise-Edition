from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterable

import pandas as pd


class SmartExcelReader:
    """
    Enterprise Excel reader with automatic header-row detection.

    It supports formatted workbooks containing titles, logos, blank
    rows or instructions above the real tabular header.
    """

    DEFAULT_HEADER_HINTS = {
        "Budget_PnL": {
            "Fiscal_Year",
            "Month",
            "Country",
            "Mode",
            "Product",
            "Budget_Revenue",
            "Budget_Cost",
        },
        "Budget_Operations": {
            "Fiscal_Year",
            "Month",
            "Country",
            "Mode",
            "Product",
            "Budget_Shipments",
            "Budget_TEUs",
            "Budget_Tons",
        },
        "Budget_OPEX": {
            "Fiscal_Year",
            "Month",
            "Country",
            "Department",
            "Total_OPEX",
        },
        "Budget_Personnel": {
            "Fiscal_Year",
            "Month",
            "Country",
            "Department",
            "Budget_HC",
            "Personnel_Expense",
        },
        "Budget_BalanceSheet": {
            "Fiscal_Year",
            "Month",
            "Country",
            "Budget_AR",
            "Budget_AP",
        },
    }

    def __init__(
        self,
        source: BinaryIO | bytes | str | Path,
    ) -> None:
        self._bytes = self._read_bytes(source)

    @staticmethod
    def _read_bytes(
        source: BinaryIO | bytes | str | Path,
    ) -> bytes:
        if isinstance(source, bytes):
            return source

        if isinstance(source, (str, Path)):
            return Path(source).read_bytes()

        if hasattr(source, "getvalue"):
            return bytes(source.getvalue())

        position = None
        if hasattr(source, "tell"):
            try:
                position = source.tell()
            except Exception:
                position = None

        if hasattr(source, "seek"):
            source.seek(0)

        payload = source.read()

        if position is not None and hasattr(source, "seek"):
            source.seek(position)

        return bytes(payload)

    def get_sheet_names(self) -> list[str]:
        with pd.ExcelFile(BytesIO(self._bytes)) as excel:
            return list(excel.sheet_names)

    @staticmethod
    def _normalize(value: object) -> str:
        if pd.isna(value):
            return ""

        return (
            str(value)
            .strip()
            .replace("\n", " ")
            .replace("\r", " ")
        )

    def detect_header_row(
        self,
        sheet_name: str,
        *,
        required_headers: Iterable[str] | None = None,
        scan_rows: int = 30,
    ) -> int:
        preview = pd.read_excel(
            BytesIO(self._bytes),
            sheet_name=sheet_name,
            header=None,
            nrows=scan_rows,
            dtype=object,
        )

        hints = set(
            required_headers
            or self.DEFAULT_HEADER_HINTS.get(
                sheet_name,
                set(),
            )
        )
        hints_folded = {
            item.casefold()
            for item in hints
        }

        best_row = 0
        best_score = float("-inf")

        for row_index, row in preview.iterrows():
            cells = [
                self._normalize(value)
                for value in row.tolist()
            ]
            non_empty = [
                value
                for value in cells
                if value
            ]
            folded = {
                value.casefold()
                for value in non_empty
            }

            hint_matches = len(
                folded & hints_folded
            )

            identifier_like = sum(
                1
                for value in non_empty
                if (
                    "_" in value
                    or value.casefold()
                    in {
                        "month",
                        "country",
                        "mode",
                        "product",
                        "currency",
                        "department",
                    }
                )
            )

            duplicate_penalty = (
                len(non_empty)
                - len(set(non_empty))
            )

            score = (
                hint_matches * 100
                + identifier_like * 5
                + len(non_empty)
                - duplicate_penalty * 3
            )

            if score > best_score:
                best_score = score
                best_row = int(row_index)

        return best_row

    def read_sheet(
        self,
        sheet_name: str,
        *,
        required_headers: Iterable[str] | None = None,
    ) -> pd.DataFrame:
        header_row = self.detect_header_row(
            sheet_name,
            required_headers=required_headers,
        )

        dataframe = pd.read_excel(
            BytesIO(self._bytes),
            sheet_name=sheet_name,
            header=header_row,
            dtype=object,
        )

        dataframe.columns = [
            self._normalize(column)
            for column in dataframe.columns
        ]

        valid_columns = [
            column
            for column in dataframe.columns
            if (
                column
                and not column.casefold().startswith(
                    "unnamed:"
                )
            )
        ]

        dataframe = dataframe.loc[
            :,
            valid_columns,
        ]
        dataframe = dataframe.dropna(
            how="all",
        )
        dataframe = dataframe.reset_index(
            drop=True,
        )

        return dataframe
