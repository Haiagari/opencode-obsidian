---
type: concept
title: "opencode obsidian architecture"
updated: 2026-10-13
status: active
---

# OpenCode-Obsidian Architecture

**Status**: Active / Core
**Type**: Architecture Decision
**Parent**: [[_index]]

## Summary
`opencode-obsidian` is a **Hard Detach** from the original `claude-obsidian` project, optimized specifically for the **OpenCode** agentic ecosystem. It implements the **LLM Wiki Pattern** to provide persistent, compounding knowledge across sessions.

![OpenCode-Obsidian architecture](../../docs/diagrams/architecture-overview.png)

The core remains local-first: Markdown is the source of truth, SQLite FTS5/BM25 is rebuildable, the optional ingest API writes only to a review inbox, and n8n is a separate extension.

## Core Pillars

### 1. Hard Detach & Identity
- **Absolute Independence**: Removal of all Anthropic/Claude-specific dependencies and naming.
- **Project Path**: `${BUNKER_HOME:-<path-to-opencode-obsidian>}`.
- **Primary Agent**: OpenCode.

### 2. Multi-Layer Knowledge (LLM Wiki Pattern)
The knowledge base is structured to be token-efficient:
1. **[[hot]]**: ~500 words. Loaded every session. High-priority context.
2. **[[index]]**: The map of all knowledge. Used when `hot` isn't enough.
3. **Individual Wiki Pages**: Detailed notes on specific concepts, entities, or sources.

### 3. Agentic Skills
Custom-built skills installed for OpenCode in `~/.config/opencode/skills/`:
- `wiki`: System orchestrator.
- `wiki-ingest`: Source processor.
- `wiki-query`: RAG-less knowledge retrieval.
- `save`: Conversation persistence.
- `wiki-lint`: Health and link maintenance.

### 4. MCP Integration
Uses `@bitbonsai/mcpvault` via `stdio` to allow the agent to:
- Read/Write notes directly.
- Search content using regex.
- List directory structures.

### 5. Local Capture and Retrieval
- The optional Go ingest API listens on loopback, requires a token, sanitizes input, and writes to `wiki/inbox/`; it does not file knowledge pages automatically.
- `scripts/retrieve.py` uses a local SQLite FTS5/BM25 index. Markdown notes remain the source of truth and the index can be rebuilt.
- n8n is an optional extension. AOC and alert webhook workflows remain inactive pending receiver-side controls.

## File Structure
- `.raw/`: Immutable source documents.
- `wiki/`: AI-generated and human-refined knowledge.
- `bin/`: Automation and setup scripts.
- `_templates/`: Obsidian formatting templates.

## Context Injection Strategy
When an agent starts in a different project, it should refer to this vault via its `AGENTS.md` using the "Three-Step Context Read" protocol:
1. Read `hot.md`.
2. If unresolved, read `index.md`.
3. If still unresolved, search/read specific pages.

---
**Created**: 2026-04-19
**Session**: [[purgado-de-referencias-y-renombramiento-de-carpeta-ra-z]]
