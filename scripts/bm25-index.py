#!/usr/bin/env python3
"""bm25-index.py — SQLite FTS5 + BM25 indexer CLI for Bunker OS wiki.

Build:  python3 scripts/bm25-index.py build
Query:  python3 scripts/bm25-index.py query "tu busqueda"
Status: python3 scripts/bm25-index.py status

Backing engine: scripts/fts_engine.py (SQLite FTS5 + BM25 with incremental indexing)
Database: .vault-meta/fts5/vault_fts.db
"""

import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import fts_engine

# Compatibility aliases and constants
VAULT = fts_engine.VAULT
INDEX_DIR = fts_engine.FTS_DIR
DB_FILE = fts_engine.DB_FILE


def build_index(vault_dir=None, force=False):
    """Build or incrementally update the FTS5 index."""
    res = fts_engine.build_or_update_index(vault_dir=vault_dir, force=force)
    print(f'✅ SQLite FTS5 Índice actualizado: {res["total_chunks"]} chunks en {res["total_pages"]} páginas.')
    print(f'   Nuevos/actualizados: {res["indexed_or_updated"]}, Sin cambios: {res["skipped"]}, Eliminados: {res["deleted"]}')
    return res


def query_index(query_str, top_k=10, vault_dir=None):
    """Search the FTS5 index using BM25 ranking."""
    return fts_engine.query_fts(query_str, top_k=top_k, vault_dir=vault_dir)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'

    if cmd == 'build':
        build_index()
    elif cmd == 'query':
        q = ' '.join(sys.argv[2:])
        if not q:
            print('Uso: python3 scripts/bm25-index.py query "texto"')
            sys.exit(1)
        results = query_index(q)
        print(f'Resultados para: {q}\n')
        for r in results[:5]:
            print(f'  [{r["score"]:6.3f}] {r["path"]}')
            print(f'         {r["preview"][:100]}')
            print()
    elif cmd == 'status':
        status = fts_engine.get_status()
        if status.get('exists'):
            print(f'📊 SQLite FTS5 (BM25) Index Status')
            print(f'   DB:      {status.get("db_path")}')
            print(f'   Páginas: {status.get("total_pages", "?")}')
            print(f'   Chunks:  {status.get("total_chunks", "?")}')
        else:
            print('📊 No hay índice FTS5. Ejecutá: python3 scripts/retrieve.py build')
    else:
        print('Uso: python3 scripts/bm25-index.py build|query "texto"|status')


if __name__ == '__main__':
    main()
