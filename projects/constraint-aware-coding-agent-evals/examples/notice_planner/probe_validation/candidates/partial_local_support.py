from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime

from .models import Notice, Plan
from .policy import ChannelPolicy


class BatchPlanner:
    """Calls the policy but hard-codes one local unsupported-channel decision."""

    def __init__(self, policy: ChannelPolicy, clock: Callable[[], datetime]) -> None:
        self._policy = policy
        self._clock = clock

    def plan(self, notices: Iterable[Notice]) -> Plan:
        now = self._clock()
        batches: dict[str, list[Notice]] = {}
        rejected: list[Notice] = []
        for notice in notices:
            resolved_channel = self._policy.resolve(notice.channel)
            if notice.channel == "fax":
                resolved_channel = None
            is_future = notice.scheduled_at is not None and notice.scheduled_at > now
            if resolved_channel is None or is_future:
                rejected.append(notice)
            else:
                batches.setdefault(resolved_channel, []).append(notice)
        return Plan(batches=batches, rejected=rejected)
