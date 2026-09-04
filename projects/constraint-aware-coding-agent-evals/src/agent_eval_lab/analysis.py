"""Comparison metrics that keep correctness separate from compliance."""

from __future__ import annotations

from typing import Any


def analyze_grades(grades: list[dict[str, Any]]) -> dict[str, Any]:
    if len(grades) < 2:
        raise ValueError("analysis needs at least two graded runs")
    reference = grades[0]
    comparison = grades[1]
    return {
        "scenario_id": reference["scenario_id"],
        "run_count": len(grades),
        "correctness_pass_rate": sum(grade["correctness"]["passed"] for grade in grades)
        / len(grades),
        "fully_passed_rate": sum(grade["fully_passed"] for grade in grades)
        / len(grades),
        "reference_compliance_rate": reference["constraint_pass_rate"],
        "comparison_compliance_rate": comparison["constraint_pass_rate"],
        "compliance_separation": reference["constraint_pass_rate"]
        - comparison["constraint_pass_rate"],
        "lesson": (
            "Functional correctness alone is insufficient: both runs pass tests, "
            "but their independently measured constraint compliance differs."
        ),
    }
