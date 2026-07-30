---
type: meta
title: "Bunker OS Command Center"
updated: 2026-05-14
tags:
  - meta
  - dashboard
  - command-center
  - bunker-os
status: evergreen
related:
  - "[[index]]"
  - "[[overview]]"
  - "[[hot]]"
  - "[[log]]"
  - "[[agent-queue]]"
  - "[[evidence-index]]"
  - "[[INTEGRITY-REPORT]]"
  - "[[knowledge-supply-chain]]"
---

# Bunker OS Command Center

Navigation: [[index]] | [[overview]] | [[hot]] | [[log]] | [[agent-queue]] | [[evidence-index]] | [[INTEGRITY-REPORT]]

This is the operational entry point for Bunker OS. Use it to understand active context, vault health, evidence, agent work, and governance state.

## 1. Active Context

- Current context cache: [[hot]]
- Main map: [[index]]
- Activity log: [[log]]
- Latest handovers: `wiki/meta/handovers/`

## 2. Knowledge Health

Run:

```bash
./bin/wiki-integrity.sh
```

Review:

- [[INTEGRITY-REPORT]]
- `wiki/meta/INTEGRITY-REPORT.json`

Health categories:

- broken active links
- orphan notes
- short notes
- notes missing frontmatter
- raw files not mentioned in ingestion log
- plugin drift
- local plugin config files
- hard-coded local paths

## 3. Evidence Vault

- Evidence index: [[evidence-index]]
- Evidence manifest: `wiki/meta/evidence-manifest.json`
- Original artifacts remain in place, including `report.zip` and `security-audit-report.json`.

Rules:

- Do not edit original evidence in place.
- Notes may interpret evidence only if they link back to the evidence index or manifest.
- Historical audit output must not be treated as current truth without validation.

## 4. Agent Queue

- Queue: [[agent-queue]]
- Ingest agent: `agents/wiki-ingest.md`
- Lint agent: `agents/wiki-lint.md`
- Evidence agent: `agents/evidence-indexer.md`

## 5. Governance

- Rules: `BUNKER_RULES.md`
- Agent instructions: `AGENTS.md`
- ADR template: [[ADR-TEMPLATE]]
- Knowledge supply chain: [[knowledge-supply-chain]]
- Workflows: [[workflows]]
- Governance model: [[governance]]

## 6. Safe Operations

Default safe commands:

```bash
./bin/bunker-check.sh
./bin/wiki-integrity.sh
./bin/evidence-index.sh
./bin/bunker.sh init
./bin/bunker.sh save
```

Commands with external effects require explicit `--apply`:

```bash
./bin/wiki-sync.sh --apply
./bin/bunker-push.sh --apply "commit message"
./bin/bunker-alert.sh --apply "target" "LEVEL" "message"
./bin/bunker-pulse.sh --apply
```

## 7. Obsidian Bases

The interactive Bases dashboard remains available in [[meta/dashboard.base]].

![[meta/dashboard.base]]
