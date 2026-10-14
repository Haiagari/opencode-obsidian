---
name: wiki-retrieve
description: >
  BM25 text retrieval for Bunker OS. Fast local keyword search over
  the wiki vault. No embeddings, no LLM, no external services —
  OpenCode reads the results and synthesizes answers.
  Triggers on: "/retrieve", "retrieve", "text search",
  "search chunks", "chunk search", "vault search",
  "búsqueda", "find in vault", "BM25".
---

# wiki-retrieve: BM25 Text Retrieval for Bunker OS

Search the wiki vault using BM25 — a pure text-based ranking algorithm.
Fast, deterministic, zero external dependencies. OpenCode reads the
ranked chunks and synthesizes the final answer.

**No embeddings. No LLM calls. No ollama. No API keys.**
The agent (OpenCode) is the only intelligence in the loop.

---

## Architecture

The CLI `scripts/retrieve.py` calls `scripts/fts_engine.py`, which indexes
eligible wiki Markdown in SQLite FTS5 and returns passages ranked with native
BM25. OpenCode reads the selected notes and synthesizes an answer.

The index is incremental, derived, and rebuildable. `meta/` and `archive/`
descendants are excluded; inbox Markdown is eligible and still needs review.
See [Architecture](../../docs/architecture.md#retrieval-internals) for storage,
selection, chunking, and ranking limits.

The index is built offline from wiki Markdown files. Each page is
split into chunks (~500 tokens each) at paragraph boundaries. The
BM25 algorithm ranks chunks by term frequency/inverse document
frequency — the same foundation Elasticsearch uses.

---

## Feature Detection

Before using retrieve, check if the index exists:

```bash
python3 scripts/retrieve.py build   # build/update index
python3 scripts/retrieve.py status  # check status
```

If the index doesn't exist, fall back to `obsidian-vault_search_notes`
or the legacy hot → index → drill read order.

---

## Usage

| Operation | Command | Description |
|-----------|---------|-------------|
| **Search** | `python3 scripts/retrieve.py "query" --top 5` | BM25 ranked results |
| **Build** | `python3 scripts/retrieve.py build` | Build or incrementally update the index |
| **Status** | `python3 scripts/retrieve.py status` | Index stats |

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--top N` | `5` | Max results to return |

---

## Integration with OpenCode Queries

When you receive a query:

1. **First**: run `python3 scripts/retrieve.py status` to verify the index exists
2. **If it exists**: run `python3 scripts/retrieve.py "consulta" --top 5`
3. **Read the results**: each result has `path` (file path), `score` (BM25 relevance), and `preview` (text excerpt)
4. **Read the pages**: use `obsidian-vault_read_note` on the relevant paths
5. **Synthesize**: answer the user with citations to the wiki sources

If the index doesn't exist or the script fails:
- Use `obsidian-vault_search_notes` with the query
- Or read `wiki/hot.md` + `wiki/index.md` + relevant pages (legacy path)

---

## Index Maintenance

Rebuild the index after adding or modifying wiki pages:

```bash
# After ingesting new sources:
python3 scripts/retrieve.py build

# Verify status:
python3 scripts/retrieve.py status
```

The build is incremental-aware but rebuilds fully from source files.
It's fast (pure Python, no network calls). Run it before heavy
search sessions.

---

## Available Tools

| Tool | Purpose |
|------|---------|
| `python3 scripts/retrieve.py build` | Build/update BM25 index |
| `python3 scripts/retrieve.py status` | Index status and stats |
| `python3 scripts/retrieve.py "query" --top N` | BM25 text search |
| `obsidian-vault_search_notes` | Fallback FTS search (when BM25 not available) |
| `obsidian-vault_read_note` | Read wiki pages from search results |

---

## Why BM25-only?

- **Zero dependencies**: stdlib Python, no numpy, no ollama, no API keys
- **Fast**: builds and queries in under a second for typical vaults
- **Deterministic**: same query = same results, every time
- **OpenCode does the synthesis**: the agent reads the chunks and
  applies its own model (Anthropic, OpenAI, local — whatever the user
  configured in OpenCode) to understand and answer
- **Portable**: works in CI, air-gapped environments, anywhere with
  Python 3.10+
