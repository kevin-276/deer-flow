"""Business semantic critic placeholder.

Responsibility:
- Validate whether SQL/result semantically answers the business question.
"""

from deerflow.bi.runtime.state import BIState


class CriticAgent:
    """MVP critic implementation placeholder."""

    def run(self, state: BIState) -> list[str]:
        _ = state.analysis_plan, state.final_sql, state.final_result
        return ["TODO: semantic validation rules are not implemented yet"]
