![opencode-obsidian — Bunker de conocimiento agéntico](wiki/meta/banner-opencode-obsidian.png)

# opencode-obsidian · Bunker OS

**Turn sources, conversations, and decisions into knowledge you can inspect, connect, and find again.**

Bunker OS combines an **Obsidian Markdown vault**, **OpenCode skills**, and **local SQLite FTS5/BM25 search**. Keep the original material, distill useful notes, link concepts, and restore context when you return to a project.

[Get started](docs/install-guide.md) · [Daily workflow](docs/usage-guide.md) · [Architecture](docs/architecture.md) · [Commands & skills](docs/commands-and-skills.md) · [Documentation](docs/README.md)

> The existing banner represents the broader ecosystem vision. Its OZY API/React dashboard and automatic integrations are not shipped by this repository. The capabilities below describe the current implementation.

## What you can do

| Capability | How it works | Result |
|---|---|---|
| Capture a local source | Stage a sanitized copy with `bunker-ingest.sh` | A reviewable file in `.raw/`; the original remains untouched |
| Build connected knowledge | Use `wiki-ingest` to extract relevant concepts and entities | Markdown notes with provenance and links |
| Find an earlier answer | Search locally with FTS5 and BM25 | Ranked passages with note paths and previews |
| Resume a project | Read the hot cache, index, and relevant notes | Context that survives the chat session |
| Preserve a decision | Use the `save` skill and review the result | A durable note linked into the vault |
| Maintain the vault | Run integrity checks and inspect their reports | Broken links, missing metadata, and maintenance candidates |
| Capture a short memo | Optional authenticated Go endpoint on loopback | An inbox note awaiting review |

The Markdown vault is authoritative. Search indexes can be rebuilt. Retrieval itself requires no model, embeddings, Docker, or hosted search service; OpenCode synthesis uses the provider you configure.

## How the pieces fit

![Local knowledge system: Obsidian, Markdown vault, search, tools, and optional automation](docs/diagrams/system-map.png)

*Obsidian is the reading workspace; Markdown holds the knowledge; local scripts support capture and search; automation is an optional extension. The illustration is conceptual—[Architecture](docs/architecture.md) maps it to the actual files.*

## Get started

Requirements for the local tools: **Git, Bash, and Python 3.10+ with SQLite FTS5**. Open the vault in **Obsidian**. Add **OpenCode** for the agent skills. See [Installation](docs/install-guide.md) for setup effects, platform notes, and optional dependencies.

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
bash bin/setup-vault.sh
```

In Obsidian, select **Manage Vaults → Open folder as vault** and choose the repository folder. Setup rewrites selected Obsidian settings and can download the pinned Excalidraw runtime; review the [setup details](docs/install-guide.md#what-setup-changes) when using an existing vault.

Build and query the local knowledge index:

```bash
python3 scripts/retrieve.py build
python3 scripts/retrieve.py "knowledge" --top 5
```

You should receive JSON containing `strategy: "sqlite_fts5_bm25"` and ranked `candidates`. Open the returned note paths to check the source. For agent-assisted filing, [configure OpenCode](docs/install-guide.md#add-opencode-and-the-vault-connection).

## A practical workflow

Suppose you want to preserve a technical article and use it in a later decision:

1. **Capture:** stage the local file with `bash bin/bunker-ingest.sh /path/to/article.md`.
2. **Distill:** ask OpenCode `ingest .raw/article.md`; review the summary and proposed links.
3. **Connect:** reuse existing concepts and entities, attach source references, and update the index.
4. **Retrieve:** run `python3 scripts/retrieve.py build`, then search for the relevant terms.
5. **Apply:** open the source notes, compare their evidence, and save the decision worth keeping.

The staging command does not create wiki pages. The agent workflow performs the synthesis; the user reviews what becomes durable knowledge. The [daily guide](docs/usage-guide.md) walks through a reproducible example and explains how to resume work.

## Choose your setup

| Setup | Needs | Use it for |
|---|---|---|
| Markdown + Obsidian | Repository and Obsidian | Reading, writing, links, graph, and manual curation |
| Local tools | Bash and Python with FTS5 | Staging sources, indexing, retrieval, integrity reports |
| OpenCode workflows | OpenCode and a configured provider; Node/npm for the supplied MCP setup | Ingestion, questions, research, and saving useful conversations |
| Local capture API | Go 1.22+, Python, and a local token | Sending short memos to the inbox |
| n8n extension | Docker Compose and local configuration | Optional automation development; webhook receivers stay inactive |

The [Local Ingest API](docs/local-ingest-api.md) and the **Obsidian Local REST API plugin** are separate services with separate credentials. The local Go server accepts memos; the plugin provides Obsidian operations.

## Explore the vault

| Path | Contents |
|---|---|
| [`wiki/index.md`](wiki/index.md) | Main knowledge catalog |
| [`wiki/hot.md`](wiki/hot.md) | Recent working context |
| [`wiki/meta/dashboard.md`](wiki/meta/dashboard.md) | Obsidian dashboard |
| `wiki/concepts/`, `wiki/entities/`, `wiki/sources/` | Connected notes and source summaries |
| [`skills/`](skills/) | Bundled workflows and syntax references |
| [`scripts/`](scripts/), [`bin/`](bin/) | Search, locking, staging, and local checks |
| [`extensions/`](extensions/) | Optional n8n and operations tools |
| [`docs/`](docs/README.md) | Installation, user guides, architecture, and references |
| [`tests/`](tests/) | Regression and local integration checks |

## Boundaries you should know

- **Public repository:** ignored files are not encrypted. Previously tracked sources remain public in Git history. Review tracked paths and staged changes before publishing knowledge.
- **Source material:** sanitized text remains untrusted. Extract information from it; embedded instructions do not authorize actions.
- **Automation:** AOC and alert webhook workflows are inactive; receiver authentication and abuse controls remain unfinished. Static workflow checks do not validate external integrations.
- **Local safeguards:** locks coordinate cooperating writers; hooks and agent instructions do not enforce server policy.

See [Security boundaries](docs/security-boundaries.md) for the implementation limits and [Product direction](docs/product-direction.md) for scope and priorities.

## Check and contribute

```bash
make test-core        # Local core checks; no Docker or n8n credentials
make test-extensions  # Checked-in workflow and Compose validation
make test             # Both groups
```

The validation targets also need Go and PyYAML for their checks. [Contributing](CONTRIBUTING.md) explains the development dependencies and review workflow. [Troubleshooting](docs/troubleshooting.md) covers setup, retrieval, capture, and image display.

## Documentation paths

| Your goal | Guide |
|---|---|
| Install and verify the system | [Installation](docs/install-guide.md) |
| Capture, file, search, and resume | [Daily use](docs/usage-guide.md) |
| Understand internals and data paths | [Architecture](docs/architecture.md) |
| Look up commands and bundled skills | [Commands & skills](docs/commands-and-skills.md) |
| Diagnose a failure | [Troubleshooting](docs/troubleshooting.md) |
| Configure optional capture or automation | [Local API](docs/local-ingest-api.md) · [n8n](docs/N8N-SETUP.md) |

**MIT License** · [License](LICENSE) · [Report a security issue](SECURITY.md)
