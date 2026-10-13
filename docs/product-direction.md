# Product Direction: Bunker OS

Bunker OS is a local-first personal knowledge workflow for capturing useful information, sanitizing and organizing it in an Obsidian vault, retrieving it later, and preserving context and decisions over time. It is designed for an individual who wants a durable, searchable knowledge base that remains a folder of local files.

## The core workflow

1. **Capture** sources, research, conversation notes, and decisions.
2. **Sanitize and organize** untrusted input, then shape knowledge into linked notes in the vault.
3. **Retrieve** relevant notes with the index, search tools, and focused queries.
4. **Preserve context** in durable notes, the vault index, and active-context/handover files so work can resume.

The Markdown vault is the source of truth. Scripts and agent skills make these steps easier; they do not replace the vault or become the product's primary identity.

## Product principles

- **Local-first:** knowledge is stored as ordinary files in the vault. Optional sync is the user's choice.
- **Useful before automated:** the capture-organize-retrieve-preserve loop should work without n8n.
- **Inspectable and portable:** notes and scripts are visible in the repository and can be used with Obsidian and compatible tools.
- **Honest about safeguards:** sanitization and file-locking utilities provide specific protections, not a complete security guarantee. The alert sender creates an HMAC signature; the current reviewed alerter does not validate that signature.
- **Keep status explicit:** distinguish implemented capabilities from experiments and future priorities.

## In scope

The core includes the Obsidian vault and its organization, source ingestion and sanitization, note capture and context preservation, wiki integrity checks, and local text retrieval (including SQLite FTS5/BM25 tooling). Agent skills and scripts support these workflows. Run `make test-core` for checks that do not require Docker or n8n configuration; `make test-extensions` validates optional workflow/config assets without starting Docker, and `make test` runs both.

## Out of focus for now

Bunker OS is not primarily an enterprise operations platform, a managed hosted knowledge service, or an automation product. Enterprise readiness, comprehensive security, and end-to-end webhook signature verification are not product claims. Existing operational features remain available, but they do not define the primary promise.

## Capability status

| Area | Current status |
|---|---|
| Vault notes and knowledge organization | Implemented as an Obsidian-compatible Markdown vault with wiki structure and links. |
| Capture and ingestion | Repository skills/scripts support source ingestion and conversation saving; sanitization is available through `scripts/sanitize_ingest.py`. |
| Retrieval | Local BM25 and SQLite FTS5 search tooling is implemented. |
| Context preservation | `wiki/hot.md`, the index, logs, and handovers support continuity; the user remains responsible for useful durable notes. |
| Agent assistance | Bundled OpenCode skills and hooks support knowledge workflows; they are optional tooling around the vault. |
| n8n and alerting | Optional automation extension in `extensions/n8n/`. Workflow availability varies; some workflows are inactive or experimental. `extensions/n8n/bin/bunker-alert.sh` signs outgoing alerts, but the reviewed alerter does not validate HMAC. The legacy `bin/bunker-alert.sh` remains a shim. |
| Host/repository operations | Optional utilities in `extensions/operations/`; legacy `bin/` paths remain compatibility shims and are not required for the knowledge workflow. |

## Staged priorities

1. **Make the core legible:** lead documentation with the personal knowledge workflow and clear setup/capture/retrieval paths.
2. **Improve the daily loop:** prioritize reliable capture, organization, context preservation, and retrieval without adding automation dependencies.
3. **Extend selectively:** improve agent integrations and optional automation only where they directly reduce friction in the core workflow. Keep n8n clearly optional and label experimental functionality accurately.

See [README.md](../README.md) for usage and [PROJECT.md](../PROJECT.md) for implementation details.
