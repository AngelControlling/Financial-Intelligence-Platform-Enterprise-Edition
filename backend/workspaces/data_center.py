from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from core.notification_manager import (
    NotificationManager,
)
from core.session_manager import SessionManager
from engines.excel_reader import ExcelReader
from repositories.data_lake_repository import (
    DataLakeRepository,
)
from services.actuals_ingestion_service import (
    ActualsIngestionService,
)
from services.budget_ingestion_service import (
    BudgetIngestionService,
)
from services.budget_template_service import (
    BudgetTemplateService,
)
from services.smart_excel_reader import (
    SmartExcelReader,
)
from services.working_capital_ingestion_service import (
    WorkingCapitalIngestionService,
)
from ui.workspace_components import (
    StatusCard,
    render_status_grid,
)


def _source_cards(
    repository: DataLakeRepository,
) -> None:
    cards = []

    specifications = [
        (
            "Actuals",
            "actuals",
            "Monthly freight and P&L performance",
            "A",
        ),
        (
            "Budget",
            "budget",
            "Annual P&L, Operations, OPEX and PERSEX",
            "B",
        ),
        (
            "Forecast",
            "forecast",
            "Rolling forecast and scenarios",
            "F",
        ),
        (
            "Prior Year",
            "prior_year",
            "Historical comparison source",
            "PY",
        ),
        (
            "Working Capital",
            "working_capital",
            "AR, AP and aging",
            "WC",
        ),
        (
            "FX Rates",
            "fx_rates",
            "Currency master source",
            "FX",
        ),
    ]

    for title, key, description, icon in specifications:
        version = repository.active_version(key)

        cards.append(
            StatusCard(
                title=title,
                status=(
                    "Active"
                    if version
                    else "Missing"
                ),
                metric=(
                    version.version_label
                    if version
                    else "Not loaded"
                ),
                description=description,
                meta=(
                    f"{version.rows:,} rows · "
                    f"Health {version.health_score:.0f}%"
                    if version
                    else "No active version"
                ),
                icon=icon,
            )
        )

    render_status_grid(
        cards,
        columns=3,
    )


