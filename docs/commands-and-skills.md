# Commands and bundled skills

[Documentation](README.md) · [Daily workflow](usage-guide.md) · [Troubleshooting](troubleshooting.md)

Run shell commands from the repository root unless a different directory is shown. OpenCode prompts are agent workflows, not shell commands. The tables describe the current implementations rather than aliases pictured in historical artwork.

## Source staging and retrieval

| Command | Effect | Expected output |
|---|---|---|
| `bash bin/bunker-ingest.sh /path/to/source.md` | Sanitizes into `.raw/<basename>`; refuses an existing destination | Staged path and reminder to run `wiki-ingest` |
| `python3 scripts/retrieve.py build` | Builds/updates the derived FTS5 index | Page/chunk counts and changed/skipped/deleted counts |
| `python3 scripts/retrieve.py status` | Inspects the local index | Database path and counts; exit 1 if unavailable |
| `python3 scripts/retrieve.py "topic" --top 5` | Searches indexed Markdown | JSON containing ranked candidates |
| `python3 scripts/bm25-index.py build` | Alternate indexing entry point | Incremental index summary |
| `python3 scripts/bm25-index.py query "topic"` | Alternate human-readable search | Paths, scores, and short previews |
| `python3 scripts/sanitize_ingest.py source.md --output /tmp/source-review.md` | Produces a separate sanitized analysis copy | Output file; source remains unchanged |

`fts_engine.py` is the imported engine module, not an executable search CLI. Use `retrieve.py` or `bm25-index.py`. `retrieve.py build` is incremental; it does not blindly rebuild every unchanged page.

