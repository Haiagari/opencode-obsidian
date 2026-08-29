#!/usr/bin/env python3
"""fts_engine.py — SQLite FTS5 + BM25 High-Performance Search Engine for Bunker OS.

Zero external dependencies (pure Python standard library: sqlite3, hashlib, json, os, re).
Provides incremental indexing using file mtimes and SHA-256 hashes.
"""

import hashlib
import json
import os
import re
import sqlite3
import sys
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VAULT = os.environ.get('BUNKER_HOME') or os.environ.get('VAULT_PATH') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_DIR = os.path.join(VAULT, '.vault-meta')
FTS_DIR = os.path.join(META_DIR, 'fts5')
DB_FILE = os.path.join(FTS_DIR, 'vault_fts.db')
CHUNKS_DIR = os.path.join(META_DIR, 'chunks')


def get_db_path(vault_dir: Optional[str] = None) -> str:
    v = vault_dir or VAULT
    fts_dir = os.path.join(v, '.vault-meta', 'fts5')
    os.makedirs(fts_dir, exist_ok=True)
    return os.path.join(fts_dir, 'vault_fts.db')


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database schema with metadata and FTS5 virtual tables."""
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    
    # Table tracking indexed files, modification time, and content hash
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_meta (
            path TEXT PRIMARY KEY,
            mtime REAL NOT NULL,
            sha256 TEXT NOT NULL,
            indexed_at REAL NOT NULL,
            chunk_count INTEGER NOT NULL
        );
    """)

    # FTS5 virtual table for chunk full-text search with native BM25 support
    # Using unicode61 tokenizer with diacritics removal for Spanish and English
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
            path UNINDEXED,
            chunk_index UNINDEXED,
            total_chunks UNINDEXED,
            title,
            content,
            tokenize = 'unicode61 remove_diacritics 2'
        );
    """)
    conn.commit()


def compute_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric terms."""
    text = re.sub(r'[^a-záéíóúñüA-ZÁÉÍÓÚÑÜ0-9\s-]', ' ', text.lower())
    return [t for t in text.split() if len(t) > 1]


