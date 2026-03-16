"""Agent entrypoints for DeerFlow-BI."""

from deerflow.bi.agents.critic_agent import CriticAgent
from deerflow.bi.agents.executor_repair_agent import ExecutorRepairAgent
from deerflow.bi.agents.planner_agent import PlannerAgent
from deerflow.bi.agents.reporter_agent import ReporterAgent
from deerflow.bi.agents.schema_retrieval_agent import SchemaRetrievalAgent
from deerflow.bi.agents.sql_generator_agent import SQLGeneratorAgent

# Backward-compatible aliases for previous placeholder naming.
ExecutionRepairAgent = ExecutorRepairAgent
SQLGenerationAgent = SQLGeneratorAgent

__all__ = [
    "PlannerAgent",
    "SchemaRetrievalAgent",
    "SQLGeneratorAgent",
    "ExecutorRepairAgent",
    "ExecutionRepairAgent",
    "CriticAgent",
    "ReporterAgent",
    "SQLGenerationAgent",
]
