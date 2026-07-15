from __future__ import annotations

from hashlib import sha1

import pandas as pd

from models.executive_alert import ExecutiveAlert


class ExecutiveAlertEngine:
    """
    Creates ranked CFO alerts from the selected period.

    The engine is deterministic and only uses period-aligned Actuals
    and the active comparison baseline already present in the dataset.
    """

    DIMENSIONS = (
        "customer",
        "trade_lane",
        "mode",
        "product",
    )

    def generate(
        self,
        dataframe: pd.DataFrame,
        *,
        comparison_label: str,
        max_alerts: int = 8,
    ) -> list[ExecutiveAlert]:
        if dataframe.empty:
            return []

        alerts: list[ExecutiveAlert] = []

        alerts.extend(
            self._overall_alerts(
                dataframe,
                comparison_label=comparison_label,
            )
        )

        for dimension in self.DIMENSIONS:
            if dimension in dataframe.columns:
                alerts.extend(
                    self._dimension_alerts(
                        dataframe,
                        dimension=dimension,
                        comparison_label=comparison_label,
                    )
                )

        ranked = sorted(
            alerts,
            key=self._priority_score,
            reverse=True,
        )

        unique: list[ExecutiveAlert] = []
        seen: set[tuple[str, str, str]] = set()

        for alert in ranked:
            key = (
                alert.category,
                alert.dimension,
                alert.dimension_value,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(alert)

            if len(unique) >= max_alerts:
                break

        return unique

    def _overall_alerts(
        self,
        dataframe: pd.DataFrame,
        *,
        comparison_label: str,
    ) -> list[ExecutiveAlert]:
        actual_revenue = self._sum(
            dataframe,
            "actual_revenue",
        )
        target_revenue = self._sum(
            dataframe,
            "estimated_revenue",
        )
        actual_gp = self._sum(
            dataframe,
            "actual_gp",
        )
        target_gp = self._sum(
            dataframe,
            "estimated_gp",
        )

        actual_margin = self._safe_ratio(
            actual_gp,
            actual_revenue,
        )
        target_margin = self._safe_ratio(
            target_gp,
            target_revenue,
        )

        alerts: list[ExecutiveAlert] = []

        revenue_pct = self._variance_pct(
            actual_revenue,
            target_revenue,
        )
        gp_pct = self._variance_pct(
            actual_gp,
            target_gp,
        )
        margin_pp = actual_margin - target_margin

        if abs(revenue_pct) >= 0.05:
            severity = (
                "success"
                if revenue_pct > 0
                else self._negative_severity(
                    revenue_pct
                )
            )
            alerts.append(
                self._build(
                    severity=severity,
                    category="Revenue",
                    title=(
                        "Revenue ahead of target"
                        if revenue_pct > 0
                        else "Revenue below target"
                    ),
                    metric=f"{revenue_pct:+.1%}",
                    message=(
                        f"Total Revenue is {abs(revenue_pct):.1%} "
                        f"{'above' if revenue_pct > 0 else 'below'} "
                        f"{comparison_label}."
                    ),
                    recommended_action=(
                        "Protect pricing and confirm that positive "
                        "performance is sustainable."
                        if revenue_pct > 0
                        else "Review volume, lost business, pricing "
                        "and customer concentration."
                    ),
                    actual_value=actual_revenue,
                    target_value=target_revenue,
                    variance_value=(
                        actual_revenue
                        - target_revenue
                    ),
                    variance_pct=revenue_pct,
                )
            )

        if abs(gp_pct) >= 0.04:
            severity = (
                "success"
                if gp_pct > 0
                else self._negative_severity(
                    gp_pct
                )
            )
            alerts.append(
                self._build(
                    severity=severity,
                    category="Gross Profit",
                    title=(
                        "Gross Profit ahead of target"
                        if gp_pct > 0
                        else "Gross Profit below target"
                    ),
                    metric=f"{gp_pct:+.1%}",
                    message=(
                        f"Gross Profit is {abs(gp_pct):.1%} "
                        f"{'above' if gp_pct > 0 else 'below'} "
                        f"{comparison_label}."
                    ),
                    recommended_action=(
                        "Preserve commercial discipline and capacity "
                        "management."
                        if gp_pct > 0
                        else "Review shipment profitability, accruals, "
                        "direct cost and pricing exceptions."
                    ),
                    actual_value=actual_gp,
                    target_value=target_gp,
                    variance_value=actual_gp - target_gp,
                    variance_pct=gp_pct,
                )
            )

        if abs(margin_pp) >= 0.01:
            severity = (
                "success"
                if margin_pp > 0
                else (
                    "critical"
                    if margin_pp <= -0.03
                    else "high"
                )
            )
            alerts.append(
                self._build(
                    severity=severity,
                    category="Margin",
                    title=(
                        "Margin expansion"
                        if margin_pp > 0
                        else "Margin compression"
                    ),
                    metric=f"{margin_pp * 100:+.2f} pp",
                    message=(
                        f"GP Margin is {abs(margin_pp) * 100:.2f} "
                        f"percentage points "
                        f"{'above' if margin_pp > 0 else 'below'} "
                        f"{comparison_label}."
                    ),
                    recommended_action=(
                        "Protect favorable mix and pricing."
                        if margin_pp > 0
                        else "Prioritize low-margin customers, products "
                        "and trade lanes for corrective action."
                    ),
                    actual_value=actual_margin,
                    target_value=target_margin,
                    variance_value=margin_pp,
                    variance_pct=margin_pp,
                )
            )

        return alerts

    def _dimension_alerts(
        self,
        dataframe: pd.DataFrame,
        *,
        dimension: str,
        comparison_label: str,
    ) -> list[ExecutiveAlert]:
        required = {
            dimension,
            "actual_revenue",
            "actual_gp",
            "estimated_revenue",
            "estimated_gp",
        }

        if not required.issubset(
            dataframe.columns
        ):
            return []

        grouped = (
            dataframe.groupby(
                dimension,
                dropna=False,
            )
            .agg(
                actual_revenue=(
                    "actual_revenue",
                    "sum",
                ),
                target_revenue=(
                    "estimated_revenue",
                    "sum",
                ),
                actual_gp=(
                    "actual_gp",
                    "sum",
                ),
                target_gp=(
                    "estimated_gp",
                    "sum",
                ),
            )
            .reset_index()
        )

        grouped["revenue_variance"] = (
            grouped["actual_revenue"]
            - grouped["target_revenue"]
        )
        grouped["gp_variance"] = (
            grouped["actual_gp"]
            - grouped["target_gp"]
        )
        grouped["gp_variance_pct"] = grouped.apply(
            lambda row: self._variance_pct(
                row["actual_gp"],
                row["target_gp"],
            ),
            axis=1,
        )
        grouped["actual_margin"] = grouped.apply(
            lambda row: self._safe_ratio(
                row["actual_gp"],
                row["actual_revenue"],
            ),
            axis=1,
        )
        grouped["target_margin"] = grouped.apply(
            lambda row: self._safe_ratio(
                row["target_gp"],
                row["target_revenue"],
            ),
            axis=1,
        )
        grouped["margin_pp"] = (
            grouped["actual_margin"]
            - grouped["target_margin"]
        )

        alerts: list[ExecutiveAlert] = []

        negative_gp = grouped[
            grouped["gp_variance"] < 0
        ].sort_values(
            "gp_variance",
            ascending=True,
        ).head(2)

        for _, row in negative_gp.iterrows():
            value = self._display_value(
                row[dimension]
            )
            gp_pct = float(
                row["gp_variance_pct"]
            )
            severity = (
                "critical"
                if gp_pct <= -0.20
                else "high"
                if gp_pct <= -0.10
                else "medium"
            )

            alerts.append(
                self._build(
                    severity=severity,
                    category="Gross Profit",
                    title=f"{value}: GP below target",
                    metric=f"${row['gp_variance']:,.0f}",
                    message=(
                        f"{dimension.replace('_', ' ').title()} "
                        f"{value} is ${abs(row['gp_variance']):,.0f} "
                        f"below {comparison_label}."
                    ),
                    recommended_action=(
                        "Drill into shipment profitability, customer "
                        "pricing and direct cost exceptions."
                    ),
                    dimension=dimension,
                    dimension_value=value,
                    actual_value=float(
                        row["actual_gp"]
                    ),
                    target_value=float(
                        row["target_gp"]
                    ),
                    variance_value=float(
                        row["gp_variance"]
                    ),
                    variance_pct=gp_pct,
                )
            )

        margin_risk = grouped[
            grouped["margin_pp"] <= -0.015
        ].sort_values(
            "margin_pp",
            ascending=True,
        ).head(1)

        for _, row in margin_risk.iterrows():
            value = self._display_value(
                row[dimension]
            )
            margin_pp = float(
                row["margin_pp"]
            )

            alerts.append(
                self._build(
                    severity=(
                        "critical"
                        if margin_pp <= -0.03
                        else "high"
                    ),
                    category="Margin",
                    title=f"{value}: margin compression",
                    metric=f"{margin_pp * 100:+.2f} pp",
                    message=(
                        f"{dimension.replace('_', ' ').title()} "
                        f"{value} is below target margin by "
                        f"{abs(margin_pp) * 100:.2f} pp."
                    ),
                    recommended_action=(
                        "Review pricing, carrier cost, product mix "
                        "and unprofitable shipments."
                    ),
                    dimension=dimension,
                    dimension_value=value,
                    actual_value=float(
                        row["actual_margin"]
                    ),
                    target_value=float(
                        row["target_margin"]
                    ),
                    variance_value=margin_pp,
                    variance_pct=margin_pp,
                )
            )

        positive_gp = grouped[
            grouped["gp_variance"] > 0
        ].sort_values(
            "gp_variance",
            ascending=False,
        ).head(1)

        for _, row in positive_gp.iterrows():
            value = self._display_value(
                row[dimension]
            )

            alerts.append(
                self._build(
                    severity="success",
                    category="Opportunity",
                    title=f"{value}: positive GP contribution",
                    metric=f"+${row['gp_variance']:,.0f}",
                    message=(
                        f"{dimension.replace('_', ' ').title()} "
                        f"{value} contributes ${row['gp_variance']:,.0f} "
                        f"above {comparison_label}."
                    ),
                    recommended_action=(
                        "Validate sustainability and replicate the "
                        "commercial or operational practices."
                    ),
                    dimension=dimension,
                    dimension_value=value,
                    actual_value=float(
                        row["actual_gp"]
                    ),
                    target_value=float(
                        row["target_gp"]
                    ),
                    variance_value=float(
                        row["gp_variance"]
                    ),
                    variance_pct=float(
                        row["gp_variance_pct"]
                    ),
                )
            )

        return alerts

    @staticmethod
    def _sum(
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        if column not in dataframe.columns:
            return 0.0

        return float(
            pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )
            .fillna(0.0)
            .sum()
        )

    @staticmethod
    def _safe_ratio(
        numerator: float,
        denominator: float,
    ) -> float:
        return (
            numerator / denominator
            if denominator
            else 0.0
        )

    @staticmethod
    def _variance_pct(
        actual: float,
        target: float,
    ) -> float:
        if target == 0:
            return 0.0

        return (
            actual - target
        ) / abs(target)

    @staticmethod
    def _display_value(
        value: object,
    ) -> str:
        if pd.isna(value):
            return "Unassigned"

        text = str(value).strip()
        return text or "Unassigned"

    @staticmethod
    def _negative_severity(
        variance_pct: float,
    ) -> str:
        if variance_pct <= -0.20:
            return "critical"
        if variance_pct <= -0.10:
            return "high"
        return "medium"

    @staticmethod
    def _priority_score(
        alert: ExecutiveAlert,
    ) -> float:
        severity_score = {
            "critical": 500,
            "high": 400,
            "medium": 300,
            "success": 100,
        }.get(
            alert.severity,
            200,
        )

        return (
            severity_score
            + abs(alert.variance_pct) * 100
            + abs(alert.variance_value) / 100000
        )

    @staticmethod
    def _build(
        *,
        severity: str,
        category: str,
        title: str,
        metric: str,
        message: str,
        recommended_action: str,
        dimension: str = "",
        dimension_value: str = "",
        actual_value: float = 0.0,
        target_value: float = 0.0,
        variance_value: float = 0.0,
        variance_pct: float = 0.0,
    ) -> ExecutiveAlert:
        raw_id = (
            f"{category}|{dimension}|"
            f"{dimension_value}|{title}"
        )
        alert_id = sha1(
            raw_id.encode("utf-8")
        ).hexdigest()[:12]

        return ExecutiveAlert(
            alert_id=alert_id,
            severity=severity,
            category=category,
            title=title,
            metric=metric,
            message=message,
            recommended_action=recommended_action,
            dimension=dimension,
            dimension_value=dimension_value,
            actual_value=actual_value,
            target_value=target_value,
            variance_value=variance_value,
            variance_pct=variance_pct,
        )
