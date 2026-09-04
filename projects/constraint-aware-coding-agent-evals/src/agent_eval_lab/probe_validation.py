"""Accepted and isolated adversarial fixtures for runtime probes."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .bundle import Bundle, BundleError, read_json
from .probes import evaluate_probe
from .verifier import run_functional_tests


@contextmanager
def _candidate_workspace(bundle: Bundle, candidate_value: str) -> Iterator[Path]:
    candidate_relative = Path(candidate_value)
    if candidate_relative.is_absolute() or ".." in candidate_relative.parts:
        raise BundleError(f"unsafe probe fixture path: {candidate_relative}")
    candidate = (bundle.root / candidate_relative).resolve()
    if bundle.root not in candidate.parents or not candidate.is_file():
        raise BundleError(f"missing or escaped probe fixture: {candidate_relative}")

    with tempfile.TemporaryDirectory(prefix="synthetic-probe-check-") as temp_dir:
        workspace = Path(temp_dir) / "workspace"
        shutil.copytree(bundle.root / "fixture", workspace)
        shutil.copyfile(candidate, workspace / "notice_planner" / "planner.py")
        yield workspace


def validate_probe_suite(bundle: Bundle) -> dict[str, Any]:
    document = read_json(bundle.root / "probe_validation" / "cases.json")
    if document.get("schema_version") != 2:
        raise BundleError("probe_validation/cases.json must use schema_version 2")
    cases = document.get("cases")
    if not isinstance(cases, list):
        raise BundleError("probe_validation/cases.json must contain a cases list")

    constraints = {item["id"]: item for item in bundle.constraints}
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    functional_cache: dict[str, bool] = {}
    accepted_fixture_count = 0
    adversarial_fixture_count = 0
    decoupling_paths: set[str] = set()

    def candidate_spec(value: Any, label: str) -> tuple[str, bool]:
        if not isinstance(value, dict):
            raise BundleError(f"{label} must be an object")
        path = value.get("path")
        expectation = value.get("functional_tests_expected")
        if not isinstance(path, str) or not path:
            raise BundleError(f"{label} needs a non-empty path")
        if not isinstance(expectation, bool):
            raise BundleError(f"{label} needs a boolean functional_tests_expected")
        return path, expectation

    def verify_functional_expectation(
        path: str, expected: bool, workspace: Path
    ) -> bool:
        if path not in functional_cache:
            functional_cache[path] = bool(run_functional_tests(workspace)["passed"])
        actual = functional_cache[path]
        if actual != expected:
            raise BundleError(
                f"functional-test expectation differs for {path}: "
                f"expected {expected}, observed {actual}"
            )
        if expected is False:
            decoupling_paths.add(path)
        return actual

    for case in cases:
        constraint_id = case.get("constraint_id")
        if constraint_id not in constraints:
            raise BundleError(
                f"probe fixture names unknown constraint: {constraint_id!r}"
            )
        if constraint_id in seen:
            raise BundleError(
                f"duplicate probe fixture for constraint: {constraint_id}"
            )
        seen.add(constraint_id)
        target_probe = constraints[constraint_id]["probe"]

        accepted_values = case.get("accepted_candidates")
        adversarial_values = case.get("adversarial_candidates")
        if not isinstance(accepted_values, list) or not accepted_values:
            raise BundleError(f"{constraint_id} needs accepted_candidates")
        if not isinstance(adversarial_values, list) or not adversarial_values:
            raise BundleError(f"{constraint_id} needs adversarial_candidates")

        accepted_results: list[dict[str, Any]] = []
        for index, value in enumerate(accepted_values):
            path, expected_functional = candidate_spec(
                value, f"accepted candidate {index} for {constraint_id}"
            )
            with _candidate_workspace(bundle, path) as workspace:
                functional_passed = verify_functional_expectation(
                    path, expected_functional, workspace
                )
                accepted, evidence = evaluate_probe(target_probe, workspace)
            if not accepted:
                raise BundleError(
                    f"accepted fixture failed for {constraint_id}: {path}: {evidence}"
                )
            accepted_fixture_count += 1
            accepted_results.append(
                {
                    "candidate": path,
                    "probe_passed": True,
                    "functional_tests_passed": functional_passed,
                    "evidence": evidence,
                }
            )

        adversarial_results: list[dict[str, Any]] = []
        for index, value in enumerate(adversarial_values):
            path, expected_functional = candidate_spec(
                value, f"adversarial candidate {index} for {constraint_id}"
            )
            failed_ids: list[str] = []
            target_evidence = ""
            with _candidate_workspace(bundle, path) as workspace:
                functional_passed = verify_functional_expectation(
                    path, expected_functional, workspace
                )
                for other_id, other in constraints.items():
                    observed, evidence = evaluate_probe(other["probe"], workspace)
                    if not observed:
                        failed_ids.append(other_id)
                        if other_id == constraint_id:
                            target_evidence = evidence
            if failed_ids != [constraint_id]:
                raise BundleError(
                    f"adversarial fixture for {constraint_id} must fail only itself; "
                    f"{path} observed {failed_ids}"
                )
            adversarial_fixture_count += 1
            adversarial_results.append(
                {
                    "candidate": path,
                    "target_rejected": True,
                    "failure_isolated": True,
                    "functional_tests_passed": functional_passed,
                    "evidence": target_evidence,
                }
            )

        results.append(
            {
                "constraint_id": constraint_id,
                "accepted_fixtures": accepted_results,
                "adversarial_fixtures": adversarial_results,
            }
        )

    if seen != set(constraints):
        raise BundleError(
            f"constraints missing probe fixtures: {sorted(set(constraints) - seen)}"
        )

    probe_expectations = accepted_fixture_count + adversarial_fixture_count
    return {
        "status": "PASS",
        "constraints_checked": len(results),
        "accepted_probe_fixtures": accepted_fixture_count,
        "isolated_adversarial_fixtures": adversarial_fixture_count,
        "functional_expectation_checks": len(functional_cache),
        "functional_decoupling_fixtures": len(decoupling_paths),
        "probe_expectations_passed": probe_expectations,
        "checks_passed": probe_expectations + len(functional_cache),
        "results": results,
    }
