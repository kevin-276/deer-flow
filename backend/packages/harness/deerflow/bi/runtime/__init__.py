"""Runtime module for DeerFlow-BI."""

from deerflow.bi.runtime.orchestration import BIOrchestrator
from deerflow.bi.runtime.state import BIExecutionLog, BIState


def run_mvp_demo(question: str, sqlite_db_path: str | None = None, artifacts_root_dir: str = "artifacts/deerflow_bi_runs") -> BIState:
    """Lazy-export demo helper to avoid importing CLI module at package import time."""
    from deerflow.bi.runtime.demo import run_mvp_demo as _run_mvp_demo

    return _run_mvp_demo(question=question, sqlite_db_path=sqlite_db_path, artifacts_root_dir=artifacts_root_dir)


__all__ = ["BIState", "BIExecutionLog", "BIOrchestrator", "run_mvp_demo"]
