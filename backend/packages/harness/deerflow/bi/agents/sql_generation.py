"""SQL generation agent placeholder."""

from deerflow.bi.agents.base import BIAgentBase
from deerflow.bi.contracts import BIAgentRole, BIPlan, SchemaCandidate, SQLDraft


class SQLGenerationAgent(BIAgentBase):
    def __init__(self) -> None:
        super().__init__(role=BIAgentRole.SQL_GENERATION)

    def run(self, plan: BIPlan, schema_candidates: list[SchemaCandidate]) -> SQLDraft:
        _ = plan, schema_candidates
        return SQLDraft(sql="SELECT 1 AS placeholder_metric", rationale="TODO: implement SQL synthesis")
