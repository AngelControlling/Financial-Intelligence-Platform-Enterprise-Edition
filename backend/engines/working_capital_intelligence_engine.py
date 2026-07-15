from __future__ import annotations

import pandas as pd

from models.working_capital_intelligence import (
    WorkingCapitalIntelligenceResult,
)


class WorkingCapitalIntelligenceEngine:
    """
    Analyze AR/AP aging and calculate robust DSO/DPO estimates.

    Preferred denominator:
    - Invoice activity from the same AR/AP population.
    - Trailing 12 months when at least 330 days of history exist.
    - Otherwise YTD invoice activity, using elapsed calendar days.

    This avoids comparing an enterprise-wide balance against an unrelated
    or narrowly filtered Mission Control revenue slice.
    """

    BUCKET_ORDER = [
        "Current",
        "0-30",
        "31-45",
        "46-60",
        "61-90",
        "90+",
    ]

    def analyze(
        self,
        dataframe: pd.DataFrame,
        *,
        external_actuals: pd.DataFrame | None = None,
    ) -> WorkingCapitalIntelligenceResult:
        if dataframe.empty:
            raise ValueError("Working Capital dataset is empty.")

        df = self._prepare(dataframe)
        ar = df[df["document_type"] == "AR"].copy()
        ap = df[df["document_type"] == "AP"].copy()

        total_ar = float(ar["open_amount"].sum())
        total_ap = float(ap["open_amount"].sum())
        overdue_ar = float(ar.loc[ar["is_overdue"], "open_amount"].sum())
        overdue_ap = float(ap.loc[ap["is_overdue"], "open_amount"].sum())
        ar_90_plus = float(
            ar.loc[ar["aging_bucket"] == "90+", "open_amount"].sum()
        )
        ap_90_plus = float(
            ap.loc[ap["aging_bucket"] == "90+", "open_amount"].sum()
        )

        overdue_ar_pct = overdue_ar / total_ar if total_ar else 0.0
        overdue_ap_pct = overdue_ap / total_ap if total_ap else 0.0

        as_of_date = self._as_of_date(df)
        dso, dso_method = self._days_from_invoice_activity(
            ar,
            balance=total_ar,
            as_of_date=as_of_date,
            label="AR invoice activity",
        )
        dpo, dpo_method = self._days_from_invoice_activity(
            ap,
            balance=total_ap,
            as_of_date=as_of_date,
            label="AP invoice activity",
        )

        top_5_ar_concentration = self._top_concentration(ar, total_ar)
        top_5_ap_concentration = self._top_concentration(ap, total_ap)

        ar_90_pct = ar_90_plus / total_ar if total_ar else 0.0
        ap_90_pct = ap_90_plus / total_ap if total_ap else 0.0

        average_ar_age = self._weighted_average_days(ar)
        average_ap_age = self._weighted_average_days(ap)

        collection_risk = self._risk_score(
            overdue_pct=overdue_ar_pct,
            ninety_plus_pct=ar_90_pct,
            concentration_pct=top_5_ar_concentration,
            weighted_age=average_ar_age,
        )
        payment_pressure = self._risk_score(
            overdue_pct=overdue_ap_pct,
            ninety_plus_pct=ap_90_pct,
            concentration_pct=top_5_ap_concentration,
            weighted_age=average_ap_age,
        )

        bucket_summary = (
            df.groupby(
                ["document_type", "aging_bucket"],
                dropna=False,
            )["open_amount"]
            .sum()
            .reset_index()
        )
        bucket_summary["aging_bucket"] = pd.Categorical(
            bucket_summary["aging_bucket"],
            categories=self.BUCKET_ORDER,
            ordered=True,
        )
        bucket_summary = bucket_summary.sort_values(
            ["document_type", "aging_bucket"]
        )

        notes = [
            "DSO and DPO use invoice activity from the same AR/AP population.",
            f"DSO method: {dso_method}.",
            f"DPO method: {dpo_method}.",
        ]
        if external_actuals is not None and not external_actuals.empty:
            notes.append(
                "Mission Control Actuals are retained for financial analysis; "
                "they are not forced into the days calculation when their "
                "scope is not demonstrably identical to the AR/AP ledger."
            )

        return WorkingCapitalIntelligenceResult(
            total_ar=total_ar,
            total_ap=total_ap,
            net_working_capital=total_ar - total_ap,
            overdue_ar=overdue_ar,
            overdue_ap=overdue_ap,
            overdue_ar_pct=overdue_ar_pct,
            overdue_ap_pct=overdue_ap_pct,
            ar_90_plus=ar_90_plus,
            ap_90_plus=ap_90_plus,
            dso=dso,
            dpo=dpo,
            dso_method=dso_method,
            dpo_method=dpo_method,
            collection_risk_score=round(collection_risk, 1),
            collection_risk_level=self._risk_level(collection_risk),
            payment_pressure_score=round(payment_pressure, 1),
            payment_pressure_level=self._risk_level(payment_pressure),
            top_5_ar_concentration=top_5_ar_concentration,
            top_5_ap_concentration=top_5_ap_concentration,
            top_overdue_ar=self._top_overdue(ar),
            top_overdue_ap=self._top_overdue(ap),
            bucket_summary=bucket_summary,
            data_quality_note=" ".join(notes),
        )

    def _prepare(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        required = {"document_type", "counterparty", "open_amount"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                "Working Capital is missing: " + ", ".join(sorted(missing))
            )

        df["document_type"] = (
            df["document_type"].fillna("").astype(str).str.strip().str.upper()
        )
        df["counterparty"] = (
            df["counterparty"]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
            .replace("", "Unassigned")
        )
        for column in ["open_amount", "original_amount", "days_overdue"]:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                ).fillna(0.0)

        if "original_amount" not in df.columns:
            df["original_amount"] = df["open_amount"]

        for column in ["invoice_date", "due_date", "as_of_date"]:
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")

        if "is_overdue" not in df.columns:
            df["is_overdue"] = df.get(
                "days_overdue", pd.Series(0, index=df.index)
            ) > 0
        else:
            df["is_overdue"] = df["is_overdue"].fillna(False).astype(bool)

        if "days_overdue" not in df.columns:
            df["days_overdue"] = 0.0

        if "aging_bucket" not in df.columns:
            df["aging_bucket"] = pd.cut(
                df["days_overdue"],
                bins=[-1, 0, 30, 45, 60, 90, float("inf")],
                labels=self.BUCKET_ORDER,
            ).astype(str)

        return df

    @staticmethod
    def _as_of_date(dataframe: pd.DataFrame) -> pd.Timestamp:
        if "as_of_date" in dataframe.columns:
            valid = dataframe["as_of_date"].dropna()
            if not valid.empty:
                return pd.Timestamp(valid.max()).normalize()
        return pd.Timestamp.today().normalize()

    @staticmethod
    def _days_from_invoice_activity(
        dataframe: pd.DataFrame,
        *,
        balance: float,
        as_of_date: pd.Timestamp,
        label: str,
    ) -> tuple[float | None, str]:
        if dataframe.empty or balance <= 0 or "invoice_date" not in dataframe:
            return None, "Unavailable"

        valid = dataframe.dropna(subset=["invoice_date"]).copy()
        valid = valid[valid["invoice_date"] <= as_of_date]
        if valid.empty:
            return None, "Unavailable"

        earliest = pd.Timestamp(valid["invoice_date"].min()).normalize()
        history_days = max((as_of_date - earliest).days + 1, 1)

        if history_days >= 330:
            start = as_of_date - pd.Timedelta(days=364)
            activity = float(
                valid.loc[
                    valid["invoice_date"].between(start, as_of_date),
                    "original_amount",
                ].sum()
            )
            if activity <= 0:
                return None, "Unavailable"
            return balance / activity * 365.0, f"Trailing 12M {label}"

        start = pd.Timestamp(as_of_date.year, 1, 1)
        ytd = valid[valid["invoice_date"].between(start, as_of_date)]
        activity = float(ytd["original_amount"].sum())
        elapsed_days = max((as_of_date - start).days + 1, 1)
        if activity <= 0:
            return None, "Unavailable"
        return balance / activity * elapsed_days, f"YTD {label}"

    @staticmethod
    def _top_concentration(
        dataframe: pd.DataFrame,
        total_balance: float,
    ) -> float:
        if dataframe.empty or total_balance <= 0:
            return 0.0
        balances = (
            dataframe.groupby("counterparty", dropna=False)["open_amount"]
            .sum()
            .sort_values(ascending=False)
        )
        return float(balances.head(5).sum()) / total_balance

    @staticmethod
    def _weighted_average_days(dataframe: pd.DataFrame) -> float:
        if dataframe.empty:
            return 0.0
        open_amount = dataframe["open_amount"].clip(lower=0)
        denominator = float(open_amount.sum())
        if denominator <= 0:
            return 0.0
        days = dataframe["days_overdue"].clip(lower=0)
        return float((open_amount * days).sum()) / denominator

    @staticmethod
    def _risk_score(
        *,
        overdue_pct: float,
        ninety_plus_pct: float,
        concentration_pct: float,
        weighted_age: float,
    ) -> float:
        """
        Balanced score that avoids immediate saturation.

        40% overdue ratio
        25% 90+ aging
        20% top-five concentration
        15% weighted overdue age
        """
        overdue_component = min(overdue_pct / 0.80, 1.0) * 40
        ninety_component = min(ninety_plus_pct / 0.35, 1.0) * 25
        concentration_component = min(
            max(concentration_pct - 0.20, 0.0) / 0.60,
            1.0,
        ) * 20
        age_component = min(weighted_age / 120.0, 1.0) * 15
        return min(
            overdue_component
            + ninety_component
            + concentration_component
            + age_component,
            100.0,
        )

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 80:
            return "Critical"
        if score >= 60:
            return "High"
        if score >= 35:
            return "Medium"
        return "Low"

    @staticmethod
    def _top_overdue(dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.empty:
            return pd.DataFrame(
                columns=["counterparty", "open_amount", "days_overdue"]
            )

        overdue = dataframe[dataframe["is_overdue"]].copy()
        if overdue.empty:
            return pd.DataFrame(
                columns=["counterparty", "open_amount", "days_overdue"]
            )

        return (
            overdue.groupby("counterparty", dropna=False)
            .agg(
                open_amount=("open_amount", "sum"),
                days_overdue=("days_overdue", "max"),
            )
            .reset_index()
            .sort_values("open_amount", ascending=False)
            .head(10)
        )
