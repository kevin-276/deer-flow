"""Reporter agent placeholder.

Responsibility:
- Generate BI artifacts (markdown/chart/result package) for end users.
"""

from deerflow.bi.runtime.state import BIState


class ReporterAgent:
    """MVP reporter implementation placeholder."""

    def run(self, state: BIState) -> list[str]:
        _ = state.final_result, state.critic_feedback
        return ["analysis.md", "result.json"]
