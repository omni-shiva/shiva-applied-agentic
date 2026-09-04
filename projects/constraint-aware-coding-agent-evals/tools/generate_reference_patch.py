#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_eval_lab.bundle import Bundle, read_json  # noqa: E402
from agent_eval_lab.reference import build_reference_patch  # noqa: E402


def main() -> int:
    example = ROOT / "examples" / "notice_planner"
    constraints = read_json(example / "constraints.json")["constraints"]
    bundle = Bundle(
        root=example,
        scenario=read_json(example / "scenario.json"),
        constraints=tuple(constraints),
    )
    output = example / "reference_evidence" / "implementation.diff"
    output.write_text(build_reference_patch(bundle), encoding="utf-8")
    print(f"PASS: wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
