from pathlib import Path

from deerflow.bi import BIOrchestrator, BIState, DeerFlowBIPipeline
from deerflow.bi.agents import (
    CriticAgent,
    ExecutorRepairAgent,
    PlannerAgent,
    ReporterAgent,
    SchemaRetrievalAgent,
    SQLGeneratorAgent,
)
from deerflow.bi.runtime import run_mvp_demo


def test_bi_modules_are_importable() -> None:
    assert PlannerAgent
    assert SchemaRetrievalAgent
    assert SQLGeneratorAgent
    assert ExecutorRepairAgent
    assert CriticAgent
    assert ReporterAgent


def test_runtime_state_has_required_fields() -> None:
    state = BIState(user_question="最近 30 天新增用户")

    assert state.user_question
    assert state.analysis_plan is None
    assert state.retrieved_schema == []
    assert state.candidate_sql == []
    assert state.final_sql is None
    assert state.execution_logs == []
    assert state.final_result is None
    assert state.critic_feedback == []
    assert state.report_artifacts == []


def test_orchestrator_runs_mvp_placeholder_flow() -> None:
    result = BIOrchestrator().run("统计最近 30 天新增用户数")
    assert result.analysis_plan is not None
    assert result.retrieved_schema
    assert result.candidate_sql
    assert result.final_sql
    assert result.final_result is not None
    assert result.execution_logs


def test_pipeline_keeps_backward_compatibility() -> None:
    output = DeerFlowBIPipeline().run("Q")
    assert isinstance(output, BIState)


def test_planner_generates_structured_plan_minimal_example() -> None:
    state = BIState(user_question="统计最近30天按渠道的新增用户数")

    plan = PlannerAgent().run(state)

    assert state.analysis_plan == plan
    assert set(plan).issuperset(
        {
            "task_type",
            "target_metric",
            "dimensions",
            "filters",
            "time_range",
            "assumptions",
            "next_action",
        }
    )
    assert plan["target_metric"] == "新增用户数"
    assert plan["time_range"] == "最近30天"
    assert plan["next_action"] == "schema_retrieval"


def test_sql_generator_outputs_structured_candidates() -> None:
    state = BIState(user_question="统计最近30天按渠道的新增用户数")
    PlannerAgent().run(state)
    state.retrieved_schema = [{"table": "user_events", "columns": ["channel", "user_id"]}]

    output = SQLGeneratorAgent().run(state)

    assert state.candidate_sql
    assert isinstance(output, dict)
    assert output["candidate_sql"] == state.candidate_sql
    assert output["dialect"] == "sqlite"
    assert output["generation_note"]
    assert "sql_generation" in state.runtime_metadata
    assert state.runtime_metadata["sql_generation"]["dialect"] == "sqlite"


def test_run_mvp_demo_returns_state_with_plan_sql_result(tmp_path) -> None:
    result = run_mvp_demo("统计最近 30 天新增用户数", artifacts_root_dir=str(tmp_path))
    assert result.analysis_plan is not None
    assert result.retrieved_schema
    assert result.candidate_sql
    assert result.final_sql
    assert result.final_result is not None


def test_mvp_demo_generates_run_specific_artifacts(tmp_path) -> None:
    run1 = run_mvp_demo("统计最近30天新增用户数", artifacts_root_dir=str(tmp_path))
    run2 = run_mvp_demo("统计最近30天新增用户数", artifacts_root_dir=str(tmp_path))

    dir1 = run1.runtime_metadata.get("artifact_run_dir")
    dir2 = run2.runtime_metadata.get("artifact_run_dir")

    assert dir1 and dir2
    assert dir1 != dir2

    required = ["plan.json", "candidate_sql.sql", "execution_log.json"]
    for filename in required:
        assert Path(dir1, filename).exists()

    assert Path(dir1, "final_result.json").exists() or Path(dir1, "final_result.csv").exists()

    assert Path(dir1, "plan.json").read_text(encoding="utf-8")
    assert Path(dir1, "candidate_sql.sql").read_text(encoding="utf-8")


def test_schema_retrieval_outputs_structured_context() -> None:
    state = BIState(user_question="统计最近30天按渠道的新增用户数")
    PlannerAgent().run(state)

    output = SchemaRetrievalAgent().run(state)

    assert isinstance(output, dict)
    assert set(output).issuperset({"retrieved_tables", "retrieved_columns", "schema_summary", "retrieval_metadata"})
    assert output["retrieved_tables"]
    assert output["retrieved_columns"]
    assert output["schema_summary"]
    assert "schema_retrieval" in state.runtime_metadata
    assert state.retrieved_schema
