"""Command-line entrypoint for the synthetic evaluation lab."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze_grades
from .bundle import BundleError, load_bundle, validate_bundle
from .grader import grade_bundle
from .manifest import build_manifest
from .privacy import scan_public_tree
from .probe_validation import validate_probe_suite
from .reporting import markdown_report


def _json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _evaluate(example: Path, output: Path | None) -> int:
    bundle = load_bundle(example)
    probe_validation = validate_probe_suite(bundle)
    grades = grade_bundle(bundle)
    analysis = analyze_grades(grades)
    report = markdown_report(grades, analysis)
    payload = {
        "probe_validation": probe_validation,
        "grades": grades,
        "analysis": analysis,
    }
    if output:
        output.mkdir(parents=True, exist_ok=True)
        (output / "evaluation.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output / "report.md").write_text(report, encoding="utf-8")
        print(f"PASS: wrote {output / 'evaluation.json'} and {output / 'report.md'}")
    else:
        print(report, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate a fully synthetic coding scenario."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate", help="validate scenario structure and probe fixtures"
    )
    validate.add_argument("example", type=Path)

    probes = subparsers.add_parser(
        "check-probes", help="run accepted and isolated adversarial probe fixtures"
    )
    probes.add_argument("example", type=Path)

    evaluate = subparsers.add_parser(
        "evaluate", help="grade all synthetic runs and create a comparison"
    )
    evaluate.add_argument("example", type=Path)
    evaluate.add_argument("--output", type=Path)

    manifest = subparsers.add_parser("manifest", help="build a SHA-256 file inventory")
    manifest.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    manifest.add_argument("--write", type=Path)

    safety = subparsers.add_parser(
        "public-safety", help="scan public source files for configured release risks"
    )
    safety.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            _json(validate_bundle(args.example))
            return 0
        if args.command == "check-probes":
            _json(validate_probe_suite(load_bundle(args.example)))
            return 0
        if args.command == "evaluate":
            return _evaluate(args.example, args.output)
        if args.command == "manifest":
            manifest = build_manifest(args.root.resolve())
            if args.write:
                args.write.write_text(manifest, encoding="utf-8")
                print(f"PASS: wrote {args.write}")
            else:
                print(manifest, end="")
            return 0
        if args.command == "public-safety":
            findings = scan_public_tree(args.root.resolve())
            if findings:
                print("FAIL: configured public-safety findings")
                for finding in findings:
                    print(f"- {finding}")
                return 1
            print("PASS: scanned public source files have no configured findings")
            print(
                "NOTE: ignored development artifacts and version-control history were not scanned"
            )
            return 0
    except (BundleError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 2
