# Architecture and data flow

[Documentation](README.md) · [Daily use](usage-guide.md) · [Security boundaries](security-boundaries.md)

Bunker OS is a file-based knowledge workspace. Obsidian reads the vault, OpenCode assists with synthesis, and Python scripts provide local retrieval and maintenance. Optional capture and automation extend that workspace without becoming its authoritative store.

![Conceptual map of the local Bunker OS knowledge system](diagrams/system-map.png)

*Read the illustration as a conceptual overview. The table below is the mapping to implemented components; it does not imply a deployed React dashboard or a remote orchestration service.*

## Component responsibilities

| Layer | Implementation | Reads | Writes / output |
|---|---|---|---|
| Knowledge store | `wiki/` Markdown | Notes, metadata, source references | Durable knowledge and context |
| Visual workspace | Obsidian and `.obsidian/` | Vault files | Notes, links, local plugin state |
| Agent workflows | `skills/*/SKILL.md` | Sources, hot cache, index, relevant notes | Reviewed summaries, linked notes, context updates |
| Source staging | `bin/bunker-ingest.sh` | Local file | Sanitized copy in `.raw/`; refuses overwrite |
| Text hygiene | `scripts/sanitize_ingest.py` | Untrusted source text | Best-effort transformed text |
| Retrieval | `scripts/fts_engine.py`, `scripts/retrieve.py` | Eligible wiki Markdown | SQLite index and ranked result JSON |
| Shared-file coordination | `scripts/vault_lock.py`, `bin/vault-lock.sh` | Target file | Locked append/prepend or atomic replacement |
| Integrity | `bin/wiki-integrity.sh` | Vault, links, configuration paths | Markdown/JSON maintenance reports |
| Local capture | `bin/ingest_server.go` | Authenticated memo body | A categorized inbox note |
| Optional automation | `extensions/n8n/` | Configured workflows and external inputs | Integration outputs when deliberately enabled |

Skill files describe agent behavior. They are not a deterministic ingestion service: completion and semantic correctness still need review. The local retrieval engine does not call a model; OpenCode can synthesize retrieved context using its configured provider.

## Storage and authority

| Path | Role | Recovery / publication implications |
|---|---|---|
| `wiki/concepts/`, `wiki/entities/`, `wiki/sources/` | Durable notes and provenance | Back up the actual files; tracked notes are public |
| `.raw/` | Staged source material | Retain originals separately where exact source preservation matters |
| `wiki/inbox/` | Pending local captures | Capture is not approval or filing |
| `wiki/hot.md`, `wiki/index.md`, `wiki/log.md` | Recent context, catalog, operation history | These baseline files are tracked; do not place private details in them |
| `.vault-meta/fts5/vault_fts.db` | Derived local search index | Rebuild from eligible Markdown |
| `wiki/meta/INTEGRITY-REPORT.*` | Derived maintenance reports | Inspect findings; reports are not fixes |
| `.obsidian/plugins/*/data.json` | Local plugin settings | Can include credentials; ignored defaults do not encrypt them |
| n8n `n8n_data` volume | Optional service state | Separate backup and credential lifecycle from the Markdown vault |

See [Security boundaries](security-boundaries.md) for the exact Git-ignore and local-access limitations.

## Source ingestion

1. `bunker-ingest.sh` validates a local filename and runs the sanitizer into a temporary file.
2. Atomic link creation publishes the sanitized staged copy in `.raw/` without overwriting an existing path.
3. The `wiki-ingest` skill treats the source as untrusted data, checks its processing manifest, and searches existing knowledge.
4. The agent creates/updates useful pages and context; a user reviews provenance, links, and claims.
5. An explicit retrieval build makes eligible notes searchable.

The CLI does not fetch URLs or create wiki notes. URL ingestion belongs to the agent skill and needs its web tools. Staged local input is a sanitized copy; the original input file is not modified.

## Local memo capture

1. A client posts to `/ingest` on loopback with a bearer or `X-Bunker-Token` credential.
2. The server applies method/authentication checks and a body limit, then invokes the Python sanitizer with a timeout.
3. Keyword heuristics assign a memo/task/bug/decision type. This is metadata classification, not semantic knowledge extraction.
4. The server writes a `0600` temporary note and atomically links it to an opaque content-derived filename in the inbox.
5. A reviewer files the useful content. The server does not update the index or publish changes.

The [API reference](local-ingest-api.md) documents duplicate handling, errors, and the narrow legacy `ioutil` check. The loopback API and the Obsidian Local REST API plugin are independent.

## Retrieval internals

### Selection and incremental updates

The engine scans `wiki/**/*.md` and excludes files below directory names `meta` or `archive`, case-insensitively. `.raw/`, root documentation, and binary assets are outside this scan. Inbox Markdown is eligible because the engine does not exclude `inbox`; default search is not a review-status filter.

A `file_meta` table tracks path, modification time, SHA-256, indexing time, and chunk count. Builds add/update changed files, skip unchanged files, and remove entries for deleted notes. The engine also supports a `force` argument through its Python function; the documented CLI build is incremental.

### Chunking and matching

Pages are split at paragraph boundaries around a 500-token target; a long single paragraph can exceed that target. The title comes from YAML `title`, the first H1, or the filename. FTS5 uses `unicode61 remove_diacritics 2` and ranks with native BM25.

Input terms are normalized into quoted prefix matches. Results contain `doc_id`, `path`, `title`, chunk position, score, and a 200-character preview. Ranking is lexical relevance, not factual confidence. Read the underlying note and follow its provenance before relying on an answer.

### Recovery

The SQLite database uses WAL mode and is derived from Markdown. For a stale index, rebuild; for a corrupt index, stop concurrent search/index operations, preserve the affected database, and rebuild. [Troubleshooting](troubleshooting.md) describes this procedure. Losing the index does not lose notes.

## File-write coordination

The lock utility uses POSIX advisory `flock` on a companion lock file and atomic replacement for supported operations. It coordinates writers that use the same protocol. Direct editor writes, unrelated tools, and distributed/network filesystems do not gain this guarantee automatically.

Git is a publication boundary. `wiki-sync.sh` defaults to dry run and only creates a commit with `--apply`; publication utilities live under the optional operations extension. Hooks do not auto-commit the vault.

## Optional n8n boundary

Compose pins the service image, publishes it on host loopback, mounts workflow JSON read-only, and persists service state separately. A running container does not establish a healthy workflow. The manual Health Check returns static status; AOC/alert webhook receivers remain inactive because their inbound controls are incomplete.

[Setup and workflow status](N8N-SETUP.md) explains what can be tested locally and what requires configured external services.

## Validation model

- Python tests exercise retrieval, sanitization, locking, setup, and local lifecycle behavior.
- Go handler tests exercise authentication, size limits, permissions, duplicates, and loopback configuration without a network listener.
- Local integration fixtures exercise capture, indexing, archiving, and publication to a local bare Git remote.
- Workflow JSON/Compose checks validate checked-in assets; they do not authenticate remote services, verify an OpenCode release's MCP schema, or judge an agent's semantic output.

Use [Contributing](../CONTRIBUTING.md) for checks and [Product direction](product-direction.md) for future acceptance criteria.
