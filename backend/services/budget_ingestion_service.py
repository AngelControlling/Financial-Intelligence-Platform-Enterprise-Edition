from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from models.budget import BudgetValidationResult
from models.data_lake import DatasetVersion
from repositories.data_lake_repository import DataLakeRepository


class BudgetIngestionService:
    """Validates, versions and activates the official FIP Budget Standard."""

    REQUIRED_SHEETS = {
        "Budget_PnL",
        "Budget_Operations",
    }

    PNL_REQUIRED = {
        "Fiscal_Year",
        "Month",
        "Country",
        "Mode",
        "Product",
        "Budget_Revenue",
        "Budget_Cost",
    }

    OPS_REQUIRED = {
        "Fiscal_Year",
        "Month",
        "Country",
        "Mode",
        "Product",
        "Budget_Shipments",
        "Budget_TEUs",
        "Budget_Tons",
    }

    MONTH_MAP = {
        "jan": 1, "january": 1, "ene": 1, "enero": 1,
        "feb": 2, "february": 2, "febrero": 2,
        "mar": 3, "march": 3, "marzo": 3,
        "apr": 4, "april": 4, "abr": 4, "abril": 4,
        "may": 5, "mayo": 5,
        "jun": 6, "june": 6, "junio": 6,
        "jul": 7, "july": 7, "julio": 7,
        "aug": 8, "august": 8, "ago": 8, "agosto": 8,
        "sep": 9, "sept": 9, "september": 9, "septiembre": 9,
        "oct": 10, "october": 10, "octubre": 10,
        "nov": 11, "november": 11, "noviembre": 11,
        "dec": 12, "december": 12, "dic": 12, "diciembre": 12,
    }

    def __init__(
        self,
        repository: DataLakeRepository | None = None,
    ) -> None:
        self.repository = repository or DataLakeRepository()

    @staticmethod
    def _clean_table(dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        df = df.dropna(how="all")
        df.columns = [
            str(column).strip()
            for column in df.columns
            if str(column).strip()
            and not str(column).strip().casefold().startswith(
                "unnamed:"
            )
        ]
        return df.reset_index(drop=True)

    @staticmethod
    def _drop_unused_template_rows(
        dataframe: pd.DataFrame,
        key_columns: list[str],
    ) -> pd.DataFrame:
        """
        Remove unused formatted template rows.

        Formula columns may contain cached zeros even when the business-input
        columns are blank, so dropna(how="all") alone is not sufficient.
        """

        df = dataframe.copy()
        available_keys = [
            column
            for column in key_columns
            if column in df.columns
        ]

        if not available_keys:
            return df

        normalized = pd.DataFrame(
            {
                column: (
                    df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
                for column in available_keys
            }
        )

        used_mask = normalized.ne("").any(axis=1)

        return (
            df.loc[used_mask]
            .reset_index(drop=True)
        )

    def _month_number(self, value: Any) -> int | None:
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            month = int(value)
            return month if 1 <= month <= 12 else None

        token = str(value).strip().casefold()
        if token.isdigit():
            month = int(token)
            return month if 1 <= month <= 12 else None

        return self.MONTH_MAP.get(token)

    def validate(
        self,
        sheets: dict[str, pd.DataFrame],
    ) -> BudgetValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        missing_sheets = sorted(
            self.REQUIRED_SHEETS
            - set(sheets)
        )
        if missing_sheets:
            errors.append(
                "Missing required sheets: "
                + ", ".join(missing_sheets)
            )

        pnl = self._clean_table(
            sheets.get(
                "Budget_PnL",
                pd.DataFrame(),
            )
        )
        operations = self._clean_table(
            sheets.get(
                "Budget_Operations",
                pd.DataFrame(),
            )
        )
        opex = self._clean_table(
            sheets.get(
                "Budget_OPEX",
                pd.DataFrame(),
            )
        )
        personnel = self._clean_table(
            sheets.get(
                "Budget_Personnel",
                pd.DataFrame(),
            )
        )
        balance_sheet = self._clean_table(
            sheets.get(
                "Budget_BalanceSheet",
                pd.DataFrame(),
            )
        )

        pnl = self._drop_unused_template_rows(
            pnl,
            [
                "Fiscal_Year",
                "Month",
                "Country",
                "Mode",
                "Product",
            ],
        )
        operations = self._drop_unused_template_rows(
            operations,
            [
                "Fiscal_Year",
                "Month",
                "Country",
                "Mode",
                "Product",
            ],
        )
        opex = self._drop_unused_template_rows(
            opex,
            [
                "Fiscal_Year",
                "Month",
                "Country",
                "Department",
            ],
        )
        personnel = self._drop_unused_template_rows(
            personnel,
            [
                "Fiscal_Year",
                "Month",
                "Country",
                "Department",
            ],
        )
        balance_sheet = self._drop_unused_template_rows(
            balance_sheet,
            [
                "Fiscal_Year",
                "Month",
                "Country",
            ],
        )

        pnl_missing = sorted(
            self.PNL_REQUIRED
            - set(pnl.columns)
        )
        ops_missing = sorted(
            self.OPS_REQUIRED
            - set(operations.columns)
        )

        if pnl_missing:
            errors.append(
                "Budget_PnL missing columns: "
                + ", ".join(pnl_missing)
            )
        if ops_missing:
            errors.append(
                "Budget_Operations missing columns: "
                + ", ".join(ops_missing)
            )

        if errors:
            return BudgetValidationResult(
                performance=pd.DataFrame(),
                opex=opex,
                personnel=personnel,
                balance_sheet=balance_sheet,
                errors=errors,
                warnings=warnings,
            )

        for frame, name in [
            (pnl, "Budget_PnL"),
            (operations, "Budget_Operations"),
        ]:
            frame["month_num"] = frame["Month"].map(
                self._month_number
            )
            invalid_months = int(
                frame["month_num"].isna().sum()
            )
            if invalid_months:
                errors.append(
                    f"{name}: {invalid_months} records "
                    "contain an invalid Month."
                )

            frame["Fiscal_Year"] = pd.to_numeric(
                frame["Fiscal_Year"],
                errors="coerce",
            )

        numeric_pnl = [
            "Budget_Revenue",
            "Budget_Cost",
        ]
        for column in numeric_pnl:
            pnl[column] = pd.to_numeric(
                pnl[column],
                errors="coerce",
            )

        for column in [
            "Budget_Shipments",
            "Budget_TEUs",
            "Budget_Tons",
        ]:
            operations[column] = pd.to_numeric(
                operations[column],
                errors="coerce",
            ).fillna(0.0)

        invalid_financial = int(
            pnl[numeric_pnl].isna().any(axis=1).sum()
        )
        if invalid_financial:
            errors.append(
                f"Budget_PnL: {invalid_financial} records "
                "contain invalid Revenue or Cost."
            )

        negative_count = int(
            (
                (pnl["Budget_Revenue"] < 0)
                | (pnl["Budget_Cost"] < 0)
            ).sum()
        )
        if negative_count:
            warnings.append(
                f"{negative_count} P&L records contain negative values."
            )

        pnl["budget_revenue"] = pnl["Budget_Revenue"]
        pnl["budget_cost"] = pnl["Budget_Cost"]
        pnl["budget_gp"] = (
            pnl["budget_revenue"]
            - pnl["budget_cost"]
        )
        pnl["budget_gp_margin"] = (
            pnl["budget_gp"]
            / pnl["budget_revenue"].replace(0, pd.NA)
        ).fillna(0.0)

        keys = [
            "Fiscal_Year",
            "month_num",
            "Country",
            "Mode",
            "Product",
        ]
        optional_keys = [
            "Business_Unit",
            "Trade_Lane",
            "Budget_Version",
            "Currency",
        ]
        keys += [
            column
            for column in optional_keys
            if column in pnl.columns
            and column in operations.columns
        ]

        pnl_agg = (
            pnl.groupby(
                keys,
                dropna=False,
            )
            .agg(
                budget_revenue=(
                    "budget_revenue",
                    "sum",
                ),
                budget_cost=(
                    "budget_cost",
                    "sum",
                ),
                budget_gp=(
                    "budget_gp",
                    "sum",
                ),
            )
            .reset_index()
        )

        ops_agg = (
            operations.groupby(
                keys,
                dropna=False,
            )
            .agg(
                budget_shipments=(
                    "Budget_Shipments",
                    "sum",
                ),
                budget_teus=(
                    "Budget_TEUs",
                    "sum",
                ),
                budget_tons=(
                    "Budget_Tons",
                    "sum",
                ),
            )
            .reset_index()
        )

        performance = pnl_agg.merge(
            ops_agg,
            on=keys,
            how="outer",
        )

        for column in [
            "budget_revenue",
            "budget_cost",
            "budget_gp",
            "budget_shipments",
            "budget_teus",
            "budget_tons",
        ]:
            performance[column] = pd.to_numeric(
                performance[column],
                errors="coerce",
            ).fillna(0.0)

        performance["budget_gp_margin"] = (
            performance["budget_gp"]
            / performance["budget_revenue"].replace(
                0,
                pd.NA,
            )
        ).fillna(0.0)

        duplicate_count = int(
            performance.duplicated(
                subset=keys,
                keep=False,
            ).sum()
        )
        if duplicate_count:
            warnings.append(
                f"{duplicate_count} duplicate budget keys were aggregated."
            )

        fiscal_years = sorted(
            int(year)
            for year in performance[
                "Fiscal_Year"
            ].dropna().unique()
        )
        currencies = sorted(
            str(value)
            for value in pnl.get(
                "Currency",
                pd.Series(dtype=str),
            ).dropna().unique()
        )
        versions = sorted(
            str(value)
            for value in pnl.get(
                "Budget_Version",
                pd.Series(dtype=str),
            ).dropna().unique()
        )

        required_values = (
            len(performance)
            * 5
        )
        valid_values = int(
            performance[
                [
                    "Fiscal_Year",
                    "month_num",
                    "Country",
                    "Mode",
                    "Product",
                ]
            ].notna().sum().sum()
        )
        completeness = (
            valid_values
            / required_values
            * 100
            if required_values
            else 0.0
        )

        quality = max(
            0.0,
            min(
                100.0,
                completeness
                - len(warnings) * 2.5
                - len(errors) * 20.0,
            ),
        )

        return BudgetValidationResult(
            performance=performance,
            opex=opex,
            personnel=personnel,
            balance_sheet=balance_sheet,
            warnings=warnings,
            errors=errors,
            quality_score=round(quality, 1),
            completeness_score=round(
                completeness,
                1,
            ),
            fiscal_years=fiscal_years,
            currencies=currencies,
            versions=versions,
        )

    def create_version(
        self,
        result: BudgetValidationResult,
        *,
        source_name: str,
        version_label: str,
        company: str,
        currency: str,
    ) -> DatasetVersion:
        if not result.valid:
            raise ValueError(
                "Budget validation errors must be resolved "
                "before creating a version."
            )

        version_id = self.repository.create_version_id(
            "budget"
        )

        storage_file = self.repository.save_dataframe(
            "budget",
            version_id,
            result.performance,
        )

        opex_file = self.repository.save_dataframe(
            "budget_opex",
            version_id,
            result.opex,
        )
        personnel_file = self.repository.save_dataframe(
            "budget_personnel",
            version_id,
            result.personnel,
        )
        bs_file = self.repository.save_dataframe(
            "budget_balance_sheet",
            version_id,
            result.balance_sheet,
        )

        fiscal_year = (
            result.fiscal_years[0]
            if len(result.fiscal_years) == 1
            else None
        )

        version = DatasetVersion(
            version_id=version_id,
            dataset_type="budget",
            version_label=version_label,
            source_name=source_name,
            sheet_name="FIP Budget Standard",
            storage_file=storage_file,
            status="validated",
            rows=len(result.performance),
            columns=len(result.performance.columns),
            quality_score=result.quality_score,
            mapping_score=100.0,
            health_score=round(
                result.quality_score * 0.8
                + result.completeness_score * 0.2,
                1,
            ),
            company=company,
            currency=(
                result.currencies[0]
                if len(result.currencies) == 1
                else currency
            ),
            fiscal_year=fiscal_year,
            period_label=(
                f"FY{fiscal_year}"
                if fiscal_year
                else "Multi-Year Budget"
            ),
            comparison_label="Budget",
            warnings=result.warnings,
            mapped_columns={
                "Budget_PnL": "performance",
                "Budget_Operations": "performance",
                "Budget_OPEX": "opex",
                "Budget_Personnel": "personnel",
                "Budget_BalanceSheet": "balance_sheet",
            },
            metadata={
                "budget_versions": result.versions,
                "fiscal_years": result.fiscal_years,
                "currencies": result.currencies,
                "opex_storage_file": opex_file,
                "personnel_storage_file": personnel_file,
                "balance_sheet_storage_file": bs_file,
                "created_by": "FP&A / Controller",
                "created_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
            },
        )

        self.repository.save_version(version)
        return version

    def activate(
        self,
        version_id: str,
    ) -> DatasetVersion:
        return self.repository.activate(
            "budget",
            version_id,
        )
