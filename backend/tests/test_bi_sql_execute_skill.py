from pathlib import Path

from deerflow.bi.agents import ExecutorRepairAgent
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


def test_executor_repair_agent_closes_loop_with_repair_rounds(tmp_path: Path) -> None:
    db_path = tmp_path / "repair_loop.db"
    execute_sql("CREATE TABLE events (user_id INTEGER)", database_path=str(db_path))
    execute_sql("INSERT INTO events (user_id) VALUES (1)", database_path=str(db_path))

    state = BIState(user_question="test")
    state.candidate_sql = ["SELEC user_id FROM events"]
    state.runtime_metadata["sqlite_db_path"] = str(db_path)

    output = ExecutorRepairAgent().run(state)

    assert output["repair_rounds"] >= 1
    assert state.final_result is not None
    assert state.final_result["success"] is True
    assert state.final_result["repair_rounds"] >= 1
    assert state.execution_logs
    assert len(state.execution_logs) >= 2


def test_executor_repair_agent_table_name_repair_uses_schema_context(tmp_path: Path) -> None:
    db_path = tmp_path / "table_fix.db"
    execute_sql("CREATE TABLE user_events (user_id INTEGER)", database_path=str(db_path))
    execute_sql("INSERT INTO user_events (user_id) VALUES (7)", database_path=str(db_path))

    state = BIState(user_question="test")
    state.candidate_sql = ["SELECT user_id FROM events"]
    state.retrieved_schema = [{"table": "user_events", "columns": ["user_id"]}]
    state.runtime_metadata["sqlite_db_path"] = str(db_path)

    output = ExecutorRepairAgent().run(state)

    assert output["repair_rounds"] >= 1
    assert state.final_result is not None
    assert state.final_result["success"] is True
    assert state.final_sql == "SELECT user_id FROM user_events"
