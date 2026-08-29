#!/usr/bin/env python3
"""test_vault_lock.py — Unit tests for concurrent file locking and atomic operations."""

import concurrent.futures
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys_path = os.path.join(REPO_ROOT, 'scripts')
import sys
if sys_path not in sys_path:
    sys.path.insert(0, sys_path)

import vault_lock


class TestVaultLock(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bunker_test_lock_")
        self.target_file = os.path.join(self.test_dir, "shared_log.md")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_atomic_write(self):
        content = "# Title\nInitial content\n"
        vault_lock.atomic_write(self.target_file, content)
        
        with open(self.target_file, 'r', encoding='utf-8') as f:
            read_back = f.read()
        self.assertEqual(read_back, content)

    def test_atomic_append(self):
        vault_lock.atomic_write(self.target_file, "Line 1\n")
        vault_lock.atomic_append(self.target_file, "Line 2\n")
        
        with open(self.target_file, 'r', encoding='utf-8') as f:
            read_back = f.read()
        self.assertEqual(read_back, "Line 1\nLine 2\n")

    def test_atomic_prepend_after_header(self):
        initial = """---
title: "Log"
updated: 2026-08-29
---
## 2026-08-28 Old Entry
- First entry
"""
        vault_lock.atomic_write(self.target_file, initial)
        
        new_entry = "## 2026-08-29 New Entry\n- Second entry\n"
        vault_lock.atomic_prepend_after_header(self.target_file, new_entry)
        
        with open(self.target_file, 'r', encoding='utf-8') as f:
            read_back = f.read()
            
        expected = """---
title: "Log"
updated: 2026-08-29
---
## 2026-08-29 New Entry
- Second entry
## 2026-08-28 Old Entry
- First entry
"""
        self.assertEqual(read_back, expected)

    def test_concurrent_multi_writer_appends(self):
        # 10 workers appending concurrently
        vault_lock.atomic_write(self.target_file, "")
        num_workers = 10
        appends_per_worker = 10

        def append_task(worker_id):
            for i in range(appends_per_worker):
                vault_lock.atomic_append(self.target_file, f"worker-{worker_id}-item-{i}\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(append_task, w) for w in range(num_workers)]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        with open(self.target_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        self.assertEqual(len(lines), num_workers * appends_per_worker)


if __name__ == '__main__':
    unittest.main()
