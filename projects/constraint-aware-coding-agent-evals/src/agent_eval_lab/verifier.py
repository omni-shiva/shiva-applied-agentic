"""Functional verification for a materialized synthetic run."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_functional_tests(workspace: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    combined_output = completed.stdout + completed.stderr
    count_match = re.search(r"\bRan (\d+) tests?\b", combined_output)
    return {
        "passed": completed.returncode == 0,
        "return_code": completed.returncode,
        "test_count": int(count_match.group(1)) if count_match else None,
    }
