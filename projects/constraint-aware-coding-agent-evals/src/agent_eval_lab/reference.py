"""Reference-patch generation from the public synthetic artifacts."""

from __future__ import annotations

from difflib import unified_diff

from .bundle import Bundle


def build_reference_patch(bundle: Bundle) -> str:
    relative = "notice_planner/planner.py"
    before = (
        (bundle.root / "fixture" / relative)
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )
    reference_run = bundle.scenario["reference_run"]
    after = (
        (bundle.root / "candidate_runs" / reference_run / "candidate" / relative)
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )
    return "".join(
        unified_diff(
            before,
            after,
            fromfile=f"a/{relative}",
            tofile=f"b/{relative}",
        )
    )
