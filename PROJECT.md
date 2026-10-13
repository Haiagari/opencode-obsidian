# opencode-obsidian — Bunker OS v1.4.0

Bunker OS is a local-first personal knowledge workflow built around an Obsidian vault: capture information, sanitize and organize it, retrieve it, and preserve context and decisions over time. The vault is the source of truth; scripts and agent tools support the workflow, while n8n is optional. See [Product Direction](docs/product-direction.md).

**Version:** 1.4.0  
**Status:** Personal knowledge vault and local workflow tooling; optional automation has varying maturity
**Test tooling:** `make test-core` runs Docker-independent core checks; `make test-extensions` validates optional n8n assets, and `make test` runs both.
**Vault path:** current repository root. Use `BUNKER_HOME` to override script resolution.

---

## Product Identity and Workflow

The primary audience is an individual using the vault day to day. The core loop is:

1. Capture sources, research, conversations, and decisions.
2. Sanitize and organize useful material as linked vault notes.
3. Retrieve relevant notes through local text-search tools and focused queries.
4. Preserve active context and decisions in durable notes, the index, and handovers.

Current supporting capabilities include source-ingestion and sanitization scripts, bundled knowledge-workflow skills, SQLite FTS5/BM25 retrieval, vault integrity checks, and file-locking utilities. Agent tooling supports the workflow but is not required to make the Markdown vault useful. n8n workflows are an optional extension and have differing activation and maturity; they are not the primary product identity.

For current capabilities, scope boundaries, and staged priorities, see [Product Direction](docs/product-direction.md).

---

## Architecture Layers

```text
Capture       → wiki/inbox, .raw, sanitize_ingest.py (best-effort text sanitization), handovers
Normalize     → _templates, skills/wiki-ingest
Concurrency   → vault_lock.py, bin/vault-lock.sh (POSIX fcntl.flock + atomic rename)
Classify      → wiki/sources, entities, concepts, projects, comparisons
Evidence      → optional report artifacts and evidence index (SHA256)
Governance    → BUNKER_RULES, ADR template, knowledge supply chain
Optional ops  → extensions/operations/ (legacy bin/ shims); n8n in extensions/n8n/ (not core workflow)
Retrieval     → SQLite FTS5 Engine (fts_engine.py, WAL mode, incremental SHA256) + BM25 ranking
Testing       → make test-core (Docker-independent) + make test-extensions; make test runs both
Agent Runtime → agents, commands, skills (13), hooks (7)
Visualization → dashboard, canvases, Obsidian graph
```

---

## Subsystems & Capabilities (v1.4.0)

### 1. SQLite FTS5 Search Engine (`scripts/fts_engine.py`)
- **Zero External Dependencies**: Pure Python standard library (`sqlite3`, `hashlib`, `json`).
- **Incremental Indexation**: Tracks document modification times (`mtime`) and content SHA-256 hashes in `file_meta` table. Only changed/new files trigger chunk extraction and re-indexing.
- **BM25 Ranking**: Uses SQLite FTS5 native `-bm25(wiki_fts)` algorithm.
- **Multilingual Support**: `unicode61 remove_diacritics 2` tokenizer for accurate queries in English and Spanish.

### 2. Multi-Writer Concurrency & Atomic File Operations (`scripts/vault_lock.py`, `bin/vault-lock.sh`)
- **POSIX Advisory File Locking**: `fcntl.flock` with timeout-bounded retry loops and companion `.lock` files.
- **Atomic Writes**: Writes to temporary files and commits via atomic `os.replace` to prevent corrupted or partial writes.
- **Concurrency-Safe Operations**: Supports `append`, `write`, and `prepend-log` operations for shared resources like `wiki/hot.md` and `wiki/log.md`.

### 3. Defensive Ingestion Pipeline (`scripts/sanitize_ingest.py`)
- **Zero-Width Token Stripping**: Cleans invisible and zero-width unicode characters used in token smuggling.
- **Best-Effort Input Hygiene**: Defangs a limited set of override phrases and strips selected invisible characters and HTML; sanitized output remains untrusted.
- **Tag & Comment Neutralization**: Strips dangerous HTML tags (`<script>`, `<iframe>`, `<object>`) and malicious comments.

### 4. Optional webhook alert signing (`extensions/n8n/bin/bunker-alert.sh`; compatibility: `bin/bunker-alert.sh`)
- The script generates an HMAC-SHA256 signature in the outgoing alert header. The reviewed alerter does not validate that signature; this is not end-to-end webhook verification or a security guarantee.

### 5. n8n configuration
- The compose configuration includes concurrency and execution-data pruning settings. These configuration values alone do not establish production readiness. n8n is optional and some documented workflows are inactive or experimental.

---

## v1.4.0 Changelog Highlights

