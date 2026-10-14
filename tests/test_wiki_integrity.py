"""Regression tests for per-file note classification in the integrity report."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WikiIntegrityTests(unittest.TestCase):
    def test_alias_type_does_not_hide_regular_orphan_or_short_note(self):
        with tempfile.TemporaryDirectory(prefix="bunker-integrity-") as temp:
            root = Path(temp)
            vault = root / "wiki"
            (vault / "meta").mkdir(parents=True)
            (root / "bin").mkdir()
            integrity_script = root / "bin" / "wiki-integrity.sh"
            integrity_script.write_bytes((ROOT / "bin" / "wiki-integrity.sh").read_bytes())

            # The alias sorts after the regular note, reproducing the stale loop variable.
            (vault / "a-regular.md").write_text(
                "---\ntype: concept\ntitle: Regular\n---\n\n# Regular\n", encoding="utf-8"
            )
            (vault / "z-alias.md").write_text(
                "---\ntype: alias\ntitle: Alias\n---\n\n# Alias\n", encoding="utf-8"
            )
            (vault / "index.md").write_text("---\ntitle: Index\nupdated: 2026-10-13\n---\n", encoding="utf-8")
            (vault / "hot.md").write_text("---\ntitle: Hot\nupdated: 2026-10-13\n---\n", encoding="utf-8")
            (vault / "log.md").write_text("---\ntitle: Log\nupdated: 2026-10-13\n---\n", encoding="utf-8")

            report = root / "report.md"
            report_json = root / "report.json"
            env = os.environ | {
                "BUNKER_HOME": str(root),
                "BUNKER_VAULT_DIR": str(vault),
                "BUNKER_INTEGRITY_REPORT": str(report),
                "BUNKER_INTEGRITY_JSON": str(report_json),
            }
            result = subprocess.run(
                ["bash", str(integrity_script)], env=env, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertIn("wiki/a-regular.md", data["orphans"])
            self.assertNotIn("wiki/z-alias.md", data["orphans"])
            self.assertIn("wiki/a-regular.md", [note["path"] for note in data["short_notes"]])
            self.assertNotIn("wiki/z-alias.md", [note["path"] for note in data["short_notes"]])


if __name__ == "__main__":
    unittest.main()
