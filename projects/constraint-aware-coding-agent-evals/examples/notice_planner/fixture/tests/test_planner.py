from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from notice_planner import BatchPlanner, MappingChannelPolicy, Notice


NOW = datetime(2035, 1, 1, 12, tzinfo=timezone.utc)


class BatchPlannerCorrectnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = MappingChannelPolicy(
            {"mail": "email", "MAIL": "email", "text": "sms"}
        )

    def test_groups_supported_notices(self) -> None:
        notices = [
            Notice("one", "mail", None, {}),
            Notice("two", "text", NOW, {}),
            Notice("three", "mail", NOW - timedelta(minutes=1), {}),
        ]
        plan = BatchPlanner(self.policy, lambda: NOW).plan(notices)
        self.assertEqual(
            [item.notice_id for item in plan.batches["email"]], ["one", "three"]
        )
        self.assertEqual([item.notice_id for item in plan.batches["sms"]], ["two"])
        self.assertEqual(plan.rejected, [])

    def test_rejects_future_and_unsupported_notices(self) -> None:
        notices = [
            Notice("future", "mail", NOW + timedelta(days=1), {}),
            Notice("unsupported", "unknown", None, {}),
        ]
        plan = BatchPlanner(self.policy, lambda: NOW).plan(notices)
        self.assertCountEqual(
            [item.notice_id for item in plan.rejected], ["future", "unsupported"]
        )

    def test_resolves_an_alias(self) -> None:
        notice = Notice("alias", "MAIL", None, {"source": "synthetic"})
        plan = BatchPlanner(self.policy, lambda: NOW).plan([notice])
        self.assertEqual([item.notice_id for item in plan.batches["email"]], ["alias"])


if __name__ == "__main__":
    unittest.main()
