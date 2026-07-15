from __future__ import annotations

from datetime import datetime
from html import escape

from models.controller_narrative import ControllerNarrative
from models.executive_brief import ExecutiveBrief


class AIExecutiveReportService:
    """Build a print-ready Executive Report enhanced by AI Controller."""

    def build_html(
        self,
        *,
        brief: ExecutiveBrief,
        narrative: ControllerNarrative,
        company: str,
        currency: str,
        controller_name: str = "Finance Controller",
    ) -> str:
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        kpi_cards = "".join(
            self._kpi_card(label, value)
            for label, value in brief.kpis.items()
        )
        risks = self._list_items(
            brief.risks,
            "No material risks detected.",
            "risk",
        )
        opportunities = self._list_items(
            brief.opportunities,
            "No material opportunities detected.",
            "opportunity",
        )
        actions = self._list_items(
            narrative.recommended_actions,
            "No management actions recommended.",
            "action",
        )
        open_actions = self._list_items(
            brief.actions,
            "No open management actions.",
            "plan",
        )

        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(brief.title)} - {escape(brief.period_label)}</title>
<style>
:root {{
    --navy:#07111f; --panel:#10243d; --border:#1d3a5f;
    --text:#17263a; --muted:#62758a; --light:#eef4f9;
    --blue:#2f80ed; --cyan:#22d3ee; --green:#15803d;
    --amber:#b45309; --red:#b91c1c; --purple:#7457e8;
}}
* {{ box-sizing:border-box; }}
body {{
    margin:0; background:#e9eff5; color:var(--text);
    font-family:"Segoe UI",Arial,sans-serif;
}}
.toolbar {{
    position:sticky; top:0; z-index:20; display:flex;
    justify-content:flex-end; gap:10px; padding:12px 18px;
    background:rgba(7,17,31,.96); border-bottom:1px solid var(--border);
}}
.toolbar button {{
    border:1px solid #365a7f; border-radius:9px; padding:10px 16px;
    color:white; background:#163654; font-weight:700; cursor:pointer;
}}
.toolbar button.primary {{
    background:linear-gradient(90deg,var(--blue),var(--purple));
    border-color:transparent;
}}
.report {{
    width:min(1120px,calc(100% - 28px)); margin:24px auto;
    background:white; border-radius:16px; overflow:hidden;
    box-shadow:0 16px 40px rgba(7,17,31,.18);
}}
.header {{
    padding:28px 32px; color:white;
    background:radial-gradient(circle at 90% 10%,rgba(47,128,237,.28),transparent 34%),
               linear-gradient(145deg,#10243d,#07111f);
}}
.eyebrow {{ color:var(--cyan); font-size:11px; font-weight:850; letter-spacing:.10em; }}
h1 {{ margin:8px 0 4px; font-size:30px; letter-spacing:-.035em; }}
.meta {{ color:#c7d4e3; font-size:13px; }}
.headline {{ margin-top:20px; max-width:900px; font-size:19px; line-height:1.45; font-weight:750; }}
.badges {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:15px; }}
.badge {{ border:1px solid rgba(255,255,255,.25); border-radius:999px; padding:6px 10px; font-size:11px; font-weight:800; }}
.content {{ padding:26px 32px 32px; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
.kpi {{ padding:14px; border:1px solid #c8d5e3; border-radius:12px; background:var(--light); }}
.kpi-label {{ color:var(--muted); font-size:10px; font-weight:850; letter-spacing:.05em; text-transform:uppercase; }}
.kpi-value {{ margin-top:7px; font-size:23px; font-weight:850; letter-spacing:-.035em; }}
.section {{ margin-top:18px; padding:18px; border:1px solid #d3dee8; border-radius:12px; }}
.section h2 {{ margin:0 0 9px; font-size:16px; }}
.section p {{ margin:0; color:#3f5368; font-size:14px; line-height:1.58; }}
.ai-section {{ border-left:5px solid var(--purple); background:linear-gradient(145deg,#fbfaff,#f4f1ff); }}
.two-column {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.item {{ margin-top:8px; padding:10px 11px; border-left:4px solid #8fa5bd; border-radius:7px; background:#f6f9fc; color:#3f5368; font-size:13px; line-height:1.45; }}
.item.risk {{ border-left-color:var(--red); }}
.item.opportunity {{ border-left-color:var(--green); }}
.item.action {{ border-left-color:var(--purple); }}
.item.plan {{ border-left-color:var(--blue); }}
.footer {{ display:flex; justify-content:space-between; gap:14px; padding:15px 32px; color:#7b8fa3; background:#f3f7fa; border-top:1px solid #d7e1ea; font-size:11px; }}
@media (max-width:780px) {{
    .kpi-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .two-column {{ grid-template-columns:1fr; }}
    .content,.header {{ padding-left:18px; padding-right:18px; }}
}}
@page {{ size:A4; margin:10mm; }}
@media print {{
    body {{ background:white; }}
    .toolbar {{ display:none !important; }}
    .report {{ width:100%; margin:0; border-radius:0; box-shadow:none; }}
    .header,.kpi,.section,.item {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .kpi,.section,.item {{ break-inside:avoid; }}
}}
</style>
</head>
<body>
<div class="toolbar">
    <button onclick="window.close()">Back to Dashboard</button>
    <button class="primary" onclick="window.print()">Print / Save as PDF</button>
</div>
<main class="report">
<header class="header">
    <div class="eyebrow">FINANCIAL INTELLIGENCE PLATFORM</div>
    <h1>Executive Financial Report</h1>
    <div class="meta">{escape(company)} · {escape(brief.period_label)} · Actual vs {escape(brief.comparison_label)} · {escape(currency)}</div>
    <div class="headline">{escape(narrative.executive_summary)}</div>
    <div class="badges">
        <span class="badge">Priority: {escape(narrative.management_priority)}</span>
        <span class="badge">Confidence: {narrative.confidence_score:.0%}</span>
    </div>
</header>
<div class="content">
    <section class="kpi-grid">{kpi_cards}</section>
    <section class="section ai-section"><h2>What Happened</h2><p>{escape(narrative.what_happened)}</p></section>
    <section class="section ai-section"><h2>Why It Happened</h2><p>{escape(narrative.why_it_happened)}</p></section>
    <div class="two-column">
        <section class="section"><h2>Business Risk</h2><p>{escape(narrative.business_risk)}</p></section>
        <section class="section"><h2>If No Action Is Taken</h2><p>{escape(narrative.no_action_outlook)}</p></section>
    </div>
    <section class="section"><h2>Recommended Management Actions</h2>{actions}</section>
    <div class="two-column">
        <section class="section"><h2>Top Risks</h2>{risks}</section>
        <section class="section"><h2>Top Opportunities</h2>{opportunities}</section>
    </div>
    <section class="section"><h2>Open Management Action Plan</h2>{open_actions}</section>
</div>
<footer class="footer">
    <span>Controller: {escape(controller_name)}</span>
    <span>Generated: {escape(generated_at)}</span>
    <span>Confidential Management Information</span>
</footer>
</main>
</body>
</html>"""

    @staticmethod
    def _list_items(items: list[str], empty_text: str, item_class: str) -> str:
        values = items or [empty_text]
        return "".join(
            f'<div class="item {escape(item_class)}">{escape(item)}</div>'
            for item in values[:8]
        )

    @staticmethod
    def _kpi_card(label: str, value) -> str:
        numeric = float(value)
        if label in {"Revenue", "Gross Profit"}:
            formatted = f"${numeric:,.0f}"
        elif "%" in label:
            formatted = f"{numeric:.1%}"
        elif "pp" in label:
            formatted = f"{numeric * 100:+.2f} pp"
        else:
            formatted = f"{numeric:,.1f}"

        return (
            '<div class="kpi">'
            f'<div class="kpi-label">{escape(label)}</div>'
            f'<div class="kpi-value">{escape(formatted)}</div>'
            '</div>'
        )
