from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_eval_lab.privacy import scan_public_tree


class PrivacyTests(unittest.TestCase):
    def test_safe_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "Fully synthetic example.\n", encoding="utf-8"
            )
            self.assertEqual(scan_public_tree(root), [])

    def test_email_and_local_path_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            risky = (
                "person"
                + "@"
                + "example.test\n"
                + "/"
                + "Users/"
                + "demo/private.txt\n"
            )
            (root / "unsafe.txt").write_text(risky, encoding="utf-8")
            findings = scan_public_tree(root)
            self.assertTrue(any("email address" in item for item in findings))
            self.assertTrue(any("home-directory path" in item for item in findings))


if __name__ == "__main__":
    unittest.main()
