# opencode-obsidian · Bunker OS

Bunker OS is a local-first knowledge workflow for an Obsidian vault. It helps you capture useful material, review it, keep durable notes in Markdown, and find them again with local search.

## Start here

Follow the [installation guide](docs/install-guide.md) to set up and open the vault. Then use the [daily use guide](docs/usage-guide.md) to capture, review, organize, and retrieve knowledge.

## The everyday workflow

Capture a source or thought, review it, file what is useful in the Markdown vault, and retrieve it when needed. The vault is the source of truth; the local search index can be rebuilt. The Go capture API and n8n workflows are optional.

| I want to… | Start with |
|---|---|
| Install or configure the vault | [Installation](docs/install-guide.md) |
| Ingest, organize, or search notes | [Daily use](docs/usage-guide.md) |
| Understand components and boundaries | [Architecture](docs/architecture.md) |
| Use the optional capture endpoint | [Local Ingest API](docs/local-ingest-api.md) |
| Review safeguards and limitations | [Security boundaries](docs/security-boundaries.md) |

The full [documentation index](docs/README.md) also links to optional integrations, project direction, and audit records.

## Important data note

This is a public repository. Git ignore rules do not encrypt files or remove content already tracked in Git history. Before adding private material, check `git ls-files .raw wiki/sources` and review `git status --short`.

## Checks

```bash
make test-core        # Core checks; no Docker or n8n credentials
make test-extensions  # Static validation for optional extensions
make test             # Both suites
```

Passing these checks validates local code and checked-in workflow assets; it does not prove remote services are configured correctly.

## Repository map

| Path | Purpose |
|---|---|
| `wiki/` | Obsidian knowledge vault |
| `skills/` | OpenCode knowledge workflows |
| `scripts/`, `bin/` | Local search, integrity, capture, and operations tools |
| `docs/` | User guides and technical references |
| `extensions/` | Optional n8n and operations tools |
| `tests/` | Core and optional-extension checks |

## Requirements

Git is required for setup. Obsidian opens and edits the vault. OpenCode is optional and enables the bundled agent workflow. Python 3.10+ is used by local tools; Go 1.22+ is needed only for the optional local ingest API. Docker is needed only for the optional n8n extension.

## License

MIT. See [LICENSE](LICENSE).
