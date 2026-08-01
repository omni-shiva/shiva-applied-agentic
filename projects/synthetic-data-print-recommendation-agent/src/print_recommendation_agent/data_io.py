from __future__ import annotations

import json
from pathlib import Path

from .models import DocumentProfile, HoldoutCase


def load_seed_documents(path: Path) -> list[DocumentProfile]:
    return [
        DocumentProfile.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_holdout_cases(path: Path) -> list[HoldoutCase]:
    return [
        HoldoutCase.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
