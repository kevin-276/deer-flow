"""Schema retrieval agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, SchemaCandidate


class SchemaRetrievalAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.SCHEMA_RETRIEVAL)

    def run(self, plan: BIPlan) -> list[SchemaCandidate]:
        return [SchemaCandidate(table="TODO_table", columns=["TODO_column"], score=0.1)]