def _history_table(
    repository: DataLakeRepository,
    dataset_type: str,
) -> None:
    versions = repository.list_versions(
        dataset_type
    )

    if not versions:
        st.info(
            "No versions available."
        )
        return

    dataframe = pd.DataFrame(
        [
            {
                "Version ID": item.version_id,
                "Label": item.version_label,
                "Status": item.status,
                "Rows": item.rows,
                "Quality": item.quality_score,
                "Mapping": item.mapping_score,
                "Health": item.health_score,
                "Source": item.source_name,
                "Created": item.created_at,
                "Activated": item.activated_at,
            }
            for item in versions
        ]
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


def _render_actuals(
    repository: DataLakeRepository,
    session: SessionManager,
    notifications: NotificationManager,
) -> None:
    service = ActualsIngestionService(
        repository
    )

    uploaded = st.file_uploader(
        "Select Actuals source",
        type=["xlsx", "xlsm", "csv"],
        key="data_center_actuals_file",
    )

    if uploaded is None:
        _history_table(
            repository,
            "actuals",
        )
        return

    reader = ExcelReader(uploaded)
    sheet_names = reader.get_sheet_names()

    selected_sheet = st.selectbox(
        "Sheet / Dataset",
        options=sheet_names,
        key="data_center_actuals_sheet",
    )

    source_dataframe = reader.read_sheet(
        selected_sheet
    )

    preview = service.preview(
        source_dataframe,
        source_name=uploaded.name,
        sheet_name=selected_sheet,
    )

    score_1, score_2, score_3 = st.columns(3)
    score_1.metric(
        "Quality",
        f"{preview.scores['quality_score']:.0f}%",
    )
    score_2.metric(
        "Mapping",
        f"{preview.scores['mapping_score']:.0f}%",
    )
    score_3.metric(
        "Health",
        f"{preview.scores['health_score']:.0f}%",
    )

    if preview.profile_applied:
        st.success(
            "A saved Controller mapping profile was applied."
        )

    if preview.missing_required_columns:
        st.error(
            "Missing required columns: "
            + ", ".join(
                preview.missing_required_columns
            )
        )
        st.stop()

    st.success(
        "Actuals passed structural validation."
    )

    audit_1, audit_2 = st.columns(2)

    with audit_1:
        st.markdown("#### Recognized Mapping")
        st.json(
            preview.mapped_columns
        )

    with audit_2:
        st.markdown("#### Unmapped Columns")
        st.write(
            preview.unmapped_columns
            or "None"
        )

    if preview.warnings:
        with st.expander("Validation Warnings"):
            for warning in preview.warnings:
                st.warning(warning)

    with st.expander("Canonical Preview"):
        st.dataframe(
            preview.dataframe.head(100),
            use_container_width=True,
            hide_index=True,
        )

    available_baselines = (
        preview.available_baselines
    )

    if not available_baselines:
        st.error(
            "No complete comparison baseline is available."
        )
        st.stop()

    version_label = st.text_input(
        "Version Label",
        value=(
            "Actuals "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        ),
        key="actuals_version_label",
    )

    comparison = st.selectbox(
        "Active Comparison Baseline",
        options=available_baselines,
        key="actuals_comparison",
    )

    save_profile = st.checkbox(
        "Save this mapping profile after Controller validation",
        value=True,
        key="actuals_save_profile",
    )

    action_1, action_2 = st.columns(2)

    with action_1:
        validate = st.button(
            "Validate and Create Version",
            type="primary",
            use_container_width=True,
            key="actuals_create_version",
        )

    if validate:
        if save_profile:
            service.save_mapping_profile(
                source_name=uploaded.name,
                sheet_name=selected_sheet,
                source_columns=[
                    str(column)
                    for column
                    in source_dataframe.columns
                ],
                mapping=preview.mapped_columns,
            )

        version = service.create_version(
            preview,
            source_name=uploaded.name,
            sheet_name=selected_sheet,
            version_label=version_label,
            company=session.get(
                "fip_company",
                "Enterprise Freight Demo",
            ),
            currency=session.get(
                "fip_currency",
                "USD",
            ),
            comparison_label=comparison,
        )

        st.session_state[
            "fip_pending_actuals_version"
        ] = version.version_id

        notifications.add(
            title="Actuals validated",
            message=(
                f"{version.version_label} is ready "
                "for activation."
            ),
            severity="success",
            workspace_key="data_center",
        )

        st.success(
            f"Version created: "
            f"{version.version_id}"
        )

    pending_id = st.session_state.get(
        "fip_pending_actuals_version"
    )

    with action_2:
        activate = st.button(
            "Activate Validated Version",
            use_container_width=True,
            disabled=not pending_id,
            key="actuals_activate_version",
        )

    if activate and pending_id:
        version = service.activate(
            pending_id
        )
        st.session_state.pop(
            "fip_active_freight_context",
            None,
        )

        notifications.add(
            title="Actuals activated",
            message=(
                f"{version.version_label} now powers "
                "Mission Control."
            ),
            severity="success",
            workspace_key="mission_control",
        )

        st.success(
            "Actuals activated. Mission Control, "
            "Financial and Operations are ready."
        )

    st.markdown("### Actuals Version History")
    _history_table(
        repository,
        "actuals",
    )


def _render_working_capital(
    repository: DataLakeRepository,
    session: SessionManager,
    notifications: NotificationManager,
) -> None:
    service = (
        WorkingCapitalIngestionService(
            repository
        )
    )

    uploaded = st.file_uploader(
        "Select Working Capital AR/AP source",
        type=["xlsx", "xlsm", "csv"],
        key="data_center_wc_file",
    )

    if uploaded is None:
        _history_table(
            repository,
            "working_capital",
        )
        return

    reader = ExcelReader(uploaded)
    sheets = reader.get_sheet_names()

    selected_sheets = st.multiselect(
        "AR/AP Sheets",
        options=sheets,
        default=sheets,
        key="data_center_wc_sheets",
    )

    previews = []

    for sheet_name in selected_sheets:
        dataframe = reader.read_sheet(
            sheet_name
        )
        preview = service.preview(dataframe)
        previews.append(preview)

        with st.expander(
            f"{sheet_name} Validation"
        ):
            st.write(
                {
                    "Quality": (
                        preview.scores[
                            "quality_score"
                        ]
                    ),
                    "Mapping": (
                        preview.scores[
                            "mapping_score"
                        ]
                    ),
                    "Health": (
                        preview.scores[
                            "health_score"
                        ]
                    ),
                }
            )
            st.json(
                preview.mapped_columns
            )
            if preview.missing_required_columns:
                st.error(
                    preview.missing_required_columns
                )

    if not previews:
        st.warning(
            "Select at least one AR/AP sheet."
        )
        return

    version_label = st.text_input(
        "Working Capital Version Label",
        value=(
            "Working Capital "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        ),
        key="wc_version_label",
    )

    wc_action_1, wc_action_2 = st.columns(2)

    with wc_action_1:
        create = st.button(
            "Validate Working Capital",
            type="primary",
            use_container_width=True,
            key="wc_create_version",
        )

    if create:
        version = service.create_version(
            previews,
            source_name=uploaded.name,
            version_label=version_label,
            company=session.get(
                "fip_company",
                "Enterprise Freight Demo",
            ),
            currency=session.get(
                "fip_currency",
                "USD",
            ),
        )
        st.session_state[
            "fip_pending_wc_version"
        ] = version.version_id
        notifications.add(
            title="Working Capital validated",
            message=(
                f"{version.version_label} is ready "
                "for activation."
            ),
            severity="success",
            workspace_key="data_center",
        )
        st.success(
            f"Version created: "
            f"{version.version_id}"
        )

    pending_id = st.session_state.get(
        "fip_pending_wc_version"
    )

    with wc_action_2:
        activate = st.button(
            "Activate Working Capital",
            use_container_width=True,
            disabled=not pending_id,
            key="wc_activate_version",
        )

    if activate and pending_id:
        version = service.activate(
            pending_id
        )
        notifications.add(
            title="Working Capital activated",
            message=(
                f"{version.version_label} is now active."
            ),
            severity="success",
            workspace_key="financial",
        )
        st.success(
            "Working Capital activated."
        )

    st.markdown(
        "### Working Capital Version History"
    )
    _history_table(
        repository,
        "working_capital",
    )



def _render_budget(
    repository: DataLakeRepository,
    session: SessionManager,
    notifications: NotificationManager,
) -> None:
    service = BudgetIngestionService(
        repository
    )
    template_service = BudgetTemplateService()

    st.markdown("#### Official FIP Budget Standard")

    try:
        template_bytes = template_service.read_bytes()
        st.download_button(
            "Download FIP Budget Template V1",
            data=template_bytes,
            file_name=(
                template_service.TEMPLATE_NAME
            ),
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
            type="primary",
        )
    except FileNotFoundError as error:
        st.error(str(error))

    st.caption(
        "Use the official template for P&L, Operations, OPEX, "
        "Personnel/PERSEX and Balance Sheet."
    )

    uploaded = st.file_uploader(
        "Select completed FIP Budget Template",
        type=["xlsx", "xlsm"],
        key="data_center_budget_file",
    )

    if uploaded is None:
        _history_table(
            repository,
            "budget",
        )
        return

    reader = SmartExcelReader(uploaded)

    sheets = {
        sheet_name: reader.read_sheet(
            sheet_name,
            required_headers=(
                SmartExcelReader.DEFAULT_HEADER_HINTS.get(
                    sheet_name
                )
            ),
        )
        for sheet_name
        in reader.get_sheet_names()
        if sheet_name.startswith("Budget_")
    }

    result = service.validate(sheets)

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric(
        "Quality",
        f"{result.quality_score:.0f}%",
    )
    metric_2.metric(
        "Completeness",
        f"{result.completeness_score:.0f}%",
    )
    metric_3.metric(
        "Performance Rows",
        f"{len(result.performance):,}",
    )

    if result.errors:
        for error in result.errors:
            st.error(error)
        st.stop()

    st.success(
        "Budget passed the official FIP structure validation."
    )

    if result.warnings:
        with st.expander("Budget Validation Warnings"):
            for warning in result.warnings:
                st.warning(warning)

    summary_1, summary_2, summary_3 = st.columns(3)
    summary_1.write(
        {
            "Fiscal Years": result.fiscal_years,
        }
    )
    summary_2.write(
        {
            "Currencies": result.currencies,
        }
    )
    summary_3.write(
        {
            "Versions": result.versions,
        }
    )

    with st.expander("Budget Performance Preview"):
        st.dataframe(
            result.performance.head(100),
            use_container_width=True,
            hide_index=True,
        )

    version_label = st.text_input(
        "Budget Version Label",
        value=(
            (
                result.versions[0]
                if len(result.versions) == 1
                else "Budget"
            )
            + " "
            + (
                f"FY{result.fiscal_years[0]}"
                if len(result.fiscal_years) == 1
                else datetime.now().strftime("%Y")
            )
        ),
        key="budget_version_label",
    )

    action_1, action_2 = st.columns(2)

    with action_1:
        create = st.button(
            "Validate and Create Budget Version",
            type="primary",
            use_container_width=True,
            key="budget_create_version",
        )

    if create:
        version = service.create_version(
            result,
            source_name=uploaded.name,
            version_label=version_label,
            company=session.get(
                "fip_company",
                "Enterprise Freight Demo",
            ),
            currency=session.get(
                "fip_currency",
                "USD",
            ),
        )

        st.session_state[
            "fip_pending_budget_version"
        ] = version.version_id

        notifications.add(
            title="Budget validated",
            message=(
                f"{version.version_label} is ready "
                "for activation."
            ),
            severity="success",
            workspace_key="data_center",
        )

        st.success(
            f"Budget version created: "
            f"{version.version_id}"
        )

    pending_id = st.session_state.get(
        "fip_pending_budget_version"
    )

    with action_2:
        activate = st.button(
            "Activate Budget Version",
            use_container_width=True,
            disabled=not pending_id,
            key="budget_activate_version",
        )

    if activate and pending_id:
        version = service.activate(
            pending_id
        )

        st.session_state.pop(
            "fip_active_freight_context",
            None,
        )

        notifications.add(
            title="Budget activated",
            message=(
                f"{version.version_label} now powers "
                "Actual vs Budget analysis."
            ),
            severity="success",
            workspace_key="mission_control",
        )

        st.success(
            "Budget activated. Mission Control will now "
            "use the independent annual Budget source."
        )

    st.markdown("### Budget Version History")
    _history_table(
        repository,
        "budget",
    )

def render_data_center_workspace() -> None:
    session = SessionManager()
    session.initialize()
    notifications = NotificationManager(
        session
    )
    repository = DataLakeRepository()

    _source_cards(repository)

    st.markdown("### Dataset Management")

    actuals_tab, budget_tab, wc_tab, future_tab = st.tabs(
        [
            "Actuals",
            "Budget",
            "Working Capital",
            "Forecast / Prior Year / FX",
        ]
    )

    with actuals_tab:
        _render_actuals(
            repository,
            session,
            notifications,
        )

    with budget_tab:
        _render_budget(
            repository,
            session,
            notifications,
        )

    with wc_tab:
        _render_working_capital(
            repository,
            session,
            notifications,
        )

    with future_tab:
        st.info(
            "Forecast, Prior Year and FX remain reserved "
            "in the frozen V2 scope. Budget is now active."
        )

        st.markdown(
            """
            **Budget Standard scope**

            - P&L: Revenue, Cost, GP and Margin
            - Operations: Shipments, TEUs and Tons
            - OPEX
            - PERSEX and Headcount
            - Balance Sheet and Working Capital targets
            - Versioning: Original, Revised and Latest
            """
        )
