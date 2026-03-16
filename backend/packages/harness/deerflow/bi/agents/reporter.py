"""Reporter agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, BIReport, Critique, RepairResult


class ReporterAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.REPORTER)

    def run(self, plan: BIPlan, repaired: RepairResult, critique: Critique) -> BIReport:
        _ = plan, repaired
        return BIReport(summary="MVP scaffold result generated.", caveats=critique.risks)
