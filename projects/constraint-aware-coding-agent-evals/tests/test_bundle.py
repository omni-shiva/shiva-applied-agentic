from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent_eval_lab.bundle import BundleError, load_bundle, validate_bundle
from agent_eval_lab.probe_validation import validate_probe_suite
from agent_eval_lab.reference import build_reference_patch


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "notice_planner"


class BundleTests(unittest.TestCase):
    def test_bundle_has_six_distinct_behavior_categories(self) -> None:
        bundle = load_bundle(EXAMPLE)
        categories = {item["failure_family"] for item in bundle.constraints}
        self.assertEqual(len(bundle.constraints), 6)
        self.assertEqual(len(categories), 6)
        self.assertTrue(
            all(
                item["covered_by_functional_tests"] is False
                for item in bundle.constraints
            )
        )

    def test_bundle_and_probe_validation_pass(self) -> None:
        result = validate_bundle(EXAMPLE)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["probe_validation"]["checks_passed"], 45)
        self.assertEqual(result["probe_validation"]["accepted_probe_fixtures"], 14)
        self.assertEqual(
            result["probe_validation"]["isolated_adversarial_fixtures"], 12
        )
        self.assertEqual(
            result["probe_validation"]["functional_expectation_checks"], 19
        )
        self.assertEqual(
            result["probe_validation"]["functional_decoupling_fixtures"], 2
        )

    def test_every_adversarial_fixture_is_isolated(self) -> None:
        result = validate_probe_suite(load_bundle(EXAMPLE))
        self.assertEqual(result["constraints_checked"], 6)
        self.assertTrue(
            all(
                fixture["probe_passed"]
                for item in result["results"]
                for fixture in item["accepted_fixtures"]
            )
        )
        self.assertTrue(
            all(
                fixture["failure_isolated"]
                for item in result["results"]
                for fixture in item["adversarial_fixtures"]
            )
        )

    def test_functional_failure_does_not_contaminate_targeted_probe_results(
        self,
    ) -> None:
        result = validate_probe_suite(load_bundle(EXAMPLE))
        decoupled = [
            (item["constraint_id"], fixture)
            for item in result["results"]
            for fixture in item["accepted_fixtures"]
            if fixture["candidate"].endswith("functionally_incomplete.py")
        ]
        self.assertEqual(
            {constraint_id for constraint_id, _ in decoupled},
            {
                "consume-input-once",
                "preserve-rejected-identity",
                "preserve-rejection-order",
            },
        )
        self.assertTrue(
            all(not fixture["functional_tests_passed"] for _, fixture in decoupled)
        )

        identity_case = next(
            item
            for item in result["results"]
            if item["constraint_id"] == "preserve-rejected-identity"
        )
        duplicate = next(
            fixture
            for fixture in identity_case["accepted_fixtures"]
            if fixture["candidate"].endswith("duplicate_original_rejections.py")
        )
        self.assertTrue(duplicate["probe_passed"])
        self.assertFalse(duplicate["functional_tests_passed"])

    def test_equivalent_valid_implementations_are_accepted(self) -> None:
        result = validate_probe_suite(load_bundle(EXAMPLE))
        expected = {
            "snapshot-clock-once": {
                "equivalent_clock_comparison.py",
                "clock_arithmetic.py",
                "clock_timestamp.py",
            },
            "delegate-channel-resolution": {"policy_twice.py"},
        }
        for constraint_id, filenames in expected.items():
            case = next(
                item
                for item in result["results"]
                if item["constraint_id"] == constraint_id
            )
            fixtures = [
                item
                for item in case["accepted_fixtures"]
                if any(item["candidate"].endswith(name) for name in filenames)
            ]
            self.assertEqual(len(fixtures), len(filenames))
            self.assertTrue(all(item["probe_passed"] for item in fixtures))
            self.assertTrue(all(item["functional_tests_passed"] for item in fixtures))

    def test_reference_patch_is_reproducible(self) -> None:
        bundle = load_bundle(EXAMPLE)
        persisted = (EXAMPLE / "reference_evidence" / "implementation.diff").read_text(
            encoding="utf-8"
        )
        self.assertEqual(persisted, build_reference_patch(bundle))

    def test_scenario_identity_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "example"
            shutil.copytree(EXAMPLE, copied)
            constraints_path = copied / "constraints.json"
            document = json.loads(constraints_path.read_text(encoding="utf-8"))
            document["scenario_id"] = "different-scenario"
            constraints_path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaisesRegex(BundleError, "scenario_id differs"):
                load_bundle(copied)


if __name__ == "__main__":
    unittest.main()
