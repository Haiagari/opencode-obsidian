# Troubleshooting

[Documentation](README.md) · [Installation](install-guide.md) · [Commands](commands-and-skills.md)

Identify which boundary failed: local setup, source staging, wiki filing, indexing, or an optional service. A successful capture is not proof of filing; a successful build is not proof that every note is indexed.

## Images or banner do not appear

The root README uses `wiki/meta/banner-opencode-obsidian.png` and `docs/diagrams/system-map.png`. Guides under `docs/` use `diagrams/<name>.png`. The [illustration catalog](diagrams/README.md) displays both generated illustrations directly.

Check the rendered Markdown file, not only the GitHub directory listing; an image stored in a folder is not automatically displayed by a README. Also verify the selected branch: changes in a PR are visible in that branch before they are merged to `main`.

```bash
git ls-files wiki/meta/banner-opencode-obsidian.png docs/diagrams/
```

Open the linked PNG from the rendered page. If the asset opens but its embed fails, check relative path/case or the viewer's Markdown support. If the asset cannot open, inspect whether it exists in the selected branch or whether browser/network filtering is blocking image delivery. Repository-relative paths do not refer to a developer's scratch directory.

## Python search prints nothing

Use the CLI wrapper:

```bash
python3 scripts/retrieve.py status
python3 scripts/retrieve.py build
python3 scripts/retrieve.py "knowledge" --top 5
```

`fts_engine.py` defines the search engine but has no command-line entry point. Running it directly can exit without printing a search result. Earlier documentation used that incorrect invocation; use `retrieve.py` or `bm25-index.py`.

## FTS5 is unavailable

If index creation reports `no such module: fts5`, the selected Python's SQLite build lacks that extension. Run the [FTS5 probe](install-guide.md#verify-local-retrieval) with the same `python3` used for indexing. Use a Python installation with SQLite FTS5 support; installing an unrelated pip package does not change the SQLite library already linked into Python.

## A note is missing from search

| Check | Why it matters |
|---|---|
| Does the note exist under `<vault-root>/wiki/`? | `.raw/` and root docs are not indexed |
| Is it below `meta/` or `archive/`? | Those directory names are excluded |
| Did you build after filing/editing/moving it? | Queries use the derived database |
| Are `BUNKER_HOME` / `VAULT_PATH` selecting another vault? | The wrong root can still have a valid index |
| Does one distinctive term match? | Multiple terms narrow lexical matching |
| Was only a source staged? | `bunker-ingest.sh` does not create wiki pages |

Inbox notes are eligible for indexing. Inspect their review status before using them as established knowledge.

## The index is corrupt

Stop concurrent indexing/search processes first. Preserve the affected database directory, then rebuild from Markdown:

```bash
backup_dir="$(mktemp -d)"
# Default-root example. Use the configured vault root if it differs.
if [ -d .vault-meta/fts5 ]; then
  mv .vault-meta/fts5 "$backup_dir/fts5"
fi
python3 scripts/retrieve.py build
python3 scripts/retrieve.py status
```

Moving the whole directory preserves the database and any WAL/SHM companions together. Keep the backup until retrieval is verified. This procedure changes derived search state, not the notes.

## Source staging refuses a file

- **File not found:** pass a readable local file path; quote paths with spaces.
- **URL rejected:** the shell helper accepts local files. Ask `wiki-ingest` to process a URL using its configured web tools.
- **Existing staged filename:** the destination uses the source basename and refuses replacement. Inspect the staged copy and choose a distinct source filename when needed.
- **Sanitizer failure:** resolve the Python/script error. Failure should not be treated as successful ingestion.

A successful stage prints a destination and asks you to run the agent skill. It does not claim that source, entity, or concept pages were created.

## OpenCode cannot load skills or MCP

Confirm you restarted OpenCode after setup and that it uses the intended configuration and skill directories. The installer logs backup paths; preserve them if rollback is needed.

```bash
opencode --version
node --version
npx --version
```

Check that `obsidian-vault` points to the vault root. The supplied installer emits a `stdio`/`command`/`args` entry; validate its schema against the installed runtime rather than assuming compatibility. Tests cover local config mutation and backups, not every OpenCode release. Verify access with a harmless read of `wiki/hot.md` before permitting writes.

The Go memo server on port 9090 is not the MCPVault connection or the Obsidian REST plugin. Starting it will not repair those integrations.

## Context did not restore

Open `wiki/hot.md` and `wiki/index.md` directly. Handovers may be absent in a clean clone. The lifecycle hook file is not proof that OpenCode loaded it; follow [Hooks](../hooks/README.md) and test the installed runtime. A shell status message from `bunker.sh init` is not an agent context load.

## Capture API errors

| Symptom | Inspect |
|---|---|
| Server exits with configuration error | Token length and loopback bind address |
| Connection refused | Server process and port selection |
| `401` | Same credential in client and server environment |
| `400` | Empty or sanitizer-emptied text |
| `409` | The sanitized content already exists in the inbox |
| `413` | Request exceeds 10 MiB or input read fails |
| `500` | Python sanitizer, timeout, write permissions, or atomic publication failure |

Use the [API contract](local-ingest-api.md) for startup, token handling, and complete status semantics. `/health` reports process responsiveness, not write readiness.

## Integrity reports flag unexpected items

A report lists findings rather than automatically fixing them. Orphans and short notes may be intentional. The raw-source heuristic scans top-level `.raw/` files against `wiki/meta/ingestion-log.md`; the ingestion skill's separate `.raw/.manifest.json` does not automatically satisfy that heuristic. Check provenance before reprocessing.

## Tests or n8n checks fail

- Missing `yaml`: install PyYAML in the selected development environment.
- Go checks skipped/unavailable: install Go 1.22+ and ensure `go` is on `PATH`.
- No Docker: core and static-extension tests still run without the service.
- n8n diagnostics fail: inspect local `.env`, `docker compose config --quiet`, and container state as described in [n8n setup](N8N-SETUP.md). Do not paste secrets into reports.

## Report a reproducible problem

Include the commit/branch, OS, relevant tool versions, exact command, exit/error text, and a harmless example input. Say whether you used the default vault root. Remove tokens and private note text. Follow [SECURITY](../SECURITY.md) for a vulnerability report.
