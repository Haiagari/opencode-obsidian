# ODD Feature: Personal Knowledge Focus

## Objective
Refocus OpenCode Obsidian as a local-first personal knowledge workflow: capture information, sanitize and organize it in an Obsidian vault, retrieve it reliably, and preserve context and decisions over time. Keep n8n/AOC and general host/repository operations as structurally separate, optional extensions.

## Problem
The repository previously presented itself simultaneously as a personal wiki, agent toolkit, automation platform, and enterprise operations/security system. This diluted the primary user promise and overclaimed some capabilities. Operational scripts were also mixed into the core `bin/` namespace.

## Why
The user selected personal daily use as the primary audience, rejected a documentation-only change as superficial, and selected preserving n8n/AOC and operational tooling as clearly separated optional extensions. When the move exposed an orphan Git gitlink, the user explicitly chose to make the extension a normal repo-owned directory.

## Scope
- Keep the vault, local capture/sanitization, retrieval, integrity, file locking, and context-preservation workflows in the core.
- Move n8n/AOC assets and host/repository operations into explicit `extensions/n8n/` and `extensions/operations/` areas.
- Preserve existing command compatibility with thin shims where useful; do not delete features.
- Decouple core ingestion and core health checks from Docker/n8n availability.
- Update tests, CI, MCP/setup references, and documentation so extension functionality remains testable and usable without making it a core runtime dependency.
- Preserve user data and local credentials; never inspect or print `.env` values.

## Constraints
- Keep repository-facing documentation in English, matching current convention.
- The repo has a GitHub origin and tracked vault content; preserve existing privacy/publication boundaries.
- Do not move whole `bin/`, `scripts/`, `skills/`, or `wiki/` directories; classify individual tools first.
- Preserve ignored local extension configuration during moves.
- No pushes, deployments, Docker startup, or release actions. The user explicitly authorized a commit for finalization; do not push.

## Tasks
- [x] T1 — Write `docs/product-direction.md` as the canonical product focus, workflow, non-goals, and staged roadmap.
- [x] T2 — Align README positioning, comparison, badges, and security language with the personal knowledge workflow.
- [x] T3 — Align PROJECT capability/changelog descriptions with the same product hierarchy and truthful status.
- [x] T4 — Map core versus optional-extension assets, callers, tests, CI, and privacy constraints.
- [x] T5 — Move n8n/AOC assets and integration implementation into repo-owned `extensions/n8n/`, retaining compatible entry points; user authorized replacing the orphan gitlink with normal files.
- [x] T6 — Move host/repository operations into `extensions/operations/` with compatibility shims and clear opt-in docs.
- [x] T7 — Decouple core ingest and health checks from n8n/Docker while retaining optional notifications and diagnostics.
- [x] T8 — Update path consumers, tests, CI, MCP/setup references, and docs; separate core and extension validation responsibilities.
- [x] T9 — Verify core and extension checks, preserved local configuration, compatibility, and final diff.
- [x] T10 — Default the unauthenticated Telegram alert webhook to inactive and document/test the activation guard.
- [x] T11 — Correct dashboard and governance guidance for direct alert sends and receiver security preconditions.
- [x] T12 — Replace the orphan gitlink with normal extension files, preserve ignored `.env`, review/stage only intended changes, and create the user-authorized commit.

## Acceptance Criteria
- README identifies the primary user, problem, and core loop immediately.
- `extensions/n8n/` and `extensions/operations/` visibly contain optional concerns.
- Core knowledge workflows work without Docker/n8n; extension operations and tests remain usable.
- Legacy entry points remain functional compatibility shims.
- Paths used by scripts, tests, CI, MCP setup, and docs resolve after the move.
- Existing workflows and local `.env` data are preserved; no secret values enter tracked files or output.
- No unverified claims imply HMAC verification, enterprise readiness, or complete security guarantees.

## Checks
- `make test` — passed independently; includes core and extension tests without starting Docker.
- `python3 tests/test_core_optional_extensions.py` — 5 tests passed.
- `git diff --check` — passed independently and in parent spot check.
- `extensions/n8n/.env` remains present and ignored; its contents were not read.
- Scoped active-path search found no old `automation/n8n-lab` references; historical integrity reports retain old paths.
- T10: `python3 tests/test_core_optional_extensions.py` — 6 passed; `make test` — 186 passed; `git diff --check` — passed. No Docker was started.
- Finalization staged 52 intended paths, removed the old gitlink, excluded `.env`, and committed after tests and native review. No push, deployment, or Docker run.

## Progress
- T1–T12 completed. The dashboard and governance docs now reflect the current direct-send alert interface and its security preconditions. Native review found the imported Telegram alert webhook active without receiver authentication; the bounded correction disabled it by default, required an explicit strong secret in the sender, documented Header Auth before activation, and added regression coverage.
- The old path was indexed as a gitlink (`160000`, commit `658e1da`) with no `.gitmodules` or recoverable module URL. The user chose to make the moved n8n extension a normal repo-owned directory rather than restore a submodule.
- Compatibility shims remain under existing `bin/` and root script paths; n8n notifications are opt-in (`BUNKER_N8N_ALERTS=1`) and cannot change ingestion or push outcomes.

## Verification Evidence
- Independent verifier: `make test` passed (186 tests overall, including workflow, scripts, integrity, and unit checks); `python3 tests/test_core_optional_extensions.py` passed (5 tests); `git diff --check` passed.
- `extensions/n8n/.env` present and ignored by `extensions/n8n/.gitignore`; no secret contents were read.
- Parent re-ran `git diff --check`; passed.
- Static review found no active old-path references except historical integrity reports. No Docker or live integrations were exercised.
- Native risk assess was unavailable (`empty output`) and failed closed to high; the required independent verification completed. Native review found CRITICAL `R1-001` on the active unauthenticated webhook. The 40-diff-line correction was applied; targeted validation approved the corrected candidate. Non-blocking warnings `R3-001` and `R4-001` remain informational follow-ups.
- Exact native acknowledgement completed for final staged lineage `review-27df857af6346be6`; authority was burned. Commit `a29d953` was created locally; review does not authorize delivery or push.

## Next Step
No further task work is pending. The commit is local; push remains a separate user decision.