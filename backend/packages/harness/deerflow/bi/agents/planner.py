"""Planner agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, BIUserQuery


class PlannerAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.PLANNER)

    def run(self, query: BIUserQuery) -> BIPlan:
        return BIPlan(objective=query.text, ambiguities=["TODO: resolve business ambiguity"])
