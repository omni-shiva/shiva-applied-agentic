"""Loading and validation for a standalone synthetic evaluation scenario."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BundleError(ValueError):
    """Raised when public scenario artifacts are inconsistent."""


@dataclass(frozen=True)
class Bundle:
    root: Path
    scenario: dict[str, Any]
    constraints: tuple[dict[str, Any], ...]

    @property
    def constraint_ids(self) -> tuple[str, ...]:
        return tuple(item["id"] for item in self.constraints)

    @property
    def run_names(self) -> tuple[str, ...]:
        return tuple(self.scenario["runs"])


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BundleError(f"invalid JSON in {path}: {exc}") from exc


def _safe_relative(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise BundleError(f"{label} must be a safe relative path: {value!r}")
    return path


def load_bundle(root: str | Path) -> Bundle:
    root_path = Path(root).resolve()
    scenario = read_json(root_path / "scenario.json")
    constraint_document = read_json(root_path / "constraints.json")

    if not isinstance(scenario, dict) or scenario.get("schema_version") != 1:
        raise BundleError("scenario.json must be an object with schema_version 1")
    if (
        not isinstance(constraint_document, dict)
        or constraint_document.get("schema_version") != 1
    ):
        raise BundleError("constraints.json must be an object with schema_version 1")
    if scenario.get("synthetic") is not True:
        raise BundleError("scenario.json must explicitly mark the example synthetic")

    scenario_id = scenario.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise BundleError("scenario.json needs a non-empty scenario_id")
    if constraint_document.get("scenario_id") != scenario_id:
        raise BundleError(
            "scenario_id differs between scenario.json and constraints.json"
        )

    constraints = constraint_document.get("constraints")
    if not isinstance(constraints, list) or not constraints:
        raise BundleError("constraints.json must contain at least one constraint")

    ids = [item.get("id") for item in constraints]
    if any(not isinstance(item, str) or not item for item in ids):
        raise BundleError("every constraint needs a non-empty string id")
    if len(ids) != len(set(ids)):
        raise BundleError("constraint ids must be unique")

    required_fields = {
        "id",
        "text",
        "evidence_mode",
        "probe",
        "target_component",
        "property_checked",
        "failure_family",
        "covered_by_functional_tests",
    }
    for item in constraints:
        missing = required_fields - item.keys()
        if missing:
            raise BundleError(
                f"constraint {item.get('id')!r} is missing {sorted(missing)}"
            )

    runs = scenario.get("runs")
    if not isinstance(runs, list) or len(runs) < 2 or len(runs) != len(set(runs)):
        raise BundleError("scenario.json must name at least two unique runs")

    required_files = [
        root_path / "scenario.md",
        root_path / "fixture" / "notice_planner" / "planner.py",
        root_path / "fixture" / "tests" / "test_planner.py",
        root_path / "probe_validation" / "cases.json",
        root_path / "reference_evidence" / "evidence_map.json",
        root_path / "reference_evidence" / "implementation.diff",
    ]
    for path in required_files:
        if not path.is_file():
            raise BundleError(f"missing required file: {path}")

    allowed_paths = scenario.get("allowed_paths")
    if not isinstance(allowed_paths, list) or not allowed_paths:
        raise BundleError("scenario.json allowed_paths must be a non-empty list")
    for path in allowed_paths:
        _safe_relative(path, "allowed path")

    for run_name in runs:
        _safe_relative(run_name, "run name")
        run_root = root_path / "candidate_runs" / run_name
        for filename in (
            "run.json",
            "changes.json",
            "observable_trace.json",
            "summary.md",
        ):
            if not (run_root / filename).is_file():
                raise BundleError(f"run {run_name!r} is missing {filename}")

    evidence_map = read_json(root_path / "reference_evidence" / "evidence_map.json")
    if evidence_map.get("scenario_id") != scenario_id:
        raise BundleError(
            "scenario_id differs between scenario.json and reference evidence"
        )
    evidence_ids = set(evidence_map.get("evidence", {}))
    if evidence_ids != set(ids):
        raise BundleError("reference evidence ids must exactly match constraint ids")

    if scenario.get("reference_run") not in runs:
        raise BundleError("scenario.json reference_run must name one declared run")

    bundle = Bundle(root=root_path, scenario=scenario, constraints=tuple(constraints))
    from .reference import build_reference_patch

    actual_patch = (root_path / "reference_evidence" / "implementation.diff").read_text(
        encoding="utf-8"
    )
    if actual_patch != build_reference_patch(bundle):
        raise BundleError(
            "reference implementation diff does not match the declared reference candidate"
        )
    return bundle


def validate_bundle(root: str | Path) -> dict[str, Any]:
    bundle = load_bundle(root)
    from .probe_validation import validate_probe_suite

    probe_validation = validate_probe_suite(bundle)
    return {
        "status": "PASS",
        "scenario_id": bundle.scenario["scenario_id"],
        "constraint_count": len(bundle.constraints),
        "run_count": len(bundle.run_names),
        "probe_validation": probe_validation,
    }
