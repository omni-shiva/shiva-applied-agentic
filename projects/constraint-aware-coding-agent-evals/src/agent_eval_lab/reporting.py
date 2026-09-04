"""Human-readable reporting for a synthetic evaluation."""

from __future__ import annotations

from typing import Any


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown_report(grades: list[dict[str, Any]], analysis: dict[str, Any]) -> str:
    lines = [
        f"# Evaluation report: {analysis['scenario_id']}",
        "",
        "All data and results in this report are synthetic.",
        "",
        "| Run | Functional tests | Constraint compliance | Fully passed |",
        "|---|---:|---:|---:|",
    ]
    for grade in grades:
        lines.append(
            "| {label} | {correctness} | {compliance} ({passed}/{total}) | {full} |".format(
                label=grade["run_label"],
                correctness="PASS" if grade["correctness"]["passed"] else "FAIL",
                compliance=_percent(grade["constraint_pass_rate"]),
                passed=grade["constraint_passed"],
                total=grade["constraint_total"],
                full="PASS" if grade["fully_passed"] else "FAIL",
            )
        )

    lines.extend(
        [
            "",
            f"Compliance separation: **{_percent(analysis['compliance_separation'])}**",
            "",
            analysis["lesson"],
            "",
            "## Constraint-level evidence",
            "",
        ]
    )
    for grade in grades:
        lines.extend([f"### {grade['run_label']}", ""])
        for judgment in grade["constraint_judgments"]:
            marker = "PASS" if judgment["passed"] else "FAIL"
            lines.append(
                f"- {marker} `{judgment['constraint_id']}`: {judgment['evidence']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
