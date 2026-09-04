from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime

from .models import Notice, Plan
from .policy import ChannelPolicy


class BatchPlanner:
    def __init__(self, policy: ChannelPolicy, clock: Callable[[], datetime]) -> None:
        self._policy = policy
        self._clock = clock

    def plan(self, notices: Iterable[Notice]) -> Plan:
        now = self._clock()
        batches: dict[str, list[Notice]] = {}
        future_rejections: list[Notice] = []
        unsupported_rejections: list[Notice] = []
        for notice in notices:
            resolved_channel = self._policy.resolve(notice.channel)
            if resolved_channel is None:
                unsupported_rejections.append(notice)
            elif notice.scheduled_at is not None and notice.scheduled_at > now:
                future_rejections.append(notice)
            else:
                batches.setdefault(resolved_channel, []).append(notice)
        return Plan(
            batches=batches, rejected=future_rejections + unsupported_rejections
        )
