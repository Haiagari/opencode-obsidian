#!/usr/bin/env python3
"""Safety tests for the opt-in GitHub metadata setup command."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "extensions" / "operations" / "bin" / "bunker-github-setup.sh"


class TestGitHubSetup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="bunker_gh_setup_")
        self.root = Path(self.temp_dir.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.log = self.root / "gh.log"
        self.env = os.environ.copy()
        self.env["PATH"] = str(self.bin_dir) + os.pathsep + os.environ.get("PATH", "")
        self.env["GH_LOG"] = str(self.log)
        fake_gh = self.bin_dir / "gh"
        fake_gh.write_text(
            "#!/bin/bash\nprintf '%s\\n' \"$*\" >> \"$GH_LOG\"\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_is_dry_run_and_does_not_call_gh(self):
        result = subprocess.run(
            ["/bin/bash", str(SCRIPT)],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run only", result.stdout)
        self.assertIn("Branch protection: unchanged", result.stdout)
        self.assertFalse(self.log.exists())

    def test_apply_changes_metadata_without_calling_protection_api(self):
        result = subprocess.run(
            ["/bin/bash", str(SCRIPT), "--apply"],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].startswith("repo edit Haiagari/opencode-obsidian"))
        self.assertNotIn("protection", calls[0])


if __name__ == "__main__":
    unittest.main()
