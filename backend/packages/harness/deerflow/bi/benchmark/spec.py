"""Benchmark contracts for DeerFlow-BI."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class BenchmarkCase:
    """Single benchmark sample."""

    case_id: str
    question: str
    reference_sql: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
