"""MVP orchestration for DeerFlow-BI multi-agent runtime."""

from dataclasses import dataclass, field

from deerflow.bi.agents import (
    CriticAgent,
    ExecutorRepairAgent,
    PlannerAgent,
    ReporterAgent,
    SchemaRetrievalAgent,
    SQLGeneratorAgent,
)
from deerflow.bi.runtime.state import BIExecutionLog, BIState


@dataclass(slots=True)
class BIOrchestrator:
    """Sequential orchestrator for the MVP stage.

    This remains intentionally simple and is expected to evolve into a
    configurable graph-driven orchestration in V2/V3.
    """

    planner: PlannerAgent = field(default_factory=PlannerAgent)
    schema_retrieval: SchemaRetrievalAgent = field(default_factory=SchemaRetrievalAgent)
    sql_generator: SQLGeneratorAgent = field(default_factory=SQLGeneratorAgent)
    executor_repair: ExecutorRepairAgent = field(default_factory=ExecutorRepairAgent)
    critic: CriticAgent = field(default_factory=CriticAgent)
    reporter: ReporterAgent = field(default_factory=ReporterAgent)

    def run(self, question: str) -> BIState:
        state = BIState(user_question=question)

        state.analysis_plan = self.planner.run(state)
        state.retrieved_schema = self.schema_retrieval.run(state)
        state.candidate_sql = self.sql_generator.run(state)

        executor_result = self.executor_repair.run(state)
        state.final_sql = executor_result.get("final_sql")
        state.final_result = executor_result.get("final_result")
        state.execution_logs.extend(BIExecutionLog(stage="executor_repair", status="ok", message="executor placeholder completed", metadata=executor_result) for _ in [0])

        state.critic_feedback = self.critic.run(state)
        state.report_artifacts = self.reporter.run(state)
        return state
