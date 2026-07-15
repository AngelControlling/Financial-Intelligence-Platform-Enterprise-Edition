from __future__ import annotations
from models.executive_alert import ExecutiveAlert
from models.management_action import ManagementAction

class ManagementActionEngine:
    def propose(
        self,
        alerts: list[ExecutiveAlert],
        *,
        period_label: str,
        max_actions: int = 8,
    ) -> list[ManagementAction]:
        proposals = []
        for alert in alerts[:max_actions]:
            action_type = self._action_type(alert)
            priority = {
                "critical": "Critical",
                "high": "High",
                "medium": "Medium",
                "success": "Opportunity",
            }.get(alert.severity, "Medium")

            proposals.append(
                ManagementAction(
                    title=f"{action_type}: {alert.dimension_value or alert.category}",
                    description=alert.recommended_action,
                    action_type=action_type,
                    priority=priority,
                    period_label=period_label,
                    source_alert_id=alert.alert_id,
                    source_dimension=alert.dimension,
                    source_value=alert.dimension_value,
                    expected_impact=abs(alert.variance_value)
                    if alert.variance_value < 0 else 0.0,
                    impact_metric=alert.category,
                )
            )
        return proposals

    @staticmethod
    def _action_type(alert: ExecutiveAlert) -> str:
        if alert.severity == "success":
            return "Growth Opportunity"
        if alert.category == "Margin":
            return "Margin Recovery"
        if alert.category == "Revenue":
            return "Revenue Recovery"
        if alert.category == "Gross Profit":
            return "Profit Recovery"
        return "Management Review"
