# Architecture

Bunker OS is a local-first knowledge workflow around an Obsidian vault. Markdown is authoritative; scripts, skills, and the local search index support it.

![Illustrated map of the Bunker OS local knowledge system](diagrams/system-map.png)

The illustration gives a high-level view. The component roles and actual paths are listed below.

## Components

| Component | Responsibility | Holds authoritative knowledge? |
|---|---|---:|
| Obsidian vault | Markdown notes, links, and the knowledge structure | Yes |
| OpenCode skills and local scripts | Capture, organize, search, and maintain notes | No |
| SQLite FTS5/BM25 index | Local full-text retrieval derived from Markdown | No; rebuildable |
| Go Local Ingest API | Authenticated loopback capture into `wiki/inbox/` | No; inbox items need review |
| n8n extension | Optional integrations and automation | No; separate from the core workflow |

## Data paths

### Source ingestion

1. A user places a local source in `.raw/` and asks the `wiki-ingest` workflow to process it.
2. The workflow treats source text as untrusted and may create or update relevant Markdown notes.
3. A user or agent reviews the notes and their links. Sanitization is a best-effort text transformation, not proof that a source is safe.

### Short-note capture

1. A local client sends an authenticated request to the Go API on loopback.
2. The API writes the note to `wiki/inbox/`; it does not classify it, create concept pages, or publish it.
3. A person or agent reviews and files useful content in the Markdown vault.

### Retrieval

1. The retrieval script builds or refreshes a local SQLite index from Markdown notes.
2. OpenCode query workflows or the command-line search retrieve relevant passages.
3. OpenCode can use those passages as context when answering. The database does not itself call an LLM.

The [daily use guide](usage-guide.md) explains these paths from the user's perspective. The [Local Ingest API reference](local-ingest-api.md) documents its request contract.

## Optional automation boundary

n8n is not required for capture, organization, retrieval, or vault integrity. It is an optional integration layer. The AOC and alert webhook workflows remain inactive; the manual Health Check returns static status and is not service monitoring. See [n8n setup](N8N-SETUP.md) and [Security boundaries](security-boundaries.md) for the current limits.

## Related references

- [Daily use](usage-guide.md)
- [Security boundaries](security-boundaries.md)
- [Local Ingest API](local-ingest-api.md)
- [Product direction](product-direction.md)
