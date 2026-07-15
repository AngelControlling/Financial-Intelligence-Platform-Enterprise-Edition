from __future__ import annotations

import pandas as pd


class DataProfiler:
    """Creates quality and structure metrics for a DataFrame."""

    FINANCIAL_KEYWORDS = {
        "revenue",
        "sales",
        "cost",
        "expense",
        "budget",
        "forecast",
        "actual",
        "account",
        "gl",
        "amount",
        "ebitda",
        "gross profit",
        "gp",
        "margin",
    }

    FREIGHT_KEYWORDS = {
        "shipment",
        "awb",
        "mawb",
        "hawb",
        "container",
        "teu",
        "weight",
        "kg",
        "origin",
        "destination",
        "carrier",
        "trade lane",
        "fcl",
        "lcl",
    }

    def profile(self, dataframe: pd.DataFrame) -> dict:
        row_count = len(dataframe)
        column_count = len(dataframe.columns)
        total_cells = row_count * column_count

        missing_cells = int(dataframe.isna().sum().sum())
        duplicate_rows = int(dataframe.duplicated().sum())

        missing_percentage = (
            round((missing_cells / total_cells) * 100, 2)
            if total_cells
            else 0.0
        )

        numeric_columns = list(
            dataframe.select_dtypes(include="number").columns
        )
        date_columns = self._detect_date_columns(dataframe)
        text_columns = [
            column
            for column in dataframe.columns
            if column not in numeric_columns and column not in date_columns
        ]

        return {
            "rows": row_count,
            "columns": column_count,
            "missing_cells": missing_cells,
            "missing_percentage": missing_percentage,
            "duplicate_rows": duplicate_rows,
            "numeric_columns": numeric_columns,
            "date_columns": date_columns,
            "text_columns": text_columns,
            "detected_type": self.detect_dataset_type(dataframe),
        }

    def detect_dataset_type(self, dataframe: pd.DataFrame) -> str:
        normalized_columns = {
            str(column).strip().lower().replace("_", " ")
            for column in dataframe.columns
        }

        financial_matches = self._count_keyword_matches(
            normalized_columns,
            self.FINANCIAL_KEYWORDS,
        )
        freight_matches = self._count_keyword_matches(
            normalized_columns,
            self.FREIGHT_KEYWORDS,
        )

        if financial_matches >= 2 and freight_matches >= 2:
            return "Financial + Freight Operational Data"

        if freight_matches >= 2:
            return "Freight Operational Data"

        if financial_matches >= 2:
            return "Financial Data"

        return "Unclassified Data"

    @staticmethod
    def _count_keyword_matches(
        columns: set[str],
        keywords: set[str],
    ) -> int:
        return sum(
            1
            for keyword in keywords
            if any(keyword in column for column in columns)
        )

    @staticmethod
    def _detect_date_columns(dataframe: pd.DataFrame) -> list[str]:
        date_columns: list[str] = []

        for column in dataframe.columns:
            if pd.api.types.is_datetime64_any_dtype(dataframe[column]):
                date_columns.append(column)
                continue

            column_name = str(column).lower()
            if any(
                keyword in column_name
                for keyword in ("date", "fecha", "period", "month", "year")
            ):
                date_columns.append(column)

        return date_columns