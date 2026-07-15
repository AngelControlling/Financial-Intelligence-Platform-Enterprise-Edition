from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd

from engines.universal_date_parser_engine import (
    UniversalDateParserEngine,
)


@dataclass(frozen=True)
class WorkingCapitalMappingResult:
    """Result returned by the Working Capital Semantic Mapping Engine."""

    dataframe: pd.DataFrame
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    missing_required_columns: list[str]
    synthesized_columns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class WorkingCapitalSemanticMappingEngine:
    """
    Maps heterogeneous AR/AP files into the canonical Working Capital model.

    Canonical columns:
    - document_id
    - counterparty
    - document_type
    - invoice_date
    - due_date
    - original_amount
    - paid_amount
    - open_amount
    - currency
    - status
    - responsible
    - business_unit
    - purchase_order
    - payment_date
    - dispute_reason
    """

    COLUMN_ALIASES: dict[str, set[str]] = {
        "document_id": {
            "document id",
            "document_id",
            "document number",
            "document no",
            "doc id",
            "doc number",
            "invoice id",
            "invoice_id",
            "invoice identifier",
            "invoice number",
            "invoice no",
            "invoice",
            "bill id",
            "bill number",
            "billing document",
            "accounting document",
            "voucher",
            "folio",
            "folio factura",
            "numero factura",
            "número factura",
            "numero de factura",
            "factura",
            "id factura",
            "documento",
            "numero documento",
            "número documento",
            "reference",
            "reference number",
        },
        "counterparty": {
            "counterparty",
            "customer",
            "customer name",
            "client",
            "client name",
            "account",
            "account name",
            "sold to",
            "bill to",
            "vendor",
            "vendor name",
            "supplier",
            "supplier name",
            "business partner",
            "cliente",
            "nombre cliente",
            "nombre del cliente",
            "proveedor",
            "nombre proveedor",
            "nombre del proveedor",
            "acreedor",
            "deudor",
            "tercero",
            "contraparte",
        },
        "document_type": {
            "document type",
            "document_type",
            "account type",
            "account_type",
            "ledger type",
            "ar ap",
            "ar/ap",
            "receivable payable",
            "type",
            "tipo documento",
            "tipo de documento",
            "tipo cuenta",
            "tipo de cuenta",
            "cuenta",
            "naturaleza",
            "modulo",
            "módulo",
        },
        "invoice_date": {
            "invoice date",
            "invoice_date",
            "billing date",
            "bill date",
            "posting date",
            "document date",
            "creation date",
            "issue date",
            "date",
            "fecha",
            "fecha factura",
            "fecha_factura",
            "fecha de factura",
            "fecha documento",
            "fecha_documento",
            "fecha de documento",
            "fecha emision",
            "fecha emisión",
            "fecha contabilizacion",
            "fecha contabilización",
            "fecha registro",
        },
        "due_date": {
            "due date",
            "due_date",
            "payment due date",
            "maturity date",
            "net due date",
            "fecha vencimiento",
            "fecha_vencimiento",
            "fecha de vencimiento",
            "vencimiento",
            "fecha limite",
            "fecha límite",
            "fecha pago esperada",
        },
        "original_amount": {
            "original amount",
            "original_amount",
            "invoice amount",
            "invoice value",
            "gross amount",
            "document amount",
            "total amount",
            "amount",
            "monto original",
            "monto_original",
            "importe original",
            "importe_original",
            "monto factura",
            "importe factura",
            "valor factura",
            "monto",
            "importe",
            "total",
        },
        "paid_amount": {
            "paid amount",
            "paid_amount",
            "payment amount",
            "applied amount",
            "settled amount",
            "collected amount",
            "received amount",
            "amount paid",
            "amount collected",
            "monto pagado",
            "monto_pagado",
            "importe pagado",
            "pago aplicado",
            "monto cobrado",
            "monto_cobrado",
            "importe cobrado",
            "cobrado",
            "pagado",
        },
        "open_amount": {
            "open amount",
            "open_amount",
            "outstanding amount",
            "outstanding balance",
            "open balance",
            "remaining balance",
            "balance due",
            "unpaid amount",
            "unsettled amount",
            "saldo pendiente",
            "saldo_pendiente",
            "saldo abierto",
            "saldo_abierto",
            "saldo vencido",
            "pendiente",
            "monto pendiente",
            "importe pendiente",
            "saldo",
            "open",
            "outstanding",
        },
        "currency": {
            "currency",
            "currency code",
            "document currency",
            "transaction currency",
            "moneda",
            "codigo moneda",
            "código moneda",
            "divisa",
        },
        "status": {
            "status",
            "document status",
            "invoice status",
            "payment status",
            "collection status",
            "workflow status",
            "estado",
            "estatus",
            "estado factura",
            "estatus factura",
            "estado pago",
            "estatus pago",
            "situacion",
            "situación",
        },
        "responsible": {
            "responsible",
            "owner",
            "collector",
            "collection owner",
            "credit analyst",
            "account manager",
            "buyer",
            "approver",
            "payment owner",
            "responsable",
            "responsable cobranza",
            "analista cobranza",
            "gestor",
            "comprador",
            "aprobador",
            "dueño",
            "dueno",
        },
        "business_unit": {
            "business unit",
            "business_unit",
            "company code",
            "legal entity",
            "entity",
            "division",
            "branch",
            "profit center",
            "cost center",
            "unidad negocio",
            "unidad de negocio",
            "sociedad",
            "entidad legal",
            "division",
            "división",
            "sucursal",
            "centro beneficio",
            "centro de costo",
        },
        "purchase_order": {
            "purchase order",
            "purchase_order",
            "po",
            "po number",
            "purchase order number",
            "orden compra",
            "orden de compra",
            "numero orden compra",
            "número orden compra",
            "pedido",
        },
        "payment_date": {
            "payment date",
            "payment_date",
            "collection date",
            "settlement date",
            "clearing date",
            "fecha pago",
            "fecha_pago",
            "fecha de pago",
            "fecha cobro",
            "fecha_cobro",
            "fecha compensacion",
            "fecha compensación",
        },
        "dispute_reason": {
            "dispute reason",
            "dispute_reason",
            "hold reason",
            "rejection reason",
            "block reason",
            "exception reason",
            "motivo disputa",
            "motivo reclamo",
            "motivo bloqueo",
            "motivo rechazo",
            "causa",
            "comentario",
            "comments",
            "notes",
        },
    }

    REQUIRED_COLUMNS = {
        "document_id",
        "counterparty",
        "document_type",
        "invoice_date",
        "due_date",
    }

    NUMERIC_COLUMNS = {
        "original_amount",
        "paid_amount",
        "open_amount",
    }

    TEXT_COLUMNS = {
        "document_id",
        "counterparty",
        "document_type",
        "currency",
        "status",
        "responsible",
        "business_unit",
        "purchase_order",
        "dispute_reason",
    }

    DATE_COLUMNS = {
        "invoice_date",
        "due_date",
        "payment_date",
    }

    AR_STATUS_ALIASES = {
        "draft": "Draft",
        "borrador": "Draft",
        "created": "Draft",
        "created draft": "Draft",
        "posted": "Posted / Open",
        "open": "Posted / Open",
        "posted open": "Posted / Open",
        "open item": "Posted / Open",
        "abierta": "Posted / Open",
        "abierto": "Posted / Open",
        "contabilizada": "Posted / Open",
        "paid": "Paid / Closed",
        "closed": "Paid / Closed",
        "paid closed": "Paid / Closed",
        "cleared": "Paid / Closed",
        "pagada": "Paid / Closed",
        "pagado": "Paid / Closed",
        "cerrada": "Paid / Closed",
        "cerrado": "Paid / Closed",
        "partially paid": "Partially Paid",
        "partial payment": "Partially Paid",
        "part paid": "Partially Paid",
        "parcialmente pagada": "Partially Paid",
        "pago parcial": "Partially Paid",
        "partially collected": "Partially Paid",
        "disputed": "Disputed",
        "in dispute": "Disputed",
        "customer dispute": "Disputed",
        "reclamada": "Disputed",
        "en disputa": "Disputed",
        "rechazada cliente": "Disputed",
        "void": "Void / Cancelled",
        "cancelled": "Void / Cancelled",
        "canceled": "Void / Cancelled",
        "void cancelled": "Void / Cancelled",
        "anulada": "Void / Cancelled",
        "cancelada": "Void / Cancelled",
        "credit note issued": "Credit Note Issued",
        "credit memo issued": "Credit Note Issued",
        "credit note": "Credit Note Issued",
        "nota de credito": "Credit Note Issued",
        "nota crédito": "Credit Note Issued",
        "overdue": "Overdue",
        "past due": "Overdue",
        "vencida": "Overdue",
        "vencido": "Overdue",
        "in process": "In Process",
        "processing": "In Process",
        "pending validation": "In Process",
        "en proceso": "In Process",
        "validacion fiscal": "In Process",
        "validación fiscal": "In Process",
    }

    AP_STATUS_ALIASES = {
        "created": "Created / Entry",
        "entry": "Created / Entry",
        "created entry": "Created / Entry",
        "entered": "Created / Entry",
        "captured": "Created / Entry",
        "registrada": "Created / Entry",
        "capturada": "Created / Entry",
        "ingresada": "Created / Entry",
        "validated": "Validated / Verified",
        "verified": "Validated / Verified",
        "validated verified": "Validated / Verified",
        "checked": "Validated / Verified",
        "validada": "Validated / Verified",
        "verificada": "Validated / Verified",
        "pending approval": "Pending Approval",
        "awaiting approval": "Pending Approval",
        "approval pending": "Pending Approval",
        "pendiente aprobacion": "Pending Approval",
        "pendiente aprobación": "Pending Approval",
        "en aprobacion": "Pending Approval",
        "approved": "Approved",
        "authorized": "Approved",
        "aprobada": "Approved",
        "autorizada": "Approved",
        "on hold": "On Hold",
        "blocked": "On Hold",
        "payment block": "On Hold",
        "hold": "On Hold",
        "bloqueada": "On Hold",
        "en espera": "On Hold",
        "scheduled": "Scheduled / Ready to Pay",
        "ready to pay": "Scheduled / Ready to Pay",
        "scheduled ready to pay": "Scheduled / Ready to Pay",
        "payment run": "Scheduled / Ready to Pay",
        "programada": "Scheduled / Ready to Pay",
        "lista para pagar": "Scheduled / Ready to Pay",
        "paid": "Paid",
        "cleared": "Paid",
        "pagada": "Paid",
        "pagado": "Paid",
        "rejected": "Rejected",
        "rechazada": "Rejected",
        "rechazado": "Rejected",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
        "void": "Cancelled",
        "cancelada": "Cancelled",
        "anulada": "Cancelled",
    }

    def __init__(self) -> None:
        self.date_parser = UniversalDateParserEngine()

    DOCUMENT_TYPE_ALIASES = {
        "ar": "AR",
        "accounts receivable": "AR",
        "receivable": "AR",
        "customer": "AR",
        "client": "AR",
        "billing": "AR",
        "billing cycle": "AR",
        "cuentas por cobrar": "AR",
        "cuenta por cobrar": "AR",
        "cobranza": "AR",
        "clientes": "AR",
        "ap": "AP",
        "accounts payable": "AP",
        "payable": "AP",
        "vendor": "AP",
        "supplier": "AP",
        "procurement": "AP",
        "payment cycle": "AP",
        "cuentas por pagar": "AP",
        "cuenta por pagar": "AP",
        "pagos": "AP",
        "proveedores": "AP",
    }

    def map_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> WorkingCapitalMappingResult:
        source_to_canonical: dict[str, str] = {}
        used_canonical_names: set[str] = set()
        unmapped_columns: list[str] = []

        normalized_source_columns = {
            self.normalize_name(str(column))
            for column in dataframe.columns
        }

        has_customer_header = any(
            column in normalized_source_columns
            for column in {
                "customer",
                "customer name",
                "client",
                "client name",
                "cliente",
                "nombre cliente",
                "nombre del cliente",
            }
        )

        has_supplier_header = any(
            column in normalized_source_columns
            for column in {
                "supplier",
                "supplier name",
                "vendor",
                "vendor name",
                "proveedor",
                "nombre proveedor",
                "nombre del proveedor",
            }
        )

        normalized_aliases = self._build_normalized_aliases()

        for source_column in dataframe.columns:
            source_text = str(source_column)
            normalized_source = self.normalize_name(source_text)
            canonical_name = normalized_aliases.get(
                normalized_source
            )

            if (
                canonical_name
                and canonical_name not in used_canonical_names
            ):
                source_to_canonical[source_text] = canonical_name
                used_canonical_names.add(canonical_name)
            else:
                unmapped_columns.append(source_text)

        df = dataframe.rename(
            columns=source_to_canonical
        ).copy()

        df = self._standardize_values(df)

        synthesized_columns: list[str] = []
        warnings: list[str] = []

        if "document_type" not in df.columns:
            if has_customer_header and not has_supplier_header:
                df["document_type"] = "AR"
                synthesized_columns.append("document_type")
                warnings.append(
                    "Document Type no venía en el archivo. Se infirió AR "
                    "porque se detectó una columna Customer/Cliente."
                )
            elif has_supplier_header and not has_customer_header:
                df["document_type"] = "AP"
                synthesized_columns.append("document_type")
                warnings.append(
                    "Document Type no venía en el archivo. Se infirió AP "
                    "porque se detectó una columna Supplier/Vendor/Proveedor."
                )

        if (
            "due_date" not in df.columns
            and "invoice_date" in df.columns
        ):
            df["due_date"] = df["invoice_date"]
            synthesized_columns.append("due_date")
            warnings.append(
                "Due Date no venía en el archivo. Se utilizó Invoice Date "
                "como fecha de vencimiento temporal. Para un aging contractual "
                "real, agrega Due Date o Fecha de Vencimiento."
            )

        if "open_amount" not in df.columns:
            if {
                "original_amount",
                "paid_amount",
            }.issubset(df.columns):
                df["open_amount"] = (
                    df["original_amount"]
                    - df["paid_amount"]
                ).clip(lower=0.0)

                synthesized_columns.append(
                    "open_amount"
                )
            elif "original_amount" in df.columns:
                if "status" in df.columns:
                    closed_statuses = {
                        "paid",
                        "closed",
                        "paid closed",
                        "cleared",
                        "void",
                        "cancelled",
                        "canceled",
                        "void cancelled",
                        "pagada",
                        "pagado",
                        "cerrada",
                        "cerrado",
                        "anulada",
                        "cancelada",
                        "rejected",
                        "rechazada",
                        "rechazado",
                    }

                    normalized_status = (
                        df["status"]
                        .astype(str)
                        .map(self.normalize_name)
                    )

                    df["open_amount"] = df[
                        "original_amount"
                    ].where(
                        ~normalized_status.isin(
                            closed_statuses
                        ),
                        0.0,
                    )
                else:
                    df["open_amount"] = df[
                        "original_amount"
                    ]

                synthesized_columns.append(
                    "open_amount"
                )

                warnings.append(
                    "Open Amount no venía en el archivo. Se calculó usando "
                    "Amount y Status; los documentos cerrados/pagados se "
                    "consideraron con saldo cero."
                )
            else:
                warnings.append(
                    "No fue posible calcular open_amount porque "
                    "falta original_amount."
                )

        if (
            "paid_amount" not in df.columns
            and {
                "original_amount",
                "open_amount",
            }.issubset(df.columns)
        ):
            df["paid_amount"] = (
                df["original_amount"]
                - df["open_amount"]
            ).clip(lower=0.0)

            synthesized_columns.append(
                "paid_amount"
            )

        if (
            "original_amount" not in df.columns
            and {
                "paid_amount",
                "open_amount",
            }.issubset(df.columns)
        ):
            df["original_amount"] = (
                df["paid_amount"]
                + df["open_amount"]
            )

            synthesized_columns.append(
                "original_amount"
            )

        if "currency" not in df.columns:
            df["currency"] = "Unassigned"
            synthesized_columns.append("currency")

        if "responsible" not in df.columns:
            df["responsible"] = "Unassigned"
            synthesized_columns.append("responsible")

        if "business_unit" not in df.columns:
            df["business_unit"] = "Unassigned"
            synthesized_columns.append("business_unit")

        if "status" not in df.columns:
            df["status"] = "Open"
            synthesized_columns.append("status")

            warnings.append(
                "El archivo no contenía Status. Se asignó 'Open' "
                "como estado temporal."
            )

        if "document_type" in df.columns:
            df["document_type"] = df[
                "document_type"
            ].map(
                self._normalize_document_type
            )

        if {
            "status",
            "document_type",
        }.issubset(df.columns):
            df["status"] = df.apply(
                lambda row: self._normalize_status(
                    status=row["status"],
                    document_type=row[
                        "document_type"
                    ],
                ),
                axis=1,
            )

        missing_required = sorted(
            self.REQUIRED_COLUMNS
            - set(df.columns)
        )

        return WorkingCapitalMappingResult(
            dataframe=df,
            mapped_columns=source_to_canonical,
            unmapped_columns=unmapped_columns,
            missing_required_columns=missing_required,
            synthesized_columns=synthesized_columns,
            warnings=warnings,
        )

    def _build_normalized_aliases(
        self,
    ) -> dict[str, str]:
        alias_lookup: dict[str, str] = {}

        for canonical_name, aliases in (
            self.COLUMN_ALIASES.items()
        ):
            alias_lookup[
                self.normalize_name(
                    canonical_name
                )
            ] = canonical_name

            for alias in aliases:
                alias_lookup[
                    self.normalize_name(alias)
                ] = canonical_name

        return alias_lookup

    def _standardize_values(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        df = dataframe.copy()

        for column in self.NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0.0)

        for column in self.DATE_COLUMNS:
            if column in df.columns:
                df[column] = (
                    self.date_parser.parse_series(
                        df[column]
                    )
                )

        for column in self.TEXT_COLUMNS:
            if column in df.columns:
                df[column] = (
                    df[column]
                    .fillna("Unassigned")
                    .astype(str)
                    .str.strip()
                )

        if "currency" in df.columns:
            df["currency"] = (
                df["currency"]
                .str.upper()
                .replace(
                    {
                        "US DOLLAR": "USD",
                        "DOLLAR": "USD",
                        "DÓLAR": "USD",
                        "PESO MEXICANO": "MXN",
                        "MEXICAN PESO": "MXN",
                        "EURO": "EUR",
                    }
                )
            )

        return df

    def _normalize_document_type(
        self,
        value,
    ) -> str:
        normalized_value = self.normalize_name(
            str(value)
        )

        return self.DOCUMENT_TYPE_ALIASES.get(
            normalized_value,
            str(value).strip().upper(),
        )

    def _normalize_status(
        self,
        status,
        document_type,
    ) -> str:
        normalized_status = self.normalize_name(
            str(status)
        )

        normalized_type = str(
            document_type
        ).strip().upper()

        if normalized_type == "AR":
            return self.AR_STATUS_ALIASES.get(
                normalized_status,
                str(status).strip(),
            )

        if normalized_type == "AP":
            return self.AP_STATUS_ALIASES.get(
                normalized_status,
                str(status).strip(),
            )

        return str(status).strip()

    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        text = cls._repair_common_mojibake(
            value
        )

        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        text = "".join(
            character
            for character in text
            if not unicodedata.combining(
                character
            )
        )

        text = text.lower().strip()
        text = re.sub(
            r"[_\-/]+",
            " ",
            text,
        )
        text = re.sub(
            r"[^a-z0-9 ]",
            "",
            text,
        )
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    @staticmethod
    def _repair_common_mojibake(
        value: str,
    ) -> str:
        replacements = {
            "Ã±": "ñ",
            "Ã‘": "Ñ",
            "Ã¡": "á",
            "Ã©": "é",
            "Ã­": "í",
            "Ã³": "ó",
            "Ãº": "ú",
            "Â": "",
        }

        repaired = value

        for bad_text, correct_text in (
            replacements.items()
        ):
            repaired = repaired.replace(
                bad_text,
                correct_text,
            )

        return repaired