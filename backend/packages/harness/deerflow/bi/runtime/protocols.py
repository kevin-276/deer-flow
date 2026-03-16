"""Agent I/O protocols for DeerFlow-BI runtime orchestration."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PlannerInput:
    question: str


@dataclass(slots=True)
class PlannerOutput:
    analysis_plan: dict[str, Any]


@dataclass(slots=True)
class SchemaRetrievalInput:
    analysis_plan: dict[str, Any]


@dataclass(slots=True)
class SchemaRetrievalOutput:
    retrieved_schema: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class SQLGeneratorInput:
    analysis_plan: dict[str, Any]
    retrieved_schema: list[dict[str, Any]]


@dataclass(slots=True)
class SQLGeneratorOutput:
    candidate_sql: list[str] = field(default_factory=list)
    dialect: str = "sqlite"
    generation_note: str = ""


@dataclass(slots=True)
class ExecutorRepairInput:
    candidate_sql: list[str]


@dataclass(slots=True)
class ExecutorRepairOutput:
    final_sql: str | None = None
    execution_logs: list[dict[str, Any]] = field(default_factory=list)
    final_result: dict[str, Any] | None = None


@dataclass(slots=True)
class CriticInput:
    analysis_plan: dict[str, Any]
    final_sql: str | None
    final_result: dict[str, Any] | None


@dataclass(slots=True)
class CriticOutput:
    critic_feedback: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReporterInput:
    question: str
    final_sql: str | None
    final_result: dict[str, Any] | None
    critic_feedback: list[str]


@dataclass(slots=True)
class ReporterOutput:
    report_artifacts: list[str] = field(default_factory=list)
