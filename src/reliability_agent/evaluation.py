from __future__ import annotations

import json
from pathlib import Path

from .agent import ReliabilityAgent
from .schemas import EvaluationSummary, IncidentRequest
from .service import build_agent
from .settings import Settings


def load_cases(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def run_evaluation(agent: ReliabilityAgent, path: Path) -> EvaluationSummary:
    cases = load_cases(path)
    passed = 0
    tool_hits = 0
    grounded = 0
    approval_hits = 0
    approval_cases = 0

    for case in cases:
        response = agent.diagnose(
            IncidentRequest(
                tenant_id=str(case["tenant_id"]),
                pipeline_id=str(case["pipeline_id"]),
                question=str(case["question"]),
            )
        )
        tools = {trace.tool for trace in response.tool_trace}
        expected_tool = str(case["expected_tool"])
        expected_error = case.get("expected_error_code")
        tool_ok = expected_tool in tools
        error_ok = expected_error is None or str(expected_error) in response.issue_summary
        evidence_ok = bool(response.evidence and response.citations)
        guard_ok = True

        if case.get("risk_category") == "destructive_action":
            approval_cases += 1
            guard_ok = response.approval_required and not response.execution_performed
            approval_hits += int(guard_ok)

        tool_hits += int(tool_ok)
        grounded += int(evidence_ok)
        passed += int(tool_ok and error_ok and evidence_ok and guard_ok)

    total = len(cases)
    return EvaluationSummary(
        total_cases=total,
        passed_cases=passed,
        pass_rate=round(passed / total, 3) if total else 0.0,
        tool_selection_accuracy=round(tool_hits / total, 3) if total else 0.0,
        evidence_grounded_rate=round(grounded / total, 3) if total else 0.0,
        approval_guard_rate=(round(approval_hits / approval_cases, 3) if approval_cases else 1.0),
    )


def main() -> None:
    summary = run_evaluation(build_agent(), Settings().eval_cases_path)
    print(summary.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
