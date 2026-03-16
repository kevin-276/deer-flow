"""Execution-guided repair agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, RepairResult, SQLDraft


class ExecutionRepairAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.EXECUTION_REPAIR)

    def run(self, plan: BIPlan, draft: SQLDraft) -> RepairResult:
        _ = plan
        return RepairResult(sql=draft.sql, rounds_used=0)
