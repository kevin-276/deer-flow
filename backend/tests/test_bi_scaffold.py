from deerflow.bi import BIOrchestrator, BIState, DeerFlowBIPipeline
from deerflow.bi.agents import (
    CriticAgent,
    ExecutorRepairAgent,
    PlannerAgent,
    ReporterAgent,
    SchemaRetrievalAgent,
    SQLGeneratorAgent,
)


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
    assert result.critic_feedback
    assert result.report_artifacts


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
