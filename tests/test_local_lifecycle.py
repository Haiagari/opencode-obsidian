"""End-to-end coverage for the local capture, archive, index, commit, and publish flow."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fts_engine


class LocalLifecycleTests(unittest.TestCase):
    def test_capture_write_archive_index_commit_and_local_publish(self):
        with tempfile.TemporaryDirectory(prefix="bunker-lifecycle-") as temp:
            base = Path(temp)
            repo = base / "vault"
            remote = base / "remote.git"
            for relative in (
                "bin", "scripts", "extensions/operations/bin", "wiki/meta",
                "wiki/concepts", "wiki/archive",
            ):
                (repo / relative).mkdir(parents=True, exist_ok=True)
            for relative in (
                "bin/bunker-ingest.sh", "bin/bunker-push.sh",
                "scripts/sanitize_ingest.py", "scripts/vault_lock.py",
                "extensions/operations/bin/bunker-push.sh",
            ):
                destination = repo / relative
                shutil.copy2(ROOT / relative, destination)

            (repo / ".gitignore").write_text(
                "/.raw/\n/.vault-meta/\nwiki/**/.*.lock\nwiki/inbox/\n", encoding="utf-8"
            )
            (repo / "wiki/index.md").write_text("# Index\n", encoding="utf-8")
            (repo / "wiki/log.md").write_text("# Log\n", encoding="utf-8")
            (repo / "wiki/meta/archive").mkdir(parents=True, exist_ok=True)

            env = os.environ.copy()
            env.update({
                "GIT_AUTHOR_NAME": "Bunker Test",
                "GIT_AUTHOR_EMAIL": "bunker-test@example.invalid",
                "GIT_COMMITTER_NAME": "Bunker Test",
                "GIT_COMMITTER_EMAIL": "bunker-test@example.invalid",
                "BUNKER_HOME": str(repo),
                "BUNKER_N8N_ALERTS": "0",
            })

            def git(*args):
                return subprocess.run(
                    ["git", *args], cwd=repo, env=env,
                    text=True, capture_output=True, check=True,
                )

            git("init", "--initial-branch=main")
            git("config", "user.name", "Bunker Test")
            git("config", "user.email", "bunker-test@example.invalid")
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            git("add", ".gitignore", "wiki")
            git("commit", "-m", "test fixture")
            git("remote", "add", "origin", str(remote))
            git("push", "--set-upstream", "origin", "main")

            source = base / "research.md"
            source.write_text(
                "Local pipeline sentinelxylophone from sanitized research.\n", encoding="utf-8"
            )
            capture = subprocess.run(
                ["bash", str(repo / "bin/bunker-ingest.sh"), str(source)],
                cwd=repo, env=env, text=True, capture_output=True,
            )
            self.assertEqual(capture.returncode, 0, capture.stderr)
            staged = repo / ".raw/research.md"
            self.assertTrue(staged.is_file())

            note = repo / "wiki/concepts/lifecycle.md"
            note_content = "---\ntype: concept\ntitle: Lifecycle test\n---\n\n" + staged.read_text(encoding="utf-8")
            subprocess.run(
                ["python3", str(repo / "scripts/vault_lock.py"), "write", str(note)],
                cwd=repo, env=env, input=note_content, text=True, capture_output=True, check=True,
            )
            subprocess.run(
                ["python3", str(repo / "scripts/vault_lock.py"), "write", "wiki/index.md"],
                cwd=repo, env=env, input="# Index\n- [[Lifecycle test]]\n", text=True,
                capture_output=True, check=True,
            )
            subprocess.run(
                ["python3", str(repo / "scripts/vault_lock.py"), "prepend-log", "wiki/log.md"],
                cwd=repo, env=env, input="- Captured and filed lifecycle test.\n", text=True,
                capture_output=True, check=True,
            )

            indexed = fts_engine.build_or_update_index(vault_dir=str(repo))
            self.assertGreater(indexed["total_pages"], 0)
            results = fts_engine.query_fts("sentinelxylophone", vault_dir=str(repo))
            self.assertTrue(any(result["path"] == "wiki/concepts/lifecycle.md" for result in results))

            archive = repo / "wiki/archive/lifecycle.md"
            note.replace(archive)
            (repo / "wiki/index.md").write_text("# Index\n- Archived: [[lifecycle]]\n", encoding="utf-8")
            archive_index = fts_engine.build_or_update_index(vault_dir=str(repo))
            self.assertGreaterEqual(archive_index["deleted"], 1)
            self.assertFalse(fts_engine.query_fts("sentinelxylophone", vault_dir=str(repo)))

            publish = subprocess.run(
                ["bash", str(repo / "bin/bunker-push.sh"), "test complete local lifecycle"],
                cwd=repo, env=env, text=True, capture_output=True,
            )
            self.assertEqual(publish.returncode, 0, publish.stderr + publish.stdout)
            published = subprocess.run(
                ["git", "--git-dir", str(remote), "show", "main:wiki/archive/lifecycle.md"],
                text=True, capture_output=True,
            )
            self.assertEqual(published.returncode, 0, published.stderr)
            private_source = subprocess.run(
                ["git", "--git-dir", str(remote), "cat-file", "-e", "main:.raw/research.md"],
                text=True, capture_output=True,
            )
            self.assertNotEqual(private_source.returncode, 0, "raw source must stay out of published Git tree")
            lock_artifact = subprocess.run(
                ["git", "--git-dir", str(remote), "cat-file", "-e", "main:wiki/.log.md.lock"],
                text=True, capture_output=True,
            )
            self.assertNotEqual(lock_artifact.returncode, 0, "runtime lock files must stay out of published Git tree")


if __name__ == "__main__":
    unittest.main()
