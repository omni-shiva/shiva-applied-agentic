"""Dual-axis grading for functional correctness and constraint compliance."""

from __future__ import annotations

from typing import Any

from .bundle import Bundle, BundleError, read_json
from .probes import evaluate_probe
from .verifier import run_functional_tests
from .workspace import materialize_run


def grade_run(bundle: Bundle, run_name: str) -> dict[str, Any]:
    run_root = bundle.root / "candidate_runs" / run_name
    run_metadata = read_json(run_root / "run.json")
    trace = read_json(run_root / "observable_trace.json")
    summary = (run_root / "summary.md").read_text(encoding="utf-8")
    if run_metadata.get("synthetic") is not True or trace.get("synthetic") is not True:
        raise BundleError(f"run {run_name!r} must be explicitly marked synthetic")
    if trace.get("run_id") != run_metadata.get("run_id"):
        raise BundleError(f"run {run_name!r} has inconsistent run ids")
    if not summary.strip():
        raise BundleError(f"run {run_name!r} has an empty summary")

    with materialize_run(bundle, run_name) as (workspace, changed_paths):
        correctness = run_functional_tests(workspace)
        judgments: list[dict[str, Any]] = []
        for constraint in bundle.constraints:
            passed, evidence = evaluate_probe(constraint["probe"], workspace)
            judgments.append(
                {
                    "constraint_id": constraint["id"],
                    "evidence_mode": constraint["evidence_mode"],
                    "passed": passed,
                    "evidence": evidence,
                }
            )

    constraint_passed = sum(1 for item in judgments if item["passed"])
    all_constraints_passed = constraint_passed == len(judgments)
    return {
        "schema_version": 1,
        "scenario_id": bundle.scenario["scenario_id"],
        "run_id": run_metadata["run_id"],
        "run_label": run_metadata["label"],
        "correctness": correctness,
        "constraint_judgments": judgments,
        "constraint_passed": constraint_passed,
        "constraint_total": len(judgments),
        "constraint_pass_rate": constraint_passed / len(judgments),
        "fully_passed": correctness["passed"] and all_constraints_passed,
        "changed_paths": list(changed_paths),
        "artifact_summary": {
            "observable_events": len(trace.get("events", [])),
            "summary_present": True,
            "synthetic": True,
        },
    }


def grade_bundle(bundle: Bundle) -> list[dict[str, Any]]:
    return [grade_run(bundle, run_name) for run_name in bundle.run_names]
