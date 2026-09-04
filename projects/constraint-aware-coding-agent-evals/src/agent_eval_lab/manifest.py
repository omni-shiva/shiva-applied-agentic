"""SHA-256 inventory generation for public reproducibility."""

from __future__ import annotations

import hashlib
from pathlib import Path


EXCLUDED_PARTS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    ".egg-info",
}


def iter_public_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        if any(
            part in EXCLUDED_PARTS or part.endswith(".egg-info")
            for part in path.relative_to(root).parts
        ):
            continue
        yield path


def build_manifest(root: Path) -> str:
    lines = []
    for path in iter_public_files(root):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
    return "\n".join(lines) + "\n"
