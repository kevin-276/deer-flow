"""Critic agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, Critique, RepairResult


class CriticAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.CRITIC)

    def run(self, plan: BIPlan, repaired: RepairResult) -> Critique:
        _ = plan, repaired
        return Critique(passed=True, risks=["TODO: add semantic validation rules"])
