"""Contracts shared by DeerFlow-BI agents."""

from dataclasses import dataclass, field
from enum import StrEnum


class BIAgentRole(StrEnum):
    """Canonical roles in DeerFlow-BI."""

    PLANNER = "planner"
    SCHEMA_RETRIEVAL = "schema_retrieval"
    SQL_GENERATION = "sql_generation"
    EXECUTION_REPAIR = "execution_repair"
    CRITIC = "critic"
    REPORTER = "reporter"


@dataclass(slots=True)
class BIUserQuery:
    """Input query from user."""

    text: str


@dataclass(slots=True)
class BIPlan:
    """Structured planning output."""

    objective: str
    dimensions: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SchemaCandidate:
    """Schema retrieval candidate."""

    table: str
    columns: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass(slots=True)
class SQLDraft:
    """SQL generation output draft."""

    sql: str
    rationale: str = ""


@dataclass(slots=True)
class ExecutionFeedback:
    """Execution feedback placeholder.

    The MVP scaffold stores only minimal status metadata; concrete
    execution engine integration will enrich this contract.
    """

    success: bool
    error_message: str | None = None


@dataclass(slots=True)
class RepairResult:
    """Execution-guided repair output."""

    sql: str
    rounds_used: int = 0


@dataclass(slots=True)
class Critique:
    """Critic output."""

    passed: bool
    risks: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BIReport:
    """User-facing reporting output."""

    summary: str
    caveats: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BIPipelineResult:
    """Full DeerFlow-BI pipeline output."""

    plan: BIPlan
    schema_candidates: list[SchemaCandidate]
    sql: str
    critique: Critique
    report: BIReport
