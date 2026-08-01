from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = PROJECT_ROOT / "data"
    eval_cases_path: Path = PROJECT_ROOT / "evals" / "cases.jsonl"
    agent_mode: str = os.getenv("AGENT_MODE", "offline").lower()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")
    max_tool_steps: int = int(os.getenv("MAX_TOOL_STEPS", "4"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def openai_enabled(self) -> bool:
        return self.agent_mode == "openai" and bool(self.openai_api_key)
