"""Conservative release checks for accidental private-data inclusion."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable


IGNORED_PARTS = {
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
ALLOWED_HIDDEN = {".github", ".gitignore"}
MAX_FILE_BYTES = 1_000_000

PATTERNS = {
    "local home-directory path": re.compile(r"(?:/Users/|/home/)[A-Za-z0-9._-]+/"),
    "Windows home-directory path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\\s]+"),
    "email address": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE
    ),
    "private key header": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "credential assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\b\s*[:=]\s*['\"][^'\"]+['\"]"
    ),
}


def _denylist() -> tuple[str, ...]:
    path_value = os.environ.get("PUBLIC_RELEASE_DENYLIST")
    if not path_value:
        return ()
    path = Path(path_value)
    return tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )


def _iter_paths(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(
            part in IGNORED_PARTS or part.endswith(".egg-info")
            for part in relative.parts
        ):
            continue
        yield path


def scan_public_tree(root: Path) -> list[str]:
    findings: list[str] = []
    denylist = _denylist()
    for path in _iter_paths(root):
        relative = path.relative_to(root)
        if path.is_symlink():
            findings.append(f"symlink is not allowed: {relative}")
            continue
        hidden_parts = [
            part
            for part in relative.parts
            if part.startswith(".") and part not in ALLOWED_HIDDEN
        ]
        if hidden_parts:
            findings.append(f"unexpected hidden path: {relative}")
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            findings.append(f"file exceeds {MAX_FILE_BYTES} bytes: {relative}")
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            findings.append(f"binary file is not allowed: {relative}")
            continue
        text = data.decode("utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label} found in {relative}")
        for marker in denylist:
            if marker.casefold() in text.casefold():
                findings.append(f"private denylist marker found in {relative}")
    return findings
