# Financial Intelligence Platform — Project State

## Release

**FIP Enterprise V2.0 — Production Candidate**  
Freeze date: 2026-07-15

## Architecture Status

The V2 architecture is frozen. New work must not alter the established Engine → Repository/Service → Workspace/UI pattern without a formal V3 decision.

## Active Data Lake Versions

- Actuals: `actuals_20260715_082300_0104ef`
- Budget: `budget_20260715_092413_325b8c`
- Working Capital: `working_capital_20260715_082433_43ba0d`

## Completed Scope

- Enterprise UX and workspace shell
- Data Center with semantic mapping and version activation
- Actuals, Budget and Working Capital ingestion
- Month, Quarter, Semester, YTD and Full Year time intelligence
- Actual vs Budget KPI alignment
- Full P&L Intelligence
- Working Capital Intelligence
- Variance Bridge and drill-down
- Root Cause Intelligence
- Profitability and concentration matrix
- Opportunity Finder
- Financial Impact Simulator
- CFO Radar
- AI Controller deterministic narrative
- Executive Alerts and Action Center
- AI Executive Report in a new browser tab
- Print / Save as PDF through the browser
- Mission Control executive tab navigation

## Frozen Presentation Flow

1. Data Center — show active versions and quality.
2. Mission Control — select YTD or Quarter.
3. Executive Overview — health, KPIs and gauges.
4. Financial Performance — Full P&L, Working Capital and Variance Bridge.
5. Drivers & Root Cause — explain the variance.
6. Opportunities & Simulation — show upside and scenario impact.
7. Risk & Actions — CFO Radar, AI Controller and Action Center.
8. Executive Report — open in new tab and print/save as PDF.

## Known Boundaries

- Forecast / Latest Estimate is not included in this production candidate.
- EBITDA is shown only when depreciation/amortization data exists.
- DSO and DPO are labeled as proxies and require compatible period activity.
- AI Controller is deterministic and does not require an external LLM.
- Missing financial fields are shown as `N/A`; no values are fabricated.

## Dependency Policy

Approved runtime dependencies are limited to Streamlit, Pandas, NumPy, OpenPyXL and Plotly. ReportLab and Matplotlib are intentionally not required.

## Next Version

V3 candidates: Forecast & Latest Estimate, configurable company branding, authentication/roles, deployment hardening, audit logging and optional LLM enrichment.
