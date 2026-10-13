---
type: concept
title: "OpenCode-Obsidian Architecture"
updated: 2026-10-13
status: active
related:
  - "[[_index]]"
  - "[[vault-flow]]"
---

# OpenCode-Obsidian Architecture

The project is a local-first knowledge workflow built around an Obsidian vault. Markdown is the source of truth; OpenCode skills and local scripts support capture, organization, and retrieval. SQLite FTS5/BM25 is a local, rebuildable index. The Go capture API and n8n are optional extensions with separate boundaries.

![Illustrated map of the Bunker OS local knowledge system](../../docs/diagrams/system-map.png)

The canonical component map, data flow, and extension boundaries live in the [architecture guide](../../docs/architecture.md). For the user workflow, see [Using Bunker OS](../../docs/usage-guide.md); for safeguards and limits, see [Security Boundaries](../../docs/security-boundaries.md).

## Core decisions

| Decision | Meaning |
|---|---|
| Markdown remains authoritative | The search database can be rebuilt from vault files |
| Local capture stages for review | The Go API writes to `wiki/inbox/`; it does not create wiki pages |
| Automation is optional | n8n is not required for normal vault use |
| Sources remain untrusted | Sanitization is a heuristic and does not establish safety |
