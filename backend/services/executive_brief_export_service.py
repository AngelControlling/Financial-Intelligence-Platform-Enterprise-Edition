from __future__ import annotations

import csv
from html import escape
from io import StringIO

from models.executive_brief import ExecutiveBrief


class ExecutiveBriefExportService:
    """Exports the Executive Brief as standalone HTML and CSV."""

    def to_html(
        self,
        brief: ExecutiveBrief,
        *,
        company: str,
        currency: str,
    ) -> bytes:
        risk_items = "".join(
            f"<li>{escape(item)}</li>"
            for item in brief.risks
        ) or "<li>No material risks detected.</li>"

        opportunity_items = "".join(
            f"<li>{escape(item)}</li>"
            for item in brief.opportunities
        ) or "<li>No material opportunities detected.</li>"

        action_items = "".join(
            f"<li>{escape(item)}</li>"
            for item in brief.actions
        ) or "<li>No open management actions.</li>"

        kpi_cards = "".join(
            self._kpi_card(
                label,
                value,
            )
            for label, value in brief.kpis.items()
        )

        html = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{escape(brief.title)}</title>
            <style>
                body {{
                    margin: 0;
                    font-family: Segoe UI, Arial, sans-serif;
                    background: #07111f;
                    color: #f4f7fb;
                }}
                .container {{
                    max-width: 1280px;
                    margin: auto;
                    padding: 28px;
                }}
                .header, .section, .kpi {{
                    background: #10243d;
                    border: 1px solid #1d3a5f;
                    border-radius: 14px;
                    box-shadow: 0 10px 28px rgba(0,0,0,.22);
                }}
                .header {{
                    padding: 22px;
                }}
                .eyebrow {{
                    color: #22d3ee;
                    font-size: 12px;
                    font-weight: 800;
                    letter-spacing: .08em;
                    text-transform: uppercase;
                }}
                h1 {{
                    margin: 8px 0 4px;
                }}
                .muted {{
                    color: #8fa5bd;
                }}
                .headline {{
                    margin-top: 18px;
                    font-size: 20px;
                    font-weight: 750;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 14px;
                    margin-top: 18px;
                }}
                .kpi {{
                    padding: 16px;
                }}
                .kpi-label {{
                    color: #8fa5bd;
                    font-size: 12px;
                    text-transform: uppercase;
                    font-weight: 800;
                }}
                .kpi-value {{
                    font-size: 24px;
                    font-weight: 850;
                    margin-top: 8px;
                }}
                .section {{
                    margin-top: 16px;
                    padding: 18px;
                }}
                .two-col {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                }}
                li {{
                    margin-bottom: 8px;
                    color: #c7d4e3;
                }}
                @media (max-width: 800px) {{
                    .two-col {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="eyebrow">Financial Intelligence Platform</div>
                    <h1>{escape(brief.title)}</h1>
                    <div class="muted">
                        {escape(company)} · {escape(brief.period_label)} ·
                        Actual vs {escape(brief.comparison_label)} ·
                        {escape(currency)}
                    </div>
                    <div class="headline">{escape(brief.headline)}</div>
                </div>

                <div class="grid">{kpi_cards}</div>

                <div class="section">
                    <h2>Financial Performance</h2>
                    <p>{escape(brief.financial_summary)}</p>
                    <h2>Operational Performance</h2>
                    <p>{escape(brief.operational_summary)}</p>
                </div>

                <div class="two-col">
                    <div class="section">
                        <h2>Risks</h2>
                        <ul>{risk_items}</ul>
                    </div>
                    <div class="section">
                        <h2>Opportunities</h2>
                        <ul>{opportunity_items}</ul>
                    </div>
                </div>

                <div class="section">
                    <h2>Open Management Actions</h2>
                    <ul>{action_items}</ul>
                </div>
            </div>
        </body>
        </html>
        """

        return html.encode("utf-8")

    def to_csv(
        self,
        brief: ExecutiveBrief,
    ) -> bytes:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Section",
                "Item",
                "Value",
            ]
        )

        for label, value in brief.kpis.items():
            writer.writerow(
                [
                    "KPI",
                    label,
                    value,
                ]
            )

        writer.writerow(
            [
                "Summary",
                "Headline",
                brief.headline,
            ]
        )
        writer.writerow(
            [
                "Summary",
                "Financial",
                brief.financial_summary,
            ]
        )
        writer.writerow(
            [
                "Summary",
                "Operational",
                brief.operational_summary,
            ]
        )

        for item in brief.risks:
            writer.writerow(
                [
                    "Risk",
                    "",
                    item,
                ]
            )

        for item in brief.opportunities:
            writer.writerow(
                [
                    "Opportunity",
                    "",
                    item,
                ]
            )

        for item in brief.actions:
            writer.writerow(
                [
                    "Action",
                    "",
                    item,
                ]
            )

        return output.getvalue().encode(
            "utf-8-sig"
        )

    @staticmethod
    def _kpi_card(
        label: str,
        value,
    ) -> str:
        if "%" in label:
            formatted = (
                f"{float(value):.1%}"
            )
        elif "pp" in label:
            formatted = (
                f"{float(value) * 100:+.2f} pp"
            )
        elif label in {
            "Revenue",
            "Gross Profit",
        }:
            formatted = (
                f"${float(value):,.0f}"
            )
        else:
            formatted = (
                f"{float(value):,.1f}"
            )

        return (
            '<div class="kpi">'
            f'<div class="kpi-label">{escape(label)}</div>'
            f'<div class="kpi-value">{escape(formatted)}</div>'
            '</div>'
        )
