"""BI-specific skill adapters.

This package hosts BI domain skills that complement DeerFlow global skills.
"""

from deerflow.bi.skills.sql_execute import SQLExecutionResult, execute_sql, write_execution_result_to_state

__all__ = ["execute_sql", "SQLExecutionResult", "write_execution_result_to_state"]
