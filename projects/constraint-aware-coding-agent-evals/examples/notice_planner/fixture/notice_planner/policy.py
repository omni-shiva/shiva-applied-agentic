from __future__ import annotations

from typing import Protocol


class ChannelPolicy(Protocol):
    def resolve(self, value: str | None) -> str | None: ...


class MappingChannelPolicy:
    def __init__(self, mapping: dict[str | None, str | None]) -> None:
        self._mapping = mapping

    def resolve(self, value: str | None) -> str | None:
        return self._mapping.get(value)
