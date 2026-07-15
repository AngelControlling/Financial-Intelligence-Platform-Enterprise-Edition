from __future__ import annotations

import pandas as pd


class DataQualityService:
    """Deterministic quality, completeness and mapping scoring."""

    INVALID_TEXT = {
        "",
        "nan",
        "none",
        "null",
        "unassigned",
        "unclassified",
    }

    def score(
        self,
        dataframe: pd.DataFrame,
        required_columns: set[str],
        mapped_count: int,
        source_column_count: int,
    ) -> dict[str, float]:
        if dataframe.empty:
            return {
                "quality_score": 0.0,
                "mapping_score": 0.0,
                "health_score": 0.0,
            }

        required_present = (
            len(
                required_columns
                & set(dataframe.columns)
            )
            / max(len(required_columns), 1)
        )

        completeness_scores = []

        for column in required_columns:
            if column not in dataframe.columns:
                completeness_scores.append(0.0)
                continue

            series = dataframe[column]

            if pd.api.types.is_numeric_dtype(series):
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
                        self.INVALID_TEXT
                    )).mean()
                )

            completeness_scores.append(valid_ratio)

        completeness = (
            sum(completeness_scores)
            / max(len(completeness_scores), 1)
        )

        mapping_score = (
            mapped_count
            / max(source_column_count, 1)
        )

        quality_score = (
            required_present * 45
            + completeness * 55
        )

        health_score = (
            quality_score * 0.70
            + mapping_score * 100 * 0.30
        )

        return {
            "quality_score": round(
                quality_score,
                1,
            ),
            "mapping_score": round(
                mapping_score * 100,
                1,
            ),
            "health_score": round(
                health_score,
                1,
            ),
        }
