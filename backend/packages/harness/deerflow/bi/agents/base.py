"""Base protocol utilities for DeerFlow-BI agents."""

from dataclasses import dataclass

from deerflow.bi.contracts import BIAgentRole


@dataclass(slots=True)
class BIAgentBase:
    """Common base class for BI agents."""

    role: BIAgentRole
