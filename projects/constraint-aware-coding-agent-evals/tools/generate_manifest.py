#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_eval_lab.manifest import build_manifest  # noqa: E402


def main() -> int:
    output = ROOT / "MANIFEST.sha256"
    output.write_text(build_manifest(ROOT), encoding="utf-8")
    print(f"PASS: wrote {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