Set `BUNKER_HOME` to a vault root for supported search/staging tools. `VAULT_PATH` is also supported by retrieval, with `BUNKER_HOME` taking precedence. The engine expects `<root>/wiki/`. See [Architecture](architecture.md#retrieval-internals) for selection and ranking rules.

### Search result fields

| Field | Meaning |
|---|---|
| `strategy` | `sqlite_fts5_bm25` identifies the retrieval method |
| `top_k` | Number of returned results, which may be below the requested limit |
| `candidates[].path` | Path of the underlying Markdown note |
| `title` | Extracted note title |
| `chunk`, `total_chunks` | Passage position within the indexed note |
| `score` | Negated BM25 score; higher values rank earlier |
| `preview` | First 200 characters of the matched chunk, with line breaks flattened |

An empty `candidates` array can mean no matching term, a missing index, or text outside indexed paths. Check `status`, build, and confirm the note location before concluding the knowledge is absent.

## Integrity and evidence

| Command | Writes | Interpretation |
|---|---|---|
| `bash bin/wiki-integrity.sh` | `wiki/meta/INTEGRITY-REPORT.md` and `.json` | Maintenance findings; does not repair the vault |
| `bash bin/evidence-index.sh` | `wiki/meta/evidence-index.md` and `evidence-manifest.json` | Artifact references and checksums, not proof of artifact correctness |
| `bash bin/bunker-check.sh` | Integrity/evidence reports and a temporary Go binary when Go is available | Operational checks; separate from the full regression suite |

Integrity output paths can be configured with `BUNKER_INTEGRITY_REPORT` and `BUNKER_INTEGRITY_JSON`; `BUNKER_VAULT_DIR` selects the wiki path. Existing report files are generated state. Review their findings before altering notes.

## Shared-file writes

Use the lock wrapper when updating shared context or logs with cooperating tools:

```bash
printf '%s\n' 'Reviewed deployment checklist.' | bash bin/vault-lock.sh append /tmp/bunker-example.md
printf '%s\n' 'Complete replacement text.' | bash bin/vault-lock.sh write /tmp/bunker-example.md
printf '%s\n' '## New reviewed operation' | bash bin/vault-lock.sh prepend-log /tmp/bunker-example-log.md
```

For real vault operations, replace the example paths with the intended files and complete note content. `write` replaces the whole target; `append` adds to the end; `prepend-log` inserts the new log entry at the top. The Python utility uses advisory POSIX locks; all participating writers must use the protocol.

## Git synchronization

| Command | Actual behavior |
|---|---|
| `bash bin/wiki-sync.sh` | Shows changes and proposed staging/commit; default dry run |
| `bash bin/wiki-sync.sh --apply -m 'docs: update reviewed notes'` | Stages the implementation's broad path set and creates a local commit; does not push |
| `bash bin/bunker.sh init` / `refresh` | Prints lifecycle status; does not itself read context into an agent |
| `bash bin/bunker.sh save` / `close` | Calls `wiki-sync.sh` in dry-run mode; printed text does not mean a handover or push occurred |

Review `git status --short`, `git diff`, and `git diff --cached` before publication. Optional `bunker-push.sh` can stage, commit, and push; use the [operations reference](../extensions/operations/README.md) before invoking it.

## Bundled skills

All thirteen skill definitions live in `skills/`. Their exact triggers, tool needs, and procedures are documented in each `SKILL.md`.

| Skill | Use it for | Typical request |
|---|---|---|
| [`wiki`](../skills/wiki/SKILL.md) | Scaffold and operate a knowledge vault | Set up the wiki |
| [`wiki-ingest`](../skills/wiki-ingest/SKILL.md) | Distill sources into useful linked notes | `ingest .raw/article.md` |
| [`wiki-query`](../skills/wiki-query/SKILL.md) | Answer from existing notes and cite them | `what do you know about rollback?` |
| [`wiki-retrieve`](../skills/wiki-retrieve/SKILL.md) | Retrieve ranked text passages | `retrieve rollback` |
| [`wiki-lint`](../skills/wiki-lint/SKILL.md) | Review vault health and maintenance | `lint the wiki` |
| [`save`](../skills/save/SKILL.md) | File useful conversation knowledge | `save this as Rollback decision` |
| [`autoresearch`](../skills/autoresearch/SKILL.md) | Research and synthesize with source provenance | `/autoresearch deployment checks` |
| [`think`](../skills/think/SKILL.md) | Structure a decision and examine assumptions | `/think how to organize sources` |
| [`canvas`](../skills/canvas/SKILL.md) | Work with Obsidian Canvas files | Create a canvas of these concepts |
| [`defuddle`](../skills/defuddle/SKILL.md) | Extract web-page content when its tool is available | Extract this article |
| [`evidence-index`](../skills/evidence-index/SKILL.md) | Link evidence artifacts and checksums | Index the evidence |
| [`obsidian-markdown`](../skills/obsidian-markdown/SKILL.md) | Obsidian Markdown syntax | Edit a note with properties and wikilinks |
| [`obsidian-bases`](../skills/obsidian-bases/SKILL.md) | Obsidian Bases syntax | Create a filtered base view |

The supplied `setup-opencode.sh` copies ten of these: `wiki`, `wiki-ingest`, `wiki-query`, `save`, `wiki-lint`, `canvas`, `autoresearch`, `obsidian-markdown`, `obsidian-bases`, and `defuddle`. It does not copy `wiki-retrieve`, `think`, or `evidence-index`. Bundled does not mean automatically installed into every runtime.

Code-review and infrastructure skills supplied by an external ECC configuration are separate dependencies. They are not necessary for ordinary local search and are not shipped in this repository.

## Validation targets

| Target | Coverage |
|---|---|
| `make test-core` | CI YAML, wiki/script checks, retrieval, Python/local integration checks |
| `make test-extensions` | Workflow JSON connections and Compose YAML |
| `make test` | Both groups |
| `make test-unit` | Python unit and local lifecycle tests |
| `make test-retrieve` | Index availability and a retrieval smoke query |
| `make test-workflows` | Checked-in workflow structure; does not call n8n |

Use the actual output for the current test count. [Contributing](../CONTRIBUTING.md) lists development requirements. Optional service commands and contracts belong in the [Local API](local-ingest-api.md) and [n8n](N8N-SETUP.md) guides.
