from __future__ import annotations

import base64
import json

import streamlit.components.v1 as components


def render_executive_report_launcher(
    report_html: str,
) -> None:
    """
    Render a native browser button that opens the report in a new tab.

    The browser tab contains its own Print / Save as PDF button.
    """

    encoded = base64.b64encode(
report_html.encode("utf-8")
    ).decode("ascii")

    launcher = f"""
    <!doctype html>
    <html>
    <head>
    <style>
    body {{
margin: 0;
font-family: "Segoe UI", Arial, sans-serif;
background: transparent;
    }}
    .report-launcher {{
display: flex;
justify-content: space-between;
gap: 14px;
align-items: center;
padding: 15px 17px;
border: 1px solid #1d3a5f;
border-radius: 13px;
background:
    linear-gradient(
        145deg,
        rgba(16,36,61,.98),
        rgba(8,22,39,.98)
    );
color: white;
    }}
    .title {{
font-size: 16px;
font-weight: 800;
    }}
    .subtitle {{
margin-top: 4px;
color: #8fa5bd;
font-size: 12px;
    }}
    button {{
min-width: 220px;
padding: 12px 16px;
border: 0;
border-radius: 10px;
color: white;
background:
    linear-gradient(90deg, #2f80ed, #7457e8);
font-size: 13px;
font-weight: 800;
cursor: pointer;
box-shadow: 0 8px 18px rgba(47,128,237,.20);
    }}
    button:hover {{
filter: brightness(1.08);
    }}
    @media (max-width: 650px) {{
.report-launcher {{
    flex-direction: column;
    align-items: stretch;
}}
button {{
    min-width: 0;
    width: 100%;
}}
    }}
    </style>
    </head>
    <body>
    <div class="report-launcher">
<div>
    <div class="title">Executive Financial Report</div>
    <div class="subtitle">
        Open a clean, print-ready CFO report in a new tab.
    </div>
</div>
<button id="open-report">
    Generate Executive Report
</button>
    </div>

    <script>
    const encodedReport = {json.dumps(encoded)};

    document
.getElementById("open-report")
.addEventListener("click", function () {{
    const binary = atob(encodedReport);
    const bytes = new Uint8Array(binary.length);

    for (let index = 0; index < binary.length; index++) {{
        bytes[index] = binary.charCodeAt(index);
    }}

    const blob = new Blob(
        [bytes],
        {{ type: "text/html;charset=utf-8" }}
    );
    const reportUrl = URL.createObjectURL(blob);
    const reportWindow = window.open(
        reportUrl,
        "_blank",
        "noopener,noreferrer"
    );

    if (!reportWindow) {{
        alert(
            "The browser blocked the new tab. "
            + "Please allow pop-ups for this application."
        );
    }}

    setTimeout(
        () => URL.revokeObjectURL(reportUrl),
        60000
    );
}});
    </script>
    </body>
    </html>
    """

    components.html(
launcher,
height=105,
scrolling=False,
    )
