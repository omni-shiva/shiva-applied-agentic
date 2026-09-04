from __future__ import annotations

import json
import unittest
from pathlib import Path

from agent_eval_lab.analysis import analyze_grades
from agent_eval_lab.bundle import load_bundle
from agent_eval_lab.grader import grade_bundle
from agent_eval_lab.probe_validation import validate_probe_suite
from agent_eval_lab.reporting import markdown_report


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "notice_planner"


class GradingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grades = grade_bundle(load_bundle(EXAMPLE))

    def test_both_candidates_pass_functional_tests(self) -> None:
        self.assertTrue(all(grade["correctness"]["passed"] for grade in self.grades))
        self.assertTrue(
            all(grade["correctness"]["test_count"] == 3 for grade in self.grades)
        )
        self.assertTrue(
            all(
                set(grade["correctness"]) == {"passed", "return_code", "test_count"}
                for grade in self.grades
            )
        )

    def test_reference_passes_all_six_constraints(self) -> None:
        reference = self.grades[0]
        self.assertEqual(reference["constraint_passed"], 6)
        self.assertTrue(reference["fully_passed"])

    def test_comparison_exposes_four_behavior_violations(self) -> None:
        comparison = self.grades[1]
        failed = {
            item["constraint_id"]
            for item in comparison["constraint_judgments"]
            if not item["passed"]
        }
        self.assertEqual(
            failed,
            {
                "consume-input-once",
                "preserve-rejected-identity",
                "do-not-mutate-inputs",
                "snapshot-clock-once",
            },
        )
        self.assertEqual(comparison["constraint_passed"], 2)

    def test_analysis_reports_compliance_separation(self) -> None:
        analysis = analyze_grades(self.grades)
        self.assertAlmostEqual(analysis["compliance_separation"], 4 / 6)
        self.assertEqual(analysis["correctness_pass_rate"], 1.0)

    def test_complete_evaluation_is_byte_reproducible(self) -> None:
        def render() -> tuple[str, str]:
            bundle = load_bundle(EXAMPLE)
            probe_validation = validate_probe_suite(bundle)
            grades = grade_bundle(bundle)
            analysis = analyze_grades(grades)
            payload = {
                "probe_validation": probe_validation,
                "grades": grades,
                "analysis": analysis,
            }
            return (
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                markdown_report(grades, analysis),
            )

        first_json, first_markdown = render()
        second_json, second_markdown = render()
        self.assertEqual(first_json, second_json)
        self.assertEqual(first_markdown, second_markdown)
        self.assertEqual(
            first_json,
            (ROOT / "reports" / "example" / "evaluation.json").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            first_markdown,
            (ROOT / "reports" / "example" / "report.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
