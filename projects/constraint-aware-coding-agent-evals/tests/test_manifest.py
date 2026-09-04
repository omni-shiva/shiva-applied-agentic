from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_eval_lab.manifest import build_manifest


class ManifestTests(unittest.TestCase):
    def test_manifest_is_sorted_and_excludes_itself(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "b.txt").write_text("b", encoding="utf-8")
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "MANIFEST.sha256").write_text("stale", encoding="utf-8")
            manifest = build_manifest(root)
            paths = [line.split("  ", 1)[1] for line in manifest.splitlines()]
            self.assertEqual(paths, ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
