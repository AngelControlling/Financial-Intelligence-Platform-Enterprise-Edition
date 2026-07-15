from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd


class FreightIntelligenceEngine:
    """Segments freight data and calculates business performance."""

    MODE_ALIASES = {
        "air": "Air",
        "air freight": "Air",
        "airfreight": "Air",
        "air cargo": "Air",
        "aereo": "Air",
        "aéreo": "Air",
        "avion": "Air",
        "avión": "Air",
        "ocean": "Ocean",
        "ocean freight": "Ocean",
        "sea": "Ocean",
        "sea freight": "Ocean",
        "maritime": "Ocean",
        "maritimo": "Ocean",
        "marítimo": "Ocean",
        "fcl": "Ocean",
        "lcl": "Ocean",
        "container": "Ocean",
        "containerized": "Ocean",
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

    AIR_HINTS = {
        "air", "airfreight", "air freight", "air cargo",
        "aereo", "aéreo", "airport", "awb",
    }

    OCEAN_HINTS = {
        "ocean", "sea", "maritime", "maritimo", "marítimo",
        "fcl", "lcl", "container", "teu", "port",
    }

    GROUND_HINTS = {
        "road", "truck", "trucking", "ground", "land",
        "terrestre", "ltl", "ftl",
    }

    def prepare_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()

        if "mode" not in df.columns:
            df["mode"] = "Unclassified"

        if "product" not in df.columns:
            df["product"] = "Unclassified"

        df["product"] = (
            df["product"]
            .fillna("Unclassified")
            .astype(str)
            .str.strip()
        )

        df["mode"] = df.apply(
            self._resolve_mode,
            axis=1,
        )

        for column in [
            "customer",
            "origin",
            "destination",
            "forwarder",
        ]:
            if column not in df.columns:
                df[column] = "Unassigned"

            df[column] = (
                df[column]
                .fillna("Unassigned")
                .astype(str)
                .str.strip()
                .replace("", "Unassigned")
            )

        if "trade_lane" not in df.columns:
            df["trade_lane"] = "Unassigned"

        df["trade_lane"] = (
            df["trade_lane"]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
            .replace("", "Unassigned")
        )

        needs_lane = df["trade_lane"].str.casefold().isin(
            {"unassigned", "unclassified", "nan", "none", ""}
        )

        valid_origin = ~df["origin"].str.casefold().isin(
            {"unassigned", "unclassified", "nan", "none", ""}
        )
        valid_destination = ~df["destination"].str.casefold().isin(
            {"unassigned", "unclassified", "nan", "none", ""}
        )

        can_build_lane = needs_lane & valid_origin & valid_destination

        df.loc[can_build_lane, "trade_lane"] = (
            df.loc[can_build_lane, "origin"]
            + " → "
            + df.loc[can_build_lane, "destination"]
        )

        required_financial_columns = [
            "actual_revenue",
            "actual_cost",
            "budget_revenue",
            "budget_cost",
        ]

        for column in required_financial_columns:
            if column not in df.columns:
                raise ValueError(
                    f"La columna canónica '{column}' es obligatoria."
                )

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        for column in ["tons", "teus"]:
            if column not in df.columns:
                df[column] = 0.0

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        if "shipment" not in df.columns:
            df["shipment"] = [
                f"AUTO-{index:06d}"
                for index in range(1, len(df) + 1)
            ]

        if "actual_gp" not in df.columns:
            df["actual_gp"] = (
                df["actual_revenue"] - df["actual_cost"]
            )

        if "budget_gp" not in df.columns:
            df["budget_gp"] = (
                df["budget_revenue"] - df["budget_cost"]
            )

        if "gp_variance" not in df.columns:
            df["gp_variance"] = (
                df["actual_gp"] - df["budget_gp"]
            )

        df["gp_margin"] = np.where(
            df["actual_revenue"] != 0,
            df["actual_gp"] / df["actual_revenue"],
            0.0,
        )

        return df

    def get_available_modes(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        df = self.prepare_data(dataframe)

        return sorted(
            value
            for value in df["mode"].dropna().unique().tolist()
            if value
        )

    def filter_by_mode(
        self,
        dataframe: pd.DataFrame,
        mode: str,
    ) -> pd.DataFrame:
        df = self.prepare_data(dataframe)

        return df[
            df["mode"].str.casefold() == mode.casefold()
        ].copy()

    def mode_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        df = self.prepare_data(dataframe)

        summary = (
            df.groupby("mode", dropna=False)
            .agg(
                Shipments=("shipment", "nunique"),
                Revenue=("actual_revenue", "sum"),
                Cost=("actual_cost", "sum"),
                GP=("actual_gp", "sum"),
                Budget_GP=("budget_gp", "sum"),
                GP_Variance=("gp_variance", "sum"),
                Tons=("tons", "sum"),
                TEUs=("teus", "sum"),
            )
            .reset_index()
            .rename(columns={"mode": "Mode"})
        )

        summary["GP_Margin"] = np.where(
            summary["Revenue"] != 0,
            summary["GP"] / summary["Revenue"],
            0.0,
        )

        summary["GP_per_Shipment"] = np.where(
            summary["Shipments"] != 0,
            summary["GP"] / summary["Shipments"],
            0.0,
        )

        return summary.sort_values("GP", ascending=False)

    def dimension_summary(
        self,
        dataframe: pd.DataFrame,
        dimension: str,
    ) -> pd.DataFrame:
        df = self.prepare_data(dataframe)

        allowed_dimensions = {
            "product",
            "customer",
            "trade_lane",
            "origin",
            "destination",
            "forwarder",
        }

        if dimension not in allowed_dimensions:
            raise ValueError(
                f"Dimensión no permitida: {dimension}"
            )

        summary = (
            df.groupby(dimension, dropna=False)
            .agg(
                Shipments=("shipment", "nunique"),
                Revenue=("actual_revenue", "sum"),
                Cost=("actual_cost", "sum"),
                GP=("actual_gp", "sum"),
                Budget_GP=("budget_gp", "sum"),
                GP_Variance=("gp_variance", "sum"),
                Tons=("tons", "sum"),
                TEUs=("teus", "sum"),
            )
            .reset_index()
        )

        summary["GP_Margin"] = np.where(
            summary["Revenue"] != 0,
            summary["GP"] / summary["Revenue"],
            0.0,
        )

        summary["GP_per_Shipment"] = np.where(
            summary["Shipments"] != 0,
            summary["GP"] / summary["Shipments"],
            0.0,
        )

        return summary.sort_values("GP", ascending=False)

    def mode_value_audit(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Returns original and normalized mode counts for troubleshooting."""

        df = dataframe.copy()

        if "mode" not in df.columns:
            return pd.DataFrame(
                columns=["Original_Mode", "Normalized_Mode", "Records"]
            )

        original_mode = (
            df["mode"]
            .fillna("Unclassified")
            .astype(str)
            .str.strip()
        )

        normalized_mode = df.apply(
            self._resolve_mode,
            axis=1,
        )

        return (
            pd.DataFrame(
                {
                    "Original_Mode": original_mode,
                    "Normalized_Mode": normalized_mode,
                }
            )
            .groupby(
                ["Original_Mode", "Normalized_Mode"],
                dropna=False,
            )
            .size()
            .reset_index(name="Records")
            .sort_values("Records", ascending=False)
            .reset_index(drop=True)
        )

    def _resolve_mode(self, row: pd.Series) -> str:
        raw_mode = self._normalize_text(
            row.get("mode", "")
        )

        if raw_mode in self.MODE_ALIASES:
            return self.MODE_ALIASES[raw_mode]

        combined_context = " ".join(
            [
                self._normalize_text(
                    row.get("mode", "")
                ),
                self._normalize_text(
                    row.get("product", "")
                ),
            ]
        )

        if self._contains_hint(
            combined_context,
            self.AIR_HINTS,
        ):
            return "Air"

        if self._contains_hint(
            combined_context,
            self.OCEAN_HINTS,
        ):
            return "Ocean"

        if self._contains_hint(
            combined_context,
            self.GROUND_HINTS,
        ):
            return "Ground"

        cleaned_mode = str(
            row.get("mode", "Unclassified")
        ).strip()

        if not cleaned_mode or cleaned_mode.casefold() in {
            "nan",
            "none",
            "unassigned",
        }:
            return "Unclassified"

        return cleaned_mode.title()

    @staticmethod
    def _contains_hint(
        text: str,
        hints: set[str],
    ) -> bool:
        return any(
            re.search(
                rf"(^|[^a-z0-9]){re.escape(hint)}([^a-z0-9]|$)",
                text,
            )
            for hint in hints
        )

    @staticmethod
    def _normalize_text(value) -> str:
        text = str(value).strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            character
            for character in text
            if not unicodedata.combining(character)
        )
        text = re.sub(r"[_/\\-]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text
