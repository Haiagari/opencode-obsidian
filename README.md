# opencode-obsidian · Bunker OS

> A local-first knowledge workflow for an Obsidian vault. Capture useful information, review it, keep durable knowledge in Markdown, and find it again with local search.

[Get started](docs/install-guide.md) · [Documentation hub](docs/README.md) · [Usage guide](docs/usage-guide.md) · [Security boundaries](docs/security-boundaries.md) · [Repository audit](docs/repository-audit.md)

## How it fits together

![Illustrated map of the Bunker OS local knowledge system](docs/diagrams/system-map.png)

Markdown is the source of truth. OpenCode skills and local scripts help capture, organize, and query notes. SQLite FTS5/BM25 is a rebuildable index. The optional n8n extension sits outside the core workflow.

For the exact component and data flows, see [Architecture](docs/architecture.md).

## Start in three steps

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
```

1. Open the folder as an Obsidian vault.
2. Open the same folder in OpenCode.
3. Follow the [first-run guide](docs/install-guide.md), then try `ingest [filename]` or `what do you know about [topic]`.

The [usage guide](docs/usage-guide.md) explains the capture → review → file → retrieve loop.

## What you can do

| Need | Built-in path |
|---|---|
| Capture and organize a source | `wiki-ingest` skill |
| Search the vault locally | SQLite FTS5 + BM25 via `wiki-retrieve` |
| Ask for context across notes | `wiki-query` skill |
| Check wiki links and note health | `wiki-lint` or `./bin/wiki-integrity.sh` |
| Preserve a conversation | `save` skill |
| Capture a short note over loopback HTTP | Optional authenticated [Local Ingest API](docs/local-ingest-api.md) |

The local API writes to a review inbox; it does not automatically create or file wiki pages. n8n is optional and is not needed for the local knowledge workflow.

## Boundaries to know

- The vault is a normal folder of Markdown files. Git ignore rules do not encrypt data or remove files already tracked in history. Check `git ls-files .raw wiki/sources` before adding private content.
- The ingestion sanitizer is a best-effort text heuristic. Sanitized content remains untrusted.
- The AOC and alert webhook workflows are inactive. Do not expose them until receiver authentication, payload validation, and rate limiting are implemented and tested.
- The n8n Health Check is a manual smoke workflow that returns static status; it is not service monitoring.

See [Security Boundaries](docs/security-boundaries.md) for current safeguards and limitations.

## Documentation

Start from the [documentation hub](docs/README.md), which groups guides by task.

| Guide | Use it for |
|---|---|
| [Install](docs/install-guide.md) | Set up the vault and first-run workflow |
| [Use Bunker OS](docs/usage-guide.md) | Capture, review, retrieve, and maintain notes |
| [Architecture](docs/architecture.md) | Components, data flows, and extension boundaries |
| [Local Ingest API](docs/local-ingest-api.md) | Run and call the local capture endpoint |
| [n8n setup](docs/N8N-SETUP.md) | Optional automation setup and diagnostics |
| [Product direction](docs/product-direction.md) | Scope, principles, and priorities |
| [Repository audit](docs/repository-audit.md) | Audit findings, fixes, evidence, and remaining work |

## Checks

Run the repository checks before contributing:

```bash
make test-core        # Core checks; no Docker or n8n credentials
make test-extensions  # Static validation for optional extensions
make test             # Both suites
```

The test commands validate local behavior and checked-in workflow assets. They do not prove that remote services or external integrations are configured correctly.

## Repository map

| Path | Purpose |
|---|---|
| `skills/` | OpenCode workflows for research, ingestion, retrieval, querying, and maintenance |
| `wiki/` | Obsidian knowledge vault |
| `scripts/`, `bin/` | Local retrieval, integrity, ingest, and operations tools |
| `docs/` | User guides, architecture, security boundaries, and audit records |
| `extensions/n8n/` | Optional automation workflows |
| `extensions/operations/` | Optional host and repository utilities |
| `tests/` | Core and optional-extension checks |

## Requirements

Obsidian and OpenCode are needed for the full workflow. Python 3.10+, Bash, and Git are used by local tools. Go 1.22+ is needed only for the optional local ingest API. Docker is needed only for the optional n8n extension.

## License

MIT. See [LICENSE](LICENSE).
