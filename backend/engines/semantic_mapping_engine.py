
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class MappingResult:
    dataframe: pd.DataFrame
    mapped_columns: dict[str, str]
    unmapped_columns: list[str]
    missing_required_columns: list[str]
    synthesized_columns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SemanticMappingEngine:
    COLUMN_ALIASES: dict[str, set[str]] = {
        "shipment": {
            "shipment", "shipment number", "shipment id", "shipment no",
            "shipment_number", "shipment_id", "id shipment", "id_shipment",
            "shipment identifier", "shipment code", "id embarque",
            "embarque", "numero embarque", "numero de embarque",
        },
        "mode": {
            "mode", "modo", "transport mode", "transportation mode",
            "freight mode", "business mode", "modalidad",
            "transport type", "shipping mode", "shipment mode",
            "modal", "mode of transport", "tipo transporte",
            "tipo de transporte",
        },
        "product": {
            "product", "producto", "service", "servicio", "service type",
            "shipment type", "movement type", "type", "cargo type",
            "freight type", "load type", "tipo carga",
            "tipo de carga", "tipo_carga", "carga",
        },
        "forwarder": {
            "forwarder", "freight forwarder", "provider",
            "service provider", "proveedor", "agente", "agente de carga",
        },
        "customer": {
            "customer", "customer name", "customer_name", "client",
            "client name", "client_name", "cliente",
            "nombre cliente", "nombre del cliente", "account",
            "account name", "key account", "sold to", "sold_to",
            "shipper", "consignee", "business partner",
        },
        "trade_lane": {
            "trade lane", "tradelane", "trade_lane", "lane", "route",
            "route name", "lane name", "ruta", "ruta comercial",
            "corredor", "corridor",
        },
        "origin": {
            "origin", "origen", "origin location", "origin port",
            "origin country", "origin_country", "country origin",
            "country of origin", "pais origen", "país origen",
            "pol", "departure", "salida",
        },
        "destination": {
            "destination", "destino", "destination location",
            "destination port", "destination country",
            "destination_country", "country destination",
            "country of destination", "pais destino", "país destino",
            "pod", "arrival", "llegada",
        },
        "teus": {"teus", "teu", "total teus", "volume teu", "volumen teu"},
        "tons": {
            "tons", "ton", "tonnes", "toneladas", "peso toneladas",
            "weight tons", "weight tonnes", "weight_tons", "total tons",
        },
        "actual_revenue": {
            "revenue", "actual revenue", "actual_revenue", "real revenue",
            "real_revenue", "revenue actual", "booked revenue",
            "actual sales", "real sales", "net revenue",
            "sales", "income", "billing", "ingresos", "ingreso",
            "ingresos reales", "ingreso real", "ventas reales",
            "ingresos usd", "ingresos_usd", "ventas",
            "facturacion", "facturacion usd",
        },
        "actual_cost": {
            "cost", "actual cost", "actual_cost", "real cost", "real_cost",
            "cost actual", "booked cost", "actual expense",
            "real expense", "direct cost", "transportation cost",
            "buy cost", "costos", "costo", "costos reales",
            "costo real", "gasto real",
            "costos usd", "costos_usd", "costo directo",
        },
        "actual_gp": {
            "gross profit", "gp", "actual gp", "actual_gp", "profit",
            "utilidad", "utilidad usd", "utilidad_usd", "margen bruto",
        },
        "reserve_revenue": {
            "revenue reserve",
            "revenue_reserve",
            "reserved revenue",
            "reserve revenue",
            "revenue accrual",
            "accrued revenue",
            "revenue provision",
            "provisioned revenue",
            "expected revenue",
            "estimated reserve revenue",
            "reserva ingresos",
            "reserva de ingresos",
            "ingresos reservados",
            "ingresos devengados",
            "provision ingresos",
            "provisión ingresos",
        },
        "reserve_cost": {
            "cost reserve",
            "cost_reserve",
            "reserved cost",
            "reserve cost",
            "cost accrual",
            "accrued cost",
            "cost provision",
            "provisioned cost",
            "expected cost",
            "estimated reserve cost",
            "reserva costos",
            "reserva de costos",
            "costos reservados",
            "costos devengados",
            "provision costos",
            "provisión costos",
        },
        "budget_revenue": {
            "budget revenue", "budget_revenue", "estimated revenue",
            "est revenue", "forecast revenue", "presupuesto ingresos",
            "ingresos presupuesto", "budget ingresos",
        },
        "budget_cost": {
            "budget cost", "budget_cost", "estimated cost",
            "est cost", "forecast cost", "presupuesto costos",
            "costos presupuesto", "budget costos",
        },
        "period": {
            "date", "fecha", "month", "month name", "month_number",
            "posting month", "closing month", "accounting month",
            "mes", "mes contable", "mes cierre", "period",
            "periodo", "accounting period", "reporting period",
            "fiscal period", "fecha reporte",
        },
        "year": {
            "year", "ano", "año", "aÃ±o", "fiscal year", "ejercicio",
        },
    }

    REQUIRED_COLUMNS = {
        "actual_revenue",
        "actual_cost",
        "period",
    }

    NUMERIC_COLUMNS = {
        "teus", "tons", "actual_revenue", "actual_cost", "actual_gp",
        "budget_revenue", "budget_cost", "reserve_revenue", "reserve_cost",
    }

    def map_dataframe(self, dataframe: pd.DataFrame) -> MappingResult:
        source_to_canonical: dict[str, str] = {}
        used_canonical_names: set[str] = set()
        unmapped_columns: list[str] = []

        normalized_aliases = self._build_normalized_aliases()

        for source_column in dataframe.columns:
            source_text = str(source_column)
            normalized_source = self.normalize_name(source_text)
            canonical_name = normalized_aliases.get(normalized_source)

            if canonical_name and canonical_name not in used_canonical_names:
                source_to_canonical[source_text] = canonical_name
                used_canonical_names.add(canonical_name)
            else:
                unmapped_columns.append(source_text)

        df = dataframe.rename(columns=source_to_canonical).copy()
        df = self._standardize_values(df)

        synthesized_columns: list[str] = []
        warnings: list[str] = []

        if "shipment" not in df.columns:
            df["shipment"] = [
                f"AUTO-{index:06d}"
                for index in range(1, len(df) + 1)
            ]
            synthesized_columns.append("shipment")

        if "mode" not in df.columns:
            df["mode"] = "Unclassified"
            synthesized_columns.append("mode")

        if "product" not in df.columns:
            df["product"] = "Unclassified"
            synthesized_columns.append("product")

        if {"actual_revenue", "actual_cost"}.issubset(df.columns):
            df["actual_gp"] = df["actual_revenue"] - df["actual_cost"]

        reserve_baseline_used = False

        if "budget_revenue" not in df.columns:
            if "reserve_revenue" in df.columns:
                df["budget_revenue"] = df["reserve_revenue"]
                reserve_baseline_used = True
            elif "actual_revenue" in df.columns:
                df["budget_revenue"] = df["actual_revenue"]

            if "budget_revenue" in df.columns:
                synthesized_columns.append("budget_revenue")

        if "budget_cost" not in df.columns:
            if "reserve_cost" in df.columns:
                df["budget_cost"] = df["reserve_cost"]
                reserve_baseline_used = True
            elif "actual_cost" in df.columns:
                df["budget_cost"] = df["actual_cost"]

            if "budget_cost" in df.columns:
                synthesized_columns.append("budget_cost")

        if reserve_baseline_used:
            warnings.append(
                "El archivo contiene Reserve Revenue y/o Reserve Cost, "
                "pero no Budget. Para mantener compatibilidad con el "
                "Variance Engine actual, Reserve se utilizó como baseline "
                "temporal. Las visualizaciones etiquetadas como Budget "
                "representan realmente Actual vs Reserve."
            )
        elif (
            "budget_revenue" in synthesized_columns
            or "budget_cost" in synthesized_columns
        ):
            warnings.append(
                "El archivo no contiene Budget ni Reserve completos. "
                "La plataforma utilizó Actual como baseline temporal. "
                "Las variaciones no representan un análisis presupuestal real."
            )

        if {"period", "year"}.issubset(df.columns):
            period_text = df["period"].astype(str).str.strip()
            year_text = df["year"].astype(str).str.strip()
            has_year = period_text.str.contains(r"20\d{2}", regex=True, na=False)
            df.loc[~has_year, "period"] = (
                period_text[~has_year] + " " + year_text[~has_year]
            )

        missing_required = sorted(
            self.REQUIRED_COLUMNS - set(df.columns)
        )

        return MappingResult(
            dataframe=df,
            mapped_columns=source_to_canonical,
            unmapped_columns=unmapped_columns,
            missing_required_columns=missing_required,
            synthesized_columns=synthesized_columns,
            warnings=warnings,
        )

    def _build_normalized_aliases(self) -> dict[str, str]:
        alias_lookup: dict[str, str] = {}
        for canonical_name, aliases in self.COLUMN_ALIASES.items():
            alias_lookup[self.normalize_name(canonical_name)] = canonical_name
            for alias in aliases:
                alias_lookup[self.normalize_name(alias)] = canonical_name
        return alias_lookup

    def _standardize_values(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()

        for column in self.NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                ).fillna(0.0)

        if "mode" in df.columns:
            df["mode"] = (
                df["mode"]
                .fillna("Unclassified")
                .astype(str)
                .str.strip()
                .str.lower()
                .replace(
                    {
                        "sea": "Ocean",
                        "sea freight": "Ocean",
                        "maritime": "Ocean",
                        "maritimo": "Ocean",
                        "marítimo": "Ocean",
                        "ocean freight": "Ocean",
                        "ocean": "Ocean",
                        "fcl": "Ocean",
                        "lcl": "Ocean",
                        "container": "Ocean",
                        "containerized": "Ocean",
                        "air freight": "Air",
                        "air cargo": "Air",
                        "airfreight": "Air",
                        "aereo": "Air",
                        "aéreo": "Air",
                        "air": "Air",
                        "road": "Ground",
                        "road freight": "Ground",
                        "truck": "Ground",
                        "trucking": "Ground",
                        "ground": "Ground",
                        "land": "Ground",
                        "terrestre": "Ground",
                        "rail": "Rail",
                        "rail freight": "Rail",
                    }
                )
                .str.title()
            )

        if "product" in df.columns:
            df["product"] = (
                df["product"]
                .fillna("Unclassified")
                .astype(str)
                .str.strip()
                .str.title()
            )

        for column in {
            "shipment", "forwarder", "customer", "trade_lane",
            "origin", "destination", "period", "year",
        }:
            if column in df.columns:
                df[column] = (
                    df[column]
                    .fillna("Unassigned")
                    .astype(str)
                    .str.strip()
                )

        return df

    @classmethod
    def normalize_name(cls, value: str) -> str:
        text = cls._repair_common_mojibake(value)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            ch for ch in text if not unicodedata.combining(ch)
        )
        text = text.lower().strip()
        text = re.sub(r"[_\-]+", " ", text)
        text = re.sub(r"[^a-z0-9 ]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _repair_common_mojibake(value: str) -> str:
        replacements = {
            "Ã±": "ñ", "Ã‘": "Ñ", "Ã¡": "á", "Ã©": "é",
            "Ã­": "í", "Ã³": "ó", "Ãº": "ú", "Â": "",
        }
        repaired = value
        for bad, good in replacements.items():
            repaired = repaired.replace(bad, good)
        return repaired
