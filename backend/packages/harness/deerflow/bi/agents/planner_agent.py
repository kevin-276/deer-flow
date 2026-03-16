"""Planner agent placeholder.

Responsibility:
- Convert natural language question into a structured analysis plan.
"""

from deerflow.bi.runtime.state import BIState


class PlannerAgent:
    """MVP planner implementation placeholder."""

    def run(self, state: BIState) -> dict:
        return {
            "objective": state.user_question,
            "dimensions": [],
            "metrics": [],
            "filters": [],
            "ambiguities": ["TODO: clarify business semantics"],
        }
