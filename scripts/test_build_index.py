"""Tests for build_index.py's package.requires handling.

No package in this repository declares requirements yet, so --check alone
never exercises them.

    python -m unittest discover -s scripts -p "test_*.py"
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_index  # noqa: E402

BASE = """apiVersion: sinas.co/v1
kind: SinasPackage
package:
  name: triage
  version: "1.0.0"
  description: Triage
  author: Test
{requires}spec: {{}}
"""


class EntryTest(unittest.TestCase):
    """entry() on a package written to a temporary repository root."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        patcher = mock.patch.object(build_index, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def entry(self, requires_yaml: str) -> dict:
        path = self.root / "packages" / "triage" / "package.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(BASE.format(requires=requires_yaml))
        return build_index.entry(path)

    def test_all_four_keys_are_kept(self):
        out = self.entry(
            "  requires:\n"
            "    - name: gmail\n"
            "      version: \">=1.2,<2\"\n"
            "      repository: sinas-official\n"
            "      instance: gmail-support\n"
            "    - name: slack\n"
        )
        self.assertEqual(out["requires"], [
            {"name": "gmail", "version": ">=1.2,<2", "repository": "sinas-official", "instance": "gmail-support"},
            {"name": "slack"},
        ])

    def test_omitted_requires_leaves_the_field_out(self):
        self.assertNotIn("requires", self.entry(""))

    def test_empty_or_null_requires_leaves_the_field_out(self):
        self.assertNotIn("requires", self.entry("  requires: []\n"))
        self.assertNotIn("requires", self.entry("  requires:\n"))

    def test_not_a_list_fails(self):
        with self.assertRaisesRegex(ValueError, "must be a list"):
            self.entry("  requires: gmail\n")

    def test_an_entry_without_a_name_fails(self):
        with self.assertRaisesRegex(ValueError, "needs a name"):
            self.entry("  requires:\n    - version: \">=1\"\n")

    def test_an_unknown_key_fails(self):
        with self.assertRaisesRegex(ValueError, "unknown keys: versions"):
            self.entry("  requires:\n    - name: gmail\n      versions: \">=1\"\n")


class RequirementsTest(unittest.TestCase):
    """requirements() on its own."""

    def test_values_become_strings_and_none_is_dropped(self):
        self.assertEqual(
            build_index.requirements(Path("x"), [{"name": "gmail", "version": None, "repository": "r"}]),
            [{"name": "gmail", "repository": "r"}],
        )

    def test_none_is_no_requirements(self):
        self.assertEqual(build_index.requirements(Path("x"), None), [])

    def test_an_empty_name_fails(self):
        with self.assertRaisesRegex(ValueError, "needs a name"):
            build_index.requirements(Path("x"), [{"name": ""}])


if __name__ == "__main__":
    unittest.main()
