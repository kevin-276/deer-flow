"""Runtime state contract for DeerFlow-BI.

This module defines a compact, extensible state object shared by BI agents.
It intentionally uses dataclasses to stay lightweight for MVP iterations.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BIExecutionLog:
    """Execution trace record produced by runtime or repair steps."""

    stage: str
    status: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BIState:
    """Unified DeerFlow-BI runtime state.

    Required MVP fields are aligned with ISSUE-003 and kept generic enough
    for benchmark and ablation evolution.
    """

    user_question: str
    analysis_plan: dict[str, Any] | None = None
    retrieved_schema: list[dict[str, Any]] = field(default_factory=list)
    candidate_sql: list[str] = field(default_factory=list)
    final_sql: str | None = None
    execution_logs: list[BIExecutionLog] = field(default_factory=list)
    final_result: dict[str, Any] | None = None
    critic_feedback: list[str] = field(default_factory=list)
    report_artifacts: list[str] = field(default_factory=list)
    # Explicit extension points for experiments.
    ablation_flags: dict[str, bool] = field(default_factory=dict)
    runtime_metadata: dict[str, Any] = field(default_factory=dict)
