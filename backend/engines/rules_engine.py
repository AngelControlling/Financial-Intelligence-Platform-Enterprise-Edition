from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RuleConfig:
    """Configurable variance and materiality thresholds."""

    amount_threshold: float = 100_000.0
    percentage_threshold: float = 0.05
    evaluation_logic: str = "OR"

    high_multiplier: float = 2.0
    critical_multiplier: float = 3.0

    def __post_init__(self) -> None:
        logic = self.evaluation_logic.upper()

        if logic not in {"OR", "AND"}:
            raise ValueError(
                "evaluation_logic debe ser 'OR' o 'AND'."
            )

        if self.amount_threshold < 0:
            raise ValueError(
                "amount_threshold no puede ser negativo."
            )

        if self.percentage_threshold < 0:
            raise ValueError(
                "percentage_threshold no puede ser negativo."
            )


class RulesEngine:
    """Evaluates financial variances against configurable rules."""

    SUPPORTED_METRICS = {
        "Revenue",
        "Cost",
        "Gross Profit",
        "GP Margin",
    }

    def evaluate_overall(
        self,
        variance_summary: dict,
        config: RuleConfig,
    ) -> pd.DataFrame:
        """Evaluates consolidated financial variances."""

        records = [
            self._evaluate_metric(
                metric="Revenue",
                amount=variance_summary["revenue_variance"],
                percentage=variance_summary[
                    "revenue_variance_pct"
                ],
                config=config,
            ),
            self._evaluate_metric(
                metric="Cost",
                amount=variance_summary["cost_variance"],
                percentage=variance_summary[
                    "cost_variance_pct"
                ],
                config=config,
            ),
            self._evaluate_metric(
                metric="Gross Profit",
                amount=variance_summary["gp_variance"],
                percentage=variance_summary[
                    "gp_variance_pct"
                ],
                config=config,
            ),
            self._evaluate_metric(
                metric="GP Margin",
                amount=variance_summary[
                    "margin_variance_pp"
                ],
                percentage=variance_summary[
                    "margin_variance_pp"
                ],
                config=config,
                is_margin=True,
            ),
        ]

        return pd.DataFrame(records)

    def evaluate_dimension(
        self,
        dimension_variance: pd.DataFrame,
        dimension: str,
        config: RuleConfig,
    ) -> pd.DataFrame:
        """Evaluates GP variances by a business dimension."""

        required_columns = {
            dimension,
            "GP_Variance",
            "GP_Variance_Pct",
            "Margin_Variance_PP",
        }

        missing_columns = sorted(
            required_columns - set(dimension_variance.columns)
        )

        if missing_columns:
            raise ValueError(
                "Faltan columnas para Rules Engine: "
                + ", ".join(missing_columns)
            )

        alerts: list[dict] = []

        for _, row in dimension_variance.iterrows():
            result = self._evaluate_metric(
                metric="Gross Profit",
                amount=float(row["GP_Variance"]),
                percentage=float(row["GP_Variance_Pct"]),
                config=config,
            )

            result.update(
                {
                    "Dimension": dimension,
                    "Business_Value": row[dimension],
                    "Margin_Variance_PP": float(
                        row["Margin_Variance_PP"]
                    ),
                }
            )

            alerts.append(result)

        alert_dataframe = pd.DataFrame(alerts)

        if alert_dataframe.empty:
            return alert_dataframe

        severity_order = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Normal": 0,
        }

        alert_dataframe["Severity_Order"] = (
            alert_dataframe["Severity"]
            .map(severity_order)
            .fillna(0)
        )

        alert_dataframe = (
            alert_dataframe
            .sort_values(
                [
                    "Severity_Order",
                    "Absolute_Amount",
                ],
                ascending=[False, False],
            )
            .drop(columns=["Severity_Order"])
            .reset_index(drop=True)
        )

        return alert_dataframe

    def material_alerts(
        self,
        alerts: pd.DataFrame,
    ) -> pd.DataFrame:
        """Returns only alerts that exceeded configured thresholds."""

        if alerts.empty:
            return alerts.copy()

        return (
            alerts[alerts["Is_Material"]]
            .reset_index(drop=True)
        )

    def alert_summary(
        self,
        alerts: pd.DataFrame,
    ) -> dict:
        """Returns alert counts by severity and direction."""

        if alerts.empty:
            return {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "favorable": 0,
                "unfavorable": 0,
            }

        material = self.material_alerts(alerts)

        return {
            "total": int(len(material)),
            "critical": int(
                (material["Severity"] == "Critical").sum()
            ),
            "high": int(
                (material["Severity"] == "High").sum()
            ),
            "medium": int(
                (material["Severity"] == "Medium").sum()
            ),
            "low": int(
                (material["Severity"] == "Low").sum()
            ),
            "favorable": int(
                (material["Direction"] == "Favorable").sum()
            ),
            "unfavorable": int(
                (
                    material["Direction"]
                    == "Unfavorable"
                ).sum()
            ),
        }

    def _evaluate_metric(
        self,
        metric: str,
        amount: float,
        percentage: float,
        config: RuleConfig,
        is_margin: bool = False,
    ) -> dict:
        """Evaluates one metric against materiality rules."""

        if metric not in self.SUPPORTED_METRICS:
            raise ValueError(
                f"Métrica no soportada: {metric}"
            )

        absolute_amount = abs(amount)
        absolute_percentage = abs(percentage)

        if is_margin:
            amount_test = (
                absolute_percentage
                >= config.percentage_threshold
            )
            percentage_test = amount_test
        else:
            amount_test = (
                absolute_amount
                >= config.amount_threshold
            )
            percentage_test = (
                absolute_percentage
                >= config.percentage_threshold
            )

        logic = config.evaluation_logic.upper()

        if logic == "AND":
            is_material = amount_test and percentage_test
        else:
            is_material = amount_test or percentage_test

        severity = self._calculate_severity(
            absolute_amount=absolute_amount,
            absolute_percentage=absolute_percentage,
            is_material=is_material,
            is_margin=is_margin,
            config=config,
        )

        direction = self._determine_direction(
            metric=metric,
            value=amount,
        )

        owner = self._determine_owner(
            severity=severity,
        )

        rule_triggered = self._describe_rule(
            amount_test=amount_test,
            percentage_test=percentage_test,
            config=config,
            is_margin=is_margin,
        )

        return {
            "Metric": metric,
            "Variance_Amount": amount,
            "Variance_Percentage": percentage,
            "Absolute_Amount": absolute_amount,
            "Absolute_Percentage": absolute_percentage,
            "Amount_Threshold_Passed": amount_test,
            "Percentage_Threshold_Passed": percentage_test,
            "Evaluation_Logic": logic,
            "Is_Material": bool(is_material),
            "Severity": severity,
            "Direction": direction,
            "Escalation_Owner": owner,
            "Rule_Triggered": rule_triggered,
        }

    @staticmethod
    def _determine_direction(
        metric: str,
        value: float,
    ) -> str:
        """Applies financial logic to favorable/unfavorable direction."""

        if value == 0:
            return "Neutral"

        if metric == "Cost":
            return (
                "Unfavorable"
                if value > 0
                else "Favorable"
            )

        return (
            "Favorable"
            if value > 0
            else "Unfavorable"
        )

    @staticmethod
    def _determine_owner(
        severity: str,
    ) -> str:
        owner_map = {
            "Critical": "CFO / Finance Director",
            "High": "Finance Manager",
            "Medium": "Business Controller",
            "Low": "Analyst / Controller",
            "Normal": "No escalation",
        }

        return owner_map[severity]

    @staticmethod
    def _calculate_severity(
        absolute_amount: float,
        absolute_percentage: float,
        is_material: bool,
        is_margin: bool,
        config: RuleConfig,
    ) -> str:
        if not is_material:
            return "Normal"

        if is_margin:
            percentage_ratio = (
                absolute_percentage
                / config.percentage_threshold
                if config.percentage_threshold
                else 0.0
            )

            maximum_ratio = percentage_ratio
        else:
            amount_ratio = (
                absolute_amount
                / config.amount_threshold
                if config.amount_threshold
                else 0.0
            )

            percentage_ratio = (
                absolute_percentage
                / config.percentage_threshold
                if config.percentage_threshold
                else 0.0
            )

            maximum_ratio = max(
                amount_ratio,
                percentage_ratio,
            )

        if maximum_ratio >= config.critical_multiplier:
            return "Critical"

        if maximum_ratio >= config.high_multiplier:
            return "High"

        if maximum_ratio >= 1.0:
            return "Medium"

        return "Low"

    @staticmethod
    def _describe_rule(
        amount_test: bool,
        percentage_test: bool,
        config: RuleConfig,
        is_margin: bool,
    ) -> str:
        if is_margin:
            if percentage_test:
                return (
                    "Margin threshold exceeded: "
                    f"{config.percentage_threshold:.1%}"
                )

            return "No materiality threshold exceeded"

        triggered: list[str] = []

        if amount_test:
            triggered.append(
                "Amount threshold exceeded "
                f"(${config.amount_threshold:,.0f})"
            )

        if percentage_test:
            triggered.append(
                "Percentage threshold exceeded "
                f"({config.percentage_threshold:.1%})"
            )

        if not triggered:
            return "No materiality threshold exceeded"

        return f" {config.evaluation_logic.upper()} ".join(
            triggered
        )