#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_eval_lab.manifest import build_manifest  # noqa: E402


def main() -> int:
    manifest_path = ROOT / "MANIFEST.sha256"
    expected = build_manifest(ROOT)
    actual = (
        manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else ""
    )
    if actual != expected:
        print("FAIL: MANIFEST.sha256 is missing or stale")
        return 1
    print("PASS: MANIFEST.sha256 matches the current public file set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
