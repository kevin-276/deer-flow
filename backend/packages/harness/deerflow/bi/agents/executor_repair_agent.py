"""Executor/repair agent MVP with SQL execution and basic repair loop.

Responsibility:
- Execute candidate SQL.
- Attempt 1~2 repair rounds when execution fails.
- Persist final SQL/result/logs metadata into runtime state.
"""

import re
from dataclasses import dataclass

from deerflow.bi.runtime.state import BIState
from deerflow.bi.skills.sql_execute import execute_sql, write_execution_result_to_state


@dataclass(slots=True)
class RepairConfig:
    """Repair loop configuration."""

    max_rounds: int = 2


class ExecutorRepairAgent:
    """MVP executor/repair with a deterministic, extensible repair strategy."""

    def __init__(self, config: RepairConfig | None = None) -> None:
        self.config = config or RepairConfig()

    def run(self, state: BIState) -> dict:
        database_path = state.runtime_metadata.get("sqlite_db_path", ":memory:")
        repair_rounds = 0
        attempted_sqls: list[str] = []

        current_sql = state.candidate_sql[0] if state.candidate_sql else "SELECT 1 AS placeholder_metric"
        result = execute_sql(sql=current_sql, database_path=database_path)
        attempted_sqls.append(current_sql)
        write_execution_result_to_state(state=state, sql=current_sql, result=result)

        while not result.success and repair_rounds < self.config.max_rounds:
            repaired_sql = self._repair_sql(current_sql, result.error_message or "", state)
            if not repaired_sql or repaired_sql == current_sql:
                break

            repair_rounds += 1
            current_sql = repaired_sql
            result = execute_sql(sql=current_sql, database_path=database_path)
            attempted_sqls.append(current_sql)
            write_execution_result_to_state(state=state, sql=current_sql, result=result)

        # enrich final_result with loop metadata for downstream analysis
        if state.final_result is None:
            state.final_result = {}

        state.final_result["repair_rounds"] = repair_rounds
        state.final_result["attempted_sqls"] = attempted_sqls

        state.runtime_metadata["executor_repair"] = {
            "repair_rounds": repair_rounds,
            "attempt_count": len(attempted_sqls),
            "success": bool(state.final_result.get("success")),
            "max_rounds": self.config.max_rounds,
        }

        return {
            "final_sql": state.final_sql,
            "execution_logs": [log.metadata for log in state.execution_logs],
            "repair_rounds": repair_rounds,
            "final_result": state.final_result,
        }

    def _repair_sql(self, sql: str, error_message: str, state: BIState) -> str:
        """Basic repair strategy based on SQLite error text.

        Extend this method in future to plug rule-based + model-based repair.
        """
        repaired = sql
        lowered_error = error_message.lower()

        # common typo: SELEC -> SELECT
        if "syntax error" in lowered_error and re.search(r"\bselec\b", repaired, flags=re.IGNORECASE):
            repaired = re.sub(r"\bselec\b", "SELECT", repaired, flags=re.IGNORECASE)

        # remove trailing comma before FROM (e.g., SELECT a, FROM t)
        if "syntax error" in lowered_error:
            repaired = re.sub(r",\s*FROM", " FROM", repaired, flags=re.IGNORECASE)

        # no such table -> use first retrieved schema table if available
        table_match = re.search(r"no such table:\s*([\w_]+)", lowered_error)
        if table_match and state.retrieved_schema:
            bad_table = table_match.group(1)
            fallback_table = state.retrieved_schema[0].get("table")
            if fallback_table:
                repaired = re.sub(rf"\b{re.escape(bad_table)}\b", str(fallback_table), repaired)

        return repaired
