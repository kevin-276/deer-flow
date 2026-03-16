"""SQL Generator agent for DeerFlow-BI MVP.

Responsibility:
- Generate one or more SQL candidates from user question, analysis plan,
  and (optionally) schema retrieval context.
"""

from dataclasses import dataclass, field
from typing import Any

from deerflow.bi.runtime.state import BIState


@dataclass(slots=True)
class SQLGenerationOutput:
    """Structured SQL generation output for runtime handoff."""

    candidate_sql: list[str] = field(default_factory=list)
    dialect: str = "sqlite"
    generation_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_sql": self.candidate_sql,
            "dialect": self.dialect,
            "generation_note": self.generation_note,
        }


class SQLGeneratorAgent:
    """MVP SQL generator with deterministic templates."""

    def run(self, state: BIState) -> dict[str, Any]:
        plan = state.analysis_plan or {}
        schema_context = state.retrieved_schema or []

        target_metric = plan.get("target_metric", "unknown_metric")
        dimensions = plan.get("dimensions", [])
        time_range = plan.get("time_range", "unspecified")

        if schema_context:
            table_name = schema_context[0].get("table", "events")
            columns = schema_context[0].get("columns", [])
            metric_column = self._infer_metric_column(target_metric, columns)
            dimension_column = self._infer_dimension_column(dimensions, columns)
            candidates = self._build_schema_aware_candidates(table_name, metric_column, dimension_column)
            note = "Schema-aware template generated from retrieved schema context."
        else:
            candidates = self._build_fallback_candidates(target_metric, dimensions)
            note = "Schema context unavailable; fallback SQL templates generated."

        note += f" Time range signal: {time_range}."

        output = SQLGenerationOutput(candidate_sql=candidates, dialect="sqlite", generation_note=note)

        state.candidate_sql = output.candidate_sql
        state.runtime_metadata["sql_generation"] = {
            "dialect": output.dialect,
            "generation_note": output.generation_note,
            "candidate_count": len(output.candidate_sql),
            "input_question": state.user_question,
        }

        return output.to_dict()

    def _build_schema_aware_candidates(self, table_name: str, metric_column: str, dimension_column: str | None) -> list[str]:
        base_metric = f"COUNT({metric_column})" if metric_column != "*" else "COUNT(*)"

        if dimension_column:
            return [
                f"SELECT {dimension_column}, {base_metric} AS metric_value FROM {table_name} GROUP BY {dimension_column};",
                f"SELECT {dimension_column}, {base_metric} AS metric_value FROM {table_name} GROUP BY {dimension_column} ORDER BY metric_value DESC;",
            ]

        return [
            f"SELECT {base_metric} AS metric_value FROM {table_name};",
            f"SELECT {base_metric} AS metric_value FROM {table_name} LIMIT 1;",
        ]

    def _build_fallback_candidates(self, target_metric: str, dimensions: list[str]) -> list[str]:
        metric_alias = target_metric if target_metric != "unknown_metric" else "metric_value"

        if dimensions:
            return [
                "SELECT 'unknown_dimension' AS dimension, COUNT(*) AS " + metric_alias + " FROM events GROUP BY 1;",
                "SELECT 'unknown_dimension' AS dimension, COUNT(*) AS " + metric_alias + " FROM events;",
            ]

        return [
            "SELECT COUNT(*) AS " + metric_alias + " FROM events;",
            "SELECT 1 AS placeholder_metric;",
        ]

    def _infer_metric_column(self, target_metric: str, columns: list[str]) -> str:
        lowered = target_metric.lower()
        for column in columns:
            col = column.lower()
            if "user" in lowered and "user" in col:
                return column
            if "order" in lowered and "order" in col:
                return column
            if "revenue" in lowered and ("amount" in col or "revenue" in col):
                return column
        return "*"

    def _infer_dimension_column(self, dimensions: list[str], columns: list[str]) -> str | None:
        if not dimensions:
            return None
        for dim in dimensions:
            dim_lower = dim.lower()
            for column in columns:
                if dim_lower in column.lower():
                    return column
        return columns[0] if columns else None
