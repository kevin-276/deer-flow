"""Helpers to write SQL execution results back into BI runtime state."""

from deerflow.bi.runtime.state import BIExecutionLog, BIState
from deerflow.bi.skills.sql_execute.executor import SQLExecutionResult


def write_execution_result_to_state(state: BIState, sql: str, result: SQLExecutionResult) -> None:
    """Persist SQL execution outputs into BIState."""
    state.final_sql = sql
    state.final_result = {
        "success": result.success,
        "rows": result.rows,
        "error_message": result.error_message,
        "metadata": result.metadata,
    }
    state.execution_logs.append(
        BIExecutionLog(
            stage="sql_execute",
            status="success" if result.success else "failure",
            message="SQL executed" if result.success else "SQL execution failed",
            metadata={"sql": sql, **result.metadata},
        )
    )
