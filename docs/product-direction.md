# Product direction

Bunker OS is a local-first personal knowledge workflow built around an Obsidian vault. Its main job is to help a person keep useful knowledge in portable Markdown and retrieve it later. The product's center is the vault, not its optional automation or agent integrations.

## Principles

- **Local-first:** the knowledge base remains a folder of files the user can inspect and back up.
- **Useful without services:** capture, organization, search, and vault maintenance do not require n8n or a hosted service.
- **Portable and inspectable:** Markdown is authoritative; the derived search index can be rebuilt.
- **Honest about guarantees:** scripts and agent instructions provide bounded safeguards, not a sandbox or complete security enforcement.
- **Selective automation:** add automation only when it makes the core knowledge loop more reliable or easier to use.

## Current scope

The working product includes the Obsidian vault, OpenCode workflows, local capture and sanitization tools, wiki integrity checks, and local BM25/SQLite FTS5 retrieval. The Go Local Ingest API and n8n workflows are optional. Some n8n webhook workflows remain inactive; see [Security boundaries](security-boundaries.md) for their status and limits.

## Out of scope

Bunker OS is not a hosted knowledge service, an enterprise data-loss-prevention system, or a general automation platform. Its current controls do not make those claims.

## Priorities

1. Keep setup and everyday vault use understandable.
2. Improve reliable capture, organization, context preservation, and retrieval.
3. Add integrations selectively while keeping the local workflow independent.

For tasks and setup, start at the [documentation index](README.md). For components and data paths, see [Architecture](architecture.md). The detailed [repository audit](repository-audit.md) records implementation evidence and remaining maintenance work.
