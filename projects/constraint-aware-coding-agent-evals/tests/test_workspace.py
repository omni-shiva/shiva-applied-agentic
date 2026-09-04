from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent_eval_lab.bundle import BundleError, load_bundle
from agent_eval_lab.workspace import materialize_run


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "notice_planner"


class WorkspaceTests(unittest.TestCase):
    def test_candidate_cannot_change_a_path_outside_task_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "example"
            shutil.copytree(EXAMPLE, copied)
            changes_path = (
                copied / "candidate_runs" / "comparison_agent" / "changes.json"
            )
            changes = json.loads(changes_path.read_text(encoding="utf-8"))
            changes["changes"][0]["path"] = "tests/test_planner.py"
            changes_path.write_text(json.dumps(changes), encoding="utf-8")

            bundle = load_bundle(copied)
            with self.assertRaisesRegex(BundleError, "outside allowed_paths"):
                with materialize_run(bundle, "comparison_agent"):
                    self.fail("out-of-scope candidate should not materialize")


if __name__ == "__main__":
    unittest.main()
