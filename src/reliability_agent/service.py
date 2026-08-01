from __future__ import annotations

from functools import lru_cache

from .agent import ReliabilityAgent
from .contracts import ContractStore
from .events import PipelineEventStore
from .knowledge import RunbookStore
from .settings import Settings
from .tools import ToolRegistry


@lru_cache(maxsize=1)
def build_agent() -> ReliabilityAgent:
    settings = Settings()
    registry = ToolRegistry(
        events=PipelineEventStore(settings.data_dir / "pipeline_events.jsonl"),
        contracts=ContractStore(settings.data_dir / "contracts"),
        runbooks=RunbookStore(settings.data_dir / "runbooks"),
    )
    return ReliabilityAgent(registry=registry, settings=settings)
