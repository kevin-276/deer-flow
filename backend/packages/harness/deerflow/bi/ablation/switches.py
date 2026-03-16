"""Ablation switches for controlled experiments."""

from dataclasses import dataclass


@dataclass(slots=True)
class AblationSwitches:
    """Feature switches used in benchmark/ablation runs."""

    enable_planner: bool = True
    enable_schema_retrieval: bool = True
    enable_execution_repair: bool = True
    enable_critic: bool = True
    enable_memory_context: bool = True
    schema_top_k: int = 8
