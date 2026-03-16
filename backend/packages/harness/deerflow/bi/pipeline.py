"""Compatibility pipeline wrapper for DeerFlow-BI.

Prefer `deerflow.bi.runtime.BIOrchestrator` for new development.
"""

from dataclasses import dataclass, field

from deerflow.bi.runtime.orchestration import BIOrchestrator
from deerflow.bi.runtime.state import BIState


@dataclass(slots=True)
class DeerFlowBIPipeline:
    """Backward-compatible entrypoint over BI orchestrator."""

    orchestrator: BIOrchestrator = field(default_factory=BIOrchestrator)

    def run(self, query: str) -> BIState:
        return self.orchestrator.run(query)
