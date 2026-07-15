
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

import numpy as np
import pandas as pd

from engines.universal_date_parser_engine import (
    UniversalDateParserEngine,
)


@dataclass(frozen=True)
class AgingConfig:
    """Configuration for working-capital aging calculations."""

    as_of_date: pd.Timestamp
    bucket_1_end: int = 30
    bucket_2_end: int = 45
    bucket_3_end: int = 60
    bucket_4_end: int = 90

    @classmethod
    def from_value(
        cls,
        as_of_date: str | date | pd.Timestamp | None = None,
    ) -> "AgingConfig":
        resolved_date = (
            pd.Timestamp.today().normalize()
            if as_of_date is None
            else pd.Timestamp(as_of_date).normalize()
        )

        return cls(as_of_date=resolved_date)


@dataclass(frozen=True)
class AgingResult:
    """Structured output returned by the aging engine."""

    dataframe: pd.DataFrame
    summary: dict
    bucket_summary: pd.DataFrame
    counterparty_summary: pd.DataFrame


class WorkingCapitalAgingEngine:
    """
    Calculates Accounts Receivable and Accounts Payable aging.

    Expected canonical columns:
    - document_id
    - counterparty
    - document_type
    - invoice_date
    - due_date
    - original_amount
    - paid_amount
    - open_amount
    - currency
    - status
    - responsible
    - business_unit

    One row must represent one invoice, credit note, debit note,
    payment request, or other open working-capital document.
    """

    def __init__(self) -> None:
        self.date_parser = UniversalDateParserEngine()

    REQUIRED_COLUMNS = {
        "document_id",
        "counterparty",
        "document_type",
        "invoice_date",
        "due_date",
    }

    OPTIONAL_COLUMNS = {
        "original_amount",
        "paid_amount",
        "open_amount",
        "currency",
        "status",
        "responsible",
        "business_unit",
    }

    NUMERIC_COLUMNS = {
        "original_amount",
        "paid_amount",
        "open_amount",
    }

    VALID_DOCUMENT_TYPES = {
        "AR",
        "AP",
    }

    BUCKET_ORDER = [
        "Current",
        "0-30",
        "31-45",
        "46-60",
        "61-90",
        "90+",
    ]

    SIGNAL_ORDER = {
        "Green": 1,
        "Yellow": 2,
        "Orange": 3,
        "Red": 4,
        "Dark Red": 5,
    }

    def prepare_data(
        self,
        dataframe: pd.DataFrame,
        config: AgingConfig | None = None,
    ) -> pd.DataFrame:
        """
        Validates and prepares invoice-level working-capital data.
        """

        if config is None:
            config = AgingConfig.from_value()

        missing_columns = sorted(
            self.REQUIRED_COLUMNS - set(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas requeridas para Working Capital Aging: "
                + ", ".join(missing_columns)
            )

        df = dataframe.copy()

        for column in self.OPTIONAL_COLUMNS:
            if column not in df.columns:
                df[column] = self._default_value(column)

        for column in self.NUMERIC_COLUMNS:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        df["invoice_date"] = (
            self.date_parser.parse_series(
                df["invoice_date"]
            )
        )

        df["due_date"] = (
            self.date_parser.parse_series(
                df["due_date"]
            )
        )

        invalid_invoice_dates = int(
            df["invoice_date"].isna().sum()
        )

        invalid_due_dates = int(
            df["due_date"].isna().sum()
        )

        if invalid_invoice_dates:
            raise ValueError(
                f"{invalid_invoice_dates} registros contienen "
                "Invoice Date inválida."
            )

        if invalid_due_dates:
            raise ValueError(
                f"{invalid_due_dates} registros contienen "
                "Due Date inválida."
            )

        df["document_id"] = (
            df["document_id"]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
        )

        df["counterparty"] = (
            df["counterparty"]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
        )

        df["document_type"] = (
            df["document_type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
            .replace(
                {
                    "ACCOUNTS RECEIVABLE": "AR",
                    "RECEIVABLE": "AR",
                    "CUSTOMER": "AR",
                    "CLIENT": "AR",
                    "COBRANZA": "AR",
                    "CUENTAS POR COBRAR": "AR",
                    "ACCOUNTS PAYABLE": "AP",
                    "PAYABLE": "AP",
                    "SUPPLIER": "AP",
                    "VENDOR": "AP",
                    "PAGO": "AP",
                    "CUENTAS POR PAGAR": "AP",
                }
            )
        )

        invalid_types = sorted(
            set(df["document_type"].unique())
            - self.VALID_DOCUMENT_TYPES
        )

        if invalid_types:
            raise ValueError(
                "Document Type contiene valores no reconocidos: "
                + ", ".join(invalid_types)
            )

        for column in [
            "currency",
            "status",
            "responsible",
            "business_unit",
        ]:
            df[column] = (
                df[column]
                .fillna("Unassigned")
                .astype(str)
                .str.strip()
            )

        calculated_open_amount = (
            df["original_amount"] - df["paid_amount"]
        )

        open_amount_missing_or_zero = (
            df["open_amount"].isna()
            | (
                (df["open_amount"] == 0)
                & (calculated_open_amount != 0)
            )
        )

        df.loc[
            open_amount_missing_or_zero,
            "open_amount",
        ] = calculated_open_amount[
            open_amount_missing_or_zero
        ]

        df["open_amount"] = df["open_amount"].clip(lower=0.0)

        df["days_to_due"] = (
            df["due_date"] - config.as_of_date
        ).dt.days

        df["days_overdue"] = np.where(
            df["open_amount"] <= 0,
            0,
            np.maximum(
                (
                    config.as_of_date
                    - df["due_date"]
                ).dt.days,
                0,
            ),
        ).astype(int)

        df["is_overdue"] = (
            (df["open_amount"] > 0)
            & (df["due_date"] < config.as_of_date)
        )

        df["aging_bucket"] = df.apply(
            lambda row: self._assign_bucket(
                open_amount=float(row["open_amount"]),
                days_overdue=int(row["days_overdue"]),
                is_overdue=bool(row["is_overdue"]),
                config=config,
            ),
            axis=1,
        )

        df["traffic_light"] = df["aging_bucket"].map(
            {
                "Current": "Green",
                "0-30": "Green",
                "31-45": "Yellow",
                "46-60": "Orange",
                "61-90": "Red",
                "90+": "Dark Red",
            }
        )

        df["cfo_signal"] = df["traffic_light"].map(
            {
                "Green": "🟢 Within Terms",
                "Yellow": "🟡 Monitor",
                "Orange": "🟠 Follow Up",
                "Red": "🔴 Escalate",
                "Dark Red": "🔴 Critical",
            }
        )

        df["open_status"] = np.select(
            [
                df["open_amount"] <= 0,
                df["is_overdue"],
            ],
            [
                "Closed",
                "Overdue",
            ],
            default="Open - Not Due",
        )

        df["as_of_date"] = config.as_of_date

        return df

    def analyze(
        self,
        dataframe: pd.DataFrame,
        config: AgingConfig | None = None,
        document_type: str | None = None,
        currency: str | None = None,
        counterparty: str | None = None,
    ) -> AgingResult:
        """
        Runs the complete working-capital aging analysis.
        """

        df = self.prepare_data(
            dataframe,
            config=config,
        )

        if document_type:
            normalized_type = document_type.strip().upper()

            if normalized_type not in self.VALID_DOCUMENT_TYPES:
                raise ValueError(
                    "document_type debe ser 'AR' o 'AP'."
                )

            df = df[
                df["document_type"] == normalized_type
            ].copy()

        if currency:
            df = df[
                df["currency"].str.upper()
                == currency.strip().upper()
            ].copy()

        if counterparty:
            df = df[
                df["counterparty"].str.casefold()
                == counterparty.strip().casefold()
            ].copy()

        summary = self.executive_summary(df)
        bucket_summary = self.bucket_summary(df)
        counterparty_summary = self.counterparty_summary(df)

        return AgingResult(
            dataframe=df,
            summary=summary,
            bucket_summary=bucket_summary,
            counterparty_summary=counterparty_summary,
        )

    def executive_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:
        """
        Returns AR/AP working-capital KPIs.
        """

        if dataframe.empty:
            return self._empty_summary()

        open_data = dataframe[
            dataframe["open_amount"] > 0
        ].copy()

        total_open = float(
            open_data["open_amount"].sum()
        )

        total_overdue = float(
            open_data.loc[
                open_data["is_overdue"],
                "open_amount",
            ].sum()
        )

        overdue_90_plus = float(
            open_data.loc[
                open_data["aging_bucket"] == "90+",
                "open_amount",
            ].sum()
        )

        current_amount = float(
            open_data.loc[
                open_data["aging_bucket"] == "Current",
                "open_amount",
            ].sum()
        )

        ar_open = float(
            open_data.loc[
                open_data["document_type"] == "AR",
                "open_amount",
            ].sum()
        )

        ap_open = float(
            open_data.loc[
                open_data["document_type"] == "AP",
                "open_amount",
            ].sum()
        )

        weighted_days_overdue = self._weighted_average(
            values=open_data["days_overdue"],
            weights=open_data["open_amount"],
        )

        open_documents = int(
            open_data["document_id"].nunique()
        )

        overdue_documents = int(
            open_data.loc[
                open_data["is_overdue"],
                "document_id",
            ].nunique()
        )

        return {
            "total_open": total_open,
            "total_overdue": total_overdue,
            "current_amount": current_amount,
            "overdue_90_plus": overdue_90_plus,
            "ar_open": ar_open,
            "ap_open": ap_open,
            "open_documents": open_documents,
            "overdue_documents": overdue_documents,
            "overdue_pct": self._safe_divide(
                total_overdue,
                total_open,
            ),
            "overdue_90_plus_pct": self._safe_divide(
                overdue_90_plus,
                total_open,
            ),
            "weighted_days_overdue": weighted_days_overdue,
            "counterparties": int(
                open_data["counterparty"].nunique()
            ),
        }

    def bucket_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Aggregates open balances by AR/AP and aging bucket.
        """

        open_data = dataframe[
            dataframe["open_amount"] > 0
        ].copy()

        if open_data.empty:
            return pd.DataFrame(
                columns=[
                    "document_type",
                    "aging_bucket",
                    "open_amount",
                    "documents",
                    "counterparties",
                    "portfolio_pct",
                    "traffic_light",
                    "cfo_signal",
                ]
            )

        summary = (
            open_data.groupby(
                [
                    "document_type",
                    "aging_bucket",
                    "traffic_light",
                    "cfo_signal",
                ],
                dropna=False,
            )
            .agg(
                open_amount=("open_amount", "sum"),
                documents=("document_id", "nunique"),
                counterparties=("counterparty", "nunique"),
            )
            .reset_index()
        )

        total_by_type = (
            summary.groupby("document_type")["open_amount"]
            .transform("sum")
        )

        summary["portfolio_pct"] = np.where(
            total_by_type != 0,
            summary["open_amount"] / total_by_type,
            0.0,
        )

        bucket_rank = {
            bucket: index
            for index, bucket in enumerate(
                self.BUCKET_ORDER,
                start=1,
            )
        }

        summary["_bucket_order"] = (
            summary["aging_bucket"]
            .map(bucket_rank)
            .fillna(999)
        )

        return (
            summary.sort_values(
                [
                    "document_type",
                    "_bucket_order",
                ]
            )
            .drop(columns=["_bucket_order"])
            .reset_index(drop=True)
        )

    def counterparty_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Aggregates open exposure by customer or supplier.
        """

        open_data = dataframe[
            dataframe["open_amount"] > 0
        ].copy()

        if open_data.empty:
            return pd.DataFrame(
                columns=[
                    "document_type",
                    "counterparty",
                    "currency",
                    "open_amount",
                    "overdue_amount",
                    "overdue_90_plus",
                    "documents",
                    "overdue_pct",
                    "weighted_days_overdue",
                    "max_days_overdue",
                    "risk_signal",
                ]
            )

        grouped = (
            open_data.groupby(
                [
                    "document_type",
                    "counterparty",
                    "currency",
                ],
                dropna=False,
            )
            .apply(
                self._counterparty_aggregation,
                include_groups=False,
            )
            .reset_index()
        )

        grouped["overdue_pct"] = np.where(
            grouped["open_amount"] != 0,
            grouped["overdue_amount"]
            / grouped["open_amount"],
            0.0,
        )

        grouped["risk_signal"] = grouped.apply(
            lambda row: self._counterparty_signal(
                overdue_pct=float(row["overdue_pct"]),
                overdue_90_plus=float(
                    row["overdue_90_plus"]
                ),
                open_amount=float(row["open_amount"]),
                max_days_overdue=int(
                    row["max_days_overdue"]
                ),
            ),
            axis=1,
        )

        return grouped.sort_values(
            [
                "overdue_90_plus",
                "overdue_amount",
                "open_amount",
            ],
            ascending=False,
        ).reset_index(drop=True)

    def top_counterparties(
        self,
        dataframe: pd.DataFrame,
        document_type: str,
        limit: int = 10,
        overdue_only: bool = False,
    ) -> pd.DataFrame:
        """
        Returns top customers or suppliers by open exposure.
        """

        summary = self.counterparty_summary(
            dataframe
        )

        normalized_type = document_type.strip().upper()

        filtered = summary[
            summary["document_type"] == normalized_type
        ].copy()

        if overdue_only:
            filtered = filtered[
                filtered["overdue_amount"] > 0
            ].copy()

            sort_columns = [
                "overdue_amount",
                "open_amount",
            ]
        else:
            sort_columns = [
                "open_amount",
                "overdue_amount",
            ]

        return (
            filtered.sort_values(
                sort_columns,
                ascending=False,
            )
            .head(limit)
            .reset_index(drop=True)
        )

    def upcoming_due(
        self,
        dataframe: pd.DataFrame,
        days: int,
        document_type: str | None = None,
    ) -> pd.DataFrame:
        """
        Returns documents due within the next N days.
        """

        if days < 0:
            raise ValueError(
                "days no puede ser negativo."
            )

        df = dataframe[
            (dataframe["open_amount"] > 0)
            & (dataframe["days_to_due"] >= 0)
            & (dataframe["days_to_due"] <= days)
        ].copy()

        if document_type:
            df = df[
                df["document_type"]
                == document_type.strip().upper()
            ].copy()

        return df.sort_values(
            [
                "due_date",
                "open_amount",
            ],
            ascending=[True, False],
        ).reset_index(drop=True)

    def exposure_by_currency(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Returns open and overdue exposure by currency and AR/AP.
        """

        open_data = dataframe[
            dataframe["open_amount"] > 0
        ].copy()

        if open_data.empty:
            return pd.DataFrame(
                columns=[
                    "document_type",
                    "currency",
                    "open_amount",
                    "overdue_amount",
                    "overdue_90_plus",
                    "documents",
                ]
            )

        return (
            open_data.groupby(
                [
                    "document_type",
                    "currency",
                ],
                dropna=False,
            )
            .agg(
                open_amount=("open_amount", "sum"),
                overdue_amount=(
                    "open_amount",
                    lambda values: float(
                        values[
                            open_data.loc[
                                values.index,
                                "is_overdue",
                            ]
                        ].sum()
                    ),
                ),
                overdue_90_plus=(
                    "open_amount",
                    lambda values: float(
                        values[
                            open_data.loc[
                                values.index,
                                "aging_bucket",
                            ]
                            == "90+"
                        ].sum()
                    ),
                ),
                documents=("document_id", "nunique"),
            )
            .reset_index()
            .sort_values(
                "open_amount",
                ascending=False,
            )
            .reset_index(drop=True)
        )

    @staticmethod
    def _default_value(column: str):
        defaults = {
            "original_amount": 0.0,
            "paid_amount": 0.0,
            "open_amount": 0.0,
            "currency": "Unassigned",
            "status": "Open",
            "responsible": "Unassigned",
            "business_unit": "Unassigned",
        }

        return defaults[column]

    @staticmethod
    def _assign_bucket(
        open_amount: float,
        days_overdue: int,
        is_overdue: bool,
        config: AgingConfig,
    ) -> str:
        if open_amount <= 0:
            return "Current"

        if not is_overdue:
            return "Current"

        if days_overdue <= config.bucket_1_end:
            return "0-30"

        if days_overdue <= config.bucket_2_end:
            return "31-45"

        if days_overdue <= config.bucket_3_end:
            return "46-60"

        if days_overdue <= config.bucket_4_end:
            return "61-90"

        return "90+"

    @staticmethod
    def _weighted_average(
        values: Iterable,
        weights: Iterable,
    ) -> float:
        values_array = np.asarray(
            values,
            dtype=float,
        )

        weights_array = np.asarray(
            weights,
            dtype=float,
        )

        total_weight = float(
            weights_array.sum()
        )

        if total_weight == 0:
            return 0.0

        return float(
            np.average(
                values_array,
                weights=weights_array,
            )
        )

    def _counterparty_aggregation(
        self,
        group: pd.DataFrame,
    ) -> pd.Series:
        open_amount = float(
            group["open_amount"].sum()
        )

        overdue_amount = float(
            group.loc[
                group["is_overdue"],
                "open_amount",
            ].sum()
        )

        overdue_90_plus = float(
            group.loc[
                group["aging_bucket"] == "90+",
                "open_amount",
            ].sum()
        )

        return pd.Series(
            {
                "open_amount": open_amount,
                "overdue_amount": overdue_amount,
                "overdue_90_plus": overdue_90_plus,
                "documents": int(
                    group["document_id"].nunique()
                ),
                "weighted_days_overdue": (
                    self._weighted_average(
                        values=group["days_overdue"],
                        weights=group["open_amount"],
                    )
                ),
                "max_days_overdue": int(
                    group["days_overdue"].max()
                ),
            }
        )

    @staticmethod
    def _counterparty_signal(
        overdue_pct: float,
        overdue_90_plus: float,
        open_amount: float,
        max_days_overdue: int,
    ) -> str:
        if open_amount <= 0:
            return "🔵 No Open Exposure"

        if overdue_90_plus > 0 or max_days_overdue > 90:
            return "🔴 Critical"

        if max_days_overdue > 60 or overdue_pct >= 0.50:
            return "🔴 High Risk"

        if max_days_overdue > 45 or overdue_pct >= 0.25:
            return "🟠 Follow Up"

        if max_days_overdue > 30 or overdue_pct > 0:
            return "🟡 Monitor"

        return "🟢 Within Terms"

    @staticmethod
    def _safe_divide(
        numerator: float,
        denominator: float,
    ) -> float:
        if denominator == 0:
            return 0.0

        return numerator / denominator

    @staticmethod
    def _empty_summary() -> dict:
        return {
            "total_open": 0.0,
            "total_overdue": 0.0,
            "current_amount": 0.0,
            "overdue_90_plus": 0.0,
            "ar_open": 0.0,
            "ap_open": 0.0,
            "open_documents": 0,
            "overdue_documents": 0,
            "overdue_pct": 0.0,
            "overdue_90_plus_pct": 0.0,
            "weighted_days_overdue": 0.0,
            "counterparties": 0,
        }
