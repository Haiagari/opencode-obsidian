#!/usr/bin/env python3
"""test_fts_engine.py — Unit tests for SQLite FTS5 BM25 search engine and incremental indexing."""

import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys_path = os.path.join(REPO_ROOT, 'scripts')
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

import fts_engine


class TestFTSEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bunker_test_fts_")
        self.wiki_dir = os.path.join(self.test_dir, 'wiki')
        os.makedirs(self.wiki_dir, exist_ok=True)

        # Create test notes
        self.note1 = os.path.join(self.wiki_dir, 'architecture.md')
        with open(self.note1, 'w', encoding='utf-8') as f:
            f.write("""---
title: "Bunker Architecture"
tags: [security, core]
---
# Bunker Architecture Overview

The Bunker OS uses SQLite FTS5 for ultra-fast BM25 lexical search.
It stores indexed markdown chunks with zero third-party dependencies.
""")

        self.note2 = os.path.join(self.wiki_dir, 'security.md')
        with open(self.note2, 'w', encoding='utf-8') as f:
            f.write("""---
title: "Security Shield"
---
# Defensive Security Mechanisms

HMAC-SHA256 signatures validate incoming alerts and webhooks.
Defensive sanitization strips prompt injections and adversarial directives.
""")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_build_and_query(self):
        res = fts_engine.build_or_update_index(vault_dir=self.test_dir, force=True)
        self.assertEqual(res['total_pages'], 2)
        self.assertGreaterEqual(res['total_chunks'], 2)
        self.assertEqual(res['indexed_or_updated'], 2)

        # Test search query
        results = fts_engine.query_fts("SQLite FTS5", top_k=5, vault_dir=self.test_dir)
        self.assertTrue(len(results) > 0)
        self.assertIn("architecture.md", results[0]['path'])
        self.assertGreaterEqual(results[0]['score'], 0)

        # Test search query for note2
        results2 = fts_engine.query_fts("HMAC-SHA256 signatures", top_k=5, vault_dir=self.test_dir)
        self.assertTrue(len(results2) > 0)
        self.assertIn("security.md", results2[0]['path'])

    def test_incremental_indexing(self):
        # Initial build
        fts_engine.build_or_update_index(vault_dir=self.test_dir, force=True)

        # Second build without changes -> 0 updated, 2 skipped
        res2 = fts_engine.build_or_update_index(vault_dir=self.test_dir, force=False)
        self.assertEqual(res2['indexed_or_updated'], 0)
        self.assertEqual(res2['skipped'], 2)

        # Modify note1
        time.sleep(0.05)
        with open(self.note1, 'a', encoding='utf-8') as f:
            f.write("\nNew section: High-throughput async concurrency.\n")

        res3 = fts_engine.build_or_update_index(vault_dir=self.test_dir, force=False)
        self.assertEqual(res3['indexed_or_updated'], 1)
        self.assertEqual(res3['skipped'], 1)

        # Query newly added term
        results = fts_engine.query_fts("async concurrency", top_k=5, vault_dir=self.test_dir)
        self.assertTrue(len(results) > 0)
        self.assertIn("architecture.md", results[0]['path'])

    def test_content_change_with_preserved_mtime_is_reindexed(self):
        fts_engine.build_or_update_index(vault_dir=self.test_dir, force=True)
        original_stat = os.stat(self.note1)

        with open(self.note1, 'w', encoding='utf-8') as f:
            f.write("# Preserved timestamp regression\n\nKuroIndexSentinelUniqueTerm\n")
        os.utime(self.note1, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))

        result = fts_engine.build_or_update_index(vault_dir=self.test_dir, force=False)
        self.assertEqual(result['indexed_or_updated'], 1)
        self.assertEqual(result['skipped'], 1)

        results = fts_engine.query_fts(
            "KuroIndexSentinelUniqueTerm", top_k=5, vault_dir=self.test_dir
        )
        self.assertTrue(results)
        self.assertIn("architecture.md", results[0]['path'])

    def test_status(self):
        fts_engine.build_or_update_index(vault_dir=self.test_dir, force=True)
        status = fts_engine.get_status(vault_dir=self.test_dir)
        self.assertTrue(status['exists'])
        self.assertEqual(status['total_pages'], 2)

    def test_archived_notes_are_removed_from_search_index(self):
        active_note = Path(self.wiki_dir) / 'old-security-note.md'
        archive_note = Path(self.wiki_dir) / 'archive' / 'old-security-note.md'
        archive_note.parent.mkdir(parents=True)
        active_note.write_text(
            '---\ntitle: Old note\n---\n\nArchiveOnlyKuroSentinel\n', encoding='utf-8'
        )
        fts_engine.build_or_update_index(vault_dir=self.test_dir, force=True)
        self.assertTrue(fts_engine.query_fts('ArchiveOnlyKuroSentinel', vault_dir=self.test_dir))

        active_note.rename(archive_note)
        result = fts_engine.build_or_update_index(vault_dir=self.test_dir, force=False)
        self.assertEqual(result['deleted'], 1)
        self.assertFalse(fts_engine.query_fts('ArchiveOnlyKuroSentinel', vault_dir=self.test_dir))


if __name__ == '__main__':
    unittest.main()
