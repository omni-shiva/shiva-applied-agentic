#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_eval_lab.privacy import scan_public_tree  # noqa: E402


def main() -> int:
    findings = scan_public_tree(ROOT)
    if findings:
        print("FAIL: configured sensitive-data patterns were found")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(
        "PASS: no configured sensitive-data patterns were found in public source files"
    )
    print(
        "NOTE: ignored development artifacts and version-control history were not scanned"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
