# FIP Enterprise V2 — Demo Runbook

## Start

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run backend/enterprise_v2.py --server.port 8504
```

## Pre-demo checks

- Open `http://localhost:8504`.
- Confirm Actuals, Budget and Working Capital are active in Data Center.
- Confirm the default period returns data.
- Allow pop-ups for localhost so the Executive Report opens in a new tab.
- Close unrelated browser tabs and maximize the presentation window.

## Recommended 12-minute story

### 1. Data governance — 2 minutes
Show Data Center, quality scores, semantic mapping and active version control.

### 2. Executive overview — 2 minutes
Select YTD or Q2. Explain Revenue, GP, Margin, gauges and operational KPIs.

### 3. Explain the result — 3 minutes
Open Financial Performance and Drivers & Root Cause. Use Variance Bridge and the dominant root-cause path.

### 4. Find value — 2 minutes
Open Opportunities & Simulation. Show margin recovery, growth upside and one scenario.

### 5. Turn insight into action — 2 minutes
Open Risk & Actions. Show CFO Radar, AI Controller and an accountable management action.

### 6. Deliver the output — 1 minute
Open Executive Report in a new tab and show Print / Save as PDF.

## Demo safety

- Do not change active Data Lake versions during the presentation.
- Avoid extreme simulator assumptions.
- Do not delete management actions.
- If a selected month is empty, switch to YTD or Full Year.
- If pop-ups are blocked, allow them and click Generate Executive Report again.
