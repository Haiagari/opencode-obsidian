"""Safety tests for optional host setup and GitHub operation scripts."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalOperationTests(unittest.TestCase):
    def test_opencode_setup_backs_up_existing_skill_and_preserves_config(self):
        with tempfile.TemporaryDirectory(prefix="bunker-opencode-setup-") as temp:
            root = Path(temp)
            vault = root / "vault"
            (vault / "wiki").mkdir(parents=True)
            for skill in ("wiki", "wiki-ingest"):
                (vault / "skills" / skill).mkdir(parents=True)
                (vault / "skills" / skill / "SKILL.md").write_text(f"new {skill}\n", encoding="utf-8")

            skills_dir = root / "opencode/skills"
            (skills_dir / "wiki").mkdir(parents=True)
            (skills_dir / "wiki/user-custom.md").write_text("keep this\n", encoding="utf-8")
            config_path = root / "opencode/opencode.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            original_config = {
                "mcp": {
                    "other-server": {"type": "remote", "url": "https://example.invalid"},
                    "obsidian-vault": {"customSetting": "preserve"},
                },
                "otherSetting": True,
            }
            config_path.write_text(json.dumps(original_config), encoding="utf-8")

            env = os.environ.copy()
            env.update({
                "VAULT_DIR": str(vault),
                "SKILLS_DIR": str(skills_dir),
                "OPENCODE_CONFIG": str(config_path),
            })
            result = subprocess.run(
                ["bash", str(ROOT / "extensions/operations/bin/setup-opencode.sh")],
                env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual((skills_dir / "wiki/SKILL.md").read_text(), "new wiki\n")
            self.assertTrue((skills_dir / "wiki-ingest/SKILL.md").is_file())
            backups = list(skills_dir.glob(".wiki.backup.*/wiki/user-custom.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "keep this\n")
            updated = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["mcp"]["other-server"], original_config["mcp"]["other-server"])
            self.assertEqual(updated["mcp"]["obsidian-vault"]["customSetting"], "preserve")
            self.assertEqual(updated["otherSetting"], True)
            self.assertIn("@bitbonsai/mcpvault@0.16.0", updated["mcp"]["obsidian-vault"]["args"])
            self.assertTrue(list(config_path.parent.glob("opencode.json.backup.*")))

    def test_bunker_pulse_dry_run_does_not_create_archive_or_move_inbox(self):
        with tempfile.TemporaryDirectory(prefix="bunker-pulse-dry-run-") as temp:
            root = Path(temp)
            inbox = root / "wiki/inbox"
            inbox.mkdir(parents=True)
            memo = inbox / "bug.md"
            memo.write_text("---\ntype: bug\ncreated: 2026-10-13\n---\n\n# Reproducible bug\nDetails.\n", encoding="utf-8")
            archive = root / "wiki/archive"
            env = os.environ.copy()
            env.update({
                "BUNKER_HOME": str(root),
                "BUNKER_INBOX_DIR": str(inbox),
                "BUNKER_ARCHIVE_DIR": str(archive),
                "BUNKER_GITHUB_REPO": "example/repo",
            })
            result = subprocess.run(
                ["bash", str(ROOT / "extensions/operations/bin/bunker-pulse.sh")],
                env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("DRY RUN", result.stdout)
            self.assertTrue(memo.is_file())
            self.assertFalse(archive.exists())

    def test_bunker_pulse_apply_pushes_archive_change_on_review_branch(self):
        with tempfile.TemporaryDirectory(prefix="bunker-pulse-apply-") as temp:
            base = Path(temp)
            root = base / "repo"
            remote = base / "remote.git"
            inbox = root / "wiki/inbox"
            inbox.mkdir(parents=True)
            (root / ".gitignore").write_text("wiki/inbox/\n", encoding="utf-8")
            (root / "README.md").write_text("temporary test repository\n", encoding="utf-8")
            env = os.environ.copy()
            env.update({
                "GIT_AUTHOR_NAME": "Bunker Test",
                "GIT_AUTHOR_EMAIL": "bunker-test@example.invalid",
                "GIT_COMMITTER_NAME": "Bunker Test",
                "GIT_COMMITTER_EMAIL": "bunker-test@example.invalid",
            })

            def git(*args):
                return subprocess.run(
                    ["git", *args], cwd=root, env=env,
                    text=True, capture_output=True, check=True,
                )

            git("init", "--initial-branch=main")
            git("config", "user.name", "Bunker Test")
            git("config", "user.email", "bunker-test@example.invalid")
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            git("add", ".gitignore", "README.md")
            git("commit", "-m", "test fixture")
            git("remote", "add", "origin", str(remote))
            git("push", "--set-upstream", "origin", "main")

            memo = inbox / "bug.md"
            memo.write_text(
                "---\ntype: bug\ncreated: 2026-10-13\n---\n\n# Reproducible bug\nMinimal report.\n",
                encoding="utf-8",
            )
            fake_bin = base / "fake-bin"
            fake_bin.mkdir()
            gh_log = base / "gh.log"
            gh = fake_bin / "gh"
            gh.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$*\" >> \"$GH_LOG\"\n"
                "if [ \"$1 $2\" = 'issue create' ]; then echo https://github.invalid/issues/7; fi\n"
                "if [ \"$1 $2\" = 'pr create' ]; then echo https://github.invalid/pull/8; fi\n",
                encoding="utf-8",
            )
            gh.chmod(0o755)
            env.update({
                "PATH": f"{fake_bin}:{env['PATH']}",
                "GH_LOG": str(gh_log),
                "BUNKER_HOME": str(root),
                "BUNKER_INBOX_DIR": str(inbox),
                "BUNKER_ARCHIVE_DIR": str(root / "wiki/archive"),
                "BUNKER_GITHUB_REPO": "example/repo",
            })
            result = subprocess.run(
                ["bash", str(ROOT / "extensions/operations/bin/bunker-pulse.sh"), "--apply"],
                cwd=root, env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(git("branch", "--show-current").stdout.strip(), "main")
            remote_branch = subprocess.run(
                ["git", "--git-dir", str(remote), "branch", "--list", "fix/autopilot-*"],
                text=True, capture_output=True, check=True,
            ).stdout.strip()
            self.assertTrue(remote_branch, "a review branch should be pushed")
            archived = subprocess.run(
                ["git", "--git-dir", str(remote), "show", f"{remote_branch}:wiki/archive/bug.md"],
                text=True, capture_output=True,
            )
            self.assertEqual(archived.returncode, 0, archived.stderr)
            self.assertIn("Minimal report", archived.stdout)
            self.assertIn("issue create", gh_log.read_text(encoding="utf-8"))
            self.assertIn("pr create", gh_log.read_text(encoding="utf-8"))

    def test_setup_vault_discards_unverified_excalidraw_download(self):
        with tempfile.TemporaryDirectory(prefix="bunker-vault-setup-") as temp:
            base = Path(temp)
            vault = base / "vault"
            plugin = vault / ".obsidian/plugins/obsidian-excalidraw-plugin"
            plugin.mkdir(parents=True)
            (plugin / "manifest.json").write_text(
                json.dumps({"version": "2.22.0"}), encoding="utf-8"
            )
            fake_bin = base / "fake-bin"
            fake_bin.mkdir()
            curl = fake_bin / "curl"
            curl.write_text(
                "#!/bin/sh\n"
                "while [ $# -gt 0 ]; do\n"
                "  if [ \"$1\" = '-o' ]; then shift; printf 'unverified' > \"$1\"; exit 0; fi\n"
                "  shift\n"
                "done\nexit 2\n",
                encoding="utf-8",
            )
            curl.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"
            result = subprocess.run(
                ["bash", str(ROOT / "bin/setup-vault.sh"), str(vault)],
                env=env, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("checksum mismatch", result.stderr)
            self.assertFalse((plugin / "main.js").exists())
            self.assertEqual(list(plugin.glob("main.js.tmp.*")), [])


if __name__ == "__main__":
    unittest.main()
