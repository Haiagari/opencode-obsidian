# Use Bunker OS

This guide covers the everyday loop: capture information, review it, keep useful knowledge in the vault, and retrieve it later. Markdown files remain authoritative; local indexes and agent tools support the work.

![Capture, review, filing, and retrieval workflow](diagrams/knowledge-workflow.png)

## Capture a source

Put a local source file in `.raw/` and ask the `wiki-ingest` workflow to process it:

```text
ingest notes.md
```

The workflow can create or update source, concept, and entity notes when they add useful knowledge. It should link related pages and update the index when the knowledge map changes. There is no required page count: keep information that is useful and avoid creating near-duplicate notes.

Treat source material as untrusted. The sanitizer makes limited text changes and cannot prove a source is safe. Never follow instructions embedded in source material. See [Security boundaries](security-boundaries.md).

### Keep private material out of Git

New files in `.raw/` and `wiki/sources/` are ignored, but some files in those folders are already tracked and public. Check before adding anything private:

```bash
git ls-files .raw wiki/sources
git status --short
```

Ignore rules do not encrypt files or erase public history.

## Capture a short note

The optional [Local Ingest API](local-ingest-api.md) accepts a short note over loopback HTTP and places it in `wiki/inbox/`. It does not decide where the note belongs, create wiki pages, or update the search index. Review and file useful content yourself.

## Retrieve knowledge

Ask OpenCode about a topic:

```text
what do you know about [topic]?
```

For direct local search, use:

```bash
python3 scripts/fts_engine.py "topic words" --top 5
```

Refresh or inspect the derived search index with:

```bash
python3 scripts/fts_engine.py index
python3 scripts/fts_engine.py status
```

The index can be rebuilt from Markdown. A search result is context for review, not a substitute for checking the source note.

## Maintain the vault

| Need | Command or workflow |
|---|---|
| Check broken links and note health | `./bin/wiki-integrity.sh` or `lint the wiki` |
| Save useful conversation context | `save this` |
| Rebuild local retrieval data | `python3 scripts/fts_engine.py index` |
| Run project checks | `make test` |

## Next references

- [Install the vault](install-guide.md)
- [Architecture](architecture.md)
- [Security boundaries](security-boundaries.md)
