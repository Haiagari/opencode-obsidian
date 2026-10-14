# Repository Audit — Bunker OS

**Audited:** 2026-10-13
**Branch:** `fix/bunker-hardening-docs-privacy`
**Scope:** repository components and skills, privacy-bearing paths, optional webhook posture, end-to-end local workflows, and documentation/code consistency.

## Five requested work items

| Work item | Result |
|---|---|
| Review remaining components and skills | Reviewed all 13 bundled skill entry points, core Python/Bash/Go scripts, optional operation utilities, four n8n workflow files, CI/Make targets, Obsidian settings/plugin manifests, and the wiki integrity output. Fixed concrete behavior/documentation defects listed below. |
| Review privacy exposure | Enumerated tracked `.raw/` and `wiki/sources/` content; scanned reachable text blobs in this branch's Git history for high-signal credential formats; removed two plugin `data.json` files from the current Git tree and strengthened ignore rules. |
| Decide n8n scope | Keep n8n optional. Keep the AOC and alert webhook workflows inactive. CI now rejects an active workflow containing a webhook trigger. The manual Health Check remains active and returns static status only. |
| Add end-to-end tests | Added a local-only lifecycle test covering sanitized capture, atomic wiki writes, retrieval indexing, archiving, commit, and push to a temporary bare Git remote. Added HTTP-handler tests without opening a network listener. Added mocked operation tests for dry-run and archive-branch behavior. |
| Align guides with behavior | Updated README, PROJECT, AGENTS, SECURITY, installation and operations guides, security boundaries, and this report. Added a dedicated local API guide and organized documentation around setup, daily use, and technical references. Replaced four repetitive illustrations with two coordinated visual assets; component roles and data paths are described in the architecture and usage guides. Corrected sanitizer claims and documented the remaining limits. |

## Findings fixed

- The Go ingest endpoint previously accepted requests without a token when its environment variable was empty, stored unsanitized text, used note text in filenames, overwrote collisions, and created world-readable notes. It now requires a token of at least 32 characters, refuses non-loopback binds, sanitizes before storage, applies body and server timeouts, uses opaque filenames and private permissions, publishes atomically, and returns `409` on a duplicate.
- `wiki-integrity.sh` reused the last page's frontmatter type when evaluating other notes. Classification is now per-file. Added regression coverage; added missing frontmatter to `wiki/log.md` and `wiki/herdr.md`.
- FTS indexing previously retained archived notes in search. It now excludes `wiki/**/archive/**` and removes archived pages from the index.
- `bunker-check.sh` failed on a clean checkout because generated evidence reports were absent. It now generates them and checks that Obsidian plugin `data.json` is not tracked.
- `setup-opencode.sh` previously deleted installed skill directories before copying and replaced the MCP config entry wholesale. It now backs up existing skills/config, installs through a staged copy, writes config atomically, preserves unrelated entries, and pins MCPVault.
- `bunker-pulse.sh` previously created its archive directory during dry-run and made an empty pushed branch before archiving the memo on the base branch. Dry-run no longer writes; `--apply` now commits the archive memo on the pushed review branch and creates an issue/draft PR. It requires a clean worktree on its configured base branch.
- `setup-vault.sh` previously downloaded the latest Excalidraw executable without a version or checksum. It now pins the version in the checked-in manifest and validates the published SHA-256 before installing the file.
- `.obsidian/plugins/calendar/data.json` and `.obsidian/plugins/thino/data.json` were tracked despite the ignore policy. They are removed from the current tree, while the local files are left intact in this checkout. New plugin state, inbox notes, lock files, and lint reports are ignored.

## Privacy inventory

- The current tree contains 3 tracked raw research documents under `.raw/` (plus `.gitkeep`) and 23 tracked source notes under `wiki/sources/`. These files are public already; ignore rules cannot make them private or erase earlier versions. Their content is research material. The reviewed high-signal credential patterns produced no matches.
- A scan of 946 reachable text blobs found no matches for the reviewed OpenAI/GitHub/AWS/Google/Slack key formats or private-key headers. Sixteen binary blobs were skipped. This is a targeted pattern scan, not a claim that every possible secret format was ruled out.
- The two plugin state files removed from the current tree contained preferences, not credentials. Their historical blobs remain publicly reachable. No history rewrite was performed.
- The Obsidian Local REST API plugin is enabled in the shared plugin list. Its bundled defaults bind to loopback, use HTTPS, and disable insecure HTTP. A real `data.json` with keys/certificates remains local and ignored.
- `.obsidian/workspace.json` and `workspace-visual.json` remain intentionally tracked as shared layouts. The checked values reference wiki notes and contain no absolute machine paths; review them before adding private vault paths.

## Current vault-integrity findings

The integrity scanner reports 32 unresolved wikilinks, 46 orphan notes, 28 notes shorter than its 30-line threshold, and 3 raw files absent from the ingestion log. Missing frontmatter is now zero. Several link warnings point at intentionally ignored private paths or template placeholders; the rest need content-owner triage. The scanner's raw-file count is a log heuristic, not proof a source was lost. No notes were auto-created or deleted to silence those findings.

## Validation

- `make test`: 197 checks passed at the audit checkpoint (unit, script, HTTP, lifecycle, retrieval, wiki, n8n JSON, and YAML checks).
- `./bin/bunker-check.sh`: passed on this checkout, including evidence generation and the privacy path check.
- `git diff --check`, Bash syntax, Go vet, and Go HTTP tests passed.
- The two revised illustrations were reviewed at full size; filenames and links were checked against the documentation hub and architecture/usage guides.
- Lifecycle publishing used a temporary local bare Git remote. No GitHub issue/PR, n8n service, or external webhook was contacted by the tests.

## Remaining boundaries

- Do not activate AOC or alert webhooks until receiver authentication, request validation, payload limits, and rate limiting exist and have integration tests.
- The sanitizer is best-effort and its output remains untrusted. It is not a prompt-injection security boundary.
- The API and n8n tests do not run a live Obsidian application, Docker container, GitHub API, or an agent's semantic page-filing decisions.
- The 32 link warnings, 46 orphans, 28 short notes, and 3 ingestion-log mismatches remain content-maintenance work rather than blockers for the code changes above.