def extract_title(text: str, filepath: str) -> str:
    # Try frontmatter title
    fm_match = re.search(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if line.strip().startswith('title:'):
                return line.split('title:', 1)[1].strip().strip('\'"')
    
    # Try first H1
    h1_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    return Path(filepath).stem


def chunk_page(filepath: str) -> Tuple[str, List[str]]:
    """Splits a markdown page into chunks (~500 tokens each). Returns (title, chunks)."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    title = extract_title(text, filepath)

    # Strip frontmatter for chunk content
    body = re.sub(r'^---.*?---\s*', '', text, flags=re.DOTALL)

    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
    chunks = []
    current: List[str] = []
    current_len = 0

    for p in paragraphs:
        tokens = len(tokenize(p))
        if current_len + tokens > 500 and current:
            chunks.append('\n\n'.join(current))
            current = []
            current_len = 0
        current.append(p)
        current_len += tokens

    if current:
        chunks.append('\n\n'.join(current))

    if not chunks:
        chunks = [body[:2000]] if body.strip() else [title]

    return title, chunks


def build_or_update_index(vault_dir: Optional[str] = None, force: bool = False) -> Dict:
    """Incrementally indexes markdown files in wiki/ using SQLite FTS5."""
    v = vault_dir or VAULT
    db_path = get_db_path(v)
    os.makedirs(os.path.join(v, '.vault-meta', 'chunks'), exist_ok=True)

    conn = sqlite3.connect(db_path)
    init_db(conn)

    files = glob(os.path.join(v, 'wiki', '**', '*.md'), recursive=True)
    files = [f for f in files if '/meta/' not in f and f.endswith('.md')]

    # Get currently indexed files
    cur = conn.cursor()
    cur.execute("SELECT path, mtime, sha256 FROM file_meta")
    existing_meta = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    active_paths = set()
    added_or_updated = 0
    skipped = 0

    for filepath in files:
        rel = os.path.relpath(filepath, v)
        active_paths.add(rel)
        mtime = os.path.getmtime(filepath)

        # Check if changed
        if not force and rel in existing_meta:
            prev_mtime, prev_hash = existing_meta[rel]
            if abs(mtime - prev_mtime) < 1e-4:
                skipped += 1
                continue
            curr_hash = compute_file_hash(filepath)
            if curr_hash == prev_hash:
                # Update mtime only
                conn.execute("UPDATE file_meta SET mtime = ? WHERE path = ?", (mtime, rel))
                skipped += 1
                continue
        else:
            curr_hash = compute_file_hash(filepath)

        # File is new or changed: index it
        title, chunks = chunk_page(filepath)

        # Remove old chunks for this file from FTS
        conn.execute("DELETE FROM wiki_fts WHERE path = ?", (rel,))

        # Insert new chunks
        for ci, chunk in enumerate(chunks):
            conn.execute(
                "INSERT INTO wiki_fts(path, chunk_index, total_chunks, title, content) VALUES (?, ?, ?, ?, ?)",
                (rel, ci, len(chunks), title, chunk)
            )

        import time
        now = time.time()
        conn.execute("""
            INSERT INTO file_meta (path, mtime, sha256, indexed_at, chunk_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                mtime = excluded.mtime,
                sha256 = excluded.sha256,
                indexed_at = excluded.indexed_at,
                chunk_count = excluded.chunk_count;
        """, (rel, mtime, curr_hash, now, len(chunks)))

        added_or_updated += 1

    # Cleanup deleted files
    deleted = 0
    for stale_path in set(existing_meta.keys()) - active_paths:
        conn.execute("DELETE FROM wiki_fts WHERE path = ?", (stale_path,))
        conn.execute("DELETE FROM file_meta WHERE path = ?", (stale_path,))
        deleted += 1

    conn.commit()

    # Get index stats
    cur.execute("SELECT COUNT(*) FROM file_meta")
    total_pages = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM wiki_fts")
    total_chunks = cur.fetchone()[0]

    conn.close()

    return {
        'status': 'ok',
        'total_pages': total_pages,
        'total_chunks': total_chunks,
        'indexed_or_updated': added_or_updated,
        'skipped': skipped,
        'deleted': deleted,
        'db_path': db_path
    }


def sanitize_fts5_query(query_str: str) -> str:
    """Sanitizes user input for FTS5 queries, supporting terms and phrases safely."""
    # Strip dangerous FTS5 operators and punctuation
    cleaned = re.sub(r'[*"\'():^{}+~]', ' ', query_str)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    if not tokens:
        return ""
    # Search for tokens with prefix matching for natural auto-complete/partial match
    # Format: "tok1"* "tok2"*
    return ' '.join(f'"{tok}"*' for tok in tokens)


def query_fts(query_str: str, top_k: int = 10, vault_dir: Optional[str] = None) -> List[Dict]:
    """Queries the SQLite FTS5 index using native BM25 ranking."""
    v = vault_dir or VAULT
    db_path = get_db_path(v)

    if not os.path.exists(db_path):
        return []

    fts_query = sanitize_fts5_query(query_str)
    if not fts_query:
        return []

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # bm25(wiki_fts) returns a negative score in SQLite (lower is better, e.g. -5.2 is better match than -1.1)
        # We negate it so higher positive score is better ranking
        query_sql = """
            SELECT path, chunk_index, total_chunks, title, content, -bm25(wiki_fts) as score
            FROM wiki_fts
            WHERE wiki_fts MATCH ?
            ORDER BY score DESC
            LIMIT ?;
        """
        cur.execute(query_sql, (fts_query, top_k))
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        # Fallback if complex MATCH expression fails
        rows = []
    finally:
        conn.close()

    results = []
    for r in rows:
        path, ci, total_c, title, content, score = r
        preview = content[:200].replace('\n', ' ')
        results.append({
            'doc_id': f"{path}#chunk-{ci}",
            'score': round(float(score), 4),
            'path': path,
            'title': title,
            'chunk': int(ci),
            'total_chunks': int(total_c),
            'preview': preview
        })

    return results


def get_status(vault_dir: Optional[str] = None) -> Dict:
    v = vault_dir or VAULT
    db_path = get_db_path(v)
    if not os.path.exists(db_path):
        return {'exists': False, 'total_pages': 0, 'total_chunks': 0}

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM file_meta")
        total_pages = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM wiki_fts")
        total_chunks = cur.fetchone()[0]
        return {
            'exists': True,
            'db_path': db_path,
            'total_pages': total_pages,
            'total_chunks': total_chunks
        }
    except sqlite3.OperationalError:
        return {'exists': False, 'total_pages': 0, 'total_chunks': 0}
    finally:
        conn.close()
