from __future__ import annotations

import pandas as pd

from models.root_cause import (
    RootCauseNode,
    RootCauseResult,
)


class RootCauseEngine:
    """
    Finds the dominant hierarchical explanation of a variance.

    The engine drills through the available business dimensions in
    order and follows the largest adverse contributor at each level.
    """

    DIMENSION_ORDER = (
        "mode",
        "product",
        "customer",
        "trade_lane",
    )

    METRICS = {
        "Revenue": (
            "actual_revenue",
            "estimated_revenue",
        ),
        "Gross Profit": (
            "actual_gp",
            "estimated_gp",
        ),
    }

    def analyze(
        self,
        dataframe: pd.DataFrame,
        *,
        metric: str = "Gross Profit",
        max_depth: int = 4,
        top_causes: int = 8,
    ) -> RootCauseResult:
        if metric not in self.METRICS:
            raise ValueError(
                f"Unsupported metric: {metric}"
            )

        actual_col, target_col = self.METRICS[
            metric
        ]

        required = {
            actual_col,
            target_col,
        }

        if not required.issubset(
            dataframe.columns
        ):
            missing = sorted(
                required
                - set(dataframe.columns)
            )
            raise ValueError(
                "Missing columns: "
                + ", ".join(missing)
            )

        df = dataframe.copy()

        for column in [
            actual_col,
            target_col,
        ]:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

        total_actual = float(
            df[actual_col].sum()
        )
        total_target = float(
            df[target_col].sum()
        )
        total_variance = (
            total_actual
            - total_target
        )

        available_dimensions = [
            dimension
            for dimension in self.DIMENSION_ORDER
            if dimension in df.columns
        ]

        top_nodes = self._top_nodes(
            df,
            actual_col=actual_col,
            target_col=target_col,
            dimensions=available_dimensions,
            total_variance=total_variance,
            limit=top_causes,
        )

        dominant_path: list[
            RootCauseNode
        ] = []

        subset = df.copy()

        for level, dimension in enumerate(
            available_dimensions[
                :max_depth
            ],
            start=1,
        ):
            grouped = self._group(
                subset,
                dimension=dimension,
                actual_col=actual_col,
                target_col=target_col,
                total_variance=total_variance,
            )

            if grouped.empty:
                break

            # If total variance is negative, follow the most negative
            # contributor. Otherwise, follow the largest absolute one.
            if total_variance < 0:
                selected = grouped.sort_values(
                    "Variance",
                    ascending=True,
                ).iloc[0]
            else:
                selected = grouped.sort_values(
                    "Abs Variance",
                    ascending=False,
                ).iloc[0]

            node = RootCauseNode(
                level=level,
                dimension=dimension,
                value=str(
                    selected[dimension]
                ),
                variance=float(
                    selected["Variance"]
                ),
                variance_pct=float(
                    selected[
                        "Variance %"
                    ]
                ),
                contribution_pct=float(
                    selected[
                        "Contribution %"
                    ]
                ),
                actual=float(
                    selected["Actual"]
                ),
                target=float(
                    selected["Target"]
                ),
            )
            dominant_path.append(node)

            subset = subset[
                subset[dimension]
                .fillna("Unassigned")
                .astype(str)
                .str.strip()
                .replace(
                    "",
                    "Unassigned",
                )
                == node.value
            ].copy()

            if subset.empty:
                break

        explained = sum(
            abs(node.variance)
            for node in top_nodes
        )
        denominator = abs(
            total_variance
        )

        explained_pct = (
            explained / denominator
            if denominator
            else 0.0
        )

        return RootCauseResult(
            metric=metric,
            total_variance=total_variance,
            total_actual=total_actual,
            total_target=total_target,
            dominant_path=dominant_path,
            top_causes=top_nodes,
            explained_variance_pct=min(
                explained_pct,
                1.0,
            ),
        )

    def _top_nodes(
        self,
        dataframe: pd.DataFrame,
        *,
        actual_col: str,
        target_col: str,
        dimensions: list[str],
        total_variance: float,
        limit: int,
    ) -> list[RootCauseNode]:
        nodes: list[
            RootCauseNode
        ] = []

        for dimension in dimensions:
            grouped = self._group(
                dataframe,
                dimension=dimension,
                actual_col=actual_col,
                target_col=target_col,
                total_variance=total_variance,
            )

            for _, row in grouped.iterrows():
                nodes.append(
                    RootCauseNode(
                        level=1,
                        dimension=dimension,
                        value=str(
                            row[
                                dimension
                            ]
                        ),
                        variance=float(
                            row[
                                "Variance"
                            ]
                        ),
                        variance_pct=float(
                            row[
                                "Variance %"
                            ]
                        ),
                        contribution_pct=float(
                            row[
                                "Contribution %"
                            ]
                        ),
                        actual=float(
                            row[
                                "Actual"
                            ]
                        ),
                        target=float(
                            row[
                                "Target"
                            ]
                        ),
                    )
                )

        if total_variance < 0:
            nodes = sorted(
                nodes,
                key=lambda item: (
                    item.variance,
                    -abs(
                        item.variance
                    ),
                ),
            )
        else:
            nodes = sorted(
                nodes,
                key=lambda item: abs(
                    item.variance
                ),
                reverse=True,
            )

        return nodes[:limit]

    @staticmethod
    def _group(
        dataframe: pd.DataFrame,
        *,
        dimension: str,
        actual_col: str,
        target_col: str,
        total_variance: float,
    ) -> pd.DataFrame:
        working = dataframe.copy()
        working[dimension] = (
            working[dimension]
            .fillna("Unassigned")
            .astype(str)
            .str.strip()
            .replace(
                "",
                "Unassigned",
            )
        )

        grouped = (
            working.groupby(
                dimension,
                dropna=False,
            )
            .agg(
                Actual=(
                    actual_col,
                    "sum",
                ),
                Target=(
                    target_col,
                    "sum",
                ),
            )
            .reset_index()
        )

        grouped["Variance"] = (
            grouped["Actual"]
            - grouped["Target"]
        )
        grouped["Variance %"] = grouped.apply(
            lambda row: (
                (
                    row["Actual"]
                    - row["Target"]
                )
                / abs(
                    row["Target"]
                )
                if row["Target"]
                else 0.0
            ),
            axis=1,
        )
        grouped["Abs Variance"] = (
            grouped["Variance"].abs()
        )
        grouped["Contribution %"] = (
            grouped["Abs Variance"]
            / abs(total_variance)
            if total_variance
            else 0.0
        )

        return grouped
