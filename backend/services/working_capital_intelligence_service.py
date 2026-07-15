from __future__ import annotations

import pandas as pd

from repositories.data_lake_repository import DataLakeRepository


class WorkingCapitalIntelligenceService:
    """Load active Working Capital and full-scope Actuals from the Data Lake."""

    def __init__(
        self,
        repository: DataLakeRepository | None = None,
    ) -> None:
        self.repository = repository or DataLakeRepository()

    def load_active(self) -> pd.DataFrame | None:
        version = self.repository.active_version("working_capital")
        dataframe = self.repository.load_active_dataframe("working_capital")
        if version is None or dataframe is None:
            return None
        return dataframe.copy()

    def load_active_actuals(self) -> pd.DataFrame | None:
        version = self.repository.active_version("actuals")
        dataframe = self.repository.load_active_dataframe("actuals")
        if version is None or dataframe is None:
            return None
        return dataframe.copy()
