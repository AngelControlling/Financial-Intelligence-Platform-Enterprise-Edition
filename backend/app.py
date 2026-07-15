from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from engines.data_profiler import DataProfiler
from engines.excel_reader import ExcelReader
from engines.executive_narrative_engine import ExecutiveNarrativeEngine
from engines.freight_intelligence_engine import FreightIntelligenceEngine
from engines.freight_kpi_engine import FreightKPIEngine
from engines.insight_engine import InsightEngine
from engines.ai_controller_engine import AIControllerEngine
from engines.baseline_classification_engine import (
    BaselineClassificationEngine,
)
from engines.recommendation_engine import RecommendationEngine
from engines.rules_engine import RuleConfig, RulesEngine
from engines.semantic_mapping_engine import SemanticMappingEngine
from engines.time_intelligence_engine import TimeIntelligenceEngine
from engines.variance_engine import VarianceEngine
from engines.working_capital_aging_engine import (
    AgingConfig,
    WorkingCapitalAgingEngine,
)
from engines.working_capital_semantic_mapping_engine import (
    WorkingCapitalSemanticMappingEngine,
)


st.set_page_config(
    page_title="Financial Intelligence Platform",
    page_icon="📊",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --bg-main: #07111f;
        --bg-panel: #0d1b2f;
        --bg-panel-2: #10243d;
        --bg-sidebar: #081426;
        --border: #1c3657;
        --text-main: #f4f7fb;
        --text-muted: #9fb2c8;
        --cyan: #22d3ee;
        --teal: #14b8a6;
        --blue: #2f80ed;
        --purple: #8b5cf6;
        --green: #22c55e;
        --red: #ef4444;
        --amber: #f59e0b;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", Inter, Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(47, 128, 237, 0.10), transparent 30%),
            linear-gradient(180deg, #07111f 0%, #091525 100%);
        color: var(--text-main);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081426 0%, #0a1a31 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main);
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {
        color: var(--text-muted) !important;
    }

    .block-container {
        max-width: 1600px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4 {
        color: var(--text-main) !important;
        letter-spacing: -0.02em;
    }

    p, span, label, div {
        color: inherit;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(16, 36, 61, 0.96), rgba(11, 27, 46, 0.96));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.82rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-weight: 700;
    }

    [data-testid="stMetricDelta"] svg {
        fill: currentColor;
    }

    [data-testid="stTabs"] button {
        color: var(--text-muted);
        font-weight: 600;
        border-radius: 10px 10px 0 0;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan) !important;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div {
        background-color: #0b1a2d !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(90deg, var(--blue), var(--purple));
        color: white;
        border: 0;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.55rem 1rem;
        box-shadow: 0 8px 18px rgba(47, 128, 237, 0.25);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
    }

    [data-testid="stDataFrame"] {
        background: rgba(13, 27, 47, 0.92);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        background: rgba(13, 27, 47, 0.92);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid var(--border);
    }

    hr {
        border-color: var(--border);
    }

    .fip-card {
        background: linear-gradient(180deg, rgba(16, 36, 61, 0.96), rgba(11, 27, 46, 0.96));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    }

    .fip-title {
        color: var(--text-main);
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .fip-muted {
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    .traffic-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(160px, 1fr));
        gap: 12px;
        margin: 10px 0 18px 0;
    }

    .traffic-card {
        background: linear-gradient(180deg, rgba(16, 36, 61, 0.98), rgba(11, 27, 46, 0.98));
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
    }

    .traffic-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 8px;
    }

    .traffic-title {
        color: var(--text-muted);
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .traffic-value {
        color: var(--text-main);
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .traffic-subtitle {
        color: var(--text-muted);
        font-size: 0.78rem;
    }

    .traffic-light {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        box-shadow: 0 0 14px currentColor;
        flex: 0 0 auto;
    }

    .signal-green {
        color: #22c55e;
        background: #22c55e;
        border: 2px solid #86efac;
    }

    .signal-amber {
        color: #f59e0b;
        background: #f59e0b;
        border: 2px solid #fcd34d;
    }

    .signal-red {
        color: #ef4444;
        background: #ef4444;
        border: 2px solid #fca5a5;
    }

    .signal-blue {
        color: #2f80ed;
        background: #2f80ed;
        border: 2px solid #93c5fd;
    }

    .signal-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
        border: 1px solid currentColor;
        background: rgba(255,255,255,0.03);
    }

    .badge-green { color: #4ade80; }
    .badge-amber { color: #fbbf24; }
    .badge-red { color: #f87171; }
    .badge-blue { color: #60a5fa; }

    @media (max-width: 1000px) {
        .traffic-grid {
            grid-template-columns: repeat(2, minmax(160px, 1fr));
        }
    }

    @media (max-width: 650px) {
        .traffic-grid {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#dce8f5"},
    "title_font": {"color": "#f4f7fb", "size": 18},
    "legend": {"font": {"color": "#dce8f5"}},
    "xaxis": {
        "gridcolor": "#1b314f",
        "zerolinecolor": "#1b314f",
        "tickfont": {"color": "#9fb2c8"},
        "title_font": {"color": "#9fb2c8"},
    },
    "yaxis": {
        "gridcolor": "#1b314f",
        "zerolinecolor": "#1b314f",
        "tickfont": {"color": "#9fb2c8"},
        "title_font": {"color": "#9fb2c8"},
    },
}

FIP_COLOR_SEQUENCE = [
    "#14b8a6",
    "#2f80ed",
    "#8b5cf6",
    "#22d3ee",
    "#f59e0b",
    "#22c55e",
    "#ef4444",
]


def apply_fip_chart_style(figure):
    """Apply the Financial Intelligence Platform visual theme."""
    figure.update_layout(**PLOTLY_LAYOUT)
    return figure



def signal_from_rule(
    severity: str,
    direction: str,
) -> tuple[str, str, str]:
    """Return CSS class, label and icon for CFO traffic-light signals."""
    severity_value = str(severity).strip().title()
    direction_value = str(direction).strip().title()

    if severity_value in {"Critical", "High"}:
        if direction_value == "Unfavorable":
            return "signal-red", "Action Required", "🔴"
        return "signal-green", "Strong Favorable", "🟢"

    if severity_value in {"Medium", "Low"}:
        return "signal-amber", "Monitor", "🟡"

    return "signal-blue", "Within Tolerance", "🔵"


def render_signal_card(
    title: str,
    value: str,
    severity: str,
    direction: str,
    subtitle: str,
) -> None:
    """Render one executive traffic-light card."""
    css_class, label, icon = signal_from_rule(
        severity,
        direction,
    )

    st.markdown(
        f"""
        <div class="traffic-card">
            <div class="traffic-header">
                <div class="traffic-title">{title}</div>
                <div class="traffic-light {css_class}"></div>
            </div>
            <div class="traffic-value">{value}</div>
            <div class="traffic-subtitle">{icon} {label} · {subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(
    severity: str,
    direction: str,
) -> str:
    """Create a compact HTML severity badge."""
    css_class, label, icon = signal_from_rule(
        severity,
        direction,
    )

    badge_class = {
        "signal-green": "badge-green",
        "signal-amber": "badge-amber",
        "signal-red": "badge-red",
        "signal-blue": "badge-blue",
    }[css_class]

    return (
        f'<span class="signal-badge {badge_class}">'
        f'{icon} {label}</span>'
    )




def render_floating_elevenlabs_agent() -> None:
    """Inject a floating ElevenLabs agent into the Streamlit parent page."""
    components.html(
        """
        <script>
        (function () {
            const parentDocument = window.parent.document;
            const widgetId = "fip-elevenlabs-floating-agent";
            const scriptId = "fip-elevenlabs-widget-script";

            if (!parentDocument.getElementById(scriptId)) {
                const script = parentDocument.createElement("script");
                script.id = scriptId;
                script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
                script.async = true;
                script.type = "text/javascript";
                parentDocument.head.appendChild(script);
            }

            if (!parentDocument.getElementById(widgetId)) {
                const container = parentDocument.createElement("div");
                container.id = widgetId;
                container.style.position = "fixed";
                container.style.right = "24px";
                container.style.bottom = "24px";
                container.style.zIndex = "999999";
                container.style.pointerEvents = "auto";

                const widget = parentDocument.createElement(
                    "elevenlabs-convai"
                );
                widget.setAttribute(
                    "agent-id",
                    "agent_8201kxf93n0eegj898dksdwwpwfv"
                );

                container.appendChild(widget);
                parentDocument.body.appendChild(container);
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )




def render_freight_mode_workspace(
    mode_name: str,
    mode_data: pd.DataFrame,
    freight_engine: FreightIntelligenceEngine,
    kpi_engine: FreightKPIEngine,
) -> None:
    """Render route, customer and shipment analysis for one freight mode."""

    st.subheader(f"{mode_name} Freight Performance")

    if mode_data.empty:
        st.warning(
            f"No existen registros clasificados como {mode_name}."
        )

        st.caption(
            "Revisa Data Quality → Mode Classification Audit "
            "para ver cómo fueron normalizados los valores originales."
        )
        return

    summary = kpi_engine.executive_summary(
        mode_data
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    metric_1.metric(
        f"{mode_name} Revenue",
        f"${summary['actual_revenue']:,.0f}",
    )
    metric_2.metric(
        f"{mode_name} GP",
        f"${summary['actual_gp']:,.0f}",
    )
    metric_3.metric(
        f"{mode_name} GP Margin",
        f"{summary['actual_gp_margin']:.1%}",
    )

    if mode_name == "Ocean":
        metric_4.metric(
            "TEUs",
            f"{summary['teus']:,.1f}",
        )
    else:
        metric_4.metric(
            "Tons",
            f"{summary['weight_tons']:,.1f}",
        )

    unit_1, unit_2, unit_3 = st.columns(3)

    if mode_name == "Ocean":
        unit_1.metric(
            "Revenue / TEU",
            f"${summary['revenue_per_teu']:,.0f}",
        )
        unit_2.metric(
            "GP / TEU",
            f"${summary['gp_per_teu']:,.0f}",
        )
    else:
        unit_1.metric(
            "Revenue / Ton",
            f"${summary['revenue_per_ton']:,.0f}",
        )
        unit_2.metric(
            "GP / Ton",
            f"${summary['gp_per_ton']:,.0f}",
        )

    unit_3.metric(
        "GP / Shipment",
        f"${summary['gp_per_shipment']:,.0f}",
    )

    dimension_labels = {
        "Trade Lane": "trade_lane",
        "Customer": "customer",
        "Product": "product",
        "Origin": "origin",
        "Destination": "destination",
        "Forwarder": "forwarder",
    }

    selected_dimension_label = st.selectbox(
        f"Analyze {mode_name} by",
        options=list(dimension_labels.keys()),
        key=f"{mode_name.lower()}_analysis_dimension",
    )

    selected_dimension = dimension_labels[
        selected_dimension_label
    ]

    dimension_data = freight_engine.dimension_summary(
        mode_data,
        selected_dimension,
    )

    st.markdown(
        f"### Top {selected_dimension_label}"
    )

    valid_dimension_data = dimension_data[
        ~dimension_data[selected_dimension]
        .astype(str)
        .str.casefold()
        .isin(
            {
                "unassigned",
                "unclassified",
                "nan",
                "none",
                "",
            }
        )
    ].copy()

    if valid_dimension_data.empty:
        st.info(
            f"No hay valores válidos para {selected_dimension_label}. "
            "La dimensión aparece vacía o no fue reconocida en el archivo."
        )
        display_dimension_data = dimension_data
    else:
        display_dimension_data = valid_dimension_data

    st.dataframe(
        display_dimension_data.head(25),
        use_container_width=True,
        hide_index=True,
    )

    if not display_dimension_data.empty:
        chart_data = display_dimension_data.head(15)

        figure = px.bar(
            chart_data,
            x=selected_dimension,
            y="GP",
            color="GP_Variance",
            color_continuous_scale="Tealrose",
            text_auto=".3s",
            title=(
                f"{mode_name} GP by "
                f"{selected_dimension_label}"
            ),
            hover_data=[
                "Shipments",
                "Revenue",
                "Cost",
                "GP_Margin",
                "GP_per_Shipment",
            ],
        )

        figure = apply_fip_chart_style(
            figure
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    route_col, customer_col = st.columns(2)

    with route_col:
        st.markdown("### Top Routes")

        route_summary = freight_engine.dimension_summary(
            mode_data,
            "trade_lane",
        )

        route_summary = route_summary[
            ~route_summary["trade_lane"]
            .astype(str)
            .str.casefold()
            .isin(
                {
                    "unassigned",
                    "unclassified",
                    "nan",
                    "none",
                    "",
                }
            )
        ]

        if route_summary.empty:
            st.info(
                "No se detectaron rutas válidas. "
                "Cuando existan Origin y Destination, "
                "la plataforma construye Origin → Destination."
            )
        else:
            st.dataframe(
                route_summary.head(10),
                use_container_width=True,
                hide_index=True,
            )

    with customer_col:
        st.markdown("### Top Customers")

        customer_summary = freight_engine.dimension_summary(
            mode_data,
            "customer",
        )

        customer_summary = customer_summary[
            ~customer_summary["customer"]
            .astype(str)
            .str.casefold()
            .isin(
                {
                    "unassigned",
                    "unclassified",
                    "nan",
                    "none",
                    "",
                }
            )
        ]

        if customer_summary.empty:
            st.info(
                "No se detectaron clientes válidos en el archivo."
            )
        else:
            st.dataframe(
                customer_summary.head(10),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown("### Shipment Detail")

    detail_columns = [
        "shipment",
        "customer",
        "trade_lane",
        "origin",
        "destination",
        "product",
        "forwarder",
        "tons",
        "teus",
        "actual_revenue",
        "actual_cost",
        "actual_gp",
        "gp_margin",
        "gp_variance",
        "period",
    ]

    available_detail_columns = [
        column
        for column in detail_columns
        if column in mode_data.columns
    ]

    detail_data = (
        mode_data[available_detail_columns]
        .sort_values(
            "actual_gp",
            ascending=False,
        )
    )

    st.dataframe(
        detail_data.head(500),
        use_container_width=True,
        hide_index=True,
    )

    detail_csv = detail_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label=f"Download {mode_name} Shipment Detail",
        data=detail_csv,
        file_name=(
            f"{mode_name.lower()}_shipment_detail.csv"
        ),
        mime="text/csv",
        key=f"download_{mode_name.lower()}_detail",
    )


def render_working_capital_workspace() -> None:
    """Render the independent AR/AP Working Capital workspace."""
    working_capital_mapping_engine = (
        WorkingCapitalSemanticMappingEngine()
    )
    working_capital_aging_engine = (
        WorkingCapitalAgingEngine()
    )

    st.subheader("Working Capital Aging")

    st.caption(
        "Analiza cuentas por cobrar y cuentas por pagar "
        "por factura, vencimiento, cliente o proveedor."
    )

    working_capital_file = st.file_uploader(
        "Carga un archivo AR/AP",
        type=["xlsx", "xlsm", "csv"],
        key="working_capital_file",
        help=(
            "Una fila debe representar una factura, nota de crédito, "
            "documento abierto o solicitud de pago."
        ),
    )

    if working_capital_file is None:
        st.info(
            "Carga una base de Accounts Receivable o Accounts "
            "Payable para calcular la antigüedad de saldos."
        )
    else:
        try:
            wc_reader = ExcelReader(
                working_capital_file
            )

            wc_sheet_names = (
                wc_reader.get_sheet_names()
            )

            wc_loaded_sheets = (
                wc_reader.read_all_sheets()
            )

            wc_selected_sheet = st.selectbox(
                "Working Capital Sheet",
                options=wc_sheet_names,
                key="working_capital_sheet",
            )

            wc_source_data = wc_loaded_sheets[
                wc_selected_sheet
            ]

            wc_mapping_result = (
                working_capital_mapping_engine
                .map_dataframe(
                    wc_source_data
                )
            )

            if (
                wc_mapping_result
                .missing_required_columns
            ):
                st.error(
                    "Faltan columnas requeridas para "
                    "Working Capital Aging:"
                )

                st.write(
                    wc_mapping_result
                    .missing_required_columns
                )

                with st.expander(
                    "Ver mapeo de Working Capital"
                ):
                    st.write(
                        "**Columnas reconocidas**"
                    )
                    st.json(
                        wc_mapping_result
                        .mapped_columns
                    )

                    if (
                        wc_mapping_result
                        .unmapped_columns
                    ):
                        st.write(
                            "**Columnas no reconocidas**"
                        )
                        st.write(
                            wc_mapping_result
                            .unmapped_columns
                        )
            else:
                for warning in (
                    wc_mapping_result.warnings
                ):
                    st.warning(warning)

                wc_as_of_date = st.date_input(
                    "Aging As of Date",
                    value=pd.Timestamp.today().date(),
                    key="working_capital_as_of_date",
                )

                wc_prepared_data = (
                    working_capital_aging_engine
                    .prepare_data(
                        wc_mapping_result.dataframe,
                        config=AgingConfig.from_value(
                            wc_as_of_date
                        ),
                    )
                )

                filter_col1, filter_col2, filter_col3 = (
                    st.columns(3)
                )

                with filter_col1:
                    wc_analysis_type = st.selectbox(
                        "Analysis Type",
                        options=[
                            "All",
                            "Accounts Receivable",
                            "Accounts Payable",
                        ],
                        key="working_capital_type",
                    )

                working_type_map = {
                    "All": None,
                    "Accounts Receivable": "AR",
                    "Accounts Payable": "AP",
                }

                selected_wc_type = (
                    working_type_map[
                        wc_analysis_type
                    ]
                )

                available_currencies = sorted(
                    wc_prepared_data[
                        "currency"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                with filter_col2:
                    selected_wc_currency = (
                        st.selectbox(
                            "Currency",
                            options=[
                                "All"
                            ]
                            + available_currencies,
                            key=(
                                "working_capital_currency"
                            ),
                        )
                    )

                available_counterparties = sorted(
                    wc_prepared_data[
                        "counterparty"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                with filter_col3:
                    selected_wc_counterparty = (
                        st.selectbox(
                            "Customer / Supplier",
                            options=[
                                "All"
                            ]
                            + available_counterparties,
                            key=(
                                "working_capital_counterparty"
                            ),
                        )
                    )

                wc_analysis = (
                    working_capital_aging_engine
                    .analyze(
                        wc_mapping_result.dataframe,
                        config=(
                            AgingConfig.from_value(
                                wc_as_of_date
                            )
                        ),
                        document_type=(
                            selected_wc_type
                        ),
                        currency=(
                            None
                            if (
                                selected_wc_currency
                                == "All"
                            )
                            else (
                                selected_wc_currency
                            )
                        ),
                        counterparty=(
                            None
                            if (
                                selected_wc_counterparty
                                == "All"
                            )
                            else (
                                selected_wc_counterparty
                            )
                        ),
                    )
                )

                wc_summary = wc_analysis.summary
                wc_data = wc_analysis.dataframe
                wc_bucket_summary = (
                    wc_analysis.bucket_summary
                )
                wc_counterparty_summary = (
                    wc_analysis
                    .counterparty_summary
                )

                kpi1, kpi2, kpi3, kpi4 = (
                    st.columns(4)
                )

                kpi1.metric(
                    "Total Open",
                    (
                        f"${wc_summary['total_open']:,.0f}"
                    ),
                )

                kpi2.metric(
                    "Total Overdue",
                    (
                        f"${wc_summary['total_overdue']:,.0f}"
                    ),
                    (
                        f"{wc_summary['overdue_pct']:.1%} "
                        "of open balance"
                    ),
                )

                kpi3.metric(
                    "90+ Days",
                    (
                        f"${wc_summary['overdue_90_plus']:,.0f}"
                    ),
                    (
                        f"{wc_summary['overdue_90_plus_pct']:.1%} "
                        "of open balance"
                    ),
                )

                kpi4.metric(
                    "Open Documents",
                    (
                        f"{wc_summary['open_documents']:,.0f}"
                    ),
                    (
                        f"{wc_summary['overdue_documents']:,.0f} "
                        "overdue"
                    ),
                )

                kpi5, kpi6, kpi7, kpi8 = (
                    st.columns(4)
                )

                kpi5.metric(
                    "AR Open",
                    (
                        f"${wc_summary['ar_open']:,.0f}"
                    ),
                )

                kpi6.metric(
                    "AP Open",
                    (
                        f"${wc_summary['ap_open']:,.0f}"
                    ),
                )

                kpi7.metric(
                    "Weighted Days Overdue",
                    (
                        f"{wc_summary['weighted_days_overdue']:.1f}"
                    ),
                )

                kpi8.metric(
                    "Customers / Suppliers",
                    (
                        f"{wc_summary['counterparties']:,.0f}"
                    ),
                )

                st.markdown(
                    "### Aging by Bucket"
                )

                if wc_bucket_summary.empty:
                    st.info(
                        "No existen documentos abiertos "
                        "con los filtros seleccionados."
                    )
                else:
                    bucket_colors = {
                        "Current": "#22c55e",
                        "0-30": "#14b8a6",
                        "31-45": "#fbbf24",
                        "46-60": "#f59e0b",
                        "61-90": "#ef4444",
                        "90+": "#991b1b",
                    }

                    fig_aging_bucket = px.bar(
                        wc_bucket_summary,
                        x="aging_bucket",
                        y="open_amount",
                        color="aging_bucket",
                        facet_col=(
                            "document_type"
                            if selected_wc_type is None
                            else None
                        ),
                        category_orders={
                            "aging_bucket": (
                                working_capital_aging_engine
                                .BUCKET_ORDER
                            )
                        },
                        color_discrete_map=(
                            bucket_colors
                        ),
                        text_auto=".3s",
                        title=(
                            "Open Balance by Aging Bucket"
                        ),
                    )

                    fig_aging_bucket = (
                        apply_fip_chart_style(
                            fig_aging_bucket
                        )
                    )

                    st.plotly_chart(
                        fig_aging_bucket,
                        use_container_width=True,
                    )

                    bucket_display = (
                        wc_bucket_summary.copy()
                    )

                    bucket_display[
                        "portfolio_pct"
                    ] *= 100

                    st.dataframe(
                        bucket_display,
                        use_container_width=True,
                        hide_index=True,
                    )

                st.markdown(
                    "### Top Customers and Suppliers"
                )

                if (
                    wc_counterparty_summary.empty
                ):
                    st.info(
                        "No hay exposición abierta "
                        "por contraparte."
                    )
                else:
                    counterparty_display = (
                        wc_counterparty_summary
                        .copy()
                    )

                    counterparty_display[
                        "overdue_pct"
                    ] *= 100

                    st.dataframe(
                        counterparty_display.head(25),
                        use_container_width=True,
                        hide_index=True,
                    )

                    fig_counterparty = px.bar(
                        (
                            wc_counterparty_summary
                            .head(15)
                        ),
                        x="counterparty",
                        y="open_amount",
                        color="risk_signal",
                        text_auto=".3s",
                        title=(
                            "Top Open Exposure by "
                            "Customer / Supplier"
                        ),
                        color_discrete_sequence=(
                            FIP_COLOR_SEQUENCE
                        ),
                    )

                    fig_counterparty = (
                        apply_fip_chart_style(
                            fig_counterparty
                        )
                    )

                    st.plotly_chart(
                        fig_counterparty,
                        use_container_width=True,
                    )

                st.markdown(
                    "### Upcoming Cash Requirements"
                )

                due_col1, due_col2, due_col3 = (
                    st.columns(3)
                )

                due_windows = [
                    (7, due_col1),
                    (15, due_col2),
                    (30, due_col3),
                ]

                for days, due_column in due_windows:
                    due_data = (
                        working_capital_aging_engine
                        .upcoming_due(
                            wc_data,
                            days=days,
                            document_type=(
                                selected_wc_type
                            ),
                        )
                    )

                    due_amount = float(
                        due_data[
                            "open_amount"
                        ].sum()
                    )

                    with due_column:
                        st.metric(
                            f"Due in {days} Days",
                            f"${due_amount:,.0f}",
                            (
                                f"{len(due_data):,.0f} "
                                "documents"
                            ),
                        )

                st.markdown(
                    "### Detailed Aging Register"
                )

                detail_columns = [
                    "cfo_signal",
                    "document_type",
                    "document_id",
                    "counterparty",
                    "invoice_date",
                    "due_date",
                    "original_amount",
                    "paid_amount",
                    "open_amount",
                    "days_overdue",
                    "aging_bucket",
                    "open_status",
                    "status",
                    "currency",
                    "responsible",
                    "business_unit",
                ]

                available_detail_columns = [
                    column
                    for column in detail_columns
                    if column in wc_data.columns
                ]

                wc_detail_display = (
                    wc_data[
                        available_detail_columns
                    ]
                    .sort_values(
                        [
                            "days_overdue",
                            "open_amount",
                        ],
                        ascending=[
                            False,
                            False,
                        ],
                    )
                )

                st.dataframe(
                    wc_detail_display,
                    use_container_width=True,
                    hide_index=True,
                )

                wc_download = (
                    wc_detail_display.to_csv(
                        index=False
                    ).encode("utf-8")
                )

                st.download_button(
                    label=(
                        "Download Aging Register"
                    ),
                    data=wc_download,
                    file_name=(
                        "working_capital_aging.csv"
                    ),
                    mime="text/csv",
                )

                with st.expander(
                    "Working Capital Mapping Audit"
                ):
                    st.write(
                        "**Columnas reconocidas**"
                    )
                    st.json(
                        wc_mapping_result
                        .mapped_columns
                    )

                    if (
                        wc_mapping_result
                        .synthesized_columns
                    ):
                        st.write(
                            "**Columnas calculadas o "
                            "completadas**"
                        )
                        st.write(
                            wc_mapping_result
                            .synthesized_columns
                        )

                    if (
                        wc_mapping_result
                        .unmapped_columns
                    ):
                        st.write(
                            "**Columnas no reconocidas**"
                        )
                        st.write(
                            wc_mapping_result
                            .unmapped_columns
                        )

        except Exception as wc_error:
            st.error(
                "No fue posible procesar el archivo "
                "de Working Capital."
            )
            st.exception(wc_error)



st.title("📊 Financial Intelligence Platform")
st.caption("Air & Ocean Profitability Workspace · Version 0.1.23")

render_floating_elevenlabs_agent()

workspace_mode = st.radio(
    "Selecciona el módulo de análisis",
    options=[
        "Freight Performance",
        "Working Capital",
    ],
    horizontal=True,
    key="workspace_mode",
)

if workspace_mode == "Working Capital":
    render_working_capital_workspace()
    st.stop()

uploaded_file = st.file_uploader(
    "Carga un archivo Freight Performance Excel o CSV",
    type=["xlsx", "xlsm", "csv"],
    key="freight_performance_file",
)

if uploaded_file is None:
    st.info("Carga un archivo Freight Performance para iniciar el análisis.")
    st.stop()

try:
    reader = ExcelReader(uploaded_file)
    profiler = DataProfiler()
    mapping_engine = SemanticMappingEngine()
    kpi_engine = FreightKPIEngine()
    freight_engine = FreightIntelligenceEngine()
    variance_engine = VarianceEngine()
    rules_engine = RulesEngine()
    insight_engine = InsightEngine()
    recommendation_engine = RecommendationEngine()
    narrative_engine = ExecutiveNarrativeEngine()
    ai_controller_engine = AIControllerEngine()
    time_engine = TimeIntelligenceEngine()
    baseline_engine = BaselineClassificationEngine()
    working_capital_mapping_engine = (
        WorkingCapitalSemanticMappingEngine()
    )
    working_capital_aging_engine = (
        WorkingCapitalAgingEngine()
    )

    sheet_names = reader.get_sheet_names()
    loaded_sheets = reader.read_all_sheets()

    st.success(f"Archivo cargado: **{uploaded_file.name}**")

    st.markdown(
        """
        <div class="fip-card">
            <div class="fip-title">Financial Intelligence Workspace</div>
            <div class="fip-muted">
                Executive analytics, business drivers, materiality alerts,
                recommendations and AI-supported commentary.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_sheet = st.sidebar.selectbox(
        "Hoja o dataset",
        options=sheet_names,
    )

    source_dataframe = loaded_sheets[selected_sheet]
    profile = profiler.profile(source_dataframe)

    mapping_result = mapping_engine.map_dataframe(
        source_dataframe
    )

    if mapping_result.missing_required_columns:
        st.error(
            "Faltan columnas requeridas para construir "
            "el modelo canónico:"
        )
        st.write(mapping_result.missing_required_columns)

        with st.expander("Ver resultado del mapeo semántico"):
            st.write("**Columnas reconocidas**")
            st.json(mapping_result.mapped_columns)

            if mapping_result.unmapped_columns:
                st.write("**Columnas no reconocidas**")
                st.write(mapping_result.unmapped_columns)

        st.stop()

    canonical_data = mapping_result.dataframe

    available_baselines = (
        baseline_engine.available_baselines(
            canonical_data
        )
    )

    if not available_baselines:
        st.error(
            "No se encontró una base completa de comparación. "
            "Se requiere al menos un par Revenue/Cost para "
            "Budget, Reserve, Forecast o Prior Year."
        )

        st.dataframe(
            baseline_engine.baseline_audit(
                canonical_data
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.stop()

    st.sidebar.divider()
    st.sidebar.subheader("Comparison Baseline")

    baseline_labels = {
        option.label: option.key
        for option in available_baselines
    }

    selected_baseline_label = (
        st.sidebar.selectbox(
            "Compare Actual Against",
            options=list(
                baseline_labels.keys()
            ),
        )
    )

    selected_baseline_key = (
        baseline_labels[
            selected_baseline_label
        ]
    )

    baseline_result = (
        baseline_engine.apply_baseline(
            canonical_data,
            selected_baseline_key,
        )
    )

    canonical_data = (
        baseline_result.dataframe
    )

    comparison_label = (
        baseline_result.selected_label
    )

    prepared_data = kpi_engine.prepare_data(canonical_data)
    freight_data = freight_engine.prepare_data(prepared_data)

    available_modes = freight_engine.get_available_modes(
        freight_data
    )

    mode_filter = st.sidebar.multiselect(
        "Mode",
        options=available_modes,
        default=available_modes,
    )

    product_options = sorted(
        freight_data["product"]
        .dropna()
        .unique()
        .tolist()
    )

    product_filter = st.sidebar.multiselect(
        "Product",
        options=product_options,
        default=product_options,
    )

    st.sidebar.divider()
    st.sidebar.subheader("Variance Rules")

    amount_threshold = st.sidebar.number_input(
        "Materiality Amount",
        min_value=0.0,
        value=100_000.0,
        step=25_000.0,
        format="%.2f",
    )

    percentage_threshold = st.sidebar.number_input(
        "Materiality Percentage",
        min_value=0.0,
        value=5.0,
        step=0.5,
        format="%.2f",
    )

    evaluation_logic = st.sidebar.selectbox(
        "Threshold Logic",
        options=["OR", "AND"],
    )

    rule_config = RuleConfig(
        amount_threshold=amount_threshold,
        percentage_threshold=percentage_threshold / 100,
        evaluation_logic=evaluation_logic,
    )

    st.sidebar.divider()
    st.sidebar.subheader("Narrative Settings")

    company_name = st.sidebar.text_input(
        "Company Name",
        value="CEVA Logistics Demo",
    )

    reporting_period = st.sidebar.text_input(
        "Reporting Period",
        value="Current Period",
    )

    st.sidebar.divider()
    st.sidebar.subheader("AI Controller")

    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help=(
            "La clave se usa únicamente durante esta sesión "
            "y no se guarda en el repositorio."
        ),
    )

    ai_model = st.sidebar.text_input(
        "OpenAI Model",
        value="gpt-5.6",
        help=(
            "Puedes cambiar el modelo si tu cuenta no tiene "
            "acceso al valor predeterminado."
        ),
    )

    filtered_data = freight_data[
        freight_data["mode"].isin(mode_filter)
        & freight_data["product"].isin(product_filter)
    ].copy()

    if filtered_data.empty:
        st.warning(
            "Los filtros seleccionados no contienen información."
        )
        st.stop()

    # ---------------------------------------------------------
    # TIME INTELLIGENCE ENGINE
    # ---------------------------------------------------------

    time_result = time_engine.prepare_periods(
        filtered_data,
        period_column="period",
        year_column="year",
    )

    filtered_data = time_result.dataframe

    st.sidebar.divider()
    st.sidebar.subheader("Time Intelligence")

    period_mode = st.sidebar.selectbox(
        "Analysis Period",
        options=["All Periods", "Monthly", "Yearly"],
    )

    selected_period_label = "All Periods"

    if period_mode == "Monthly":
        available_months = time_engine.available_months(
            filtered_data
        )

        if not available_months:
            st.sidebar.warning(
                "No fue posible identificar meses válidos."
            )
        else:
            selected_month = st.sidebar.selectbox(
                "Select Month",
                options=available_months,
                format_func=time_engine.month_label,
            )

            filtered_data = time_engine.filter_month(
                filtered_data,
                selected_month,
            )

            selected_period_label = time_engine.month_label(
                selected_month
            )

    elif period_mode == "Yearly":
        available_years = time_engine.available_years(
            filtered_data
        )

        if not available_years:
            st.sidebar.warning(
                "No fue posible identificar años válidos."
            )
        else:
            selected_year = st.sidebar.selectbox(
                "Select Year",
                options=available_years,
            )

            filtered_data = time_engine.filter_year(
                filtered_data,
                selected_year,
            )

            selected_period_label = str(selected_year)

    if time_result.unparsed_count:
        st.sidebar.warning(
            f"{time_result.unparsed_count} registros no pudieron "
            "interpretarse como fecha."
        )

    if filtered_data.empty:
        st.warning(
            "El periodo seleccionado no contiene información."
        )
        st.stop()

    summary = kpi_engine.executive_summary(filtered_data)
    mode_summary = freight_engine.mode_summary(filtered_data)
    variance_summary = variance_engine.overall_summary(
        filtered_data
    )

    st.markdown(
        f'''
        <div class="fip-card">
            <div class="fip-title">Active Analysis Period</div>
            <div class="fip-muted">{selected_period_label}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="fip-card">
            <div class="fip-title">Active Comparison Baseline</div>
            <div class="fip-muted">Actual vs {comparison_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dimension_map = {
        "Mode": "mode",
        "Product": "product",
        "Customer": "customer",
        "Trade Lane": "trade_lane",
        "Forwarder": "forwarder",
        "Origin": "origin",
        "Destination": "destination",
        "Period": "period",
    }

    (
        tab_exec,
        tab_variance,
        tab_insights,
        tab_recommendations,
        tab_narrative,
        tab_ai_controller,
        tab_working_capital,
        tab_air,
        tab_ocean,
        tab_commercial,
        tab_data,
    ) = st.tabs(
        [
            "Vista Ejecutiva",
            "Variances",
            "Insights",
            "Recommendations",
            "Executive Narrative",
            "AI Controller",
            "Working Capital",
            "Air",
            "Ocean",
            "Comercial",
            "Data Quality",
        ]
    )

    with tab_exec:
        st.subheader("Executive Performance")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Revenue",
            f"${summary['actual_revenue']:,.0f}",
            f"${summary['revenue_variance']:,.0f} vs Budget",
        )
        col2.metric(
            "Gross Profit",
            f"${summary['actual_gp']:,.0f}",
            f"${summary['gp_variance']:,.0f} vs Budget",
        )
        col3.metric(
            "GP Margin",
            f"{summary['actual_gp_margin']:.1%}",
            (
                f"{summary['margin_variance_pp'] * 100:+.2f} "
                f"pp vs {comparison_label}"
            ),
        )
        col4.metric(
            "Shipments",
            f"{summary['shipments']:,.0f}",
        )

        col5, col6, col7, col8 = st.columns(4)

        col5.metric("Tons", f"{summary['weight_tons']:,.1f}")
        col6.metric("TEUs", f"{summary['teus']:,.1f}")
        col7.metric(
            "GP / Shipment",
            f"${summary['gp_per_shipment']:,.0f}",
        )
        col8.metric(
            "Revenue / Shipment",
            f"${summary['revenue_per_shipment']:,.0f}",
        )

        st.subheader("Performance by Mode")

        mode_display = mode_summary.copy()

        if "GP_Margin" in mode_display.columns:
            mode_display["GP_Margin"] *= 100

        st.dataframe(
            mode_display,
            use_container_width=True,
            hide_index=True,
        )

        fig_mode = px.bar(
            mode_summary,
            color_discrete_sequence=FIP_COLOR_SEQUENCE,
            x="Mode",
            y="GP",
            color="Mode",
            text_auto=".3s",
            title="Gross Profit by Mode",
        )

        fig_mode = apply_fip_chart_style(fig_mode)

        st.plotly_chart(
            fig_mode,
            use_container_width=True,
        )

    with tab_variance:
        st.subheader(f"Actual vs {comparison_label} Variance Analysis")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Revenue Variance",
            f"${variance_summary['revenue_variance']:,.0f}",
            f"{variance_summary['revenue_variance_pct']:+.1%}",
        )
        col2.metric(
            "Cost Variance",
            f"${variance_summary['cost_variance']:,.0f}",
            (
                f"{-variance_summary['cost_variance_pct']:+.1%} "
                "financial impact"
            ),
        )
        col3.metric(
            "GP Variance",
            f"${variance_summary['gp_variance']:,.0f}",
            f"{variance_summary['gp_variance_pct']:+.1%}",
        )
        col4.metric(
            "Margin Variance",
            (
                f"{variance_summary['margin_variance_pp'] * 100:+.2f} "
                "pp"
            ),
        )

        st.subheader("Executive Findings")

        for finding in variance_engine.executive_findings(
            filtered_data
        ):
            st.write(f"• {finding}")

        variance_dimension_label = st.selectbox(
            "Analizar variación por",
            options=list(dimension_map.keys()),
            key="variance_dimension",
        )

        variance_dimension = dimension_map[
            variance_dimension_label
        ]

        dimension_variance = variance_engine.dimension_variance(
            filtered_data,
            variance_dimension,
        )

        st.subheader(
            f"Variance by {variance_dimension_label}"
        )

        st.dataframe(
            dimension_variance,
            use_container_width=True,
            hide_index=True,
        )

        positive, negative = variance_engine.top_drivers(
            filtered_data,
            variance_dimension,
            limit=5,
        )

        positive_col, negative_col = st.columns(2)

        with positive_col:
            st.markdown("### Top Favorable Drivers")
            if positive.empty:
                st.info("No existen drivers favorables.")
            else:
                st.dataframe(
                    positive,
                    use_container_width=True,
                    hide_index=True,
                )

        with negative_col:
            st.markdown("### Top Unfavorable Drivers")
            if negative.empty:
                st.info("No existen drivers desfavorables.")
            else:
                st.dataframe(
                    negative,
                    use_container_width=True,
                    hide_index=True,
                )

        fig_variance = px.bar(
            dimension_variance.head(15),
            color_discrete_sequence=FIP_COLOR_SEQUENCE,
            x=variance_dimension,
            y="GP_Variance",
            color="Direction",
            text_auto=".3s",
            title=(
                f"Top GP Variance Drivers by "
                f"{variance_dimension_label}"
            ),
        )

        fig_variance = apply_fip_chart_style(fig_variance)

        st.plotly_chart(
            fig_variance,
            use_container_width=True,
        )

        pareto_data = variance_engine.pareto_analysis(
            filtered_data,
            variance_dimension,
        )

        st.subheader("Pareto Analysis")
        st.dataframe(
            pareto_data,
            use_container_width=True,
            hide_index=True,
        )

        fig_pareto = px.line(
            pareto_data.head(20),
            color_discrete_sequence=FIP_COLOR_SEQUENCE,
            x=variance_dimension,
            y="Cumulative_Contribution",
            markers=True,
            title=(
                f"Cumulative Variance Contribution by "
                f"{variance_dimension_label}"
            ),
        )

        fig_pareto.add_hline(
            y=0.80,
            line_dash="dash",
            annotation_text="80% threshold",
        )

        fig_pareto = apply_fip_chart_style(fig_pareto)

        st.plotly_chart(
            fig_pareto,
            use_container_width=True,
        )

        st.divider()
        st.subheader("Business Rules & Materiality Alerts")

        overall_rules = rules_engine.evaluate_overall(
            variance_summary,
            rule_config,
        )

        st.markdown("### CFO Variance Traffic Lights")

        signal_columns = st.columns(4)

        signal_rows = {
            str(row["Metric"]): row
            for _, row in overall_rules.iterrows()
        }

        signal_specs = [
            (
                "Revenue",
                (
                    f"${variance_summary['revenue_variance']:,.0f}"
                ),
                (
                    f"{variance_summary['revenue_variance_pct']:+.1%} "
                    f"vs {comparison_label}"
                ),
            ),
            (
                "Cost",
                (
                    f"${variance_summary['cost_variance']:,.0f}"
                ),
                (
                    f"{variance_summary['cost_variance_pct']:+.1%} "
                    f"vs {comparison_label}"
                ),
            ),
            (
                "Gross Profit",
                (
                    f"${variance_summary['gp_variance']:,.0f}"
                ),
                (
                    f"{variance_summary['gp_variance_pct']:+.1%} "
                    f"vs {comparison_label}"
                ),
            ),
            (
                "GP Margin",
                (
                    f"{variance_summary['margin_variance_pp'] * 100:+.2f} pp"
                ),
                f"Margin movement vs {comparison_label}",
            ),
        ]

        for column, (metric_name, metric_value, metric_subtitle) in zip(
            signal_columns,
            signal_specs,
        ):
            rule_row = signal_rows.get(metric_name)

            if rule_row is None:
                severity = "Normal"
                direction = "Neutral"
            else:
                severity = str(rule_row["Severity"])
                direction = str(rule_row["Direction"])

            with column:
                render_signal_card(
                    title=metric_name,
                    value=metric_value,
                    severity=severity,
                    direction=direction,
                    subtitle=(
                        f"{severity} · {metric_subtitle}"
                    ),
                )

        st.caption(
            "Semáforo ejecutivo: rojo = acción inmediata; "
            "amarillo = monitoreo; verde = favorable; "
            "azul = dentro de tolerancia."
        )

        dimension_alerts = rules_engine.evaluate_dimension(
            dimension_variance,
            variance_dimension,
            rule_config,
        )

        material_alerts = rules_engine.material_alerts(
            dimension_alerts
        )

        alert_counts = rules_engine.alert_summary(
            dimension_alerts
        )

        alert1, alert2, alert3, alert4 = st.columns(4)

        alert1.metric("Material Alerts", alert_counts["total"])
        alert2.metric("Critical", alert_counts["critical"])
        alert3.metric("High", alert_counts["high"])
        alert4.metric("Unfavorable", alert_counts["unfavorable"])

        st.markdown("### Consolidated Rules Evaluation")
        st.dataframe(
            overall_rules,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            f"### Material Alerts by "
            f"{variance_dimension_label}"
        )

        if material_alerts.empty:
            st.success(
                "No existen variaciones materiales con "
                "los límites configurados."
            )
        else:
            material_alerts_display = material_alerts.copy()

            material_alerts_display.insert(
                0,
                "Signal",
                material_alerts_display.apply(
                    lambda row: (
                        "🔴 Action Required"
                        if (
                            row["Severity"] in {"Critical", "High"}
                            and row["Direction"] == "Unfavorable"
                        )
                        else "🟢 Strong Favorable"
                        if (
                            row["Severity"] in {"Critical", "High"}
                            and row["Direction"] == "Favorable"
                        )
                        else "🟡 Monitor"
                        if row["Severity"] in {"Medium", "Low"}
                        else "🔵 Within Tolerance"
                    ),
                    axis=1,
                ),
            )

            st.dataframe(
                material_alerts_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Signal": st.column_config.TextColumn(
                        "CFO Signal",
                        width="medium",
                    ),
                },
            )

            signal_summary = (
                material_alerts_display.groupby(
                    ["Signal", "Direction"],
                    dropna=False,
                )
                .size()
                .reset_index(name="Alerts")
            )

            fig_signal_summary = px.bar(
                signal_summary,
                x="Signal",
                y="Alerts",
                color="Direction",
                barmode="group",
                color_discrete_map={
                    "Favorable": "#22c55e",
                    "Unfavorable": "#ef4444",
                    "Neutral": "#2f80ed",
                },
                title="CFO Alerts by Traffic-Light Signal",
            )

            fig_signal_summary = apply_fip_chart_style(
                fig_signal_summary
            )

            st.plotly_chart(
                fig_signal_summary,
                use_container_width=True,
            )

    with tab_insights:
        st.subheader("Deterministic Controller Insights")

        insight_dimension_label = st.selectbox(
            "Generate insights by",
            options=list(dimension_map.keys()),
            key="insight_dimension",
        )

        insight_dimension = dimension_map[
            insight_dimension_label
        ]

        insight_variance = variance_engine.dimension_variance(
            filtered_data,
            insight_dimension,
        )

        insight_alerts = rules_engine.evaluate_dimension(
            insight_variance,
            insight_dimension,
            rule_config,
        )

        material_insight_alerts = (
            rules_engine.material_alerts(
                insight_alerts
            )
        )

        insight_pareto = variance_engine.pareto_analysis(
            filtered_data,
            insight_dimension,
        )

        overall_insights = insight_engine.overall_insights(
            variance_summary
        )

        dimension_insights = insight_engine.dimension_insights(
            insight_variance,
            insight_dimension,
            limit=5,
        )

        alert_insights = (
            insight_engine.material_alert_insights(
                material_insight_alerts,
                insight_dimension,
                limit=10,
            )
        )

        concentration = insight_engine.concentration_insight(
            insight_pareto,
            insight_dimension,
        )

        executive_bullets = insight_engine.executive_bullets(
            overall_insights,
            dimension_insights,
            concentration,
        )

        st.markdown("### Executive Summary")

        for bullet in executive_bullets:
            st.write(f"• {bullet}")

        st.markdown("### Consolidated Financial Insights")
        st.dataframe(
            overall_insights,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            f"### Main Drivers by "
            f"{insight_dimension_label}"
        )

        st.dataframe(
            dimension_insights,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Material Alert Insights")

        if alert_insights.empty:
            st.success(
                "No material alert insights were generated."
            )
        else:
            st.dataframe(
                alert_insights,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Variance Concentration")

        concentration1, concentration2, concentration3 = (
            st.columns(3)
        )

        concentration1.metric(
            "Primary Drivers",
            concentration["Primary_Drivers"],
        )
        concentration2.metric(
            "Total Drivers",
            concentration["Total_Drivers"],
        )
        concentration3.metric(
            "Concentration",
            f"{concentration['Concentration']:.1%}",
        )

        st.info(concentration["Headline"])
        st.write(concentration["Evidence"])

    with tab_recommendations:
        st.subheader("Controller Recommendation Engine")

        recommendation_dimension_label = st.selectbox(
            "Generate recommendations by",
            options=list(dimension_map.keys()),
            key="recommendation_dimension",
        )

        recommendation_dimension = dimension_map[
            recommendation_dimension_label
        ]

        recommendation_variance = (
            variance_engine.dimension_variance(
                filtered_data,
                recommendation_dimension,
            )
        )

        recommendation_alerts = (
            rules_engine.evaluate_dimension(
                recommendation_variance,
                recommendation_dimension,
                rule_config,
            )
        )

        recommendation_material_alerts = (
            rules_engine.material_alerts(
                recommendation_alerts
            )
        )

        recommendation_overall_insights = (
            insight_engine.overall_insights(
                variance_summary
            )
        )

        recommendation_dimension_insights = (
            insight_engine.dimension_insights(
                recommendation_variance,
                recommendation_dimension,
                limit=10,
            )
        )

        recommendation_alert_insights = (
            insight_engine.material_alert_insights(
                recommendation_material_alerts,
                recommendation_dimension,
                limit=15,
            )
        )

        recommendations = (
            recommendation_engine.generate_recommendations(
                recommendation_overall_insights,
                recommendation_dimension_insights,
                recommendation_alert_insights,
            )
        )

        recommendation_summary = (
            recommendation_engine.priority_summary(
                recommendations
            )
        )

        immediate_actions = (
            recommendation_engine.immediate_actions(
                recommendations,
                limit=5,
            )
        )

        action_plan = (
            recommendation_engine.action_plan_by_owner(
                recommendations
            )
        )

        executive_actions = (
            recommendation_engine.executive_action_bullets(
                recommendations,
                limit=5,
            )
        )

        rec1, rec2, rec3, rec4 = st.columns(4)

        rec1.metric(
            "Total Recommendations",
            recommendation_summary["total"],
        )
        rec2.metric(
            "Critical",
            recommendation_summary["critical"],
        )
        rec3.metric(
            "High",
            recommendation_summary["high"],
        )
        rec4.metric(
            "Commercial Actions",
            recommendation_summary["commercial"],
        )

        st.markdown("### Immediate Management Actions")

        for action in executive_actions:
            st.write(f"• {action}")

        st.markdown("### Priority Action List")

        if immediate_actions.empty:
            st.success(
                "No immediate actions were identified."
            )
        else:
            st.dataframe(
                immediate_actions,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Complete Recommendation Register")

        st.dataframe(
            recommendations,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Action Plan by Owner")

        st.dataframe(
            action_plan,
            use_container_width=True,
            hide_index=True,
        )

        if not recommendations.empty:
            area_summary = (
                recommendations.groupby(
                    ["Business_Area", "Priority"],
                    dropna=False,
                )
                .size()
                .reset_index(name="Actions")
            )

            fig_recommendations = px.bar(
                area_summary,
                color_discrete_sequence=FIP_COLOR_SEQUENCE,
                x="Business_Area",
                y="Actions",
                color="Priority",
                barmode="group",
                title="Recommendations by Area and Priority",
            )

            fig_recommendations = apply_fip_chart_style(fig_recommendations)

            st.plotly_chart(
                fig_recommendations,
                use_container_width=True,
            )

    with tab_narrative:
        st.subheader("Executive Narrative Engine")

        narrative_dimension_label = st.selectbox(
            "Generate narrative by",
            options=list(dimension_map.keys()),
            key="narrative_dimension",
        )

        narrative_dimension = dimension_map[
            narrative_dimension_label
        ]

        narrative_variance = (
            variance_engine.dimension_variance(
                filtered_data,
                narrative_dimension,
            )
        )

        narrative_alerts = (
            rules_engine.evaluate_dimension(
                narrative_variance,
                narrative_dimension,
                rule_config,
            )
        )

        narrative_material_alerts = (
            rules_engine.material_alerts(
                narrative_alerts
            )
        )

        narrative_overall_insights = (
            insight_engine.overall_insights(
                variance_summary
            )
        )

        narrative_dimension_insights = (
            insight_engine.dimension_insights(
                narrative_variance,
                narrative_dimension,
                limit=10,
            )
        )

        narrative_alert_insights = (
            insight_engine.material_alert_insights(
                narrative_material_alerts,
                narrative_dimension,
                limit=15,
            )
        )

        narrative_recommendations = (
            recommendation_engine.generate_recommendations(
                narrative_overall_insights,
                narrative_dimension_insights,
                narrative_alert_insights,
            )
        )

        narrative_package = narrative_engine.build_package(
            variance_summary=variance_summary,
            overall_insights=narrative_overall_insights,
            dimension_insights=narrative_dimension_insights,
            recommendations=narrative_recommendations,
            selected_dimension_label=narrative_dimension_label,
            company_name=company_name,
            reporting_period=reporting_period,
        )

        st.markdown("### Executive Summary")
        st.info(narrative_package.executive_summary)

        st.markdown("### Management Talking Points")

        for point in narrative_package.meeting_talking_points:
            st.write(f"• {point}")

        st.markdown("### Priority Management Actions")

        for action in narrative_package.management_actions:
            st.write(f"• {action}")

        st.markdown("### CFO Email")

        st.text_input(
            "Email Subject",
            value=narrative_package.cfo_email_subject,
            key="cfo_email_subject",
        )

        st.text_area(
            "Email Body",
            value=narrative_package.cfo_email_body,
            height=450,
            key="cfo_email_body",
        )

        st.download_button(
            label="Download CFO Email as TXT",
            data=narrative_package.cfo_email_body,
            file_name="cfo_financial_summary.txt",
            mime="text/plain",
        )

        narrative_table = narrative_engine.build_narrative_table(
            variance_summary=variance_summary,
            overall_insights=narrative_overall_insights,
            dimension_insights=narrative_dimension_insights,
            recommendations=narrative_recommendations,
            selected_dimension_label=narrative_dimension_label,
        )

        narrative_csv = narrative_table.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Narrative Package as CSV",
            data=narrative_csv,
            file_name="executive_narrative_package.csv",
            mime="text/csv",
        )


    with tab_ai_controller:
        st.subheader("AI Financial Controller")

        st.caption(
            "La IA interpreta únicamente resultados ya calculados "
            "por los motores determinísticos. No recalcula cifras."
        )

        ai_dimension_label = st.selectbox(
            "Analyze business drivers by",
            options=list(dimension_map.keys()),
            key="ai_controller_dimension",
        )

        ai_dimension = dimension_map[
            ai_dimension_label
        ]

        ai_variance = variance_engine.dimension_variance(
            filtered_data,
            ai_dimension,
        )

        ai_alerts = rules_engine.evaluate_dimension(
            ai_variance,
            ai_dimension,
            rule_config,
        )

        ai_material_alerts = rules_engine.material_alerts(
            ai_alerts
        )

        ai_overall_insights = insight_engine.overall_insights(
            variance_summary
        )

        ai_dimension_insights = insight_engine.dimension_insights(
            ai_variance,
            ai_dimension,
            limit=10,
        )

        ai_alert_insights = (
            insight_engine.material_alert_insights(
                ai_material_alerts,
                ai_dimension,
                limit=15,
            )
        )

        ai_recommendations = (
            recommendation_engine.generate_recommendations(
                ai_overall_insights,
                ai_dimension_insights,
                ai_alert_insights,
            )
        )

        ai_context = ai_controller_engine.build_context(
            company_name=company_name,
            reporting_period=reporting_period,
            selected_dimension_label=ai_dimension_label,
            variance_summary=variance_summary,
            overall_insights=ai_overall_insights,
            dimension_insights=ai_dimension_insights,
            recommendations=ai_recommendations,
        )

        if not openai_api_key:
            st.warning(
                "Ingresa una OpenAI API Key en la barra lateral "
                "para activar el AI Controller."
            )

            with st.expander(
                "Ver contexto validado que recibirá la IA"
            ):
                st.code(ai_context, language="text")
        else:
            generation_col1, generation_col2 = st.columns(2)

            with generation_col1:
                if st.button(
                    "Generate CFO Commentary",
                    use_container_width=True,
                ):
                    with st.spinner(
                        "Generating executive commentary..."
                    ):
                        try:
                            commentary = (
                                ai_controller_engine
                                .generate_executive_commentary(
                                    api_key=openai_api_key,
                                    model=ai_model,
                                    context=ai_context,
                                )
                            )

                            st.session_state[
                                "ai_cfo_commentary"
                            ] = commentary
                        except Exception as ai_error:
                            st.error(
                                "No fue posible generar el comentario."
                            )
                            st.exception(ai_error)

            with generation_col2:
                if st.button(
                    "Generate Closing Review",
                    use_container_width=True,
                ):
                    with st.spinner(
                        "Generating month-end review..."
                    ):
                        try:
                            closing_review = (
                                ai_controller_engine
                                .generate_closing_review(
                                    api_key=openai_api_key,
                                    model=ai_model,
                                    context=ai_context,
                                )
                            )

                            st.session_state[
                                "ai_closing_review"
                            ] = closing_review
                        except Exception as ai_error:
                            st.error(
                                "No fue posible generar el closing review."
                            )
                            st.exception(ai_error)

            if st.session_state.get(
                "ai_cfo_commentary"
            ):
                st.markdown(
                    "### AI CFO Commentary"
                )
                st.write(
                    st.session_state[
                        "ai_cfo_commentary"
                    ]
                )

                st.download_button(
                    label="Download CFO Commentary",
                    data=st.session_state[
                        "ai_cfo_commentary"
                    ],
                    file_name="ai_cfo_commentary.txt",
                    mime="text/plain",
                )

            if st.session_state.get(
                "ai_closing_review"
            ):
                st.markdown(
                    "### AI Month-End Closing Review"
                )
                st.write(
                    st.session_state[
                        "ai_closing_review"
                    ]
                )

                st.download_button(
                    label="Download Closing Review",
                    data=st.session_state[
                        "ai_closing_review"
                    ],
                    file_name="ai_month_end_review.txt",
                    mime="text/plain",
                )

            st.divider()
            st.markdown(
                "### Ask the AI Controller"
            )

            user_question = st.text_area(
                "Question",
                placeholder=(
                    "Example: Why did Gross Profit miss Budget, "
                    "which business drivers matter most, and what "
                    "should management do next?"
                ),
                height=120,
                key="ai_controller_question",
            )

            if st.button(
                "Ask AI Controller",
                type="primary",
            ):
                if not user_question.strip():
                    st.warning(
                        "Escribe una pregunta antes de continuar."
                    )
                else:
                    with st.spinner(
                        "Analyzing validated financial context..."
                    ):
                        try:
                            ai_answer = (
                                ai_controller_engine
                                .answer_question(
                                    api_key=openai_api_key,
                                    model=ai_model,
                                    context=ai_context,
                                    question=user_question,
                                )
                            )

                            st.session_state[
                                "ai_controller_answer"
                            ] = ai_answer
                        except Exception as ai_error:
                            st.error(
                                "No fue posible responder la pregunta."
                            )
                            st.exception(ai_error)

            if st.session_state.get(
                "ai_controller_answer"
            ):
                st.markdown(
                    "### AI Controller Answer"
                )
                st.write(
                    st.session_state[
                        "ai_controller_answer"
                    ]
                )

            with st.expander(
                "Audit: validated context sent to AI"
            ):
                st.code(ai_context, language="text")



    with tab_working_capital:
        render_working_capital_workspace()

    with tab_air:
        air_data = freight_engine.filter_by_mode(
            filtered_data,
            "Air",
        )

        render_freight_mode_workspace(
            mode_name="Air",
            mode_data=air_data,
            freight_engine=freight_engine,
            kpi_engine=kpi_engine,
        )

    with tab_ocean:
        ocean_data = freight_engine.filter_by_mode(
            filtered_data,
            "Ocean",
        )

        render_freight_mode_workspace(
            mode_name="Ocean",
            mode_data=ocean_data,
            freight_engine=freight_engine,
            kpi_engine=kpi_engine,
        )

    with tab_commercial:
        st.subheader("Commercial Profitability")

        commercial_dimension_label = st.selectbox(
            "Analizar por",
            options=[
                "Customer",
                "Trade Lane",
                "Product",
                "Forwarder",
                "Origin",
                "Destination",
            ],
            key="commercial_dimension",
        )

        commercial_dimension = dimension_map[
            commercial_dimension_label
        ]

        commercial_summary = (
            freight_engine.dimension_summary(
                filtered_data,
                commercial_dimension,
            )
        )

        st.dataframe(
            commercial_summary,
            use_container_width=True,
            hide_index=True,
        )

        fig_commercial = px.bar(
            commercial_summary.head(15),
            color_discrete_sequence=FIP_COLOR_SEQUENCE,
            x=commercial_dimension,
            y="GP",
            text_auto=".3s",
            title=(
                f"Top 15 GP by "
                f"{commercial_dimension_label}"
            ),
        )

        fig_commercial = apply_fip_chart_style(fig_commercial)

        st.plotly_chart(
            fig_commercial,
            use_container_width=True,
        )

    with tab_data:
        st.subheader("Data Quality")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rows", profile["rows"])
        col2.metric("Columns", profile["columns"])
        col3.metric(
            "Missing Cells",
            profile["missing_cells"],
        )
        col4.metric(
            "Duplicate Rows",
            profile["duplicate_rows"],
        )

        st.success(
            "Todas las columnas fueron reconocidas por "
            "el Semantic Mapping Engine."
        )

        st.write("**Mapeo aplicado**")
        st.json(mapping_result.mapped_columns)

        if mapping_result.unmapped_columns:
            st.warning("Existen columnas no reconocidas.")
            st.write(mapping_result.unmapped_columns)

        st.subheader("Mode Classification Audit")

        st.dataframe(
            freight_engine.mode_value_audit(
                prepared_data
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Esta auditoría muestra cómo los valores originales "
            "de Mode/Product fueron clasificados como Air, Ocean, "
            "Ground, Rail o Unclassified."
        )

        st.subheader("Baseline Classification Audit")

        st.dataframe(
            baseline_engine.baseline_audit(
                canonical_data
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            f"Active comparison: Actual vs {comparison_label}. "
            f"Revenue source: {baseline_result.revenue_source}; "
            f"Cost source: {baseline_result.cost_source}."
        )

        st.subheader("Canonical Dataset")

        st.dataframe(
            filtered_data.head(500),
            use_container_width=True,
        )

except Exception as error:
    st.error("No fue posible procesar el archivo.")
    st.exception(error)