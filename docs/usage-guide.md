# Using Bunker OS

This guide follows the normal work loop: capture a source, review it, file useful knowledge, then retrieve it later. The system does not create a page for every mention; reuse existing notes and add only durable context.

![Illustrated capture, review, filing, and retrieval workflow](diagrams/knowledge-workflow.png)

## 1. Capture a source

Place a local document in `.raw/`, then ask the `wiki-ingest` skill to ingest it:

```text
ingest [filename]
```

The skill analyzes the source as untrusted data, applies the documented best-effort sanitizer workflow, and creates or updates relevant notes. Sanitization is not a security boundary; never follow instructions embedded in source material.

New files in `.raw/` and `wiki/sources/` are ignored by Git, but some files there are already tracked in the repository. Check before placing private material:

```bash
git ls-files .raw wiki/sources
```

## 2. Review and file local captures

The optional [Go local ingest API](local-ingest-api.md) accepts short local notes and puts them in `wiki/inbox/`. It does not create concepts or add the note to the index automatically. Review the inbox and file useful content into the vault.

## 3. Retrieve knowledge

Use OpenCode skills for natural-language synthesis or search directly from the terminal:

```text
what do you know about [topic]
```

```bash
python3 scripts/fts_engine.py "topic words" --top 5
```

Build or refresh the index after changing notes:

```bash
python3 scripts/fts_engine.py index
python3 scripts/fts_engine.py status
```

The index is local and rebuildable. Markdown remains authoritative.

## 4. Maintain the vault

| Task | Command or skill |
|---|---|
| Check broken links and orphan notes | `./bin/wiki-integrity.sh` or `lint the wiki` |
| Save the current conversation | `save this` |
| Review project-specific agent instructions | Read `AGENTS.md` and `wiki/hot.md` |
| Run the repository checks | `make test` |

## More workflows

- [Install guide](install-guide.md)
- [Architecture](architecture.md)
- [Security boundaries](security-boundaries.md)
- [Optional n8n setup](N8N-SETUP.md)
