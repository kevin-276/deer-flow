from pathlib import Path

from deerflow.bi.runtime.state import BIState
from deerflow.bi.skills.sql_execute import execute_sql, write_execution_result_to_state


def test_sql_execute_skill_success_with_sqlite_file(tmp_path: Path) -> None:
    db_path = tmp_path / "bi_test.db"

    create_result = execute_sql("CREATE TABLE users (id INTEGER, name TEXT)", database_path=str(db_path))
    assert create_result.success is True

    insert_result = execute_sql("INSERT INTO users (id, name) VALUES (1, 'alice')", database_path=str(db_path))
    assert insert_result.success is True

    select_result = execute_sql("SELECT id, name FROM users", database_path=str(db_path))
    assert select_result.success is True
    assert select_result.rows == [{"id": 1, "name": "alice"}]
    assert select_result.metadata["dialect"] == "sqlite"
    assert select_result.metadata["row_count"] == 1


def test_sql_execute_skill_returns_structured_error() -> None:
    result = execute_sql("SELECT * FROM table_not_exists", database_path=":memory:")

    assert result.success is False
    assert result.rows == []
    assert result.error_message
    assert result.metadata["dialect"] == "sqlite"
    assert result.metadata["error_type"]


def test_sql_execute_result_can_be_written_to_runtime_state(tmp_path: Path) -> None:
    db_path = tmp_path / "state_write.db"
    execute_sql("CREATE TABLE t (v INTEGER)", database_path=str(db_path))
    execute_sql("INSERT INTO t (v) VALUES (42)", database_path=str(db_path))

    state = BIState(user_question="示例问题")
    sql = "SELECT v FROM t"
    result = execute_sql(sql, database_path=str(db_path))
    write_execution_result_to_state(state, sql=sql, result=result)

    assert state.final_sql == sql
    assert state.final_result is not None
    assert state.final_result["success"] is True
    assert state.final_result["rows"] == [{"v": 42}]
    assert state.execution_logs
    assert state.execution_logs[-1].stage == "sql_execute"
