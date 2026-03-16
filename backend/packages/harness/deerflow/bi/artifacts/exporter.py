"""Artifact export helpers for DeerFlow-BI MVP runs."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from deerflow.bi.runtime.state import BIState


def export_run_artifacts(state: BIState, artifacts_root_dir: str) -> str:
    """Export run artifacts into a unique run-specific directory.

    Required files:
    - plan.json
    - candidate_sql.sql
    - execution_log.json
    - final_result.json or final_result.csv
    """
    root = Path(artifacts_root_dir)
    run_id = _new_run_id()
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    _write_plan(run_dir, state)
    _write_candidate_sql(run_dir, state)
    _write_execution_logs(run_dir, state)
    _write_final_result(run_dir, state)

    state.runtime_metadata["artifact_run_dir"] = str(run_dir)
    state.report_artifacts = [
        str(run_dir / "plan.json"),
        str(run_dir / "candidate_sql.sql"),
        str(run_dir / "execution_log.json"),
        str(run_dir / "final_result.json") if (run_dir / "final_result.json").exists() else str(run_dir / "final_result.csv"),
    ]

    return str(run_dir)


def _new_run_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"run_{timestamp}_{uuid4().hex[:8]}"


def _write_plan(run_dir: Path, state: BIState) -> None:
    plan = state.analysis_plan or {}
    (run_dir / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_candidate_sql(run_dir: Path, state: BIState) -> None:
    candidates = state.candidate_sql or []
    sql_text = "\n\n-- candidate separator --\n\n".join(candidates) if candidates else "-- no candidate sql --"
    (run_dir / "candidate_sql.sql").write_text(sql_text + "\n", encoding="utf-8")


def _write_execution_logs(run_dir: Path, state: BIState) -> None:
    logs = [log.metadata for log in state.execution_logs]
    (run_dir / "execution_log.json").write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_final_result(run_dir: Path, state: BIState) -> None:
    final_result = state.final_result or {}

    rows = final_result.get("rows") if isinstance(final_result, dict) else None
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        fieldnames = sorted({key for row in rows for key in row.keys()})
        with (run_dir / "final_result.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return

    (run_dir / "final_result.json").write_text(json.dumps(final_result, ensure_ascii=False, indent=2), encoding="utf-8")
