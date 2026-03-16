"""MVP orchestration for DeerFlow-BI multi-agent runtime.

ISSUE-008 scope: keep a minimal runnable chain:
Planner -> SQL Generator -> Executor/Repair.
"""

from dataclasses import dataclass, field

from deerflow.bi.agents import ExecutorRepairAgent, PlannerAgent, SQLGeneratorAgent
from deerflow.bi.runtime.state import BIState


@dataclass(slots=True)
class BIOrchestrator:
    """Minimal sequential orchestrator for DeerFlow-BI MVP."""

    planner: PlannerAgent = field(default_factory=PlannerAgent)
    sql_generator: SQLGeneratorAgent = field(default_factory=SQLGeneratorAgent)
    executor_repair: ExecutorRepairAgent = field(default_factory=ExecutorRepairAgent)

    def run(self, question: str) -> BIState:
        """Run Planner -> SQL Generator -> Executor/Repair and return final state."""
        state = BIState(user_question=question)

        self.planner.run(state)
        self.sql_generator.run(state)
        self.executor_repair.run(state)

        return state
