"""SQL generator agent placeholder.

Responsibility:
- Build candidate SQL from analysis plan and retrieved schema context.
"""

from deerflow.bi.runtime.state import BIState


class SQLGeneratorAgent:
    """MVP SQL generator implementation placeholder."""

    def run(self, state: BIState) -> list[str]:
        _ = state.analysis_plan, state.retrieved_schema
        return ["SELECT 1 AS placeholder_metric"]
