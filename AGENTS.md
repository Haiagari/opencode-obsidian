# OpenCode-Bunker — Wiki Vault

This directory is the Bunker OS repository. It contains skills, scripts, automation, and a **wiki vault** that compounds knowledge across sessions.

> [!important] STARTUP INSTRUCTIONS
> On every session, the agent MUST:
> 1. Read `wiki/hot.md` for active context.
> 2. Read the latest handover in `wiki/meta/handovers/`.
> 3. Act under the **Proactive Protocol** below.

## Vault

```
wiki/           → Your knowledge base (entities, concepts, sources, handovers)
skills/         → Agent skills
scripts/        → BM25 retrieval, indexing
hooks/          → OpenCode hooks
```

The `wiki/` baseline (core index, hot cache, evergreen concepts, entities, and skills) is tracked in git. Private and volatile folders such as `wiki/projects/`, `wiki/meta/handovers/`, `wiki/decisions/`, `wiki/blueprints/`, and `wiki/sources/` (as well as `wiki/.raw/`, `wiki/questions/`, `wiki/canvases/`, and `wiki/meta/archive/`) are gitignored so sensitive and personal content stays local.

## Proactive Protocol

Do NOT wait for orders on maintenance tasks:

1. **Source Detection**: On startup, check `wiki/.raw/`. If new files, offer to ingest.
2. **Context Retention**: If conversation drifts, re-read `wiki/hot.md`.
3. **Smart Close**: At session end, generate handover and Engram summary.
4. **Link Maintenance**: After creating a note, link related notes with `[[ ]]`.

## Ingestion Workflow

When receiving a resource (URL, file, topic):

### Destination by type

| Resource type | Folder | Example |
|--------------|--------|---------|
| Entity (person, org, product) | `wiki/entities/` | `wiki/entities/[name].md` |
| Technical concept | `wiki/concepts/tech-stack/` | `wiki/concepts/tech-stack/[name].md` |
| General concept | `wiki/concepts/` | `wiki/concepts/[name].md` |
| External source | `wiki/sources/` | `wiki/sources/[slug].md` |

### Required steps

1. Create source page in `wiki/sources/`
2. Create entity page in `wiki/entities/`
3. Create concept page in correct folder
4. Update `wiki/index.md`
5. Prepend to `wiki/log.md`
6. Check for contradictions with existing pages

### DO NOT

- ❌ Save only to Engram — wiki pages survive across sessions
- ❌ Skip the index update — it's the vault's entry point

### Page format

```markdown
---
type: [entity|concept|source]
title: "[Title]"
domain: [tech-stack|design|ai|etc]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: [active|mature|seed]
related: []
sources: []
---

# Title

## Definition
[One-line description]

## How It Works
[Mechanism]

## Example
```language
code here
```

## Source
- URL
```

## Available Skills

| Skill | Trigger | Operates on |
|-------|---------|-------------|
| `wiki` | Setup, scaffold | `wiki/` |
| `ingest [file]` | Source ingestion | `wiki/` |
| `query [question]` | Answer from wiki | `wiki/` |
| `retrieve [query]` | BM25 search | `wiki/` |
| `lint` | Health check | `wiki/` |
| `save this` | Save conversation | `wiki/` |
| `autoresearch` | Web research | `wiki/` |
| `think` | Decision framework | Both |

## How to Use

1. **Ingest**: `ingest ~/Documents/article.md`
2. **Query**: `what do you know about X?`
3. **Save**: `save this` or `/save`
4. **Maintenance**: `lint the wiki`
5. **Retrieve**: `retrieve [query]` (BM25 text search)

## Cross-Project Access

To reference this wiki from another OpenCode project, add to that project's `AGENTS.md`:

```markdown
## Wiki Knowledge Base
Path: /path/to/opencode-obsidian

When you need context:
1. Read wiki/hot.md first (~500 words)
2. If not enough, read wiki/index.md
3. Only then read individual pages

Do NOT read the wiki for general coding questions.
```

## MCP (Configured)

1. **obsidian-vault** (`~/.config/opencode/opencode.json`):
   - `list_notes`, `read_note`, `search_notes`, `write_note`
   - Pointed at this repo's `wiki/`
2. **n8n-mcp**: n8n automation workflows in `automation/n8n-lab/`

## Tool Governance

1. **Search & Ingestion**:
   - **Context7**: PRIMARY for library docs (React, Go, etc.)
   - **Exa**: SECONDARY for news, trends, general topics
2. **Action**:
   - **GitHub MCP**: For PRs, issues, repo management
   - **n8n MCP**: For async workflows, alerts
3. **Memory**: Save ALL architectural decisions, bug fixes, and patterns to Engram.

## Skills (Ported from claude-obsidian)

| Skill | Description | Location |
|-------|-------------|----------|
| **autoresearch** | 3-round autonomous web research | `skills/autoresearch/` |
| **wiki-retrieve** | BM25 text search | `skills/wiki-retrieve/` + `scripts/retrieve.py` |
| **think** | 10-principle decision framework | `skills/think/` |

## Test Suite

```bash
make test        # 430 tests, 5 suites
make test-wiki   # Vault integrity
make test-scripts # Bash syntax + secrets
make test-workflows # n8n connections
make test-retrieve # BM25 text retrieval
```

## CI

GitHub Actions in `.github/workflows/test.yml`. Runs on every push/PR to main.

## References

- Skills: `skills/`
- Scripts: `scripts/retrieve.py`, `scripts/bm25-index.py`
