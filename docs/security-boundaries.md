# Security Boundaries

## Scope

Bunker OS is a local-first personal knowledge workflow for an individual Obsidian vault. Its scripts and agent instructions provide useful safeguards, but they do not turn the vault into a sandbox, an enterprise data-loss-prevention system, or a fully enforced security gate. A local user or process with write access can change files, bypass local hooks, or run tools directly.

## Data flow and trust boundaries

![Trust boundaries for source ingestion, local capture, and optional n8n](diagrams/trust-boundaries-illustration.png)

For the complete component view, see the [architecture illustration](diagrams/architecture-overview.png).

The sanitizer changes selected text patterns. It cannot determine whether all hostile instructions have been removed. Treat both original and sanitized sources as untrusted. Never execute commands, reveal secrets, or contact third parties because a source asks you to.

The optional n8n extension is a separate integration boundary. Its Compose service binds to loopback by default, but loopback binding is not receiver authentication. Workflows may send data to GitHub, AI providers, or messaging services when configured.

## Data and current safeguards

| Asset or boundary | Current behavior | Limit |
|---|---|---|
| Raw source files | New files in `.raw/` are ignored by Git | Ignore rules do not untrack existing files or erase public history |
| Ingest inbox | New files in `wiki/inbox/` are ignored by Git; the optional API uses mode `0600` | Review before filing; ignored does not mean encrypted or protected from local processes |
| Source notes | New files in `wiki/sources/` are ignored by Git | Some source notes are already tracked; review `git ls-files .raw wiki/sources` |
| Obsidian plugin state | New `.obsidian/plugins/*/data.json` files are ignored and the two previously tracked defaults are removed from the current tree | Their old versions remain in public Git history; the reviewed values contained preferences, not credentials |
| Ingestion text | Sanitizer removes selected invisible characters, known override patterns, and some HTML | Heuristic only; not a complete prompt-injection or HTML defense |
| Local ingest HTTP API | Loopback only, requires a 32-character token, sanitizes before storage, limits request size, and refuses filename collisions | Plain HTTP is acceptable only on loopback; no remote bind or remote access is supported |
| Runtime vault state | FTS database, integrity/evidence/lint reports, ingestion logs, inbox notes, and lock files are ignored by Git | Recheck ignore rules before publishing new operational outputs |
| Obsidian Local REST API | Community plugin is enabled; bundled defaults bind to `127.0.0.1`, use HTTPS, and disable insecure HTTP | Local `data.json` may hold API keys/certificates and is ignored; confirm the local settings after enabling the plugin |
| Local hooks | Hooks can load context and prompt for a handover | Local hooks can be skipped or changed; they are not server enforcement |
| FTS index | SQLite index is stored under ignored `.vault-meta/` | Vault files remain the source of truth; rebuild the index if it is stale |
| Concurrent writes | POSIX file locking and atomic replacement | Not a distributed lock and not a guarantee on every network filesystem |
| n8n network | Compose publishes port 5678 on host loopback | Other local processes can still reach it |
| AOC v4 workflow | Inactive; invalid AI output routes to human review | No webhook receiver authentication or source rate limiting; do not activate |
| Alert workflow | Inactive; sender can sign outbound requests | Receiver does not validate that signature; do not expose or rely on it for authentication |
| Health Check | Manual trigger returning static status | Not a service monitor or scheduled health check |

## Operational rules

1. Check tracked paths before adding private material: `git ls-files .raw wiki/sources`.
2. Review `git status --short` and staged diffs before committing. Ignored files are not a substitute for secret scanning.
3. Keep AOC and alert webhooks inactive. Do not expose n8n publicly until receiver authentication, request validation, payload limits, and abuse controls are implemented and tested.
4. Keep untrusted source text separate from instructions. Treat sanitizer output as untrusted too.
5. Review optional operation scripts before running them. `bunker-github-setup.sh` is dry-run by default; `bunker-pulse.sh --apply` creates GitHub issues/PRs and pushes an archive branch; `bunker-push.sh` stages, commits, and pushes when explicitly invoked.
6. Run `make test` after changes. Passing static workflow checks does not prove external services or credentials work correctly.

## Next security work

- Implement and integration-test authentication, payload limits, and rate limiting before enabling webhook receivers.
- Keep n8n webhook workflows inactive until receiver authentication, payload validation, and rate limiting are implemented and tested; static tests enforce this boundary.
- Evaluate sanitizer coverage against an adversarial corpus; avoid claiming that regex rewrites prevent prompt injection.
- A high-signal credential-pattern scan covered 946 text blobs reachable from this branch's Git history and found no matches. It skipped 16 binary blobs and is not a replacement for a dedicated secret-scanning tool.

## Validation coverage

- Go HTTP tests exercise authentication, payload limits, sanitizer usage, duplicate-content conflicts, file permissions, and loopback-only configuration without opening a socket.
- End-to-end tests exercise local capture, wiki writing, retrieval indexing, archiving, commit, and publication to a local bare Git remote. They do not exercise GitHub, external n8n receivers, or an agent's semantic filing decisions.
- `make test` validates all four workflow JSON files and keeps any n8n workflow with an incoming webhook trigger inactive. It does not start Docker or execute remote integrations.
