#!/usr/bin/env python3
"""Regression checks for core independence from optional extensions."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalExtensionBoundaryTests(unittest.TestCase):
    def test_core_checks_do_not_probe_docker_or_n8n_configuration(self):
        check = (ROOT / "bin/bunker-check.sh").read_text()
        integrity = (ROOT / "tests/test_wiki_integrity.sh").read_text()
        self.assertNotIn("docker ", check)
        self.assertNotIn("extensions/n8n/.env", check)
        self.assertNotIn("docker ", integrity)
        self.assertNotIn("extensions/n8n/.env", integrity)

    def test_ingestion_notification_is_opt_in_and_failure_is_nonfatal(self):
        ingest = (ROOT / "bin/bunker-ingest.sh").read_text()
        self.assertIn('BUNKER_N8N_ALERTS:-0', ingest)
        self.assertIn('BUNKER_N8N_ALERTS=1', ingest)
        self.assertIn('Ingestion completed; optional n8n alert failed.', ingest)

    def test_push_notifications_are_opt_in_and_nonfatal(self):
        push = (ROOT / "extensions/operations/bin/bunker-push.sh").read_text()
        self.assertEqual(push.count('BUNKER_N8N_ALERTS:-0'), 2)
        self.assertIn('if ! "$REPO_ROOT/bin/bunker-alert.sh"', push)
        self.assertIn('falló la notificación opcional de n8n.', push)

    def test_legacy_entry_points_delegate_to_extensions(self):
        self.assertIn("extensions/n8n/bin", (ROOT / "bin/bunker-alert.sh").read_text())
        for name in (
            "audit-repo.sh", "bunker-github-setup.sh", "bunker-pulse.sh",
            "bunker-push.sh", "bunker-scaffold.sh", "setup-multi-agent.sh",
            "setup-opencode.sh",
        ):
            with self.subTest(name=name):
                shim = ROOT / "bin" / name
                impl = ROOT / "extensions/operations/bin" / name
                self.assertTrue(shim.is_file())
                self.assertTrue(impl.is_file())
                self.assertIn("extensions/operations/bin", shim.read_text())
                self.assertTrue(shim.stat().st_mode & 0o111)
                self.assertTrue(impl.stat().st_mode & 0o111)

    def test_alert_workflow_defaults_inactive_and_sender_requires_secret(self):
        import json

        workflow = json.loads((ROOT / "extensions/n8n/workflows/bunker-ultimate-alerter.json").read_text())
        sender = (ROOT / "extensions/n8n/bin/bunker-alert.sh").read_text()
        self.assertFalse(workflow["active"])
        self.assertNotIn("bunker_default_webhook_secret", sender)
        self.assertIn('AOC_WEBHOOK_SECRET must be set', sender)

    def test_n8n_configuration_is_ignored_and_workflow_assets_moved(self):
        ignore = (ROOT / "extensions/n8n/.gitignore").read_text()
        self.assertIn(".env", ignore)
        self.assertTrue((ROOT / "extensions/n8n/docker-compose.yml").is_file())
        self.assertTrue((ROOT / "extensions/n8n/workflows").is_dir())
        self.assertTrue((ROOT / "extensions/n8n/bin/check-n8n.sh").is_file())

    def test_n8n_compose_uses_safe_local_defaults(self):
        compose = (ROOT / "extensions/n8n/docker-compose.yml").read_text()
        self.assertIn('"127.0.0.1:5678:5678"', compose)
        self.assertIn("docker.n8n.io/n8nio/n8n:2.43.4", compose)
        self.assertNotIn(":latest", compose)
        self.assertIn("./workflows:/data/workflows:ro", compose)
        self.assertIn("n8n_data:/home/node/.n8n", compose)
        self.assertNotIn("n8n_data:/home/node/.n8n:ro", compose)


if __name__ == "__main__":
    unittest.main()
