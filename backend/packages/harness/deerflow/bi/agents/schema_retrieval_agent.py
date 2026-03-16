"""Schema Retrieval agent for DeerFlow-BI MVP.

Responsibilities:
- table-level retrieval
- column-level retrieval
- build compact schema context for downstream SQL generation
"""

from dataclasses import dataclass, field
from typing import Any

from deerflow.bi.runtime.state import BIState


@dataclass(slots=True)
class SchemaRetrievalOutput:
    """Structured schema retrieval output."""

    retrieved_tables: list[str] = field(default_factory=list)
    retrieved_columns: list[str] = field(default_factory=list)
    schema_summary: str = ""
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "retrieved_tables": self.retrieved_tables,
            "retrieved_columns": self.retrieved_columns,
            "schema_summary": self.schema_summary,
            "retrieval_metadata": self.retrieval_metadata,
        }


class SchemaRetrievalAgent:
    """MVP schema retrieval with lightweight lexical matching."""

    def run(self, state: BIState) -> dict[str, Any]:
        plan = state.analysis_plan or {}
        question = state.user_question
        target_metric = str(plan.get("target_metric", ""))
        dimensions = [str(d) for d in plan.get("dimensions", [])]
        query_text = f"{question} {target_metric} {' '.join(dimensions)}".lower()

        catalog = self._get_schema_catalog(state)
        scored_tables = []
        for item in catalog:
            table = item.get("table", "")
            columns = item.get("columns", [])
            score = self._score_item(query_text=query_text, table=table, columns=columns)
            scored_tables.append({"table": table, "columns": columns, "score": score})

        scored_tables.sort(key=lambda x: x["score"], reverse=True)
        top_k = int(state.runtime_metadata.get("schema_top_k", 3))
        selected = [s for s in scored_tables[:top_k] if s["score"] > 0]
        if not selected:
            selected = scored_tables[:1]

        # compact context for SQL generator
        state.retrieved_schema = [{"table": s["table"], "columns": s["columns"], "score": s["score"]} for s in selected]

        retrieved_tables = [s["table"] for s in selected]
        retrieved_columns = list(dict.fromkeys(col for s in selected for col in s["columns"]))
        summary = self._build_summary(selected)

        output = SchemaRetrievalOutput(
            retrieved_tables=retrieved_tables,
            retrieved_columns=retrieved_columns,
            schema_summary=summary,
            retrieval_metadata={
                "strategy": "lexical_overlap_mvp",
                "catalog_size": len(catalog),
                "selected_count": len(selected),
                "top_k": top_k,
            },
        )
        state.runtime_metadata["schema_retrieval"] = output.to_dict()
        return output.to_dict()

    def _get_schema_catalog(self, state: BIState) -> list[dict[str, Any]]:
        custom_catalog = state.runtime_metadata.get("schema_catalog")
        if isinstance(custom_catalog, list) and custom_catalog:
            return custom_catalog

        return [
            {"table": "events", "columns": ["event_time", "user_id", "channel", "event_name"]},
            {"table": "orders", "columns": ["order_id", "user_id", "amount", "created_at", "channel"]},
            {"table": "users", "columns": ["user_id", "signup_time", "region", "device"]},
        ]

    def _score_item(self, query_text: str, table: str, columns: list[str]) -> int:
        score = 0
        table_tokens = table.lower().split("_")
        for token in table_tokens:
            if token and token in query_text:
                score += 2

        for col in columns:
            for token in col.lower().split("_"):
                if token and token in query_text:
                    score += 1

        return score

    def _build_summary(self, selected: list[dict[str, Any]]) -> str:
        if not selected:
            return "No schema matched."

        parts = []
        for item in selected:
            table = item["table"]
            columns = ", ".join(item["columns"][:5])
            parts.append(f"{table}({columns})")
        return " | ".join(parts)
