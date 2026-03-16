"""CLI/demo entrypoint for DeerFlow-BI MVP orchestration."""

import argparse
import json

from deerflow.bi.runtime.orchestration import BIOrchestrator
from deerflow.bi.runtime.state import BIState


def run_mvp_demo(question: str, sqlite_db_path: str | None = None) -> BIState:
    """Execute the MVP chain and return BIState for programmatic usage."""
    orchestrator = BIOrchestrator()
    state = BIState(user_question=question)
    if sqlite_db_path:
        state.runtime_metadata["sqlite_db_path"] = sqlite_db_path

    orchestrator.planner.run(state)
    orchestrator.sql_generator.run(state)
    orchestrator.executor_repair.run(state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DeerFlow-BI MVP demo pipeline")
    parser.add_argument("question", help="Natural language BI question")
    parser.add_argument("--sqlite-db-path", default=None, help="Optional SQLite database path")
    args = parser.parse_args()

    state = run_mvp_demo(question=args.question, sqlite_db_path=args.sqlite_db_path)
    print(
        json.dumps(
            {
                "analysis_plan": state.analysis_plan,
                "candidate_sql": state.candidate_sql,
                "final_sql": state.final_sql,
                "final_result": state.final_result,
                "execution_logs": [log.metadata for log in state.execution_logs],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
