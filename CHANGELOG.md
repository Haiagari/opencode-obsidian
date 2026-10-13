# Changelog

## Unreleased — Optional Extension Boundary

### Changed
- Moved n8n/AOC assets to `extensions/n8n/` and host/repository utilities to `extensions/operations/`; preserved legacy shell entry points as compatibility shims.
- Made n8n ingestion alerts opt-in and separated core validation from optional n8n workflow/config checks.

## v1.4.0 — Multi-Writer Concurrency, SQLite FTS5 Engine & Defensive Security — 2026-08-29

### Added
- **SQLite FTS5 Search Engine** (`scripts/fts_engine.py`): Incremental full-text search with SHA-256 caching and native `-bm25` ranking in WAL mode with zero external dependencies.
- **POSIX Multi-Writer File Locking** (`scripts/vault_lock.py`, `bin/vault-lock.sh`): Advisory file locks (`fcntl.flock`) and atomic file replacement (`os.replace`) to guarantee safety under concurrent multi-agent access.
- **Anti-Prompt-Injection & Ingest Sanitizer** (`scripts/sanitize_ingest.py`): Defensive ingestion pipeline stripping zero-width unicode tokens, defanging prompt injection overrides, and neutralizing malicious HTML tags/scripts.
- **HMAC-SHA256 Sender Signature** (`extensions/n8n/bin/bunker-alert.sh`; legacy entry point: `bin/bunker-alert.sh`): Adds an `X-Bunker-Signature` header; the reviewed receiver does not validate it, so this is not end-to-end webhook verification.
- **Unit Testing Suite** (`make test-unit`): Added 11+ dedicated unit tests covering FTS5 indexing/search, concurrency file locking, and prompt injection sanitization.

### Hardened
- **n8n Concurrency & Pruning**: Upgraded `N8N_CONCURRENCY_PRODUCTION_LIMIT=20`, configured `EXECUTIONS_DATA_PRUNE=true`, `EXECUTIONS_DATA_MAX_AGE=168`, and `EXECUTIONS_DATA_PRUNE_MAX_COUNT=50000` in `extensions/n8n/docker-compose.yml`.

### Fixed
- **Canonical Author & Identity**: Unified author and repository identity to `Haiagari` across documentation, metadata, and git configuration.

### Changed
- Updated `README.md`, `PROJECT.md`, `AGENTS.md`, and `BUNKER_RULES.md` to reflect v1.4.0 architectural and security capabilities.

## v1.3.1 — Feature Port from claude-obsidian v1.9 — 2026-07-02

### Added

**Skills**
- **Autoresearch**: 3-round autonomous research loop with Exa + webfetch + wiki filing. Ported from claude-obsidian v1.9.2, adapted to OpenCode.
- **wiki-retrieve**: BM25 text retrieval over wiki pages. Pure Python, zero deps, no embeddings needed. OpenCode reads results and synthesizes.
- **/think**: 10-principle framework (OBSERVE-OBSERVE-LISTEN-THINK-CONNECT-CONNECT-FEEL-ACCEPT-CREATE-GROW) for architectural decisions.

**Testing**
- **Makefile** with 5 targets: n8n workflows, wiki integrity, scripts, YAML, retrieve
- **test_workflow_connections.py**: 344 tests validating all n8n workflow nodes and connections
- **test_wiki_integrity.sh**: 21 tests for essential files, frontmatter, docker status
- **test_scripts.sh**: 61 tests for bash syntax, shebang, hardcoded secrets, go vet
- **GitHub Actions CI** (`.github/workflows/test.yml`): 5 suites on every push/PR to main

**n8n Automation**
- **Dead Letter Queue**: Global error trigger that catches errors from all workflows and persists to staticData
- **AOC v4 Enterprise**: 37 nodes with AI triage (OpenRouter/Mistral), Redis idempotency, GitHub issues + Slack/Telegram/Discord
- Docker tuning: `N8N_CONCURRENCY_PRODUCTION_LIMIT`, `EXECUTIONS_DATA_PRUNE`, `N8N_METRICS`, `N8N_LOG_FORMAT=json`
- Cleaned 5 zombie workflows from the repo

**Infrastructure**
- `.env` cleaned: removed dead API keys, added AOC v4 vars, dry-run by default
- docker-compose: removed deprecated `version:`, added production tuning
- Hooks improved: PostCompact with `cat` command, Stop with auto-update hot.md prompt, PostToolUse stages tests
- n8n token updated, Excalidraw MCP removed

### Changed
- README updated with feature comparison table, claude-obsidian comparison, CI badges
- PROJECT updated to v1.3.1, 13 skills, new architecture
- n8n restarted with new environment configuration

## v1.3.0 — Local Knowledge Operating System — 2026-05-14

### Added

- `bin/bunker-check.sh` one-command local health check.
- `wiki/meta/knowledge-supply-chain.md`.
- `wiki/meta/workflows.md`.
- `wiki/meta/governance.md`.
- Release notes under `docs/releases/v1.3.0-local-knowledge-os.md`.

### Changed

- Updated README and PROJECT to describe Bunker OS as a local-first knowledge operating system.
- Dashboard now acts as command center.

## v1.2.9 — Knowledge Supply Chain — 2026-05-14

### Added

- Formal source-to-handover workflow.
- Governance model for evidence, decisions, and automation.

## v1.2.8 — Command Center Dashboard — 2026-05-14

### Changed

- Rebuilt `wiki/meta/dashboard.md` around active context, health, evidence, agents, governance, and safe operations.

## v1.2.7 — Agent Operating Layer — 2026-05-14

### Added

- `agents/evidence-indexer.md`.
- `skills/evidence-index/SKILL.md`.
- `commands/evidence.md`.
- `wiki/meta/agent-queue.md`.

## v1.2.6 — Evidence Vault — 2026-05-14

### Added

- `bin/evidence-index.sh`.
- `wiki/meta/evidence-index.md`.
- `wiki/meta/evidence-manifest.json`.

## v1.2.5 — Integrity Engine — 2026-05-14

### Changed

- Rebuilt `bin/wiki-integrity.sh` to emit Markdown and JSON health reports.

## v1.2.4 — Hardening Release — 2026-05-14

### Security

- Removed shared Local REST API `data.json` from distributable tree.
- Added safe Local REST API example and security note.
- Ingest server now binds to localhost by default and supports token protection.

### Changed

- Scripts now resolve root through `BUNKER_HOME`.
- External-effect scripts default to dry-run.
- Removed missing `calendar-beta` from declared plugins.
