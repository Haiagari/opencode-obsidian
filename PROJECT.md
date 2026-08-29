# opencode-obsidian — Bunker OS v1.4.0

This repository is an OpenCode agent environment and an Obsidian wiki vault.

**Version:** 1.4.0  
**Status:** Local-first operational knowledge system with n8n automation & multi-writer concurrency  
**Tests:** 6 suites passing (`make test` with unit + integration suites)  
**Vault path:** current repository root. Use `BUNKER_HOME` to override script resolution.

---

## Core Identity

Bunker OS is not a traditional application. It is a local-first knowledge operating system for:

- AI session continuity
- structured research (**autoresearch**, **/think** framework)
- audit evidence preservation (**SHA256 checksums**)
- project intelligence & defensive ingestion (**prompt injection sanitizer**)
- agent-guided workflow (**n8n AOC v4**, **Dead Letter Queue**, **HMAC-SHA256 webhooks**)
- SQLite FTS5 + BM25 text retrieval (**incremental hashing, zero-dependency**)
- multi-writer concurrency (**POSIX `fcntl.flock` advisory locks + atomic renames**)
- governance and decisions
- visual command center operations

---

## Architecture Layers

```text
Capture       → wiki/inbox, .raw, sanitize_ingest.py (prompt injection defense), handovers
Normalize     → _templates, skills/wiki-ingest
Concurrency   → vault_lock.py, bin/vault-lock.sh (POSIX fcntl.flock + atomic rename)
Classify      → wiki/sources, entities, concepts, projects, comparisons
Evidence      → report.zip, security-audit-report.json, evidence index (SHA256)
Governance    → BUNKER_RULES, ADR template, knowledge supply chain
Automation    → bin/ (Sync ops + HMAC signatures) + n8n (Async flows, alerts, DLQ)
Retrieval     → SQLite FTS5 Engine (fts_engine.py, WAL mode, incremental SHA256) + BM25 ranking
Testing       → 6 suites: workflows n8n, wiki integrity, scripts, YAML, retrieve, unit tests
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
- **Anti-Prompt-Injection**: Identifies and defangs adversarial override phrases (e.g. "ignore previous instructions", "system prompt override", developer mode jailbreaks).
- **Tag & Comment Neutralization**: Strips dangerous HTML tags (`<script>`, `<iframe>`, `<object>`) and malicious comments.

### 4. Webhook HMAC-SHA256 Security (`bin/bunker-alert.sh`)
- **Cryptographic Request Signing**: Signs JSON payloads sent to n8n webhooks using HMAC-SHA256 with `X-Bunker-Signature`.
- **Tamper Resistance**: Prevents unauthorized or forged alert triggering.

### 5. n8n Production Concurrency & Scaling (`automation/n8n-lab/docker-compose.yml`)
- **Concurrency Tuning**: Configured with `N8N_CONCURRENCY_PRODUCTION_LIMIT=20` to prevent memory bottlenecks.
- **Automated Data Pruning**: Configured with `EXECUTIONS_DATA_PRUNE=true`, `EXECUTIONS_DATA_MAX_AGE=168` (7 days), and `EXECUTIONS_DATA_PRUNE_MAX_COUNT=50000`.

---

## v1.4.0 Changelog Highlights

### Added
- **SQLite FTS5 Engine**: Incremental indexing and BM25 ranking via stdlib `sqlite3`.
- **Multi-Writer Locking**: POSIX `fcntl.flock` advisory locks and atomic file mutations.
- **Defensive Ingestion**: Anti-prompt-injection and payload sanitization pipeline.
- **HMAC-SHA256 Signatures**: Webhook payload security for `bunker-alert.sh`.
- **Unit Testing Suite**: `make test-unit` covering all core Python subsystems.

### Testing
- `Makefile` with 6 targets: workflows, wiki, scripts, YAML, retrieve, unit.
- Comprehensive unit test coverage in `tests/`.

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

## The n8n Orchestrator Role

n8n acts as the asynchronous execution engine and "nervous system" of the Bunker:

- **Security & Decoupling**: API keys and external integrations live in n8n, keeping bash scripts clean and secure. Scripts fire webhooks to `localhost:5678`.
- **Agentic MCP Bridge**: Gives OpenCode "hands" to trigger complex pipelines (e.g., assisted remediation) in a sandboxed manner.
- **Complex Pipelines**: Manages retries, conditional logic, and LLM evaluations via visually orchestrated flows stored in `automation/n8n-lab`.

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
| Full local check | `./bin/bunker-check.sh` |
| Full test suite | `make test` (6 suites) |
| BM25 text retrieval | `python3 scripts/retrieve.py "query"` |
| Autoresearch | `/autoresearch [topic]` via OpenCode |
| n8n status | `docker ps --filter name=n8n` |

---

## Safety Model

- Concurrency safety guaranteed via POSIX `fcntl.flock` and atomic file replacements (`vault_lock.py`).
- Untrusted ingestion sanitized against prompt injections, invisible characters, and malicious HTML (`sanitize_ingest.py`).
- Webhook alerts cryptographically signed with HMAC-SHA256 (`bunker-alert.sh`).
- Scripts resolve the vault through `BUNKER_HOME` or repository root.
- External-effect scripts default to dry-run.
- Ingest server binds to `127.0.0.1:9090` by default.
- Evidence artifacts are indexed, not modified.
- n8n secrets managed via `.env` (gitignored) + n8n credential vault.

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
