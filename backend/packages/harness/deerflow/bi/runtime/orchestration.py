"""MVP orchestration for DeerFlow-BI multi-agent runtime.

Current MVP chain:
Planner -> Schema Retrieval -> SQL Generator -> Executor/Repair.
"""

from dataclasses import dataclass, field

from deerflow.bi.agents import ExecutorRepairAgent, PlannerAgent, SchemaRetrievalAgent, SQLGeneratorAgent
from deerflow.bi.artifacts import export_run_artifacts
from deerflow.bi.runtime.state import BIState


@dataclass(slots=True)
class BIOrchestrator:
    """Minimal sequential orchestrator for DeerFlow-BI MVP."""

    planner: PlannerAgent = field(default_factory=PlannerAgent)
    schema_retrieval: SchemaRetrievalAgent = field(default_factory=SchemaRetrievalAgent)
    sql_generator: SQLGeneratorAgent = field(default_factory=SQLGeneratorAgent)
    executor_repair: ExecutorRepairAgent = field(default_factory=ExecutorRepairAgent)

    def run(self, question: str, artifacts_root_dir: str | None = None, sqlite_db_path: str | None = None) -> BIState:
        """Run Planner -> Schema Retrieval -> SQL Generator -> Executor/Repair and return final state."""
        state = BIState(user_question=question)
        if sqlite_db_path:
            state.runtime_metadata["sqlite_db_path"] = sqlite_db_path

        self.planner.run(state)
        self.schema_retrieval.run(state)
        self.sql_generator.run(state)
        self.executor_repair.run(state)

        if artifacts_root_dir:
            export_run_artifacts(state=state, artifacts_root_dir=artifacts_root_dir)

        return state
