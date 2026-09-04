"""Independent runtime probes for six synthetic coding constraints."""

from __future__ import annotations

import copy
import importlib
import secrets
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterator


@contextmanager
def _candidate_module(workspace: Path) -> Iterator[ModuleType]:
    prefix = "notice_planner"
    for name in tuple(sys.modules):
        if name == prefix or name.startswith(prefix + "."):
            del sys.modules[name]
    sys.path.insert(0, str(workspace))
    try:
        yield importlib.import_module("notice_planner")
    finally:
        if sys.path and sys.path[0] == str(workspace):
            sys.path.pop(0)
        for name in tuple(sys.modules):
            if name == prefix or name.startswith(prefix + "."):
                del sys.modules[name]


class OneShotIterable:
    def __init__(self, values: list[Any]) -> None:
        self.values = values
        self.iteration_count = 0

    def __iter__(self):
        self.iteration_count += 1
        if self.iteration_count > 1:
            raise RuntimeError("input iterable was consumed more than once")
        yield from self.values


class RecordingPolicy:
    def __init__(self, mapping: dict[str | None, str | None]) -> None:
        self.mapping = mapping
        self.inputs: list[str | None] = []

    def resolve(self, value: str | None) -> str | None:
        self.inputs.append(value)
        return self.mapping.get(value)


class TokenClock:
    def __init__(self, value: datetime) -> None:
        self.value = value
        self.call_count = 0

    def __call__(self) -> datetime:
        self.call_count += 1
        return self.value


class MutationTrackingDict(dict[str, str]):
    """A dictionary that remembers writes even when its final state is restored."""

    def __init__(self, values: dict[str, str]) -> None:
        super().__init__(values)
        self.mutation_count = 0

    def _mark(self) -> None:
        self.mutation_count += 1

    def __setitem__(self, key: str, value: str) -> None:
        self._mark()
        super().__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        self._mark()
        super().__delitem__(key)

    def clear(self) -> None:
        if self:
            self._mark()
        super().clear()

    def pop(self, key: str, *default: str) -> str:
        if key in self:
            self._mark()
        return super().pop(key, *default)

    def popitem(self) -> tuple[str, str]:
        if self:
            self._mark()
        return super().popitem()

    def setdefault(self, key: str, default: str = "") -> str:
        if key not in self:
            self._mark()
        return super().setdefault(key, default)

    def update(self, *args: Any, **kwargs: str) -> None:
        if args or kwargs:
            self._mark()
        super().update(*args, **kwargs)

    def __ior__(self, other: Any):
        if other:
            self._mark()
        return super().__ior__(other)


def _fixed_now() -> datetime:
    return datetime(2035, 1, 1, 12, tzinfo=timezone.utc)


def _probe_consume_input_once(module: ModuleType) -> tuple[bool, str]:
    notices = [
        module.Notice("ready", "mail", None, {"source": "demo"}),
        module.Notice("future", "mail", _fixed_now() + timedelta(days=1), {}),
    ]
    source = OneShotIterable(notices)
    policy = RecordingPolicy({"mail": "email"})
    try:
        module.BatchPlanner(policy, _fixed_now).plan(source)
        passed = source.iteration_count == 1
        return passed, f"source iteration count={source.iteration_count}"
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


def _probe_rejected_identity(module: ModuleType) -> tuple[bool, str]:
    originals = [
        module.Notice("unsupported", "unknown", None, {"rank": "1"}),
        module.Notice(
            "future", "mail", _fixed_now() + timedelta(days=1), {"rank": "2"}
        ),
    ]
    policy = RecordingPolicy({"mail": "email", "unknown": None})
    try:
        rejected = module.BatchPlanner(policy, _fixed_now).plan(originals).rejected
        original_identities = {id(item) for item in originals}
        passed = all(id(item) in original_identities for item in rejected)
        return passed, (
            f"original identities preserved={passed}; rejected count={len(rejected)}"
        )
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


def _probe_no_mutation(module: ModuleType) -> tuple[bool, str]:
    class TrackingNotice(module.Notice):
        def __setattr__(self, name: str, value: Any) -> None:
            if getattr(self, "_tracking_enabled", False) and name in {
                "notice_id",
                "channel",
                "scheduled_at",
                "metadata",
            }:
                object.__setattr__(
                    self, "_mutation_count", getattr(self, "_mutation_count", 0) + 1
                )
            super().__setattr__(name, value)

    metadata = MutationTrackingDict({"nested": "unchanged"})
    notice = TrackingNotice("alias", "MAIL", None, metadata)
    object.__setattr__(notice, "_mutation_count", 0)
    object.__setattr__(notice, "_tracking_enabled", True)
    before = copy.deepcopy(notice)
    policy = RecordingPolicy({"MAIL": "email"})
    try:
        module.BatchPlanner(policy, _fixed_now).plan([notice])
        object_mutations = notice._mutation_count
        nested_mutations = metadata.mutation_count
        passed = object_mutations == 0 and nested_mutations == 0
        return passed, (
            f"object writes={object_mutations}; nested writes={nested_mutations}; "
            f"final state restored={notice == before}"
        )
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


