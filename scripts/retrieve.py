#!/usr/bin/env python3
"""retrieve.py — SQLite FTS5 + BM25 text retrieval for Bunker OS.

High-performance native SQLite FTS5 BM25 search. Zero external dependencies.
OpenCode (the agent) reads the ranked results and synthesizes answers.

Pipeline:
  query → SQLite FTS5 BM25 → ranked results

Uso:
  python3 scripts/retrieve.py "consulta" --top 5
  python3 scripts/retrieve.py build
  python3 scripts/retrieve.py status

Deps: Python 3.10+ (stdlib only — sqlite3 FTS5, no external packages required)
"""

import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import fts_engine

# Vault path: env var overrides default (repo root)
DEFAULT_VAULT = os.path.dirname(SCRIPTS)
VAULT_PATH = os.environ.get('BUNKER_HOME') or os.environ.get('VAULT_PATH') or DEFAULT_VAULT


def build_index():
    return fts_engine.build_or_update_index(vault_dir=VAULT_PATH)


def query_index(query_str, top_k=5):
    return fts_engine.query_fts(query_str, top_k=top_k, vault_dir=VAULT_PATH)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print('Uso: python3 scripts/retrieve.py "query" [--top N]')
        print('      python3 scripts/retrieve.py build  (construir/actualizar índice incremental FTS5)')
        print('      python3 scripts/retrieve.py status (estado del índice SQLite FTS5)')
        print('')
        print('Sin dependencias externas. SQLite FTS5 + BM25. OpenCode sintetiza.')
        sys.exit(0)

    if args[0] == 'build':
        res = build_index()
        print(f'✅ SQLite FTS5 Índice actualizado: {res["total_chunks"]} chunks en {res["total_pages"]} páginas.')
        print(f'   Nuevos/actualizados: {res["indexed_or_updated"]}, Sin cambios: {res["skipped"]}, Eliminados: {res["deleted"]}')
        return
    elif args[0] == 'status':
        status = fts_engine.get_status(vault_dir=VAULT_PATH)
        if status.get('exists'):
            print(f'📊 SQLite FTS5 (BM25) Index Status')
            print(f'   DB:      {status.get("db_path")}')
            print(f'   Páginas: {status.get("total_pages", "?")}')
            print(f'   Chunks:  {status.get("total_chunks", "?")}')
        else:
            print('📊 No hay índice FTS5. Ejecutá: python3 scripts/retrieve.py build')
            sys.exit(1)
        return

    query = args[0]
    if not query.strip():
        print('Error: la consulta no puede estar vacía', file=sys.stderr)
        sys.exit(1)

    top_k = 5

    for i, a in enumerate(args[1:], 1):
        if a == '--top' and i + 1 < len(args):
            try:
                top_k = int(args[i + 1])
            except ValueError:
                print(f'Error: --top debe ser un número entero, no "{args[i + 1]}"', file=sys.stderr)
                sys.exit(1)

    candidates = query_index(query, top_k=top_k)
    if not candidates:
        print(json.dumps({'query': query, 'strategy': 'sqlite_fts5_bm25', 'top_k': 0, 'candidates': []},
                         ensure_ascii=False, indent=2))
        return

    results = candidates[:top_k]
    output = {
        'query': query,
        'strategy': 'sqlite_fts5_bm25',
        'top_k': len(results),
        'candidates': results
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
