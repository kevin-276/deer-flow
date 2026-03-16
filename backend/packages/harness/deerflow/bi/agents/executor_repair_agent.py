"""Executor/repair agent MVP with SQL execution skill integration.

Responsibility:
- Execute SQL candidate(s) and return structured execution output.
- Keep extension point for future execution-guided repair loops.
"""

from deerflow.bi.runtime.state import BIState
from deerflow.bi.skills.sql_execute import execute_sql, write_execution_result_to_state


class ExecutorRepairAgent:
    """MVP executor/repair implementation with SQLite execution."""

    def run(self, state: BIState) -> dict:
        sql = state.candidate_sql[0] if state.candidate_sql else "SELECT 1 AS placeholder_metric"
        database_path = state.runtime_metadata.get("sqlite_db_path", ":memory:")

        result = execute_sql(sql=sql, database_path=database_path)
        write_execution_result_to_state(state=state, sql=sql, result=result)

        return {
            "final_sql": state.final_sql,
            "final_result": state.final_result,
            "execution_logs": [log.metadata for log in state.execution_logs],
        }
