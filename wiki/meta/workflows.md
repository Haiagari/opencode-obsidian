---
type: workflow
title: "Bunker OS Workflows"
updated: 2026-05-14
status: active
tags: [workflow, operations, bunker-os]
related: [[dashboard]], [[knowledge-supply-chain]], [[agent-queue]]
---

# Bunker OS Workflows

## Session Start

```bash
./bin/bunker.sh init
```

Then read:

1. `wiki/hot.md`
2. latest file in `wiki/meta/handovers/`
3. `wiki/meta/dashboard.md`

## Ingest Workflow

1. Place raw source in `.raw/` or send content to the local ingest server.
2. Convert the source into a structured note using `_templates/`.
3. Update `wiki/meta/ingestion-log.md`.
4. Link the note from `wiki/index.md`.
5. Run `./bin/wiki-integrity.sh`.

## Evidence Workflow

```bash
./bin/evidence-index.sh
./bin/wiki-integrity.sh
```

Rules:

- Do not edit original evidence.
- Interpret evidence in wiki notes.
- Link interpretations back to `wiki/meta/evidence-index.md`.

## Safe Sync Workflow

```bash
./bin/wiki-sync.sh
./bin/wiki-sync.sh --apply
```

Default run is review-only. Use `--apply` only after reviewing changed files.

## Release Close Workflow

```bash
./bin/bunker-check.sh
```

Then create/update:

- `docs/releases/<release>.md`
- `wiki/meta/handovers/<date>-<release>.md`
- `CHANGELOG.md`
