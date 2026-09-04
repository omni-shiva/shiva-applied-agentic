"""Temporary materialization of authored synthetic candidate runs."""

from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .bundle import Bundle, BundleError


def _relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise BundleError(f"unsafe synthetic change path: {value!r}")
    return path


def load_changes(run_root: Path) -> list[dict[str, str]]:
    data = json.loads((run_root / "changes.json").read_text(encoding="utf-8"))
    changes = data.get("changes")
    if not isinstance(changes, list) or not changes:
        raise BundleError(f"{run_root / 'changes.json'} must contain changes")
    return changes


@contextmanager
def materialize_run(
    bundle: Bundle, run_name: str
) -> Iterator[tuple[Path, tuple[str, ...]]]:
    if run_name not in bundle.run_names:
        raise BundleError(f"unknown run: {run_name}")

    run_root = bundle.root / "candidate_runs" / run_name
    with tempfile.TemporaryDirectory(prefix="synthetic-agent-eval-") as temp_dir:
        workspace = Path(temp_dir) / "workspace"
        shutil.copytree(bundle.root / "fixture", workspace)
        changed_paths: list[str] = []
        allowed_paths = set(bundle.scenario["allowed_paths"])

        for change in load_changes(run_root):
            target_rel = _relative_path(change.get("path", ""))
            source_rel = _relative_path(change.get("source", ""))
            if target_rel.as_posix() not in allowed_paths:
                raise BundleError(
                    f"synthetic change is outside allowed_paths: {target_rel.as_posix()}"
                )
            source = (run_root / source_rel).resolve()
            if run_root.resolve() not in source.parents:
                raise BundleError(f"change source escapes run directory: {source_rel}")
            if not source.is_file():
                raise BundleError(f"missing synthetic change source: {source}")
            target = workspace / target_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            changed_paths.append(target_rel.as_posix())

        if len(changed_paths) != len(set(changed_paths)):
            raise BundleError(f"run {run_name!r} changes a path more than once")
        yield workspace, tuple(changed_paths)
