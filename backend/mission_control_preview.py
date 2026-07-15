from __future__ import annotations

import pandas as pd
import streamlit as st

from engines.baseline_classification_engine import (
    BaselineClassificationEngine,
)
from engines.data_profiler import DataProfiler
from engines.excel_reader import ExcelReader
from engines.freight_intelligence_engine import (
    FreightIntelligenceEngine,
)
from engines.freight_kpi_engine import FreightKPIEngine
from engines.semantic_mapping_engine import (
    SemanticMappingEngine,
)
from engines.time_intelligence_engine import (
    TimeIntelligenceEngine,
)
from engines.variance_engine import VarianceEngine
from workspaces.mission_control import (
    render_mission_control_workspace,
)
from ui.component_registry import (
    apply_component_library_css,
)
from ui.theme import apply_enterprise_theme


st.set_page_config(
    page_title="FIP V2 Mission Control",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


apply_enterprise_theme()
apply_component_library_css()


def calculate_data_quality_score(
    dataframe: pd.DataFrame,
) -> float:
    """
    Calculate a simple deterministic completeness score.

    This score evaluates the canonical dimensions required by Mission Control.
    It does not replace the existing Data Profiler.
    """

    if dataframe.empty:
        return 0.0

    evaluated_columns = [
        column
        for column in [
            "shipment",
            "mode",
            "product",
            "customer",
            "trade_lane",
            "origin",
            "destination",
            "actual_revenue",
            "actual_cost",
            "period",
        ]
        if column in dataframe.columns
    ]

    if not evaluated_columns:
        return 0.0

    invalid_text_values = {
        "",
        "nan",
        "none",
        "null",
        "unassigned",
        "unclassified",
    }

    column_scores: list[float] = []

    for column in evaluated_columns:
        series = dataframe[column]

        if pd.api.types.is_numeric_dtype(
            series
        ):
            valid_ratio = float(
                series.notna().mean()
            )
        else:
            normalized = (
                series
                .fillna("")
                .astype(str)
                .str.strip()
                .str.casefold()
            )

            valid_ratio = float(
                (~normalized.isin(
                    invalid_text_values
                )).mean()
            )

        column_scores.append(
            valid_ratio * 100.0
        )

    return round(
        sum(column_scores)
        / len(column_scores),
        1,
    )


def render_preview_sidebar() -> dict:
    """Render preview-specific configuration controls."""

    st.sidebar.markdown(
        "## Mission Control Preview"
    )

    st.sidebar.caption(
        "Entorno independiente para validar la experiencia V2 "
        "sin modificar la aplicación V1."
    )

    st.sidebar.divider()

    company_name = st.sidebar.text_input(
        "Company",
        value="Enterprise Freight Demo",
    )

    currency = st.sidebar.selectbox(
        "Currency",
        options=[
            "USD",
            "MXN",
            "EUR",
            "CAD",
            "BRL",
        ],
        index=0,
    )

    return {
        "company_name": company_name,
        "currency": currency,
    }


sidebar_context = render_preview_sidebar()


st.markdown(
    """
    <div style="margin-bottom: 0.9rem;">
        <div style="
            color: var(--fip-cyan);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.11em;
        ">
            FIP V2.1.3 · NATIVE HTML PREVIEW
        </div>
        <div style="
            color: var(--fip-text-muted);
            font-size: 0.86rem;
            margin-top: 0.2rem;
        ">
            Carga una base Freight Performance para probar Mission Control.
            La V1 permanece intacta.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


uploaded_file = st.file_uploader(
    "Freight Performance File",
    type=[
        "xlsx",
        "xlsm",
        "csv",
    ],
    key="mission_control_preview_file",
)


if uploaded_file is None:
    st.info(
        "Carga una base compatible con Freight Performance "
        "para iniciar la vista previa."
    )

    st.markdown(
        """
        ### Flujo de validación

        1. Carga el mismo archivo que utilizas en la V1.
        2. Selecciona la hoja o dataset.
        3. Elige el baseline disponible.
        4. Aplica filtros de modo, producto y periodo.
        5. Revisa Mission Control sin alterar `app.py`.
        """
    )

    st.stop()


try:
    reader = ExcelReader(
        uploaded_file
    )

    profiler = DataProfiler()
    mapping_engine = SemanticMappingEngine()
    kpi_engine = FreightKPIEngine()
    freight_engine = (
        FreightIntelligenceEngine()
    )
    variance_engine = VarianceEngine()
    time_engine = TimeIntelligenceEngine()
    baseline_engine = (
        BaselineClassificationEngine()
    )

    sheet_names = reader.get_sheet_names()
    loaded_sheets = reader.read_all_sheets()

    selected_sheet = st.sidebar.selectbox(
        "Sheet / Dataset",
        options=sheet_names,
        key="preview_sheet",
    )

    source_dataframe = loaded_sheets[
        selected_sheet
    ]

    profile = profiler.profile(
        source_dataframe
    )

    mapping_result = (
        mapping_engine.map_dataframe(
            source_dataframe
        )
    )

    if (
        mapping_result
        .missing_required_columns
    ):
        st.error(
            "Faltan columnas requeridas para "
            "construir el modelo canónico."
        )

        st.write(
            mapping_result
            .missing_required_columns
        )

        with st.expander(
            "Semantic Mapping Audit"
        ):
            st.write(
                "**Recognized columns**"
            )

            st.json(
                mapping_result
                .mapped_columns
            )

            if (
                mapping_result
                .unmapped_columns
            ):
                st.write(
                    "**Unrecognized columns**"
                )

                st.write(
                    mapping_result
                    .unmapped_columns
                )

        st.stop()

    canonical_data = (
        mapping_result.dataframe
    )

    available_baselines = (
        baseline_engine
        .available_baselines(
            canonical_data
        )
    )

    if not available_baselines:
        st.error(
            "No se encontró un baseline completo. "
            "Se requiere un par Revenue/Cost para "
            "Budget, Reserve, Forecast o Prior Year."
        )

        st.dataframe(
            baseline_engine
            .baseline_audit(
                canonical_data
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.stop()

    st.sidebar.divider()
    st.sidebar.markdown(
        "### Comparison"
    )

    baseline_label_to_key = {
        option.label: option.key
        for option in available_baselines
    }

    selected_baseline_label = (
        st.sidebar.selectbox(
            "Compare Actual Against",
            options=list(
                baseline_label_to_key
                .keys()
            ),
            key=(
                "preview_baseline"
            ),
        )
    )

    baseline_result = (
        baseline_engine.apply_baseline(
            canonical_data,
            baseline_label_to_key[
                selected_baseline_label
            ],
        )
    )

    comparison_label = (
        baseline_result
        .selected_label
    )

    prepared_data = (
        kpi_engine.prepare_data(
            baseline_result
            .dataframe
        )
    )

    freight_data = (
        freight_engine.prepare_data(
            prepared_data
        )
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        "### Business Filters"
    )

    available_modes = (
        freight_engine
        .get_available_modes(
            freight_data
        )
    )

    selected_modes = (
        st.sidebar.multiselect(
            "Mode",
            options=available_modes,
            default=available_modes,
            key="preview_modes",
        )
    )

    available_products = sorted(
        freight_data[
            "product"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_products = (
        st.sidebar.multiselect(
            "Product",
            options=available_products,
            default=available_products,
            key="preview_products",
        )
    )

    filtered_data = freight_data[
        freight_data[
            "mode"
        ].isin(
            selected_modes
        )
        & freight_data[
            "product"
        ].isin(
            selected_products
        )
    ].copy()

    if filtered_data.empty:
        st.warning(
            "Los filtros seleccionados no contienen información."
        )

        st.stop()

    time_result = (
        time_engine.prepare_periods(
            filtered_data,
            period_column="period",
            year_column="year",
        )
    )

    filtered_data = (
        time_result.dataframe
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        "### Time Intelligence"
    )

    period_mode = (
        st.sidebar.selectbox(
            "Analysis Period",
            options=[
                "All Periods",
                "Monthly",
                "Yearly",
            ],
            key=(
                "preview_period_mode"
            ),
        )
    )

    selected_period_label = (
        "All Periods"
    )

    if period_mode == "Monthly":
        available_months = (
            time_engine.available_months(
                filtered_data
            )
        )

        if available_months:
            selected_month = (
                st.sidebar.selectbox(
                    "Month",
                    options=available_months,
                    format_func=(
                        time_engine
                        .month_label
                    ),
                    key=(
                        "preview_month"
                    ),
                )
            )

            filtered_data = (
                time_engine.filter_month(
                    filtered_data,
                    selected_month,
                )
            )

            selected_period_label = (
                time_engine.month_label(
                    selected_month
                )
            )
        else:
            st.sidebar.warning(
                "No se identificaron meses válidos."
            )

    elif period_mode == "Yearly":
        available_years = (
            time_engine.available_years(
                filtered_data
            )
        )

        if available_years:
            selected_year = (
                st.sidebar.selectbox(
                    "Year",
                    options=available_years,
                    key=(
                        "preview_year"
                    ),
                )
            )

            filtered_data = (
                time_engine.filter_year(
                    filtered_data,
                    selected_year,
                )
            )

            selected_period_label = (
                str(selected_year)
            )
        else:
            st.sidebar.warning(
                "No se identificaron años válidos."
            )

    if time_result.unparsed_count:
        st.sidebar.warning(
            f"{time_result.unparsed_count} registros "
            "no pudieron interpretarse como fecha."
        )

    if filtered_data.empty:
        st.warning(
            "El periodo seleccionado no contiene información."
        )

        st.stop()

    summary = (
        kpi_engine.executive_summary(
            filtered_data
        )
    )

    variance_summary = (
        variance_engine.overall_summary(
            filtered_data
        )
    )

    data_quality_score = (
        calculate_data_quality_score(
            filtered_data
        )
    )

    render_mission_control_workspace(
        dataframe=filtered_data,
        summary=summary,
        variance_summary=(
            variance_summary
        ),
        comparison_label=(
            comparison_label
        ),
        selected_period_label=(
            selected_period_label
        ),
        company_name=(
            sidebar_context[
                "company_name"
            ]
        ),
        currency=(
            sidebar_context[
                "currency"
            ]
        ),
        data_quality_score=(
            data_quality_score
        ),
    )

    with st.expander(
        "Preview Technical Audit"
    ):
        st.write(
            "**Uploaded file**"
        )

        st.write(
            uploaded_file.name
        )

        st.write(
            "**Source profile**"
        )

        st.json(profile)

        st.write(
            "**Semantic mapping**"
        )

        st.json(
            mapping_result
            .mapped_columns
        )

        if (
            mapping_result
            .synthesized_columns
        ):
            st.write(
                "**Synthesized columns**"
            )

            st.write(
                mapping_result
                .synthesized_columns
            )

        if (
            mapping_result
            .warnings
        ):
            st.write(
                "**Mapping warnings**"
            )

            for warning in (
                mapping_result
                .warnings
            ):
                st.warning(
                    warning
                )

        st.write(
            "**Baseline audit**"
        )

        st.dataframe(
            baseline_engine
            .baseline_audit(
                canonical_data
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.write(
            "**Normalized mode audit**"
        )

        st.dataframe(
            freight_engine
            .mode_value_audit(
                prepared_data
            ),
            use_container_width=True,
            hide_index=True,
        )

except Exception as error:
    st.error(
        "No fue posible construir Mission Control Preview."
    )

    st.exception(error)
