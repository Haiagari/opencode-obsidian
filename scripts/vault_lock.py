#!/usr/bin/env python3
"""vault_lock.py — Multi-Writer Concurrency & Atomic File Operations for Bunker OS.

Provides robust advisory file locking (via fcntl.flock) and atomic writes
(via write-to-temp + os.replace) for safe concurrent reads/writes by multiple agents.
"""

import argparse
import contextlib
import fcntl
import os
import sys
import tempfile
import time
from typing import Generator, Optional


@contextlib.contextmanager
def file_lock(filepath: str, exclusive: bool = True, timeout: float = 10.0) -> Generator[None, None, None]:
    """Context manager for advisory file locking using fcntl.flock.
    
    Creates a `.lock` companion file in the same directory as `filepath` to avoid
    truncating or interfering with open target file handles.
    """
    abs_path = os.path.abspath(filepath)
    lock_dir = os.path.dirname(abs_path)
    os.makedirs(lock_dir, exist_ok=True)
    
    lock_file = os.path.join(lock_dir, f".{os.path.basename(abs_path)}.lock")
    flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    flags |= fcntl.LOCK_NB

    start_time = time.time()
    lock_fd = None

    try:
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_RDWR, 0o644)
        while True:
            try:
                fcntl.flock(lock_fd, flags)
                break
            except (BlockingIOError, IOError):
                if time.time() - start_time >= timeout:
                    raise TimeoutError(f"Timeout ({timeout}s) waiting to acquire lock on {filepath}")
                time.sleep(0.05)
        
        yield
    finally:
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                os.close(lock_fd)
            except Exception:
                pass


def atomic_write(filepath: str, content: str, encoding: str = 'utf-8', timeout: float = 10.0) -> None:
    """Safely writes content to `filepath` atomically under an exclusive lock.
    
    Writes to a temporary file in the same directory first, then performs `os.replace`.
    """
    abs_path = os.path.abspath(filepath)
    target_dir = os.path.dirname(abs_path)
    os.makedirs(target_dir, exist_ok=True)

    with file_lock(abs_path, exclusive=True, timeout=timeout):
        temp_fd, temp_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(abs_path)}.",
            suffix=".tmp",
            dir=target_dir
        )
        try:
            with open(temp_fd, 'w', encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, abs_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


def atomic_append(filepath: str, content: str, encoding: str = 'utf-8', timeout: float = 10.0) -> None:
    """Safely appends content to `filepath` under an exclusive lock."""
    abs_path = os.path.abspath(filepath)
    target_dir = os.path.dirname(abs_path)
    os.makedirs(target_dir, exist_ok=True)

    with file_lock(abs_path, exclusive=True, timeout=timeout):
        existing = ""
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
                existing = f.read()
        
        # Combine existing and new content
        new_content = existing + content
        
        temp_fd, temp_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(abs_path)}.",
            suffix=".tmp",
            dir=target_dir
        )
        try:
            with open(temp_fd, 'w', encoding=encoding) as f:
                f.write(new_content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, abs_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


def atomic_prepend_after_header(filepath: str, content: str, encoding: str = 'utf-8', timeout: float = 10.0) -> None:
    """Inserts content at the top of the body (after YAML frontmatter or H1 title),
    standard pattern for wiki/log.md entries."""
    abs_path = os.path.abspath(filepath)
    target_dir = os.path.dirname(abs_path)
    os.makedirs(target_dir, exist_ok=True)

    with file_lock(abs_path, exclusive=True, timeout=timeout):
        existing = ""
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding=encoding, errors='replace') as f:
                existing = f.read()

        import re
        # Check for frontmatter
        fm_match = re.match(r'^(---\s*\n.*?\n---\s*\n)', existing, re.DOTALL)
        if fm_match:
            header = fm_match.group(1)
            body = existing[len(header):]
            new_content = header + content + ("\n" if not content.endswith("\n") else "") + body
        else:
            new_content = content + ("\n" if not content.endswith("\n") else "") + existing

        temp_fd, temp_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(abs_path)}.",
            suffix=".tmp",
            dir=target_dir
        )
        try:
            with open(temp_fd, 'w', encoding=encoding) as f:
                f.write(new_content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, abs_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


def main():
    parser = argparse.ArgumentParser(description="Multi-Writer Concurrency & Atomic File Operations for Bunker OS.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # append
    p_append = subparsers.add_parser("append", help="Atomically append text to a file")
    p_append.add_argument("file", help="Target file path")
    p_append.add_argument("text", nargs="?", default=None, help="Text to append (or read from stdin)")

    # write
    p_write = subparsers.add_parser("write", help="Atomically overwrite a file")
    p_write.add_argument("file", help="Target file path")
    p_write.add_argument("text", nargs="?", default=None, help="Text to write (or read from stdin)")

    # prepend-log
    p_log = subparsers.add_parser("prepend-log", help="Atomically prepend entry to log file after frontmatter")
    p_log.add_argument("file", help="Target file path (e.g. wiki/log.md)")
    p_log.add_argument("text", nargs="?", default=None, help="Log entry text")

    args = parser.parse_args()

    content = args.text
    if content is None:
        content = sys.stdin.read()

    if args.action == "append":
        atomic_append(args.file, content)
        print(f"✅ Appended atomically to {args.file}")
    elif args.action == "write":
        atomic_write(args.file, content)
        print(f"✅ Written atomically to {args.file}")
    elif args.action == "prepend-log":
        atomic_prepend_after_header(args.file, content)
        print(f"✅ Prepended log entry atomically to {args.file}")


if __name__ == "__main__":
    main()
