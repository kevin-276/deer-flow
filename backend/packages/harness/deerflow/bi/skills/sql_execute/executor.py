"""SQLite SQL execution skill for DeerFlow-BI MVP.

This module intentionally starts with SQLite to ensure local reliability.
The interface is designed to be dialect-extensible in future iterations.
"""

import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SQLExecutionResult:
    """Structured SQL execution result contract."""

    success: bool
    rows: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable dictionary representation."""
        return asdict(self)


def execute_sql(sql: str, database_path: str = ":memory:", params: tuple[Any, ...] | None = None, timeout_seconds: float = 5.0) -> SQLExecutionResult:
    """Execute SQL against SQLite and return structured result.

    Args:
        sql: SQL statement to execute.
        database_path: SQLite file path or ':memory:'.
        params: Optional query params for parameterized SQL.
        timeout_seconds: SQLite connection timeout.
    """
    started = time.perf_counter()
    params = params or ()

    db_path_str = str(Path(database_path)) if database_path != ":memory:" else database_path

    try:
        with sqlite3.connect(db_path_str, timeout=timeout_seconds) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            statement = sql.strip()
            query_type = statement.split(None, 1)[0].upper() if statement else "UNKNOWN"

            cursor.execute(statement, params)

            if query_type in {"SELECT", "WITH", "PRAGMA"}:
                fetched_rows = cursor.fetchall()
                rows = [dict(row) for row in fetched_rows]
            else:
                conn.commit()
                rows = []

            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            return SQLExecutionResult(
                success=True,
                rows=rows,
                metadata={
                    "dialect": "sqlite",
                    "database_path": db_path_str,
                    "query_type": query_type,
                    "row_count": len(rows),
                    "elapsed_ms": elapsed_ms,
                },
            )
    except sqlite3.Error as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        return SQLExecutionResult(
            success=False,
            rows=[],
            error_message=str(exc),
            metadata={
                "dialect": "sqlite",
                "database_path": db_path_str,
                "elapsed_ms": elapsed_ms,
                "error_type": exc.__class__.__name__,
            },
        )
