"""Executor/repair agent placeholder.

Responsibility:
- Execute SQL candidate(s) and perform execution-guided repair loops.
"""

from deerflow.bi.runtime.state import BIState


class ExecutorRepairAgent:
    """MVP executor/repair implementation placeholder."""

    def run(self, state: BIState) -> dict:
        sql = state.candidate_sql[0] if state.candidate_sql else None
        return {
            "final_sql": sql,
            "final_result": {"rows": [], "note": "TODO: wire real SQL executor"},
            "execution_logs": [{"status": "placeholder", "sql": sql}],
        }
