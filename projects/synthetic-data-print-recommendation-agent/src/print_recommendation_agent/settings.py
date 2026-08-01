from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    seed_path: Path = PROJECT_ROOT / "data" / "seed_documents.jsonl"
    holdout_path: Path = PROJECT_ROOT / "evals" / "holdout_documents.jsonl"
    training_scale: int = int(os.getenv("TRAINING_SCALE", "10"))
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    review_confidence_threshold: float = float(
        os.getenv("REVIEW_CONFIDENCE_THRESHOLD", "0.65")
    )

    def __post_init__(self) -> None:
        if self.training_scale not in {1, 10, 100}:
            raise ValueError("TRAINING_SCALE must be one of 1, 10 or 100")
        if not 0.0 <= self.review_confidence_threshold <= 1.0:
            raise ValueError("REVIEW_CONFIDENCE_THRESHOLD must be between 0 and 1")
