"""Schema retrieval agent placeholder.

Responsibility:
- Perform schema linking / large-schema retrieval for the planned objective.
"""

from deerflow.bi.runtime.state import BIState


class SchemaRetrievalAgent:
    """MVP schema retrieval implementation placeholder."""

    def run(self, state: BIState) -> list[dict]:
        _ = state.analysis_plan
        return [{"table": "TODO_table", "columns": ["TODO_column"], "score": 0.1}]