### Added
- **SQLite FTS5 Engine**: Incremental indexing and BM25 ranking via stdlib `sqlite3`.
- **Multi-Writer Locking**: POSIX `fcntl.flock` advisory locks and atomic file mutations.
- **Defensive Ingestion**: Best-effort text sanitization with explicit limits; sanitized content remains untrusted.
- **HMAC-SHA256 header generation**: `bunker-alert.sh` adds a signature to outgoing webhook requests; the reviewed alerter does not validate it, so this is not end-to-end webhook verification.
- **Unit Testing Suite**: `make test-unit` adds tests for selected Python subsystems.

### Testing
- `Makefile` separates core checks from optional n8n workflow and compose validation.
- Tests cover selected behaviors in the listed subsystems; suite presence does not imply complete coverage or passing results.

### Infrastructure
- docker-compose: `N8N_CONCURRENCY_PRODUCTION_LIMIT=20`, pruning and security limits.
- Author and identity unified to `Haiagari`.

---

## Skills (13 repo + 6 ECC global)

### Bundled in this repo

| Skill | Description |
|-------|-------------|
| `autoresearch` | 3-round autonomous web research |
| `wiki-retrieve` | SQLite FTS5 & BM25 text retrieval (stdlib Python) |
| `think` | 10-principle framework for decisions |
| `wiki-ingest` | Ingest sources into wiki |
| `wiki-query` | Query the wiki |
| `wiki-lint` | Vault health check |
| `save` | Save conversation as note |
| `wiki` | Wiki orchestrator |
| `canvas` | Visual canvas layer |
| `defuddle` | Web extraction wrapper |
| `evidence-index` | Evidence indexing |
| `obsidian-bases` | Bases schema reference |
| `obsidian-markdown` | OFM syntax reference |

### Provided by ECC global config

| Skill | Description |
|-------|-------------|
| `code-review` | Code quality review |
| `security-review` | Security review |
| `infra-design` | Infrastructure design |
| `tdd-workflow` | TDD red-green-refactor |
| `verification-loop` | Build/test/lint pre-PR |
| `work-unit-commits` | Organized commits |

---

## Optional n8n Extension

n8n can support asynchronous workflows and integrations, but it is not required for capturing, organizing, or retrieving vault knowledge. The extension and setup guidance live in `extensions/n8n/` and `docs/N8N-SETUP.md`; workflow activation varies, so verify a workflow before relying on it. Do not interpret credential placement or configuration settings as proof of complete security, sandboxing, or enterprise readiness. Core ingestion alerts are opt-in with `BUNKER_N8N_ALERTS=1`.

---

## Operational Entry Points

| Purpose | File/Command |
|---|---|
| Active context | `wiki/hot.md` |
| Main map | `wiki/index.md` |
| Dashboard | `wiki/meta/dashboard.md` |
| Agent queue | `wiki/meta/agent-queue.md` |
| Integrity scan | `./bin/wiki-integrity.sh` |
| Evidence indexing | `./bin/evidence-index.sh` |
| Atomic lock & write | `./bin/vault-lock.sh append wiki/log.md "entry"` |
| Signed webhook alert | `./bin/bunker-alert.sh target info "msg"` |
| SQLite FTS5 search | `python3 scripts/fts_engine.py "query"` |
| Pre-ingest sanitizer | `python3 scripts/sanitize_ingest.py [file]` |
| Optional local HTTP capture | `docs/local-ingest-api.md` (loopback only, token required) |
| Full local check | `./bin/bunker-check.sh` |
| Core checks | `make test-core` (no Docker/n8n config) |
| Full test suite | `make test` (core + optional extension validation) |
| BM25 text retrieval | `python3 scripts/retrieve.py "query"` |
| Autoresearch | `/autoresearch [topic]` via OpenCode |
| Optional n8n status | `extensions/n8n/bin/check-n8n.sh` |

---

## Safeguards and Limits

- `vault_lock.py` uses POSIX `fcntl.flock` and atomic replacement for supported file operations; this does not guarantee safety for every writer or environment.
- `sanitize_ingest.py` targets specified prompt-injection markers, invisible characters, and selected HTML. Sanitization is a defense-in-depth aid, not complete protection against malicious content.
- `bunker-alert.sh` generates an HMAC-SHA256 signature; the reviewed alerter does not validate it.
- Scripts resolve the vault through `BUNKER_HOME` or the repository root. Verify individual script defaults and effects before use.
- n8n configuration and secret storage do not constitute a complete security review or enterprise-readiness claim.

---

## Cross-Project Access

To use this brain from another project, point that project to the vault root and follow the read order:

1. `wiki/hot.md`
2. latest `wiki/meta/handovers/*`
3. `wiki/index.md`
4. specific notes only when needed

Avoid hard-coded absolute paths. Use `BUNKER_HOME` or project-local configuration.

---

MIT License © 2026 | **Haiagari**
