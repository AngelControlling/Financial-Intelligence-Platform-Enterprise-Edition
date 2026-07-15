from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


class ExcelReader:
    """Reads Excel and CSV files uploaded through Streamlit."""

    EXCEL_EXTENSIONS = {".xlsx", ".xlsm"}
    CSV_EXTENSIONS = {".csv"}

    def __init__(self, uploaded_file) -> None:
        self.file_name = uploaded_file.name
        self.extension = Path(self.file_name).suffix.lower()
        self.file_bytes = uploaded_file.getvalue()

        supported = self.EXCEL_EXTENSIONS | self.CSV_EXTENSIONS
        if self.extension not in supported:
            raise ValueError(
                f"Formato no soportado: {self.extension}. "
                "Usa archivos XLSX, XLSM o CSV."
            )

    def get_sheet_names(self) -> list[str]:
        """Returns Excel sheet names or a virtual name for CSV files."""
        if self.extension in self.CSV_EXTENSIONS:
            return ["CSV_Data"]

        excel_file = pd.ExcelFile(
            BytesIO(self.file_bytes),
            engine="openpyxl",
        )
        return excel_file.sheet_names

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Reads one sheet into a pandas DataFrame."""
        if self.extension in self.CSV_EXTENSIONS:
            return self._read_csv()

        return pd.read_excel(
            BytesIO(self.file_bytes),
            sheet_name=sheet_name,
            engine="openpyxl",
        )

    def read_all_sheets(self) -> dict[str, pd.DataFrame]:
        """Reads every available sheet."""
        return {
            sheet_name: self.read_sheet(sheet_name)
            for sheet_name in self.get_sheet_names()
        }

    def _read_csv(self) -> pd.DataFrame:
        """Reads CSV with separator and encoding fallbacks."""
        encodings = ("utf-8-sig", "utf-8", "latin-1")

        for encoding in encodings:
            try:
                return pd.read_csv(
                    BytesIO(self.file_bytes),
                    encoding=encoding,
                    sep=None,
                    engine="python",
                )
            except UnicodeDecodeError:
                continue

        raise ValueError("No fue posible identificar la codificación del CSV.")