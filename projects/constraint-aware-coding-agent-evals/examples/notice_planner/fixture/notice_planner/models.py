from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notice:
    notice_id: str
    channel: str | None
    scheduled_at: datetime | None
    metadata: dict[str, str]


@dataclass
class Plan:
    batches: dict[str, list[Notice]]
    rejected: list[Notice]