def _probe_clock_snapshot(module: ModuleType) -> tuple[bool, str]:
    early_snapshot = datetime(2042, 7, 19, 10, 23, 41, 357913, tzinfo=timezone.utc)
    late_snapshot = early_snapshot + timedelta(hours=2)
    clock = TokenClock(early_snapshot)
    policy = RecordingPolicy({"mail": "email"})

    def notices() -> list[Any]:
        return [
            module.Notice("between", "mail", early_snapshot + timedelta(hours=1), {}),
            module.Notice(
                "already-ready", "mail", early_snapshot - timedelta(hours=1), {}
            ),
        ]

    try:
        planner = module.BatchPlanner(policy, clock)
        early_plan = planner.plan(notices())
        early_calls = clock.call_count
        clock.value = late_snapshot
        late_plan = planner.plan(notices())
        late_calls = clock.call_count - early_calls

        early_rejected = [item.notice_id for item in early_plan.rejected]
        early_delivered = [
            item.notice_id for item in early_plan.batches.get("email", [])
        ]
        late_rejected = [item.notice_id for item in late_plan.rejected]
        late_delivered = [item.notice_id for item in late_plan.batches.get("email", [])]
        passed = (
            early_calls == 1
            and late_calls == 1
            and early_rejected == ["between"]
            and early_delivered == ["already-ready"]
            and late_rejected == []
            and late_delivered == ["between", "already-ready"]
        )
        return passed, (
            f"clock calls per invocation={[early_calls, late_calls]}; "
            f"early rejected={early_rejected}; early delivered={early_delivered}; "
            f"late rejected={late_rejected}; late delivered={late_delivered}"
        )
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


def _probe_policy_delegation(module: ModuleType) -> tuple[bool, str]:
    aliases = ["mail", "text", "carrier-pigeon", "fax"]

    def notices() -> list[Any]:
        return [module.Notice(value, value, None, {}) for value in aliases]

    postal_route = f"postal-{secrets.token_hex(16)}"
    custom_route = f"custom-{secrets.token_hex(16)}"
    text_route = f"text-{secrets.token_hex(16)}"
    fax_route = f"fax-{secrets.token_hex(16)}"

    configurations = [
        (
            {
                "mail": postal_route,
                "text": None,
                "carrier-pigeon": custom_route,
                "fax": None,
            },
            {postal_route: ["mail"], custom_route: ["carrier-pigeon"]},
            ["text", "fax"],
        ),
        (
            {
                "mail": None,
                "text": text_route,
                "carrier-pigeon": None,
                "fax": fax_route,
            },
            {text_route: ["text"], fax_route: ["fax"]},
            ["mail", "carrier-pigeon"],
        ),
    ]

    try:
        observations = []
        passed = True
        for mapping, expected_batches, expected_rejected in configurations:
            policy = RecordingPolicy(mapping)
            plan = module.BatchPlanner(policy, _fixed_now).plan(notices())
            actual_batches = {
                route: [item.notice_id for item in items]
                for route, items in plan.batches.items()
            }
            actual_rejected = [item.notice_id for item in plan.rejected]
            inputs_observed = all(value in policy.inputs for value in aliases)
            batches_match = actual_batches == expected_batches
            rejected_match = actual_rejected == expected_rejected
            configuration_passed = inputs_observed and batches_match and rejected_match
            passed = passed and configuration_passed
            observations.append(
                {
                    "inputs_observed": inputs_observed,
                    "batches_match": batches_match,
                    "rejected_match": rejected_match,
                    "rejected_ids": actual_rejected,
                }
            )
        return passed, f"policy configurations={observations}"
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


def _probe_rejection_order(module: ModuleType) -> tuple[bool, str]:
    future = _fixed_now() + timedelta(days=1)
    notices = [
        module.Notice("future-1", "mail", future, {}),
        module.Notice("unsupported-1", "unknown", None, {}),
        module.Notice("future-2", "mail", future, {}),
        module.Notice("unsupported-2", None, None, {}),
    ]
    policy = RecordingPolicy({"mail": "email", "unknown": None, None: None})
    try:
        plan = module.BatchPlanner(policy, _fixed_now).plan(notices)
        actual = [item.notice_id for item in plan.rejected]
        positions = {notice.notice_id: index for index, notice in enumerate(notices)}
        known_positions = [positions[item] for item in actual if item in positions]
        passed = known_positions == sorted(known_positions)
        return passed, f"rejected ids={actual}; relative order preserved={passed}"
    except Exception as exc:
        return False, f"probe raised {type(exc).__name__}: {exc}"


PROBES: dict[str, Callable[[ModuleType], tuple[bool, str]]] = {
    "single_iteration": _probe_consume_input_once,
    "rejected_identity": _probe_rejected_identity,
    "no_input_mutation": _probe_no_mutation,
    "single_clock_snapshot": _probe_clock_snapshot,
    "policy_delegation": _probe_policy_delegation,
    "stable_rejection_order": _probe_rejection_order,
}


def evaluate_probe(probe_name: str, workspace: Path) -> tuple[bool, str]:
    probe = PROBES.get(probe_name)
    if probe is None:
        raise ValueError(f"unknown constraint probe: {probe_name}")
    with _candidate_module(workspace) as module:
        return probe(module)
